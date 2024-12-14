import logging
import os
import zipfile
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Literal, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from rich.console import Console
from rich.panel import Panel
from tqdm import tqdm
from urllib3.util.retry import Retry

from intelligence.core.adapter import IntelligenceAdapter
from intelligence.core.exceptions import IngestionError
from intelligence.core.schemas import SessionResponse

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

    async def __aenter__(self):
        """Async context manager entry."""
        console.print("\n[bold blue]🚀 Initializing Intelligence Session...[/]")
        self._session_id = await self._get_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._delete_session:
            try:
                console.print("\n[bold blue]🔄 Cleaning up session...[/]")
                await self._adapter.delete_session(self._session_id)
                console.print("[bold green]✓[/] Session cleaned up successfully")
            except Exception as e:
                console.print("[bold red]✗ Failed to clean up session[/]")
                logger.error("Failed to clean up session: %s", str(e))
                raise

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

        with console.status("[bold blue]🚀 Deleting session...[/]") as status:
            await self._adapter.delete_session(self._session_id)
            console.print(f"[bold green]✓[/] Session deleted successfully")

    async def _count_files(self, input_path: Path) -> int:
        """Count the total number of files to process."""
        return sum(1 for _ in input_path.rglob("*") if _.is_file())

    async def _create_zip_archive(self, input_path: Path, zip_path: str) -> None:
        """Create a ZIP archive from the input directory with progress bar."""
        total_files = await self._count_files(input_path)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            with tqdm(
                total=total_files,
                desc="[1/3] 📁 Compressing files",
                unit="file",
                bar_format="{desc:<30} |{bar:30} {percentage:>3.0f}% | {n_fmt}/{total_fmt} files",
                colour="blue",
            ) as pbar:
                for file_path in input_path.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(input_path)
                        zipf.write(file_path, arcname)
                        pbar.update(1)

    async def _upload_with_progress(self, file_path: str, url: str, chunk_size: int) -> None:
        """Upload file with progress bar."""
        file_size = os.path.getsize(file_path)

        session = requests.Session()
        session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(
                    total=5,
                    backoff_factor=2,
                    status_forcelist=[500, 502, 503, 504, 404],
                    allowed_methods=["PUT", "GET", "POST"],
                )
            ),
        )

        try:
            with (
                open(file_path, "rb") as f,
                tqdm(
                    total=file_size,
                    desc="[2/3] 📤 Uploading files",
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    bar_format="{desc:<30} |{bar:30} {percentage:>3.0f}% | {rate_fmt}",
                    colour="green",
                ) as pbar,
            ):
                response = session.put(
                    url,
                    data=f.read(),
                    headers={"Content-Type": "application/zip", "Content-Length": str(file_size)},
                    timeout=300,
                )
                pbar.update(file_size)
                response.raise_for_status()

        except RequestException as e:
            console.print("[bold red]✗ Upload failed[/]")
            logger.error("Failed to upload files: %s", str(e))
            raise IngestionError(f"Upload failed: {str(e)}") from e
        finally:
            session.close()

    async def ingest(self, input_dir: str, chunk_size: int = 1024 * 1024) -> None:
        """Compress and upload files from the input directory for processing."""
        console.print("\n[bold blue]🚀 Starting Ingestion Process[/]")
        console.print(Panel(f"Source directory: {input_dir}", title="Configuration"))

        input_path = Path(input_dir)
        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_dir}")

        if not self._session_id:
            raise ValueError("Session ID is required")

        try:
            with NamedTemporaryFile(suffix=".zip", delete=True) as tmp_zip:
                await self._create_zip_archive(input_path, tmp_zip.name)
                console.print("[bold green]✓[/] Files compressed successfully")

                console.print("[bold yellow]⚙️ Getting presigned URL...[/]")
                url = await self._adapter._get_presigned_url(session_id=self._session_id)
                console.print("[bold green]✓[/] Presigned URL retrieved successfully")

                console.print("[bold yellow]⚙️ Uploading files...[/]")
                await self._upload_with_progress(tmp_zip.name, url, chunk_size)
                console.print("[bold green]✓[/] Files uploaded successfully")

                console.print("[bold blue]⚙️ Processing files...[/]")
                with console.status(
                    "[bold yellow]Processing... This may take a few minutes[/]", spinner="dots"
                ) as status:
                    await self._adapter.ingest(session_id=self._session_id)

                console.print("[bold green]✓[/] Files processed successfully")
                console.print("\n[bold green]✨ Ingestion completed successfully![/]\n")

        except Exception as e:
            console.print(f"\n[bold red]✗ Ingestion failed: {str(e)}[/]")
            logger.error("Ingestion failed: %s", str(e))
            raise IngestionError(f"Failed to ingest files: {str(e)}") from e

    async def query(self, query: str, display: bool = False) -> str:
        """Query the processed data."""
        console.print("\n[bold blue]🔍 Processing Query[/]")
        console.print(Panel(query, title="Query"))

        try:
            if not self._session_id:
                raise ValueError("Session ID is required")
            with console.status("[bold yellow]Processing query...[/]", spinner="dots"):
                response = await self._adapter.query(session_id=self._session_id, query=query)

            if display:
                console.print(Panel(response, title="Response", border_style="green"))
            console.print("[bold green]✓[/] Query processed successfully")
            return response

        except RequestException as e:
            console.print("[bold red]✗ Query failed[/]")
            logger.error("Query failed: %s", str(e))
            raise
