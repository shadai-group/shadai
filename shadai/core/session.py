import asyncio
import logging
import os
from pathlib import Path
from typing import List, Literal, Optional

from requests.exceptions import RequestException
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from shadai.core.adapter import IntelligenceAdapter
from shadai.core.enums import AIModels, MediaFileExtensions, QueryMode
from shadai.core.exceptions import IngestionError
from shadai.core.files import FileManager
from shadai.core.schemas import JobResponse, Query, QueryResponse, SessionResponse

logger = logging.getLogger(__name__)
console = Console()


class Session:
    """
    A session manager for the Intelligence API that handles file ingestion and querying.

    Args:
        session_id (Optional[str]): The session ID to use.
        alias (Optional[str]): The alias to use for the session.
        type (Literal["light", "standard", "deep"]): The type of session to create.
        llm_model (str): The LLM model to use.
        llm_temperature (float): The temperature to use for the LLM.
        llm_max_tokens (int): The maximum number of tokens to use for the LLM.
        query_mode (str): The query mode to use.
        language (str): The language to use for the session.
        delete (bool): Whether to delete the session after it is no longer needed.

    Returns:
        Session: The session object
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        alias: Optional[str] = None,
        type: Literal["light", "standard", "deep"] = "standard",
        llm_model: AIModels = AIModels.CLAUDE_3_5_HAIKU,
        llm_temperature: float = 0.7,
        llm_max_tokens: int = 4096,
        query_mode: QueryMode = QueryMode.HYBRID,
        language: str = "es",
        delete: bool = True,
    ) -> None:
        """Initialize a new session with the specified parameters."""
        self._adapter = IntelligenceAdapter()
        self._file_manager = FileManager()
        self._session_id = session_id
        self._alias = alias
        self._type = type
        self._llm_model = llm_model.value
        self._llm_temperature = llm_temperature
        self._llm_max_tokens = llm_max_tokens
        self._query_mode = query_mode.value
        self._language = language
        self._delete = delete

    @property
    def id(self) -> Optional[str]:
        """Get the session ID.

        Returns:
            Optional[str]: The session ID
        """
        return self._session_id

    async def __aenter__(self) -> "Session":
        """Async context manager entry.

        Returns:
            Session: The session object
        """
        console.print("\n[bold blue]🚀 Initializing Intelligence Session...[/]")

        self._session_id = await self._get()
        console.print("[bold green]✓[/] Session initialized successfully\n")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit.

        Args:
            exc_type (type): The exception type
            exc_val (Exception): The exception value
            exc_tb (traceback): The exception traceback
        """
        if self._delete:
            await self.delete()

    async def _get(self) -> str:
        """Get the session ID."""
        if self._session_id or self._alias:
            with console.status("[bold yellow]Getting existing session..."):
                session = await self._adapter.get_session(
                    session_id=self._session_id, alias=self._alias
                )
                if session is None and self._alias is not None:
                    console.print(
                        f"[bold red]✗[/] [bold red]Session not found with alias:[/] [bold white]{self._alias}[/]"
                    )
                else:
                    console.print(
                        f"[bold green]✓ Retrieved existing session ->[/] alias: [bold white]{session.alias}[/] ([bold white]ID:[/] {session.session_id})"
                    )
            if session is None and self._alias is not None:
                session = await self._create()
        else:
            session = await self._create()
        return session.session_id

    async def _create(self) -> SessionResponse:
        """Create a new session."""
        with console.status(f"[bold yellow]Creating new {self._type} session...\n\n"):
            session: SessionResponse = await self._adapter.create_session(
                type=self._type,
                llm_model=self._llm_model,
                llm_temperature=self._llm_temperature,
                llm_max_tokens=self._llm_max_tokens,
                query_mode=self._query_mode,
                language=self._language,
                alias=self._alias,
            )
            table = Table(
                title="Session Configuration",
                show_header=True,
                header_style="bold blue",
            )
            table.add_column("Parameter", style="cyan")
            table.add_column("Value", style="green")
            config = session.model_dump()
            for key, value in config.items():
                table.add_row(key, str(value))
            console.print(table)

        console.print("\n[bold green]✓[/] Session created successfully")
        console.print(
            f"[bold green]✓[/] Alias: [bold yellow]{session.alias}[/] (ID: {session.session_id})"
        )
        return session

    async def _upload_files(
        self,
        input_dir: str,
        session_id: str,
        destination: Literal["documents", "media"] = "documents",
        max_concurrent_uploads: int = 5,
    ) -> List[Path]:
        """Upload files from the input directory in parallel.

        Args:
            input_dir (str): The path to the directory containing the files to upload.
            session_id (str): The session ID to use for uploading.
            destination (Literal["documents", "media"]): The destination to upload the files to.
            max_concurrent_uploads (int): The maximum number of files to upload concurrently.

        Returns:
            List[Path]: List of successfully uploaded files.

        Raises:
            FileNotFoundError: If the directory doesn't exist.
            ValueError: If no files are found in the directory.
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_dir}")

        if not session_id:
            raise ValueError("Session ID is required")

        files = [
            f
            for f in input_path.rglob("*")
            if f.is_file() and not f.name.startswith(".")
        ]
        if not files:
            raise ValueError(f"No files found in directory: {input_dir}")

        total_files = len(files)
        total_bytes = sum(os.path.getsize(f) for f in files)

        console.print(
            f"[bold yellow]Found {total_files} files to process ({total_bytes / (1024*1024):.1f} MB total)[/]"
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            DownloadColumn(binary_units=True),
            expand=True,
            refresh_per_second=10,
        ) as progress:
            overall_task_id = progress.add_task(
                "[bold blue]Overall Progress", total=total_bytes, start=True
            )

            for i in range(0, total_files, max_concurrent_uploads):
                chunk = files[i : i + max_concurrent_uploads]
                upload_tasks = [
                    self._file_manager._upload_file(
                        session_id=session_id,
                        file_path=file_path,
                        destination=destination,
                        progress=progress,
                        overall_task_id=overall_task_id,
                    )
                    for file_path in chunk
                ]
                await asyncio.gather(*upload_tasks)

        console.print("[bold green]✓[/] All files uploaded successfully")
        return files

    async def ingest(self, input_dir: str, max_concurrent_uploads: int = 5) -> bool:
        """Upload files from the input directory in parallel for processing.

        Args:
            input_dir (str): The path to the directory containing the files to process.
            max_concurrent_uploads (int): The maximum number of files to upload concurrently.

        Returns:
            bool: True if ingestion was successful, False otherwise.
        """
        console.print("\n[bold blue]🚀 Starting Ingestion Process[/]")

        try:
            await self._upload_files(
                input_dir=input_dir,
                session_id=self._session_id,
                destination="documents",
                max_concurrent_uploads=max_concurrent_uploads,
            )

            console.print("\n[bold blue]⚙️ Processing uploaded files...[/]")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                expand=True,
                refresh_per_second=10,
            ) as processing_progress:
                processing_task_id = processing_progress.add_task(
                    "[bold yellow]Processing Documents", total=100, start=True
                )

                try:
                    job: JobResponse = await self._adapter.ingest(
                        session_id=self._session_id
                    )

                    async for progress in self._adapter.track_job_with_progress(
                        job_id=job.job_id,
                        timeout=900,
                    ):
                        progress_percentage = progress * 100
                        processing_progress.update(
                            processing_task_id,
                            completed=progress_percentage,
                            refresh=True,
                        )
                    processing_progress.update(
                        processing_task_id,
                        description="[bold green]Processing Complete",
                        completed=100,
                        refresh=True,
                    )
                except Exception as e:
                    raise IngestionError(f"Processing failed: {str(e)}") from e

            console.print("[bold green]✓[/] All files processed successfully")
            console.print("\n[bold green]✨ Ingestion completed successfully![/]\n")
            return True
        except Exception as e:
            console.print(f"\n[bold red]✗ Ingestion failed: {str(e)}[/]")
            logger.error("Ingestion failed: %s", str(e))
            return False

    async def _query(
        self,
        query: str,
        role: Optional[str] = None,
    ) -> str:
        """Query the processed data.

        Args:
            query (str): The query to process.
            role (Optional[str]): The role to use for the query.

        Returns:
            str: The query response.
        """
        job: JobResponse = await self._adapter.query(
            session_id=self._session_id, query=query, role=role
        )

        response: JobResponse = await self._adapter.track_job(
            job_id=job.job_id,
        )

        return response.result

    async def query(
        self, query: str, role: Optional[str] = None, display_in_console: bool = False
    ) -> str:
        """Query the processed data.

        Args:
            query (str): The query to process.
            role (Optional[str]): The role to use for the query.
            display_in_console (bool): Whether to display the query in the console.

        Returns:
            str: The query response.
        """
        console.print("\n[bold blue]🔍 Processing Query[/]")
        console.print(Panel(query, title="Query"))

        try:
            if not self._session_id:
                raise ValueError("Session ID is required")
            with console.status("[bold yellow]Processing query...[/]", spinner="dots"):
                response = await self._query(query=query, role=role)
            if display_in_console:
                console.print(Panel(response, title="Response", border_style="green"))
            console.print("[bold green]✓[/] Query processed successfully")
            return response

        except RequestException as e:
            console.print("[bold red]✗ Query failed[/]")
            logger.error("Query failed: %s", str(e))
            raise

    async def multiple_queries(self, queries: List[Query]) -> List[QueryResponse]:
        """Query the processed data with multiple queries in parallel.

        Args:
            queries (List[Query]): The queries to process.

        Returns:
            List[QueryResponse]: The query responses.
        """
        try:
            if not self._session_id:
                raise ValueError("Session ID is required")

            console.print(
                f"\n[bold blue]Processing {len(queries)} queries in parallel...[/]"
            )

            with console.status(
                "[bold yellow]Processing multiple queries...[/]", spinner="dots"
            ):
                query_tasks = [
                    self._query(query=query.query, role=query.role) for query in queries
                ]

                responses = await asyncio.gather(*query_tasks, return_exceptions=True)

                results: List[QueryResponse] = []
                for i, (query, response) in enumerate(zip(queries, responses)):
                    if isinstance(response, Exception):
                        console.print(
                            f"[bold red]Query {i+1} failed: {str(response)}[/]"
                        )
                        results.append(
                            QueryResponse(
                                query=query,
                                response=f"Error: {str(response)}",
                                display_in_console=query.display_in_console,
                            )
                        )
                    else:
                        results.append(
                            QueryResponse(
                                query=query,
                                response=response,
                                display_in_console=query.display_in_console,
                            )
                        )

                displayed_count = 0
                for result in results:
                    if result.display_in_console:
                        displayed_count += 1
                        console.print(
                            Panel(result.query.query, title=f"Query {displayed_count}")
                        )
                        console.print(
                            Panel(
                                result.response, title="Response", border_style="green"
                            )
                        )

            console.print(
                f"[bold green]✓[/] {len(queries)} queries processed successfully"
            )
            return results

        except Exception as e:
            console.print("[bold red]✗ Multiple queries failed[/]")
            logger.error("Multiple queries failed: %s", str(e))
            raise

    async def summarize(self, display_in_console: bool = False) -> str:
        """Get session summary.

        Args:
            display_in_console (bool): Whether to display the summary in the console.

        Returns:
            str: The session summary.
        """
        console.print("\n[bold blue]🔍 Getting session summary...[/]")
        if not self._session_id:
            raise ValueError("Session ID is required")
        with console.status(
            "[bold yellow]Getting session summary...[/]", spinner="dots"
        ):
            job: JobResponse = await self._adapter.get_knowledge_summary(
                session_id=self._session_id
            )
            response: JobResponse = await self._adapter.track_job(
                job_id=job.job_id,
            )
        if display_in_console:
            console.print(
                Panel(response.result, title="Session Summary", border_style="green")
            )
        console.print("[bold green]✓[/] Session summary retrieved successfully")
        return response.result

    async def article(self, topic: str, display_in_console: bool = False) -> str:
        """Create an article on the topic.

        Args:
            topic (str): The topic to create the article on.
            display_in_console (bool): Whether to display the article in the console.

        Returns:
            str: The article.
        """
        console.print("\n[bold blue]🚀 Creating article...[/]")
        console.print(Panel(topic, title="Topic"))
        if not self._session_id:
            raise ValueError("Session ID is required")
        with console.status("[bold yellow]Creating article...[/]", spinner="dots"):
            job: JobResponse = await self._adapter.create_article(
                session_id=self._session_id, topic=topic
            )
            response: JobResponse = await self._adapter.track_job(
                job_id=job.job_id,
            )
        if display_in_console:
            console.print(Panel(response.result, title="Article", border_style="green"))
        console.print("[bold green]✓[/] Article created successfully")
        return response.result

    async def _validate_files(
        self,
        media_path: Optional[str] = None,
    ) -> bool:
        """Validate media files.

        Args:
            media_path (Optional[str]): The path to the media directory.

        Returns:
            bool: True if files are valid, False otherwise.
        """

        def validate_media_path(
            path: str, media_type: str, allowed_extensions: set
        ) -> bool:
            """Validate a media directory and its contents."""
            path_obj = Path(path)

            # Validate directory
            if not path_obj.exists():
                console.print(
                    f"[bold red]✗[/] {media_type.capitalize()} path not found: {path}"
                )
                return False
            if not path_obj.is_dir():
                console.print(
                    f"[bold red]✗[/] {media_type.capitalize()} path is not a directory: {path}"
                )
                return False

            # Get all files, excluding hidden files (those starting with a dot)
            files = [
                f
                for f in path_obj.iterdir()
                if f.is_file() and not f.name.startswith(".")
            ]

            if not files:
                console.print(
                    f"[bold red]✗[/] No valid files found in {media_type} directory (hidden files are excluded)"
                )
                return False

            invalid_files = [
                f.name for f in files if f.suffix.lower() not in allowed_extensions
            ]

            if invalid_files:
                display_files = invalid_files[:5]
                overflow = (
                    f" and {len(invalid_files) - 5} more"
                    if len(invalid_files) > 5
                    else ""
                )
                console.print(
                    f"[bold red]✗ Invalid {media_type} file(s): {', '.join(display_files)}{overflow}[/]"
                )
                return False

            file_count = len(files)
            console.print(f"[bold cyan]Found {file_count} valid {media_type} files[/]")
            return True

        is_valid = validate_media_path(
            media_path, "media", MediaFileExtensions.values()
        )
        if is_valid:
            console.print("[bold green]✓[/] Media path and files are valid")
        return is_valid

    async def llm_call(
        self,
        prompt: str,
        use_history: bool = False,
        media_path: Optional[str] = None,
        display_prompt: bool = False,
        display_in_console: bool = True,
    ) -> str:
        """Call the LLM with the prompt.

        Args:
            prompt (str): The prompt to call the LLM with.
            use_history (bool): Whether to use the history of the chat.
            media_path (Optional[str]): The path to the media.
            display_prompt (bool): Whether to display the prompt in the console.
            display_in_console (bool): Whether to display the response in the console.

        Returns:
            str: The response from the LLM.
        """
        if media_path:
            if not await self._validate_files(
                media_path=media_path,
            ):
                return
            input_dir = media_path
            destination = "media"
            await self._upload_files(
                input_dir=input_dir,
                session_id=self._session_id,
                destination=destination,
            )

        console.print("\n[bold blue]🚀 Calling LLM...[/]")
        if display_prompt:
            console.print(Panel(prompt, title="Prompt"))

        with console.status("[bold yellow]Calling LLM...[/]", spinner="dots"):
            job: JobResponse = await self._adapter.llm_call(
                session_id=self._session_id,
                prompt=prompt,
                use_history=use_history,
                use_media=bool(media_path),
            )
            response: JobResponse = await self._adapter.track_job(
                job_id=job.job_id,
            )
        if display_in_console:
            console.print(
                Panel(response.result, title="Response", border_style="green")
            )
        console.print("[bold green]✓[/] LLM call processed successfully")
        return response.result

    async def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        use_history: bool = True,
        display_in_console: bool = True,
    ) -> str:
        """Chat with the LLM using the session context and knowledge base.

        Args:
            message (str): The message to send to the LLM
            system_prompt (Optional[str]): The system prompt to use for the chat
            use_history (bool): Whether to use the history of the chat
            display_in_console (bool): Whether to display the chat in the console

        Returns:
            str: The chat response
        """
        console.print("\n[bold blue]🚀 Chatting with LLM...[/]")
        if system_prompt:
            console.print("\n[bold yellow]✨ Input System Prompt[/]")
            console.print(Panel(system_prompt, title="System Prompt"))

        console.print("\n[bold yellow]🔍 Input Message[/]")
        console.print(Panel(message, title="Message"))

        with console.status("[bold yellow]Chatting with LLM...[/]", spinner="dots"):
            if use_history:
                job: JobResponse = await self._adapter.chat(
                    session_id=self._session_id,
                    message=message,
                    system_prompt=system_prompt,
                )
                response = await self._adapter.track_job(
                    job_id=job.job_id,
                )
            else:
                prompt = f"System prompt: {system_prompt}\n\n User message: {message}"
                job: JobResponse = await self._adapter.llm_call(
                    session_id=self._session_id,
                    prompt=prompt,
                )
                response = await self._adapter.track_job(
                    job_id=job.job_id,
                )

        if display_in_console:
            console.print(
                Panel(response.result, title="Response", border_style="green")
            )
        console.print("[bold green]✓[/] Chat processed successfully")
        return response.result

    async def cleanup_chat(self) -> None:
        """Cleanup the chat history.

        Raises:
            ValueError: If the session ID is not set.
        """
        if not self._session_id:
            raise ValueError("Session ID is required")

        with console.status("[bold blue]🚀 Cleaning up chat history...[/]"):
            job: JobResponse = await self._adapter.cleanup_chat(
                session_id=self._session_id
            )
            await self._adapter.track_job(
                job_id=job.job_id,
            )
            console.print("[bold green]✓[/] Chat history cleaned up successfully")

    async def delete(self) -> None:
        """Delete the session.

        Raises:
            ValueError: If the session ID is not set.
        """
        if getattr(self, "_session_cleaned_up", False):
            logger.debug("Session already cleaned up, skipping duplicate deletion")
            return

        if not self._session_id and not self._alias:
            console.print(
                "[yellow]⚠️  Cannot delete: Session ID or alias is required[/]"
            )
            return

        setattr(self, "_cleanup_in_progress", True)
        try:
            with console.status("[bold blue]Cleaning up session...[/]"):
                job: JobResponse = await self._adapter.delete_session(
                    session_id=self._session_id, alias=self._alias
                )
                await self._adapter.track_job(
                    job_id=job.job_id,
                )
            setattr(self, "_session_cleaned_up", True)
        finally:
            setattr(self, "_cleanup_in_progress", False)
