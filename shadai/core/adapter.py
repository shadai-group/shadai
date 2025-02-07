import asyncio
import logging
import os
from typing import Any, AsyncGenerator, Dict, Literal, Optional

from dotenv import load_dotenv
from requests import Session
from rich.console import Console
from rich.table import Table

from shadai.core.decorators import retry_on_server_error
from shadai.core.exceptions import ConfigurationError, IntelligenceAPIError
from shadai.core.schemas import JobResponse, JobStatus, SessionCreate, SessionResponse

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
        self.base_url = "https://api.shadai.ai"
        self.api_key = os.getenv("SHADAI_API_KEY")
        if not self.api_key:
            raise ConfigurationError("SHADAI_API_KEY environment variable not set")
        self._session = Session()
        self._session.headers.update({"ApiKey": self.api_key})

    def _construct_url(self, endpoint: str) -> str:
        """Construct the full URL from the base URL and endpoint."""
        if not self.base_url.endswith("/"):
            self.base_url += "/"
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        return self.base_url + endpoint

    @retry_on_server_error()
    async def _make_request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic and error handling."""
        url = self._construct_url(endpoint)
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

    async def _poll_job(
        self, job_id: str, interval: float
    ) -> AsyncGenerator[JobResponse, None]:
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

    async def _wait_until_final_status(
        self, poll_generator: AsyncGenerator[JobResponse, None], timeout: float
    ) -> JobResponse:
        """
        Wait until job reaches a final status (COMPLETED or FAILED).

        Args:
            poll_generator: The polling generator
            timeout: Maximum time to wait in seconds

        Returns:
            JobResponse with final status

        Raises:
            TimeoutError if timeout is reached
        """

        while True:
            response = await asyncio.wait_for(
                poll_generator.__anext__(), timeout=timeout
            )
            if response.status in {JobStatus.COMPLETED, JobStatus.FAILED}:
                return response

    async def _wait_for_job(
        self,
        job_id: str,
        polling_interval: float = 5.0,
        timeout: float = 25,
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
            IntelligenceAPIError: If job fails, times out, or exceeds max attempts
        """
        try:
            poll_generator = self._poll_job(job_id=job_id, interval=polling_interval)
            response = await self._wait_until_final_status(
                poll_generator=poll_generator, timeout=timeout
            )

            if response.status == JobStatus.COMPLETED:
                return response.result
            if response.status == JobStatus.FAILED:
                raise IntelligenceAPIError(f"Job {job_id} failed: Unknown error")

        except asyncio.TimeoutError:
            raise IntelligenceAPIError(
                f"Job {job_id} timed out after {timeout} seconds"
            )

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
            response = await self._make_request(
                method="POST", endpoint=f"/ingestion/{session_id}"
            )
            return await self._wait_for_job(
                job_id=response.get("job_id"), polling_interval=10, timeout=600
            )
        except Exception as e:
            logger.error("Ingestion failed: %s", str(e))
            raise IntelligenceAPIError(f"Ingestion failed: {str(e)}") from e

    async def _handle_job_with_retries(
        self,
        job_response: dict,
        operation_name: str,
        max_retries: int = 3,
        retry_delay: int = 5,
        polling_interval: int = 5,
        timeout: int = 180,
    ) -> str:
        """
        Handle job execution with retries for empty responses.

        Args:
            job_response: The response containing the job ID
            operation_name: Name of the operation for logging
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            polling_interval: Interval for polling job status
            timeout: Timeout for job completion

        Returns:
            str: The job result

        Raises:
            IntelligenceAPIError: If job fails or returns empty response after all retries
        """
        for attempt in range(max_retries):
            response = await self._wait_for_job(
                job_id=job_response.get("job_id"),
                polling_interval=polling_interval,
                timeout=timeout,
            )
            if "empty response" not in response.lower():
                return response

            if attempt < max_retries - 1:
                logger.warning(
                    f"{operation_name} returned 'Empty response' on attempt {attempt + 1}/{max_retries}, retrying in {retry_delay} seconds..."
                )
                await asyncio.sleep(retry_delay)
                continue

        raise IntelligenceAPIError(
            f"{operation_name} returned 'Empty response' after all retry attempts. The server might still be processing the data."
        )

    async def query(
        self, session_id: str, query: str, max_retries: int = 3, retry_delay: int = 5
    ) -> str:
        """Execute query and wait for response."""
        try:
            job_response = await self._make_request(
                method="GET",
                endpoint=f"/querying/{session_id}",
                params={"query": query},
            )
            return await self._handle_job_with_retries(
                job_response=job_response,
                operation_name="Query",
                max_retries=max_retries,
                retry_delay=retry_delay,
            )
        except Exception as e:
            logger.error("Query failed: %s", str(e))
            raise IntelligenceAPIError(f"Query failed: {str(e)}") from e

    async def create_session(
        self, type: Literal["light", "standard", "deep"], **kwargs: Any
    ) -> SessionResponse:
        """
        Create new processing session.
        """
        session_create = SessionCreate(config_name=type, **kwargs)
        console.print(f"[bold blue]🔧 Creating new {type} session...[/]")
        response = await self._make_request(
            method="POST", endpoint="/sessions", json=session_create.model_dump()
        )
        session_response = SessionResponse(**response)
        table = Table(
            title="Session Configuration", show_header=True, header_style="bold blue"
        )
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="green")

        config = session_response.model_dump()
        for key, value in config.items():
            table.add_row(key, str(value))
        console.print(table)
        return session_response

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
            response = await self._make_request(
                method="GET", endpoint=f"/sessions/{session_id}"
            )
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
            response = await self._make_request(
                method="DELETE", endpoint=f"/sessions/{session_id}"
            )
            await self._wait_for_job(
                job_id=response.get("job_id"), polling_interval=5, timeout=180
            )
        except Exception as e:
            logger.error("Failed to delete session: %s", str(e))
            raise IntelligenceAPIError(f"Session deletion failed: {str(e)}") from e

    async def _get_presigned_url(self, session_id: str, filename: str) -> str:
        """Generate a pre-signed URL for file upload."""
        try:
            response = await self._make_request(
                method="GET",
                endpoint=f"/ingestion/{session_id}",
                params={"filename": filename},
            )
            return response.get("url")
        except Exception as e:
            logger.error("Failed to generate upload URL: %s", str(e))
            raise IntelligenceAPIError(
                f"Failed to generate upload URL: {str(e)}"
            ) from e

    async def _get_session_summary(self, session_id: str) -> str:
        """Get session summary."""
        try:
            job_response = await self._make_request(
                method="GET", endpoint=f"/sessions/{session_id}/summary"
            )
            return await self._handle_job_with_retries(
                job_response=job_response, operation_name="Session summary"
            )
        except Exception as e:
            logger.error("Failed to get session summary: %s", str(e))
            raise IntelligenceAPIError(
                f"Failed to get session summary: {str(e)}"
            ) from e

    async def _create_article(
        self, session_id: str, topic: str, n_docs: Optional[int] = None
    ) -> str:
        """Create an article on the topic."""
        try:
            job_response = await self._make_request(
                method="POST",
                endpoint=f"/sessions/{session_id}/articles",
                params={"topic": topic, "n_docs": n_docs},
            )
            return await self._handle_job_with_retries(
                job_response=job_response, operation_name="Article creation"
            )
        except Exception as e:
            logger.error("Failed to create article: %s", str(e))
            raise IntelligenceAPIError(f"Failed to create article: {str(e)}") from e

    async def _llm_call(self, session_id: str, prompt: str) -> str:
        """Call the LLM with the prompt."""
        try:
            job_response = await self._make_request(
                method="POST",
                endpoint=f"/llms/{session_id}/call",
                json={"prompt": prompt},
            )
            return await self._handle_job_with_retries(
                job_response=job_response, operation_name="LLM call"
            )
        except Exception as e:
            logger.error("Failed to call LLM: %s", str(e))
            raise IntelligenceAPIError(f"Failed to call LLM: {str(e)}") from e
