import asyncio
import logging
import os
from pathlib import Path
from typing import Literal, Optional

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

from shadai.core.adapter import IntelligenceAdapter
from shadai.core.decorators import handle_errors
from shadai.core.exceptions import IngestionError
from shadai.core.schemas import SessionResponse

logger = logging.getLogger(__name__)
console = Console()


class Session:
    """A session manager for the Intelligence API that handles file ingestion and querying."""

    def __init__(
        self,
        session_id: Optional[str] = None,
        type: Literal["light", "standard", "deep"] = "standard",
        llm_model: Optional[str] = None,
        llm_temperature: Optional[float] = None,
        llm_max_tokens: Optional[int] = None,
        query_mode: Optional[str] = None,
        language: Optional[str] = None,
        delete_session: bool = True,
    ) -> None:
        """Initialize a new session with the specified parameters."""
        self._adapter = IntelligenceAdapter()
        self._session_id = session_id
        self._type = type
        self._llm_model = llm_model
        self._llm_temperature = llm_temperature
        self._llm_max_tokens = llm_max_tokens
        self._query_mode = query_mode
        self._language = language
        self._delete_session = delete_session

    @property
    def session_id(self) -> Optional[str]:
        """Get the session ID."""
        return self._session_id

    @handle_errors
    async def __aenter__(self):
        """Async context manager entry."""
        console.print("\n[bold blue]🚀 Initializing Intelligence Session...[/]")
        self._session_id = await self._get_session()
        console.print("[bold green]✓[/] Session initialized successfully\n")
        return self

    @handle_errors
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._delete_session:
            await self.delete_session()

    async def _get_session(self) -> str:
        """Get the session ID."""
        if self._session_id:
            with console.status("[bold yellow]Getting existing session..."):
                session = await self._adapter.get_session(session_id=self._session_id)
                console.print(
                    f"[bold green]✓[/] Retrieved existing session (ID: {session.session_id})"
                )
        else:
            session = await self._create_session()
        return session.session_id

    async def _create_session(self) -> SessionResponse:
        """Create a new session."""
        with console.status("[bold yellow]Creating new session..."):
            session = await self._adapter.create_session(
                type=self._type,
                llm_model=self._llm_model,
                llm_temperature=self._llm_temperature,
                llm_max_tokens=self._llm_max_tokens,
                query_mode=self._query_mode,
                language=self._language,
            )
            console.print(
                f"[bold green]✓[/] Session created successfully (ID: {session.session_id})"
            )
        return session

    async def delete_session(self) -> None:
        """Delete the session."""
        if not self._session_id:
            raise ValueError("Session ID is required")

        with console.status("[bold blue]🚀 Cleaning up session...[/]"):
            await self._adapter.delete_session(self._session_id)
            console.print("[bold green]✓[/] Session cleaned up successfully")

    async def _count_files(self, input_path: Path) -> int:
        """Count the total number of files to process."""
        return sum(1 for _ in input_path.rglob("*") if _.is_file())

    async def _upload_file(
        self,
        file_path: Path,
        progress: Progress,
        overall_task_id: int,
    ) -> None:
        """Upload a single file with progress tracking and update overall progress."""
        try:
            url = await self._adapter._get_presigned_url(
                session_id=self._session_id, filename=file_path.name
            )
            file_size = os.path.getsize(file_path)
            file_task_id = progress.add_task(
                f"[cyan]└─ {file_path.name}", total=file_size, start=True, visible=True
            )
            with open(file_path, "rb") as f:
                file_data = f.read()
            response = self._adapter._session.put(
                url,
                data=file_data,
                headers={
                    "Content-Type": "application/octet-stream",
                    "Content-Length": str(file_size),
                },
            )
            if not response.ok:
                raise RequestException(
                    f"Upload failed for {file_path.name}: {response.status_code}"
                )
            progress.update(
                task_id=file_task_id,
                completed=file_size,
                description=f"[green]└─ ✓ {file_path.name}",
                refresh=True,
            )
            progress.update(task_id=overall_task_id, advance=file_size, refresh=True)

        except Exception as e:
            if "file_task_id" in locals():
                progress.update(
                    task_id=file_task_id,
                    description=f"[red]└─ ✗ {file_path.name}",
                    refresh=True,
                )
            logger.error(f"Failed to upload {file_path.name}: {str(e)}")
            raise

    @handle_errors
    async def ingest(self, input_dir: str, max_concurrent_uploads: int = 5) -> None:
        """Upload files from the input directory in parallel for processing."""
        console.print("\n[bold blue]🚀 Starting Ingestion Process[/]")

        input_path = Path(input_dir)
        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_dir}")

        if not self._session_id:
            raise ValueError("Session ID is required")

        try:
            files = [f for f in input_path.rglob("*") if f.is_file()]
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
                        self._upload_file(
                            file_path=file_path,
                            progress=progress,
                            overall_task_id=overall_task_id,
                        )
                        for file_path in chunk
                    ]
                    await asyncio.gather(*upload_tasks)

            console.print("\n[bold blue]⚙️ Processing uploaded files...[/]")
            with console.status(
                "[bold yellow]Processing... This may take a few minutes[/]",
                spinner="dots",
            ):
                await self._adapter.ingest(session_id=self._session_id)
            console.print("[bold green]✓[/] All files processed successfully")
            console.print("\n[bold green]✨ Ingestion completed successfully![/]\n")
        except Exception as e:
            console.print(f"\n[bold red]✗ Ingestion failed: {str(e)}[/]")
            logger.error("Ingestion failed: %s", str(e))
            raise IngestionError(f"Failed to ingest files: {str(e)}") from e

    @handle_errors
    async def query(self, query: str, display_in_console: bool = False) -> str:
        """Query the processed data."""
        console.print("\n[bold blue]🔍 Processing Query[/]")
        console.print(Panel(query, title="Query"))

        try:
            if not self._session_id:
                raise ValueError("Session ID is required")
            with console.status("[bold yellow]Processing query...[/]", spinner="dots"):
                response = await self._adapter.query(
                    session_id=self._session_id, query=query
                )

            if display_in_console:
                console.print(Panel(response, title="Response", border_style="green"))
            console.print("[bold green]✓[/] Query processed successfully")
            return response

        except RequestException as e:
            console.print("[bold red]✗ Query failed[/]")
            logger.error("Query failed: %s", str(e))
            raise

    @handle_errors
    async def summarize(self, display_in_console: bool = False) -> str:
        """Get session summary."""
        console.print("\n[bold blue]🔍 Getting session summary...[/]")
        if not self._session_id:
            raise ValueError("Session ID is required")
        with console.status(
            "[bold yellow]Getting session summary...[/]", spinner="dots"
        ):
            summary = await self._adapter._get_session_summary(self._session_id)
        if display_in_console:
            console.print(Panel(summary, title="Session Summary", border_style="green"))
        console.print("[bold green]✓[/] Session summary retrieved successfully")
        return summary

    @handle_errors
    async def create_article(self, topic: str, display_in_console: bool = False) -> str:
        """Create an article on the topic."""
        console.print("\n[bold blue]🚀 Creating article...[/]")
        console.print(Panel(topic, title="Topic"))
        if not self._session_id:
            raise ValueError("Session ID is required")
        with console.status("[bold yellow]Creating article...[/]", spinner="dots"):
            article = await self._adapter._create_article(
                session_id=self._session_id, topic=topic
            )
        if display_in_console:
            console.print(Panel(article, title="Article", border_style="green"))
        console.print("[bold green]✓[/] Article created successfully")
        return article

    @handle_errors
    async def llm_call(
        self,
        prompt: str,
        display_prompt: bool = False,
        display_in_console: bool = True,
    ) -> str:
        """Call the LLM with the prompt."""
        console.print("\n[bold blue]🚀 Calling Agent LLM...[/]")
        if display_prompt:
            console.print(Panel(prompt, title="Prompt"))

        with console.status("[bold yellow]Calling Agent LLM...[/]", spinner="dots"):
            response = await self._adapter._llm_call(
                session_id=self._session_id, prompt=prompt
            )
        if display_in_console:
            console.print(Panel(response, title="Response", border_style="green"))
        console.print("[bold green]✓[/] Agent LLM call processed successfully")
        return response
