"""
Session Context Manager
-----------------------
Context manager for managing RAG session lifecycle.
"""

import json
import os
from typing import Optional
from uuid import uuid4

from .client import ShadaiClient
from .exceptions import InvalidArgumentsError


class Session:
    """Context manager for RAG session lifecycle.

    Automatically handles session creation, retrieval, and optional deletion.

    Usage:
        # Create a new session
        async with Session() as session:
            uuid = session.uuid

        # Use existing session by UUID
        async with Session(uuid="existing-uuid") as session:
            ...

        # Use existing session by name
        async with Session(name="my-session") as session:
            ...

        # Auto-delete session on exit
        async with Session(delete=True) as session:
            ...

    Args:
        uuid: Optional session UUID to retrieve existing session
        name: Optional session name to retrieve existing session
        delete: If True, delete session on context exit (default: False)
        api_key: Optional API key for authentication

    Raises:
        InvalidArgumentsError: If both uuid and name are provided
    """

    def __init__(
        self,
        uuid: Optional[str] = None,
        name: Optional[str] = None,
        delete: bool = False,
    ) -> None:
        """Initialize session context manager.

        Args:
            uuid: Optional session UUID to retrieve
            name: Optional session name to retrieve
            delete: Whether to delete session on exit
        """
        if uuid and name:
            raise InvalidArgumentsError(
                "Cannot provide both 'uuid' and 'name' parameters. "
                "Please provide only one or neither."
            )

        self._uuid = uuid
        self._name = name
        self._delete = delete
        self._client = ShadaiClient()
        self._session_data: Optional[dict] = None

    @property
    def uuid(self) -> Optional[str]:
        """Get session UUID."""
        return str(self._session_data.get("uuid")) if self._session_data else None

    @property
    def name(self) -> Optional[str]:
        """Get session name."""
        return self._session_data.get("name") if self._session_data else None

    async def __aenter__(self) -> "Session":
        """Enter context: create or retrieve session.

        Returns:
            Session instance with populated session data
        """
        if self._uuid:
            # Retrieve by UUID
            result = await self._client.call_tool(
                tool_name="session_retrieve",
                arguments={"session_uuid": self._uuid},
            )
            self._session_data = json.loads(result)
        elif self._name:
            # Retrieve by name
            result = await self._client.call_tool(
                tool_name="session_retrieve",
                arguments={"name": self._name},
            )
            self._session_data = json.loads(result)
        else:
            # Create new session with generated name
            generated_name = f"session-{uuid4().hex[:8]}"
            result = await self._client.call_tool(
                tool_name="session_create",
                arguments={"name": generated_name},
            )
            self._session_data = json.loads(result)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context: optionally delete session.

        Args:
            exc_type: Exception type if raised
            exc_val: Exception value if raised
            exc_tb: Exception traceback if raised
        """
        if self._delete and self.uuid:
            await self._client.call_tool(
                tool_name="session_delete",
                arguments={"session_uuid": self.uuid},
            )
