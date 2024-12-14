import asyncio
import random
from functools import wraps
from typing import Any, Callable

from requests.exceptions import HTTPError, RequestException
from rich.console import Console

from intelligence.core.exceptions import IntelligenceAPIError

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
                    wait_time = min(base_delay * (2**attempt), 8) * (1 + random.random() * 0.1)
                    console.print(
                        f"[yellow]⚠️  Retrying request ({attempt + 1}/{max_retries}) in {wait_time:.1f}s...[/]"
                    )
                    await asyncio.sleep(wait_time)

        return wrapper

    return decorator
