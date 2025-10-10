# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Shadai Client** is an official Python SDK for Shadai AI services. It provides a clean, async-first API for querying knowledge bases (RAG), web search, document summarization, and intelligent agent orchestration with custom tools.

**Key Features:**
- Async streaming responses for all operations
- MCP (Model Context Protocol) communication via JSON-RPC and SSE
- Intelligent agent workflow: plan → execute → synthesize
- Automatic tool schema inference using LangChain Core
- Type-safe with Pydantic models

## Development Commands

### Environment Setup
```bash
# Install in development mode
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"
```

### Running Examples
```bash
# Set API key
export SHADAI_API_KEY="your-api-key"

# Run examples
python examples/query_example.py
python examples/agent_example.py
python examples/websearch_example.py
python examples/summary_example.py
```

### Testing & Quality
```bash
# Run tests (when available)
pytest

# Format code
black shadai/

# Type checking
mypy shadai/

# Lint
ruff check shadai/
```

### Building & Publishing
```bash
# Build package
python -m build

# Test install
pip install dist/shadai-*.whl
```

## Architecture

### Core Components

**3-Layer Architecture:**

1. **ShadaiClient** (`client.py`) - Low-level MCP client
   - Handles JSON-RPC communication and SSE streaming
   - Manages authentication, health checks, error handling
   - Methods: `call_rpc()`, `stream_tool()`, `call_tool()`, `list_tools()`
   - All server communication flows through this layer

2. **Tool Wrappers** (`tools.py`) - High-level API interfaces
   - `QueryTool` - RAG-based knowledge base queries
   - `SummarizeTool` - Document summarization
   - `WebSearchTool` - Web search with citations
   - `EngineTool` - Multi-tool orchestration
   - `_AgentOrchestrator` - Internal agent workflow coordinator
   - Each tool wraps `ShadaiClient` methods with domain-specific interfaces

3. **Shadai Main Client** (`tools.py`) - Unified entry point
   - Convenience methods that create and execute tools in one step
   - Methods: `query()`, `summarize()`, `web_search()`, `engine()`, `agent()`
   - Handles tool instantiation and delegation

### Agent Workflow

The `agent()` method orchestrates a complete agentic workflow:

1. **Plan** - Calls `shadai_planner` tool on server with user prompt and tool definitions
   - Server returns which tools to use and infers arguments from prompt
   - Tool definitions include name, description, and JSON Schema parameters

2. **Execute** - Runs selected tools **locally** with inferred arguments
   - Merges user-provided default arguments with planner-inferred arguments
   - Supports both sync and async tool implementations
   - Captures outputs or errors for each tool execution

3. **Synthesize** - Calls `shadai_synthesizer` tool on server
   - Sends tool execution results back to server
   - Server generates unified, coherent response from all tool outputs
   - Streams response back to client

### Tool Definition System

**Two approaches for defining tools:**

1. **Manual Definition** - `AgentTool` class with explicit schema
   ```python
   AgentTool(
       name="search_db",
       description="Search database",
       implementation=search_func,
       parameters={"type": "object", "properties": {...}},
       arguments={"limit": 10}  # Optional defaults
   )
   ```

2. **Automatic Schema Inference** - `@tool` decorator or `AgentTool.from_function()`
   - Uses `langchain_core.tools.base.create_schema_from_function()` to create Pydantic model
   - Converts Pydantic model to JSON Schema via `model_json_schema()`
   - Extracts name from function name
   - Extracts description from docstring (full docstring with Args section)
   - Infers parameter types and descriptions from type hints and Google-style docstrings
   - Requires proper type hints and Google-style docstring Args section for parameter descriptions

### Communication Protocol

**MCP (Model Context Protocol):**
- JSON-RPC 2.0 for non-streaming calls (`/mcp/rpc`)
- Server-Sent Events (SSE) for streaming (`/mcp/stream`)
- Progress notifications via `notifications/progress` method
- Authentication via Bearer token in headers

**Tool Call Format:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "shadai_query",
    "arguments": {"session_uuid": "...", "query": "..."}
  },
  "id": 1
}
```

## Code Patterns

### Session Management
All knowledge base and engine tools require a `session_uuid`. This identifies the document collection context on the server. Sessions are managed server-side (not in this client).

### Streaming Pattern
All main API methods return `AsyncIterator[str]` for streaming:
```python
async for chunk in shadai.query(query="...", session_uuid="..."):
    print(chunk, end="", flush=True)
```

### Error Handling
Custom exception hierarchy in `exceptions.py`:
- `ShadaiError` - Base exception
- `AuthenticationError` - Invalid API key (HTTP 401)
- `ConnectionError` - Network/connection failures
- `ServerError` - Server-side errors from JSON-RPC

### Memory System
Optional `use_memory` parameter enables conversation history:
- When `True`, server maintains context across queries in a session
- When `False`, each query is independent
- Memory is session-scoped

## Important Conventions

### Type Safety
- Full type hints required (`mypy --disallow-untyped-defs`)
- Pydantic models for all data structures
- Use `Union[Callable[..., Any], Callable[..., Any]]` for sync/async callables

### Async Patterns
- All I/O operations are async
- Use `inspect.iscoroutinefunction()` to check if tool implementation is async
- Always use `async with` for aiohttp sessions

### Tool Implementation Requirements
When creating tools for the agent:
1. Must have proper type hints for automatic schema inference (e.g., `query: str`, `limit: int = 10`)
2. Should have Google-style docstrings with Args section for parameter descriptions
   ```python
   def my_tool(query: str, limit: int = 10) -> str:
       """Tool description here.

       Args:
           query: Description of query parameter
           limit: Description of limit parameter
       """
       return "result"
   ```
3. Can be sync or async (agent handles both via `inspect.iscoroutinefunction()`)
4. Should return string or JSON-serializable data
5. The `create_schema_from_function()` will parse the docstring to extract parameter descriptions

### Versioning
- Version defined in `__version__.py` and synced to `pyproject.toml` and `setup.py`
- Follow semantic versioning (currently v0.1.28)
- Update all three files when bumping version

## File Organization

```
shadai/
├── __init__.py         # Package exports (use __all__)
├── __version__.py      # Version constants
├── client.py           # Low-level MCP client
├── tools.py            # High-level tools + main Shadai class
├── models.py           # Pydantic models (Tool, AgentTool, etc.)
└── exceptions.py       # Exception hierarchy
```

## Dependencies

**Core:**
- `aiohttp>=3.8.0` - Async HTTP client for MCP communication
- `pydantic>=2.0.0` - Data validation and serialization
- `langchain-core==1.0.0a8` - Function schema inference utilities

**Dev:**
- `pytest>=7.0` + `pytest-asyncio>=0.21.0`
- `black>=23.0` (line-length=88, target py310+)
- `mypy>=1.0` (strict mode)
- `ruff>=0.1.0`

## API Server Tools

The client communicates with these server-side tools:

1. **shadai_query** - RAG knowledge base queries
2. **shadai_summarize** - Document summarization
3. **shadai_web_search** - Web search with citations
4. **shadai_engine** - Multi-tool orchestration
5. **shadai_planner** - Tool selection and argument inference (used by agent)
6. **shadai_synthesizer** - Output synthesis (used by agent)

## Testing Approach

When writing tests:
- Use `pytest-asyncio` for async test support
- Mock `aiohttp.ClientSession` responses for unit tests
- Set `SHADAI_API_KEY` in test environment
- Test both streaming and non-streaming paths
- Verify exception handling for 401, connection errors, and server errors
