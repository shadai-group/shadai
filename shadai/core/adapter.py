import asyncio
import logging
import os
import random
from typing import Any, AsyncGenerator, Dict, Literal, Optional

from dotenv import load_dotenv
from requests import Session
from rich.console import Console

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
            ConfigurationError: If SHADAI_API_KEY is not set.
        """
        self.core_base_url = "http://127.0.0.1:8000"
        self.api_key = os.getenv("SHADAI_API_KEY")
        if not self.api_key:
            raise ConfigurationError("SHADAI_API_KEY environment variable not set")
        self._session = Session()
        self._session.headers.update({"ApiKey": self.api_key})

    def _construct_url(self, endpoint: str) -> str:
        """Construct the full URL from the base URL and endpoint."""
        if not self.core_base_url.endswith("/"):
            self.core_base_url += "/"
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        return self.core_base_url + endpoint

    @retry_on_server_error()
    async def _make_request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic and error handling."""
        url = self._construct_url(endpoint)
        kwargs["timeout"] = kwargs.get("timeout", 25)

        response = self._session.request(method=method, url=url, **kwargs)
        if response.status_code == 402:
            raise IntelligenceAPIError(
                "Insufficient balance. Please top up your account."
            )
        response.raise_for_status()
        json_response = response.json()
        return json_response.get("data")

    async def _get_job_status(
        self, job_id: str, max_retries: int = 5, retry_delay: float = 1.0
    ) -> JobResponse:
        """
        Get the status of a job with retry for None responses.

        Args:
            job_id: The job identifier
            max_retries: Maximum number of retries for None responses
            retry_delay: Initial delay between retries (with exponential backoff)

        Returns:
            JobResponse: The job status response

        Raises:
            IntelligenceAPIError: If job status check fails after all retries
        """
        for attempt in range(max_retries):
            try:
                response = await self._make_request("GET", f"/jobs/{job_id}")
                if response is None:
                    # API returned None during temporary unavailability
                    if attempt < max_retries - 1:
                        # Use exponential backoff with jitter
                        backoff_delay = (
                            retry_delay * (2**attempt) * (1 + random.random() * 0.1)
                        )
                        logger.warning(
                            f"Job status check received None response (attempt {attempt + 1}/{max_retries}), "
                            f"retrying in {backoff_delay:.2f} seconds..."
                        )
                        await asyncio.sleep(backoff_delay)
                        continue
                    else:
                        raise IntelligenceAPIError(
                            f"Job status check failed: Received None response after {max_retries} attempts"
                        )

                return JobResponse.model_validate(response)

            except Exception as e:
                if attempt < max_retries - 1 and "NoneType" in str(e):
                    # Handle NoneType errors with exponential backoff
                    backoff_delay = (
                        retry_delay * (2**attempt) * (1 + random.random() * 0.1)
                    )
                    await asyncio.sleep(backoff_delay)
                    continue
                else:
                    logger.error("Failed to get job status: %s", str(e))
                    raise IntelligenceAPIError(
                        f"Failed to get job status: {str(e)}"
                    ) from e

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
        retries = 0
        max_consecutive_failures = 5

        while True:
            try:
                response = await self._get_job_status(job_id=job_id)
                # Reset retry counter on success
                retries = 0
                yield response

                # If job is done, no need to continue polling
                if response.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                    break

                await asyncio.sleep(interval)

            except Exception as e:
                retries += 1
                if retries < max_consecutive_failures:
                    logger.warning(
                        f"Job polling failed (attempt {retries}/{max_consecutive_failures}), "
                        f"retrying in {interval} seconds... Error: {str(e)}"
                    )
                    await asyncio.sleep(interval)
                    continue
                else:
                    logger.error(
                        f"Job polling failed after {max_consecutive_failures} attempts: {str(e)}"
                    )
                    raise

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
        polling_interval: float = 10.0,
        timeout: float = 30,
        max_retries: int = 5,
    ) -> str:
        """
        Wait for job completion with timeout and retry on temporary service unavailability.

        Args:
            job_id (str): The job identifier to wait for
            polling_interval (float): Time in seconds between status checks. Defaults to 10.0.
            timeout (float): Maximum time to wait in seconds. Defaults to 30.
            max_retries (int): Maximum number of consecutive retries on failure. Defaults to 5.

        Returns:
            str: The job result data

        Raises:
            IntelligenceAPIError: If job fails, times out, or exceeds max attempts
        """
        try:
            poll_generator = self._poll_job(job_id=job_id, interval=polling_interval)

            # Use a higher timeout for _wait_until_final_status to allow for recovery from temporary unavailability
            response = await self._wait_until_final_status(
                poll_generator=poll_generator, timeout=timeout * 1.5
            )

            if response.status == JobStatus.COMPLETED:
                if response.result is None:
                    # Special handling for None result from a completed job
                    logger.warning(
                        f"Job {job_id} completed but returned None result, treating as empty response"
                    )
                    return "Empty response from the server. The data might still be processing."
                return response.result

            if response.status == JobStatus.FAILED:
                raise IntelligenceAPIError(f"Job {job_id} failed: Unknown error")

            # This should not happen (status not COMPLETED or FAILED)
            logger.error(
                f"Job {job_id} ended with unexpected status: {response.status}"
            )
            raise IntelligenceAPIError(
                f"Job {job_id} ended with unexpected status: {response.status}"
            )

        except asyncio.TimeoutError:
            # Log extra information when timeout occurs
            logger.error(f"Job {job_id} timed out after {timeout} seconds")
            raise IntelligenceAPIError(
                f"Job {job_id} timed out after {timeout} seconds. The service may be experiencing high load."
            )
        except Exception as e:
            # More detailed logging for any other exceptions
            logger.error(f"Error waiting for job {job_id}: {str(e)}")
            if "NoneType" in str(e):
                # Handle NoneType errors specifically
                logger.warning(
                    f"NoneType error detected for job {job_id}, service may be temporarily unavailable"
                )
                raise IntelligenceAPIError(
                    f"Service temporarily unavailable while processing job {job_id}. Please try again later."
                ) from e
            raise IntelligenceAPIError(
                f"Error waiting for job {job_id}: {str(e)}"
            ) from e

    async def ingest(self, session_id: str, max_retries: int = 3) -> str:
        """
        Start ingestion process and wait for completion with enhanced error handling.

        Args:
            session_id (str): The session identifier for ingestion
            max_retries (int): Maximum number of retries for transient errors

        Returns:
            str: Result of the ingestion process

        Raises:
            IntelligenceAPIError: If ingestion fails after all retries
        """
        retries = 0
        last_error = None

        while retries < max_retries:
            try:
                # Try to start the ingestion process
                response = await self._make_request(
                    method="POST", endpoint=f"/ingestion/{session_id}"
                )

                if not response or "job_id" not in response:
                    # Handle case where response is None or missing job_id
                    logger.warning(
                        f"Ingestion request returned invalid response: {response} "
                        f"(attempt {retries + 1}/{max_retries})"
                    )
                    retries += 1
                    await asyncio.sleep(2**retries)  # Exponential backoff
                    continue

                # Wait for the job to complete with enhanced timeout
                return await self._wait_for_job(
                    job_id=response.get("job_id"),
                    polling_interval=10,
                    timeout=600,
                    max_retries=5,
                )

            except Exception as e:
                last_error = e
                # Check if this is a NoneType error (likely temporary service unavailability)
                if "NoneType" in str(e):
                    retries += 1
                    if retries < max_retries:
                        backoff = 2**retries
                        logger.warning(
                            f"Ingestion encountered temporary service unavailability "
                            f"(attempt {retries}/{max_retries}), retrying in {backoff} seconds... Error: {str(e)}"
                        )
                        await asyncio.sleep(backoff)
                        continue
                    else:
                        logger.error(
                            f"Ingestion failed after {max_retries} attempts: {str(e)}"
                        )
                        raise IntelligenceAPIError(
                            f"Ingestion failed due to service unavailability after {max_retries} attempts. "
                            f"Please try again later."
                        ) from e
                else:
                    # For other errors, just raise immediately
                    logger.error(f"Ingestion failed: {str(e)}")
                    raise IntelligenceAPIError(f"Ingestion failed: {str(e)}") from e

        # This should only be reached if all retries are exhausted
        logger.error(f"Ingestion failed after {max_retries} attempts")
        raise IntelligenceAPIError(
            f"Ingestion failed after {max_retries} attempts: {str(last_error)}"
        )

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

    async def get_presigned_url(self, session_id: str, filename: str) -> str:
        """Generate a pre-signed URL for file upload.

        Args:
            session_id (str): The session identifier
            filename (str): The filename to upload

        Returns:
            str: The pre-signed URL
        """
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

    async def create_session(
        self, type: Literal["light", "standard", "deep"], **kwargs: Any
    ) -> SessionResponse:
        """
        Create new processing session.
        """
        session_create = SessionCreate(config_name=type, **kwargs)
        response = await self._make_request(
            method="POST", endpoint="/sessions", json=session_create.model_dump()
        )
        session_response = SessionResponse.model_validate(response)
        return session_response

    async def get_session(
        self, session_id: Optional[str] = None, alias: Optional[str] = None
    ) -> Optional[SessionResponse]:
        """Get session by ID.

        Args:
            session_id (Optional[str]): The session identifier
            alias (Optional[str]): The alias to use for the session
        Returns:
            Optional[SessionResponse]: The session response or None if the session is not found

        Raises:
            IntelligenceAPIError: If session retrieval fails
        """
        try:
            response = await self._make_request(
                method="GET",
                endpoint=f"/sessions/{session_id}",
                params={"alias": alias},
            )
            if alias is not None and response is None:
                return None
            return SessionResponse.model_validate(response)
        except Exception as e:
            logger.error("Failed to get session: %s", str(e))
            raise IntelligenceAPIError(f"Session retrieval failed: {str(e)}") from e

    async def delete_session(
        self, session_id: Optional[str] = None, alias: Optional[str] = None
    ) -> None:
        """
        Delete session and wait for completion.

        Args:
            session_id (Optional[str]): The session identifier to delete
            alias (Optional[str]): The alias to use for the session
        Raises:
            IntelligenceAPIError: If deletion fails
        """
        try:
            response = await self._make_request(
                method="DELETE",
                endpoint=f"/sessions/{session_id}",
                params={"alias": alias},
            )
            await self._wait_for_job(
                job_id=response.get("job_id"), polling_interval=5, timeout=180
            )
        except Exception as e:
            logger.error("Failed to delete session: %s", str(e))
            raise IntelligenceAPIError(f"Session deletion failed: {str(e)}") from e

    async def cleanup_namespace(self) -> None:
        """
        Cleanup the namespace

        Raises:
            IntelligenceAPIError: If cleanup fails
        """
        try:
            response = await self._make_request(
                method="DELETE",
                endpoint="/sessions/",
            )
            await self._wait_for_job(
                job_id=response.get("job_id"), polling_interval=5, timeout=180
            )
        except Exception as e:
            logger.error("Failed to delete session: %s", str(e))
            raise IntelligenceAPIError(f"Session deletion failed: {str(e)}") from e

    async def list_sessions(self):
        """
        List all sessions related to an user

        Returns:
            List[SessionResponse]: A list of session responses
        """
        try:
            response = await self._make_request(method="GET", endpoint="/sessions/")
            return [SessionResponse.model_validate(session) for session in response]
        except Exception as e:
            logger.error("Failed to list sessions: %s", str(e))
            raise IntelligenceAPIError(f"Failed to list sessions: {str(e)}") from e

    async def query(
        self,
        session_id: str,
        query: str,
        role: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: int = 5,
    ) -> str:
        """Execute query and wait for response.

        Args:
            session_id (str): The session identifier
            query (str): The query to execute
            role (Optional[str]): The role to use for the query
            max_retries (int): Maximum number of retry attempts
            retry_delay (int): Delay between retries in seconds

        Returns:
            str: The query response

        Raises:
            IntelligenceAPIError: If query fails or returns empty response after all retries
        """
        try:
            job_response = await self._make_request(
                method="GET",
                endpoint=f"/retrieval/{session_id}/query",
                params={"query": query, "role": role},
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

    async def get_knowledge_summary(self, session_id: str) -> str:
        """Get session knowledge summary.

        Args:
            session_id (str): The session identifier

        Returns:
            str: The knowledge summary
        """
        try:
            job_response = await self._make_request(
                method="GET", endpoint=f"/retrieval/{session_id}/summary"
            )
            return await self._handle_job_with_retries(
                job_response=job_response, operation_name="Knowledge summary"
            )
        except Exception as e:
            logger.error("Failed to get knowledge summary: %s", str(e))
            raise IntelligenceAPIError(
                f"Failed to get knowledge summary: {str(e)}"
            ) from e

    async def create_article(self, session_id: str, topic: str) -> str:
        """Create an article on the topic.

        Args:
            session_id (str): The session identifier
            topic (str): The topic to create the article on

        Returns:
            str: The article creation response
        """
        try:
            job_response = await self._make_request(
                method="POST",
                endpoint=f"/retrieval/{session_id}/article",
                json={"topic": topic},
            )
            return await self._handle_job_with_retries(
                job_response=job_response, operation_name="Article creation"
            )
        except Exception as e:
            logger.error("Failed to create article: %s", str(e))
            raise IntelligenceAPIError(f"Failed to create article: {str(e)}") from e

    async def chat(
        self, session_id: str, message: str, system_prompt: Optional[str] = None
    ) -> str:
        """Chat with the LLM using the session context and knowledge base.

        Args:
            session_id (str): The session identifier
            message (str): The message to send to the LLM
            system_prompt (Optional[str]): The system prompt to use for the chat

        Returns:
            str: The chat response
        """
        try:
            job_response = await self._make_request(
                method="POST",
                endpoint=f"/inference/{session_id}/chat",
                json={"message": message, "system_prompt": system_prompt},
            )
            return await self._handle_job_with_retries(
                job_response=job_response, operation_name="Chat"
            )
        except Exception as e:
            logger.error("Failed to chat: %s", str(e))
            raise IntelligenceAPIError(f"Failed to chat: {str(e)}") from e

    async def llm_call(self, session_id: str, prompt: str) -> str:
        """Call the LLM with the prompt.

        Args:
            session_id (str): The session identifier
            prompt (str): The prompt to send to the LLM

        Returns:
            str: The LLM response
        """
        try:
            job_response = await self._make_request(
                method="POST",
                endpoint=f"/inference/{session_id}/completion",
                json={"prompt": prompt},
            )
            return await self._handle_job_with_retries(
                job_response=job_response, operation_name="LLM call"
            )
        except Exception as e:
            logger.error("Failed to call LLM: %s", str(e))
            raise IntelligenceAPIError(f"Failed to call LLM: {str(e)}") from e

    async def cleanup_chat(self, session_id: str) -> None:
        """
        Cleanup the chat history.

        Args:
            session_id (str): The session identifier to cleanup
        Raises:
            IntelligenceAPIError: If cleanup fails
        """
        try:
            job_response = await self._make_request(
                method="DELETE",
                endpoint=f"/inference/{session_id}/cleanup-chat",
            )
            await self._wait_for_job(
                job_id=job_response.get("job_id"), polling_interval=5, timeout=180
            )
        except Exception as e:
            logger.error("Failed to cleanup chat: %s", str(e))
            raise IntelligenceAPIError(f"Chat cleanup failed: {str(e)}") from e
