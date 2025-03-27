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
from shadai.core.files import FileManager
from shadai.core.schemas import SessionResponse

logger = logging.getLogger(__name__)
console = Console()


class Session:
    """
    A session manager for the Intelligence API that handles file ingestion and querying.

    Args:
        session_id (Optional[str]): The session ID to use.
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
        type: Literal["light", "standard", "deep"] = "standard",
        llm_model: str = "us.anthropic.claude-3-5-haiku-20241022-v1:0",
        llm_temperature: float = 0.7,
        llm_max_tokens: int = 4096,
        query_mode: str = "hybrid",
        language: str = "es",
        delete: bool = True,
    ) -> None:
        """Initialize a new session with the specified parameters."""
        self._adapter = IntelligenceAdapter()
        self._file_manager = FileManager()
        self._session_id = session_id
        self._type = type
        self._llm_model = llm_model
        self._llm_temperature = llm_temperature
        self._llm_max_tokens = llm_max_tokens
        self._query_mode = query_mode
        self._language = language
        self._delete = delete

    @property
    def id(self) -> Optional[str]:
        """Get the session ID.

        Returns:
            Optional[str]: The session ID
        """
        return self._session_id

    @handle_errors
    async def __aenter__(self):
        """Async context manager entry.

        Returns:
            Session: The session object
        """
        console.print("\n[bold blue]🚀 Initializing Intelligence Session...[/]")
        self._session_id = await self._get()
        console.print("[bold green]✓[/] Session initialized successfully\n")
        return self

    @handle_errors
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit.

        Args:
            exc_type (type): The exception type
            exc_val (Exception): The exception value
            exc_tb (traceback): The exception traceback
        """
        if self._delete:
            await self.adelete()

    @handle_errors
    async def _get(self) -> str:
        """Get the session ID."""
        if self._session_id:
            with console.status("[bold yellow]Getting existing session..."):
                session = await self._adapter.get_session(session_id=self._session_id)
                console.print(
                    f"[bold green]✓[/] Retrieved existing session (ID: {session.session_id})"
                )
        else:
            session = await self._create()
        return session.session_id

    async def _create(self) -> SessionResponse:
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

    @handle_errors
    async def aingest(self, input_dir: str, max_concurrent_uploads: int = 5) -> None:
        """Upload files from the input directory in parallel for processing.

        Args:
            input_dir (str): The path to the directory containing the files to process.
            max_concurrent_uploads (int): The maximum number of files to upload concurrently.
        """
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
                        self._file_manager._upload_file(
                            session_id=self._session_id,
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

    def ingest(self, input_dir: str, max_concurrent_uploads: int = 5) -> None:
        """Upload files from the input directory in parallel for processing.

        Args:
            input_dir (str): The path to the directory containing the files to process.
            max_concurrent_uploads (int): The maximum number of files to upload concurrently.
        """
        event_loop = asyncio.get_event_loop()
        return event_loop.run_until_complete(
            self.aingest(
                input_dir=input_dir, max_concurrent_uploads=max_concurrent_uploads
            )
        )

    @handle_errors
    async def aquery(self, query: str, display_in_console: bool = False) -> str:
        """Query the processed data.

        Args:
            query (str): The query to process.
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

    def query(self, query: str, display_in_console: bool = False) -> str:
        """Query the processed data.

        Args:
            query (str): The query to process.
            display_in_console (bool): Whether to display the query in the console.

        Returns:
            str: The query response.
        """
        event_loop = asyncio.get_event_loop()
        return event_loop.run_until_complete(
            self.aquery(query=query, display_in_console=display_in_console)
        )

    @handle_errors
    async def asummarize(self, display_in_console: bool = False) -> str:
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
            summary = await self._adapter._get_session_summary(self._session_id)
        if display_in_console:
            console.print(Panel(summary, title="Session Summary", border_style="green"))
        console.print("[bold green]✓[/] Session summary retrieved successfully")
        return summary

    def summarize(self, display_in_console: bool = False) -> str:
        """Get session summary.

        Args:
            display_in_console (bool): Whether to display the summary in the console.

        Returns:
            str: The session summary.
        """
        event_loop = asyncio.get_event_loop()
        return event_loop.run_until_complete(
            self.asummarize(display_in_console=display_in_console)
        )

    @handle_errors
    async def aarticle(self, topic: str, display_in_console: bool = False) -> str:
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
            article = await self._adapter._create_article(
                session_id=self._session_id, topic=topic
            )
        if display_in_console:
            console.print(Panel(article, title="Article", border_style="green"))
        console.print("[bold green]✓[/] Article created successfully")
        return article

    def article(self, topic: str, display_in_console: bool = False) -> str:
        """Create an article on the topic.

        Args:
            topic (str): The topic to create the article on.
            display_in_console (bool): Whether to display the article in the console.

        Returns:
            str: The article.
        """
        event_loop = asyncio.get_event_loop()
        return event_loop.run_until_complete(
            self.aarticle(topic=topic, display_in_console=display_in_console)
        )

    @handle_errors
    async def acall(
        self,
        prompt: str,
        display_prompt: bool = False,
        display_in_console: bool = True,
    ) -> str:
        """Call the LLM with the prompt.

        Args:
            prompt (str): The prompt to call the LLM with.
            display_prompt (bool): Whether to display the prompt in the console.
            display_in_console (bool): Whether to display the response in the console.

        Returns:
            str: The response from the LLM.
        """
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

    def call(
        self, prompt: str, display_prompt: bool = False, display_in_console: bool = True
    ) -> str:
        """Call the LLM with the prompt.

        Args:
            prompt (str): The prompt to call the LLM with.
        """
        event_loop = asyncio.get_event_loop()
        return event_loop.run_until_complete(
            self.acall(
                prompt=prompt,
                display_prompt=display_prompt,
                display_in_console=display_in_console,
            )
        )

    @handle_errors
    async def achat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        display_in_console: bool = True,
    ) -> str:
        """Chat with the LLM using the session context and knowledge base.

        Args:
            message (str): The message to send to the LLM
            system_prompt (Optional[str]): The system prompt to use for the chat
            display_in_console (bool): Whether to display the chat in the console

        Returns:
            str: The chat response
        """
        console.print("\n[bold blue]🚀 Chatting with Agent LLM...[/]")
        if system_prompt:
            console.print("\n[bold yellow]✨ Input System Prompt[/]")
            console.print(Panel(system_prompt, title="System Prompt"))

        console.print("\n[bold yellow]🔍 Input Message[/]")
        console.print(Panel(message, title="Message"))

        with console.status(
            "[bold yellow]Chatting with Agent LLM...[/]", spinner="dots"
        ):
            response = await self._adapter._chat(
                session_id=self._session_id,
                message=message,
                system_prompt=system_prompt,
            )

        if display_in_console:
            console.print(Panel(response, title="Response", border_style="green"))
        console.print("[bold green]✓[/] Chat processed successfully")
        return response

    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        display_in_console: bool = True,
    ) -> str:
        """Chat with the LLM using the session context and knowledge base.

        Args:
            message (str): The message to send to the LLM
            system_prompt (Optional[str]): The system prompt to use for the chat
            display_in_console (bool): Whether to display the chat in the console

        Returns:
            str: The chat response
        """
        event_loop = asyncio.get_event_loop()
        return event_loop.run_until_complete(
            self.achat(
                message=message,
                system_prompt=system_prompt,
                display_in_console=display_in_console,
            )
        )

    async def adelete(self) -> None:
        """Delete the session.

        Raises:
            ValueError: If the session ID is not set.
        """
        if not self._session_id:
            raise ValueError("Session ID is required")

        with console.status("[bold blue]🚀 Cleaning up session...[/]"):
            await self._adapter.delete_session(self._session_id)
            console.print("[bold green]✓[/] Session cleaned up successfully")

    def delete(self) -> None:
        """Delete the session.

        Raises:
            ValueError: If the session ID is not set.
        """
        event_loop = asyncio.get_event_loop()
        return event_loop.run_until_complete(self.adelete())
