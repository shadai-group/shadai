import asyncio
import logging
import os
from typing import Any, AsyncGenerator, Dict, Literal, Optional
from urllib.parse import urljoin

from dotenv import load_dotenv
from requests import Session
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from intelligence.core.decorators import retry_on_server_error
from intelligence.core.exceptions import ConfigurationError, IntelligenceAPIError
from intelligence.core.schemas import JobResponse, JobStatus, SessionCreate, SessionResponse

logger = logging.getLogger(__name__)
load_dotenv()

console = Console()


class IntelligenceAdapter:
    """Intelligence API adapter with robust error handling."""

    def __init__(self) -> None:
        """
        Initialize the adapter with configuration.

        Args:
            base_url (Optional[str]): Base URL for the API. Defaults to localhost.

        Raises:
            ConfigurationError: If INTELLIGENCE_API_KEY is not set.
        """
        self.base_url = "https://api.intel.shadai.ai"
        self.api_key = os.getenv("INTELLIGENCE_API_KEY")
        if not self.api_key:
            raise ConfigurationError("INTELLIGENCE_API_KEY environment variable not set")
        self._session = Session()
        self._session.headers.update({"ApiKey": self.api_key})

    @retry_on_server_error()
    async def _make_request(self, method: str, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """Make HTTP request with retry logic and error handling."""
        url = urljoin(self.base_url, endpoint)
        kwargs["timeout"] = kwargs.get("timeout", 25)

        response = self._session.request(method=method, url=url, **kwargs)
        response.raise_for_status()
        return response.json()

    async def _get_job_status(self, job_id: str) -> JobResponse:
        """
        Get the status of a job.
        """
        try:
            response = await self._make_request("GET", f"/jobs/{job_id}")
            return JobResponse.model_validate(response)
        except Exception as e:
            logger.error("Failed to get job status: %s", str(e))
            raise IntelligenceAPIError(f"Failed to get job status: {str(e)}") from e

    async def _poll_job(self, job_id: str, interval: float) -> AsyncGenerator[JobResponse, None]:
        """
        Poll job status until completion.

        Args:
            job_id (str): The job identifier to poll
            interval (float): Time in seconds between polls

        Yields:
            JobResponse: Current status of the job
        """
        while True:
            response = await self._get_job_status(job_id=job_id)
            yield JobResponse.model_validate(response)
            await asyncio.sleep(interval)

    async def _wait_for_job(
        self, job_id: str, polling_interval: float = 5.0, timeout: float = 25
    ) -> str:
        """
        Wait for job completion with timeout.

        Args:
            job_id (str): The job identifier to wait for
            polling_interval (float): Time in seconds between status checks. Defaults to 5.0.
            timeout (float): Maximum time to wait in seconds. Defaults to 25.

        Returns:
            str: The job result data

        Raises:
            IntelligenceAPIError: If job fails or times out
        """
        try:
            async with asyncio.timeout(timeout):
                async for status in self._poll_job(job_id=job_id, interval=polling_interval):
                    if status.status == JobStatus.COMPLETED:
                        return status.data.get("response", "")
                    if status.status == JobStatus.FAILED:
                        raise IntelligenceAPIError(f"Job {job_id} failed: Unknown error")
            return f"There was an error processing your request. Job ID: {job_id}"
        except asyncio.TimeoutError:
            raise IntelligenceAPIError(f"Job {job_id} timed out after {timeout} seconds")

    async def ingest(self, session_id: str) -> str:
        """
        Start ingestion process and wait for completion.

        Args:
            session_id (str): The session identifier for ingestion

        Returns:
            str: Result of the ingestion process

        Raises:
            IntelligenceAPIError: If ingestion fails
        """
        try:
            response = await self._make_request(method="POST", endpoint=f"/ingestion/{session_id}")
            return await self._wait_for_job(
                job_id=response.get("job_id"), polling_interval=10, timeout=600
            )
        except Exception as e:
            logger.error("Ingestion failed: %s", str(e))
            raise IntelligenceAPIError(f"Ingestion failed: {str(e)}") from e

    async def query(self, session_id: str, query: str) -> str:
        """
        Execute query and wait for response.

        Args:
            session_id (str): The session identifier
            query (str): The query to execute

        Returns:
            str: The query result

        Raises:
            IntelligenceAPIError: If query execution fails
        """
        try:
            job_response = await self._make_request(
                method="GET", endpoint=f"/querying/{session_id}", params={"query": query}
            )
            return await self._wait_for_job(
                job_id=job_response.get("job_id"), polling_interval=5, timeout=180
            )
        except Exception as e:
            logger.error("Query failed: %s", str(e))
            raise IntelligenceAPIError(f"Query failed: {str(e)}") from e

    async def create_session(
        self, type: Literal["light", "standard", "deep"], **kwargs: Any
    ) -> SessionResponse:
        """Create new processing session."""
        session_create = SessionCreate(config_name=type, **kwargs)
        console.status(f"\n[bold blue]🔧 Creating new {type} session...[/]",spinner="dots", spinner_style="blue")

        try:
            response = await self._make_request(
                method="POST", endpoint="/sessions", json=session_create.model_dump()
            )
            session_response = SessionResponse(**response)
            table = Table(title="Session Configuration", show_header=True, header_style="bold blue")
            table.add_column("Parameter", style="cyan")
            table.add_column("Value", style="green")

            config = session_response.model_dump()
            for key, value in config.items():
                table.add_row(key, str(value))

            console.print(table)
            return session_response
        except Exception as e:
            logger.error("Failed to create session: %s", str(e))
            raise IntelligenceAPIError("Session creation failed") from e

    async def get_session(self, session_id: str) -> SessionResponse:
        """Get session by ID.

        Args:
            session_id (str): The session identifier

        Returns:
            str: The session ID

        Raises:
            IntelligenceAPIError: If session retrieval fails
        """
        try:
            response = await self._make_request(method="GET", endpoint=f"/sessions/{session_id}")
            return SessionResponse.model_validate(response)
        except Exception as e:
            logger.error("Failed to get session: %s", str(e))
            raise IntelligenceAPIError(f"Session retrieval failed: {str(e)}") from e

    async def delete_session(self, session_id: str) -> None:
        """
        Delete session and wait for completion.

        Args:
            session_id: The session identifier to delete

        Raises:
            IntelligenceAPIError: If deletion fails
        """
        try:
            response = await self._make_request(method="DELETE", endpoint=f"/sessions/{session_id}")
            await self._wait_for_job(job_id=response.get("job_id"), polling_interval=5, timeout=180)
        except Exception as e:
            logger.error("Failed to delete session: %s", str(e))
            raise IntelligenceAPIError(f"Session deletion failed: {str(e)}") from e

    async def _get_presigned_url(self, session_id: str) -> str:
        """Generate a pre-signed URL for file upload."""
        try:
            response = await self._make_request(method="GET", endpoint=f"/ingestion/{session_id}")
            return response.get("url")
        except Exception as e:
            logger.error("Failed to generate upload URL: %s", str(e))
            raise IntelligenceAPIError(f"Failed to generate upload URL: {str(e)}") from e
