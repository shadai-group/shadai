import asyncio
import random
from functools import wraps
from typing import Any, Callable

from requests import HTTPError, RequestException
from rich.console import Console
from rich.panel import Panel

from shadai.core.exceptions import (
    AgentConfigurationError,
    AgentExecutionError,
    AgentFunctionError,
    ConfigurationError,
    IngestionError,
    IntelligenceAPIError,
)

console = Console()


def retry_on_server_error(max_retries: int = 5, base_delay: float = 1.0) -> Callable:
    """Decorator for retrying requests on server errors."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except RequestException as e:
                    if isinstance(e, HTTPError) and 400 <= e.response.status_code < 500:
                        raise
                    if attempt == max_retries - 1:
                        raise IntelligenceAPIError("Max retries reached") from e
                    wait_time = min(base_delay * (2**attempt), 8) * (
                        1 + random.random() * 0.1
                    )
                    console.print(
                        f"[yellow]⚠️  Retrying request ({attempt + 1}/{max_retries}) in {wait_time:.1f}s...[/]"
                    )
                    await asyncio.sleep(wait_time)

        return wrapper

    return decorator


def handle_errors(func: Callable) -> Callable:
    """Decorator for handling session errors with rich output."""

    ERROR_MESSAGES = {
        IntelligenceAPIError: {
            "title": "API Error",
            "suggestions": [
                "Check your API key",
                "Verify the API server is running",
                "Ensure you have network connectivity",
            ],
        },
        ConfigurationError: {
            "title": "Configuration Error",
            "suggestions": [
                "Set INTELLIGENCE_API_KEY environment variable",
                "Check your configuration settings",
            ],
        },
        IngestionError: {
            "title": "Ingestion Error",
            "suggestions": [
                "Verify your input files exist",
                "Check file permissions",
                "Ensure files are in supported format",
            ],
        },
        AgentConfigurationError: {
            "title": "Agent Configuration Error",
            "suggestions": [
                "Check your agent configuration",
            ],
        },
        AgentExecutionError: {
            "title": "Agent Execution Error",
            "suggestions": [
                "Check your agent configuration",
            ],
        },
        AgentFunctionError: {
            "title": "Agent Function Error",
            "suggestions": [
                "Check your agent configuration",
            ],
        },
    }

    async def cleanup_session(instance: Any) -> None:
        """Helper function to cleanup session if needed."""
        if (
            instance
            and hasattr(instance, "_delete_session")
            and instance._delete_session
            and func.__name__ != "__aexit__"
            and not getattr(instance, "_session_cleaned_up", False)
        ):
            try:
                console.print("[yellow]⚙️  Cleaning up session...[/]")
                await instance.delete_session()
                setattr(instance, "_session_cleaned_up", True)
                console.print("[green]✓[/] Session cleaned up")
            except Exception as cleanup_error:
                console.print(
                    f"[red]✗[/] Failed to cleanup session: {str(cleanup_error)}"
                )

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)

        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️  Process interrupted by user[/]")
            if args:
                await cleanup_session(args[0])
            raise SystemExit(130)

        except tuple(ERROR_MESSAGES.keys()) as e:
            error_config = ERROR_MESSAGES[type(e)]
            console.print(
                Panel(
                    f"[bold red]{error_config['title']}[/]\n\n"
                    f"[yellow]Details:[/] {str(e)}\n\n"
                    f"[blue]Suggestions:[/]\n"
                    + "".join(f"• {s}\n" for s in error_config["suggestions"]),
                    title="[red]Error",
                    border_style="red",
                )
            )
            if args:
                await cleanup_session(args[0])
            raise SystemExit(1)

        except Exception as e:
            console.print(
                Panel(
                    f"[bold red]Unexpected Error[/]\n\n"
                    f"[yellow]Error Type:[/] {type(e).__name__}\n"
                    f"[yellow]Details:[/] {str(e)}",
                    title="[red]System Error",
                    border_style="red",
                )
            )
            if args:
                await cleanup_session(args[0])
            raise SystemExit(1)

    return wrapper
