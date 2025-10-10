"""
Shadai Tools - High-Level API Wrappers
---------------------------------------
Beautiful, Pythonic interfaces for Shadai AI tools.
"""

from typing import Any, AsyncIterator, Dict, List

from .client import ShadaiClient
from .models import AgentTool


class QueryTool:
    """
    Knowledge Base Query Tool.

    Retrieves relevant information from uploaded documents using RAG
    (Retrieval-Augmented Generation).

    Examples:
        >>> query = QueryTool(client=client, session_uuid="...")
        >>> async for chunk in query("What is machine learning?"):
        ...     print(chunk, end="", flush=True)
    """

    def __init__(self, client: ShadaiClient, session_uuid: str) -> None:
        """
        Initialize Query tool.

        Args:
            client: Shadai client instance
            session_uuid: Your session UUID
        """
        self.client = client
        self.session_uuid = session_uuid

    async def __call__(
        self,
        query: str,
        use_memory: bool = False,
    ) -> AsyncIterator[str]:
        """
        Query the knowledge base with streaming response.

        Args:
            query: Your question or search query
            use_memory: Enable conversation memory

        Yields:
            Text chunks from the knowledge base

        Examples:
            >>> async for chunk in query_tool("Explain transformers"):
            ...     print(chunk, end="")
        """
        async for chunk in self.client.stream_tool(
            tool_name="shadai_query",
            arguments={
                "session_uuid": self.session_uuid,
                "query": query,
                "use_memory": use_memory,
            },
        ):
            yield chunk


class SummarizeTool:
    """
    Document Summarization Tool.

    Generates comprehensive summaries of all documents in a session.

    Examples:
        >>> summarize = SummarizeTool(client=client, session_uuid="...")
        >>> async for chunk in summarize():
        ...     print(chunk, end="", flush=True)
    """

    def __init__(self, client: ShadaiClient, session_uuid: str) -> None:
        """
        Initialize Summarize tool.

        Args:
            client: Shadai client instance
            session_uuid: Your session UUID
        """
        self.client = client
        self.session_uuid = session_uuid

    async def __call__(self, use_memory: bool = False) -> AsyncIterator[str]:
        """
        Generate summary of all session documents.

        Args:
            use_memory: Enable conversation memory

        Yields:
            Text chunks from the summary

        Examples:
            >>> async for chunk in summarize_tool():
            ...     print(chunk, end="")
        """
        async for chunk in self.client.stream_tool(
            tool_name="shadai_summarize",
            arguments={
                "session_uuid": self.session_uuid,
                "use_memory": use_memory,
            },
        ):
            yield chunk


class WebSearchTool:
    """
    Web Search Tool.

    Searches the internet for current information and provides cited answers.

    Examples:
        >>> search = WebSearchTool(client=client, session_uuid="...")
        >>> async for chunk in search("Latest AI developments 2024"):
        ...     print(chunk, end="", flush=True)
    """

    def __init__(self, client: ShadaiClient, session_uuid: str) -> None:
        """
        Initialize Web Search tool.

        Args:
            client: Shadai client instance
            session_uuid: Your session UUID
        """
        self.client = client
        self.session_uuid = session_uuid

    async def __call__(
        self,
        prompt: str,
        use_web_search: bool = True,
        use_memory: bool = False,
    ) -> AsyncIterator[str]:
        """
        Search the web and get an answer.

        Args:
            prompt: Your question or search query
            use_web_search: Enable web search (default: True)
            use_memory: Enable conversation memory

        Yields:
            Text chunks from the search results

        Examples:
            >>> async for chunk in search_tool("Current weather in Paris"):
            ...     print(chunk, end="")
        """
        async for chunk in self.client.stream_tool(
            tool_name="shadai_web_search",
            arguments={
                "session_uuid": self.session_uuid,
                "prompt": prompt,
                "use_web_search": use_web_search,
                "use_memory": use_memory,
            },
        ):
            yield chunk


class EngineTool:
    """
    Shadai Engine Tool.

    Orchestrates multiple tools (knowledge base, summarization, web search)
    to provide comprehensive answers.

    Examples:
        >>> engine = EngineTool(client=client, session_uuid="...")
        >>> async for chunk in engine(
        ...     prompt="Compare my docs with current trends",
        ...     use_knowledge_base=True,
        ...     use_web_search=True
        ... ):
        ...     print(chunk, end="", flush=True)
    """

    def __init__(self, client: ShadaiClient, session_uuid: str) -> None:
        """
        Initialize Engine tool.

        Args:
            client: Shadai client instance
            session_uuid: Your session UUID
        """
        self.client = client
        self.session_uuid = session_uuid

    async def __call__(
        self,
        prompt: str,
        use_knowledge_base: bool = False,
        use_summary: bool = False,
        use_web_search: bool = False,
        use_memory: bool = False,
    ) -> AsyncIterator[str]:
        """
        Execute engine with multiple tool capabilities.

        Args:
            prompt: Your question or prompt
            use_knowledge_base: Enable knowledge base retrieval
            use_summary: Enable document summarization
            use_web_search: Enable web search
            use_memory: Enable conversation memory

        Yields:
            Text chunks from the engine

        Examples:
            >>> async for chunk in engine_tool(
            ...     "What are ML trends?",
            ...     use_knowledge_base=True,
            ...     use_web_search=True
            ... ):
            ...     print(chunk, end="")
        """
        async for chunk in self.client.stream_tool(
            tool_name="shadai_engine",
            arguments={
                "session_uuid": self.session_uuid,
                "prompt": prompt,
                "use_knowledge_base": use_knowledge_base,
                "use_summary": use_summary,
                "use_web_search": use_web_search,
                "use_memory": use_memory,
            },
        ):
            yield chunk


class _AgentOrchestrator:
    """
    Internal orchestrator for Shadai Agent workflow.

    The agent automatically:
    1. Plans which tools to use (via planner)
    2. Executes the selected tools with provided arguments
    3. Synthesizes all outputs into a unified answer (via synthesizer)

    This provides a complete agentic workflow where you provide tools with their
    implementations and arguments, and the agent handles the orchestration.
    """

    def __init__(self, client: ShadaiClient) -> None:
        """
        Initialize Agent orchestrator.

        Args:
            client: Shadai client instance
        """
        self.client = client

    async def __call__(
        self,
        prompt: str,
        tools: List[AgentTool],
    ) -> AsyncIterator[str]:
        """
        Execute agentic workflow: plan → execute → synthesize.

        Args:
            prompt: User's question or task
            tools: List of AgentTool objects with name, description, implementation, and arguments

        Yields:
            Text chunks from the synthesized final answer
        """
        import inspect
        import json

        # Convert list to dictionary for lookup
        tools_dict: Dict[str, AgentTool] = {tool.name: tool for tool in tools}

        # Step 1: Plan - Get tool selection from server
        tool_definitions = [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
            for tool in tools_dict.values()
        ]

        plan_result = await self.client.call_tool(
            tool_name="shadai_planner",
            arguments={
                "prompt": prompt,
                "available_tools": tool_definitions,
            },
        )
        plan = json.loads(plan_result)

        # Step 2: Execute - Run selected tools locally with inferred arguments
        tool_executions = []

        for tool_item in plan["tool_plan"]:
            tool_name = tool_item["name"]
            # Use inferred arguments from planner
            inferred_args = tool_item.get("arguments", {})

            if tool_name not in tools_dict:
                # Tool not available, record error
                tool_executions.append(
                    {
                        "tool_name": tool_name,
                        "arguments": inferred_args,
                        "output": f"Error: Tool '{tool_name}' not found in provided tools",
                    }
                )
                continue

            tool = tools_dict[tool_name]
            tool_impl = tool.implementation

            # Merge user-provided arguments with inferred arguments (inferred takes precedence)
            final_args = {**tool.arguments, **inferred_args}

            # Execute the tool implementation with final arguments
            try:
                if inspect.iscoroutinefunction(tool_impl):
                    result = await tool_impl(**final_args)
                else:
                    result = tool_impl(**final_args)

                tool_executions.append(
                    {
                        "tool_name": tool_name,
                        "arguments": final_args,
                        "output": str(result),
                    }
                )
            except Exception as e:
                tool_executions.append(
                    {
                        "tool_name": tool_name,
                        "arguments": final_args,
                        "output": f"Error executing tool: {str(e)}",
                    }
                )

        # Step 3: Synthesize - Combine outputs via server
        async for chunk in self.client.stream_tool(
            tool_name="shadai_synthesizer",
            arguments={
                "prompt": prompt,
                "tool_definitions": tool_definitions,
                "tool_executions": tool_executions,
            },
        ):
            yield chunk


class Shadai:
    """
    Main entry point for Shadai AI client.

    Provides convenient access to all Shadai tools with a clean, intuitive API.

    Examples:
        >>> from client.shadai import Shadai, AgentTool
        >>>
        >>> shadai = Shadai(api_key="your-api-key")
        >>>
        >>> # Check server health
        >>> health = await shadai.health()
        >>> print(health)
        >>>
        >>> # Query knowledge base (one-step)
        >>> async for chunk in shadai.query(
        ...     query="What is AI?",
        ...     session_uuid="..."
        ... ):
        ...     print(chunk, end="")
        >>>
        >>> # Use intelligent agent (orchestrates plan → execute → synthesize)
        >>> tools = [
        ...     AgentTool(
        ...         name="my_tool",
        ...         description="Does something",
        ...         implementation=my_function,
        ...         arguments={"param": "value"}
        ...     )
        ... ]
        >>> async for chunk in shadai.agent(
        ...     prompt="Do task",
        ...     tools=tools
        ... ):
        ...     print(chunk, end="")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost",
        timeout: int = 30,
    ) -> None:
        """
        Initialize Shadai client.

        Args:
            api_key: Your Shadai API key (required)
            base_url: Base URL of Shadai server
            timeout: Request timeout in seconds

        Examples:
            >>> shadai = Shadai(api_key="your-api-key")
            >>> shadai = Shadai(
            ...     api_key="your-api-key",
            ...     base_url="https://api.shadai.com"
            ... )
        """
        self.client = ShadaiClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )

    async def health(self) -> Dict[str, Any]:
        """
        Check server health.

        Returns:
            Server health information

        Examples:
            >>> health = await shadai.health()
            >>> print(f"Status: {health['status']}")
        """
        return await self.client.health_check()

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools.

        Returns:
            List of tool definitions

        Examples:
            >>> tools = await shadai.list_tools()
            >>> for tool in tools:
            ...     print(tool["name"])
        """
        return await self.client.list_tools()

    async def query(
        self,
        query: str,
        session_uuid: str,
        use_memory: bool = False,
    ) -> AsyncIterator[str]:
        """
        Query the knowledge base with streaming response.

        Args:
            query: Your question or search query
            session_uuid: Your session UUID
            use_memory: Enable conversation memory

        Yields:
            Text chunks from the knowledge base

        Examples:
            >>> async for chunk in shadai.query(
            ...     query="What is ML?",
            ...     session_uuid="..."
            ... ):
            ...     print(chunk, end="")
        """
        query_tool = QueryTool(client=self.client, session_uuid=session_uuid)
        async for chunk in query_tool(query=query, use_memory=use_memory):
            yield chunk

    async def summarize(
        self,
        session_uuid: str,
        use_memory: bool = False,
    ) -> AsyncIterator[str]:
        """
        Generate summary of all session documents.

        Args:
            session_uuid: Your session UUID
            use_memory: Enable conversation memory

        Yields:
            Text chunks from the summary

        Examples:
            >>> async for chunk in shadai.summarize(session_uuid="..."):
            ...     print(chunk, end="")
        """
        summarize_tool = SummarizeTool(client=self.client, session_uuid=session_uuid)
        async for chunk in summarize_tool(use_memory=use_memory):
            yield chunk

    async def web_search(
        self,
        prompt: str,
        session_uuid: str,
        use_web_search: bool = True,
        use_memory: bool = False,
    ) -> AsyncIterator[str]:
        """
        Search the web and get an answer.

        Args:
            prompt: Your question or search query
            session_uuid: Your session UUID
            use_web_search: Enable web search (default: True)
            use_memory: Enable conversation memory

        Yields:
            Text chunks from the search results

        Examples:
            >>> async for chunk in shadai.web_search(
            ...     prompt="Latest AI news",
            ...     session_uuid="..."
            ... ):
            ...     print(chunk, end="")
        """
        search_tool = WebSearchTool(client=self.client, session_uuid=session_uuid)
        async for chunk in search_tool(
            prompt=prompt,
            use_web_search=use_web_search,
            use_memory=use_memory,
        ):
            yield chunk

    async def engine(
        self,
        prompt: str,
        session_uuid: str,
        use_knowledge_base: bool = False,
        use_summary: bool = False,
        use_web_search: bool = False,
        use_memory: bool = False,
    ) -> AsyncIterator[str]:
        """
        Execute unified engine with multiple tool capabilities.

        Args:
            prompt: Your question or prompt
            session_uuid: Your session UUID
            use_knowledge_base: Enable knowledge base retrieval
            use_summary: Enable document summarization
            use_web_search: Enable web search
            use_memory: Enable conversation memory

        Yields:
            Text chunks from the engine

        Examples:
            >>> async for chunk in shadai.engine(
            ...     prompt="Analyze my docs",
            ...     session_uuid="...",
            ...     use_knowledge_base=True
            ... ):
            ...     print(chunk, end="")
        """
        engine_tool = EngineTool(client=self.client, session_uuid=session_uuid)
        async for chunk in engine_tool(
            prompt=prompt,
            use_knowledge_base=use_knowledge_base,
            use_summary=use_summary,
            use_web_search=use_web_search,
            use_memory=use_memory,
        ):
            yield chunk

    async def agent(
        self,
        prompt: str,
        tools: List[AgentTool],
    ) -> AsyncIterator[str]:
        """
        Execute intelligent agent workflow: plan → execute → synthesize.

        The agent orchestrates a complete workflow:
        1. Plans which tools to use (via planner API)
        2. Executes tools locally with provided arguments
        3. Synthesizes outputs (via synthesizer API)

        Args:
            prompt: User's question or task
            tools: List of AgentTool objects

        Yields:
            Text chunks from the synthesized response

        Examples:
            >>> from client.shadai import AgentTool
            >>>
            >>> # Define tools
            >>> tools = [
            ...     AgentTool(
            ...         name="search_database",
            ...         description="Search database",
            ...         implementation=search_func,
            ...         arguments={"query": "users", "limit": 10}
            ...     ),
            ...     AgentTool(
            ...         name="generate_report",
            ...         description="Generate report",
            ...         implementation=report_func,
            ...         arguments={"format": "markdown"}
            ...     )
            ... ]
            >>>
            >>> # Agent handles plan → execute → synthesize
            >>> async for chunk in shadai.agent(
            ...     prompt="Find and analyze data",
            ...     tools=tools
            ... ):
            ...     print(chunk, end="")
        """
        orchestrator = _AgentOrchestrator(client=self.client)
        async for chunk in orchestrator(prompt=prompt, tools=tools):
            yield chunk
