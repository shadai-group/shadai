# Shadai Client - Official Python SDK

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Beautiful, Pythonic client for Shadai AI services.** Query your knowledge base, orchestrate custom tools with intelligent agents, and more with an intuitive, production-ready API.

## ✨ Features

- 🚀 **Easy to use** - Clean, intuitive API design with one-step async patterns
- ⚡ **Async streaming** - Real-time streaming responses for all tools
- 🛠️ **Multiple tools** - Query, summarize, search, engine, and intelligent agent
- 🤖 **Intelligent agent** - Automatic plan → execute → synthesize workflow
- 🔒 **Type-safe** - Full type hints and Pydantic models for better IDE support
- 📦 **Minimal dependencies** - Only requires `aiohttp` and `pydantic`
- 🎯 **Production-ready** - Comprehensive error handling

## 📦 Installation

```bash
pip install shadai-client
```

Or install from source:

```bash
cd client
pip install -e .
```

## 🚀 Quick Start

```python
import asyncio
from shadai import Shadai

async def main():
    # Initialize client
    shadai = Shadai(api_key="your-api-key")

    # Query knowledge base (one-step)
    async for chunk in shadai.query(
        query="What is machine learning?",
        session_uuid="your-session-uuid"
    ):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

## 📚 Usage Examples

### Knowledge Base Query

Query your uploaded documents using RAG (Retrieval-Augmented Generation):

```python
from shadai import Shadai

shadai = Shadai(api_key="your-api-key")

# Ask questions about your documents
async for chunk in shadai.query(
    query="What are the key findings?",
    session_uuid="your-session-uuid"
):
    print(chunk, end="", flush=True)

# Query with conversation memory
async for chunk in shadai.query(
    query="Tell me more",
    session_uuid="your-session-uuid",
    use_memory=True
):
    print(chunk, end="", flush=True)
```

### Document Summarization

Generate comprehensive summaries of all documents in a session:

```python
async for chunk in shadai.summarize(session_uuid="your-session-uuid"):
    print(chunk, end="", flush=True)
```

### Web Search

Search the internet for current information:

```python
async for chunk in shadai.web_search(
    prompt="Latest AI developments 2024",
    session_uuid="your-session-uuid"
):
    print(chunk, end="", flush=True)
```

### Unified Engine

Orchestrate multiple tools for comprehensive answers:

```python
async for chunk in shadai.engine(
    prompt="Compare my docs with current trends",
    session_uuid="your-session-uuid",
    use_knowledge_base=True,
    use_web_search=True,
    use_memory=True
):
    print(chunk, end="", flush=True)
```

### Intelligent Agent

Orchestrate plan → execute → synthesize workflow with custom tools.
**The planner automatically infers tool arguments from your prompt!**

```python
from shadai import Shadai, AgentTool

shadai = Shadai(api_key="your-api-key")

# Define your custom tools
def search_database(query: str, limit: int = 10) -> str:
    """Search database for user information."""
    # Your implementation
    return "Search results..."

def generate_report(data: str, format: str = "text") -> str:
    """Generate a formatted report."""
    # Your implementation
    return "Generated report..."

# Create list of tools WITHOUT specifying arguments
# The planner will infer them from your prompt!
tools = [
    AgentTool(
        name="search_database",
        description="Search the database for user information",
        implementation=search_database,
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Max results"}
            },
            "required": ["query"]
        }
    ),
    AgentTool(
        name="generate_report",
        description="Generate a formatted report from data",
        implementation=generate_report,
        parameters={
            "type": "object",
            "properties": {
                "data": {"type": "string", "description": "Data for report"},
                "format": {"type": "string", "description": "Report format"}
            }
        }
    )
]

# Agent automatically infers arguments from your prompt!
async for chunk in shadai.agent(
    prompt="Find the top 5 users and create a PDF report",
    tools=tools
):
    print(chunk, end="", flush=True)
```

The agent automatically:
1. **Plans** which tools to use based on your prompt
2. **Infers** the appropriate arguments for each tool from your prompt
3. **Executes** the selected tools locally with inferred arguments
4. **Synthesizes** all outputs into a unified, coherent answer

## 🔧 Configuration

### Environment Variables

```bash
export SHADAI_API_KEY="your-api-key"
export SHADAI_BASE_URL="http://localhost"  # Optional
```

### Client Initialization

```python
# Basic
shadai = Shadai(api_key="your-api-key")

# Custom server
shadai = Shadai(
    api_key="your-api-key",
    base_url="https://api.shadai.com"
)

# Custom timeout
shadai = Shadai(
    api_key="your-api-key",
    timeout=60  # seconds
)
```

## 🛠️ Available Tools

| Tool | Description | Streaming |
|------|-------------|-----------|
| `query()` | Query knowledge base with RAG | ✅ |
| `summarize()` | Summarize all session documents | ✅ |
| `web_search()` | Search web for current information | ✅ |
| `engine()` | Unified multi-tool orchestration | ✅ |
| `agent()` | Intelligent agent (plan → execute → synthesize) | ✅ |

## 📖 API Reference

### Shadai

Main entry point for the client.

```python
shadai = Shadai(api_key: str, base_url: str = "http://localhost", timeout: int = 30)
```

**Methods:**
- `health()` → `Dict[str, Any]` - Check server health
- `list_tools()` → `List[Dict]` - List available tools
- `query(query, session_uuid, use_memory)` → `AsyncIterator[str]` - Query knowledge base
- `summarize(session_uuid, use_memory)` → `AsyncIterator[str]` - Summarize documents
- `web_search(prompt, session_uuid, use_web_search, use_memory)` → `AsyncIterator[str]` - Search web
- `engine(prompt, session_uuid, **options)` → `AsyncIterator[str]` - Unified engine
- `agent(prompt, tools)` → `AsyncIterator[str]` - Intelligent agent

### query()

Query your knowledge base with streaming responses.

```python
async for chunk in shadai.query(
    query="What is AI?",
    session_uuid="...",
    use_memory=False
):
    print(chunk, end="")
```

### summarize()

Summarize all documents in a session.

```python
async for chunk in shadai.summarize(
    session_uuid="...",
    use_memory=False
):
    print(chunk, end="")
```

### web_search()

Search the web for current information.

```python
async for chunk in shadai.web_search(
    prompt="Latest AI news",
    session_uuid="...",
    use_web_search=True,
    use_memory=False
):
    print(chunk, end="")
```

### engine()

Unified engine with multiple tool capabilities.

```python
async for chunk in shadai.engine(
    prompt="Analyze my documents",
    session_uuid="...",
    use_knowledge_base=True,
    use_web_search=True,
    use_summary=False,
    use_memory=False
):
    print(chunk, end="")
```

### agent()

Intelligent agent that orchestrates custom tools.

```python
from shadai import AgentTool

tools = [
    AgentTool(
        name="my_tool",
        description="Does something",
        implementation=my_function,
        arguments={"param": "value"}
    )
]

async for chunk in shadai.agent(
    prompt="Do task",
    tools=tools
):
    print(chunk, end="")
```

## 🚨 Error Handling

```python
from shadai import (
    Shadai,
    AuthenticationError,
    ConnectionError,
    ServerError
)

try:
    shadai = Shadai(api_key="invalid-key")
    await shadai.health()
except AuthenticationError:
    print("Invalid API key")
except ConnectionError:
    print("Cannot connect to server")
except ServerError as e:
    print(f"Server error: {e}")
```

## 📝 Examples

Check the `examples/` directory for complete examples:

- `query_example.py` - Knowledge base queries
- `summary_example.py` - Document summarization
- `websearch_example.py` - Web search
- `agent_example.py` - Intelligent agent workflow
- `agent_synthesis_example.py` - Advanced synthesis with multiple data sources
- `complete_workflow.py` - Full agent workflow with multiple examples

Run examples:

```bash
cd client/
python examples/query_example.py
python examples/summary_example.py
python examples/websearch_example.py
python examples/agent_example.py
python examples/agent_synthesis_example.py
python examples/complete_workflow.py
```

## 🔒 Security

- Always use environment variables for API keys
- Never commit API keys to version control
- Use HTTPS in production (`base_url="https://..."`)

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines.

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- **Documentation**: https://docs.shadai.com
- **GitHub**: https://github.com/shadai/shadai-client
- **Issues**: https://github.com/shadai/shadai-client/issues

## 💡 Support

- 📧 Email: support@shadai.com
- 💬 Discord: https://discord.gg/shadai
- 📖 Docs: https://docs.shadai.com

---

Made with ❤️ by the Shadai Team
