"""
Shadai Client - Base MCP Client
--------------------------------
Low-level client for communicating with Shadai MCP servers.
"""

import json
from typing import Any, AsyncIterator, Dict, Optional

import aiohttp
import os

from .exceptions import (
    AuthenticationError,
    ConnectionError,
    ServerError,
)
from dotenv import load_dotenv

load_dotenv()


class ShadaiClient:
    """
    Async client for Shadai AI MCP servers.

    This is the low-level client that handles JSON-RPC communication
    and Server-Sent Events (SSE) streaming.

    Examples:
        >>> client = ShadaiClient(api_key="your-api-key")
        >>> health = await client.health_check()
        >>> print(health)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost",
        timeout: int = 30,
    ) -> None:
        """
        Initialize Shadai client.

        Args:
            api_key: Your Shadai API key (required)
            base_url: Base URL of the Shadai server
            timeout: Request timeout in seconds

        Raises:
            ValueError: If api_key is not provided
        """
        if not api_key:
            api_key = os.getenv("SHADAI_API_KEY")
            if not api_key:
                raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout)

        self.rpc_url = f"{self.base_url}/mcp/rpc"
        self.stream_url = f"{self.base_url}/mcp/stream"
        self.health_url = f"{self.base_url}/mcp/health"

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for requests."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        Check server health and availability.

        Returns:
            Dictionary with server status, version, and available tools count

        Raises:
            ConnectionError: If server is unreachable
            ServerError: If server returns an error

        Examples:
            >>> health = await client.health_check()
            >>> print(f"Status: {health['status']}")
            >>> print(f"Tools: {health['tools']}")
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url=self.health_url) as response:
                    if response.status == 401:
                        raise AuthenticationError("Invalid API key")
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            raise ConnectionError(f"Failed to connect to server: {e}") from e

    async def initialize(
        self,
        client_name: str = "shadai-python-client",
        client_version: str = "1.0.0",
    ) -> Dict[str, Any]:
        """
        Initialize MCP connection with server.

        Args:
            client_name: Name of your client application
            client_version: Version of your client application

        Returns:
            Server capabilities and information

        Examples:
            >>> info = await client.initialize(
            ...     client_name="my-app",
            ...     client_version="1.0.0"
            ... )
        """
        return await self.call_rpc(
            method="initialize",
            params={
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": client_name,
                    "version": client_version,
                },
            },
        )

    async def list_tools(self) -> list:
        """
        List all available tools on the server.

        Returns:
            List of tool definitions with names, descriptions, and parameters

        Examples:
            >>> tools = await client.list_tools()
            >>> for tool in tools:
            ...     print(f"{tool['name']}: {tool['description']}")
        """
        response = await self.call_rpc(method="tools/list")
        return response.get("result", {}).get("tools", [])

    async def call_rpc(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make a JSON-RPC call to the server (non-streaming).

        Args:
            method: JSON-RPC method name
            params: Method parameters

        Returns:
            JSON-RPC response

        Raises:
            ServerError: If server returns an error
            ConnectionError: If connection fails
        """
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1,
        }

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    url=self.rpc_url,
                    json=request,
                    headers=self._get_headers(),
                ) as response:
                    if response.status == 401:
                        raise AuthenticationError("Invalid API key")
                    response.raise_for_status()
                    data = await response.json()

                    if "error" in data:
                        error = data["error"]
                        raise ServerError(
                            f"{error.get('message', 'Unknown error')} "
                            f"(code: {error.get('code')})"
                        )

                    return data
        except aiohttp.ClientError as e:
            raise ConnectionError(f"Request failed: {e}") from e

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> str:
        """
        Call a tool and get the complete response (non-streaming).

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments as dictionary

        Returns:
            Complete tool response as string

        Examples:
            >>> result = await client.call_tool(
            ...     tool_name="shadai_planner",
            ...     arguments={"prompt": "What tools should I use?"}
            ... )
        """
        response = await self.call_rpc(
            method="tools/call",
            params={
                "name": tool_name,
                "arguments": arguments,
            },
        )

        content = response.get("result", {}).get("content", [])
        if content:
            return content[0].get("text", "")
        return ""

    async def stream_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> AsyncIterator[str]:
        """
        Call a tool and stream response chunks.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments as dictionary

        Yields:
            Text chunks from the tool response

        Examples:
            >>> async for chunk in client.stream_tool(
            ...     tool_name="shadai_query",
            ...     arguments={"session_uuid": "...", "query": "What is ML?"}
            ... ):
            ...     print(chunk, end="", flush=True)
        """
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
            "id": 1,
        }

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    url=self.stream_url,
                    json=request,
                    headers=self._get_headers(),
                ) as response:
                    if response.status == 401:
                        raise AuthenticationError("Invalid API key")
                    response.raise_for_status()

                    async for line in response.content:
                        line_str = line.decode("utf-8").strip()

                        if not line_str or not line_str.startswith("data:"):
                            continue

                        data_str = line_str.split(":", 1)[1].strip()
                        try:
                            data = json.loads(data_str)

                            if data.get("method") == "notifications/progress":
                                chunk = data.get("params", {}).get("progress", "")
                                if chunk:
                                    yield chunk

                        except json.JSONDecodeError:
                            continue

        except aiohttp.ClientError as e:
            raise ConnectionError(f"Streaming request failed: {e}") from e
