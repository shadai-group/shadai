# Shadai Client API Reference

Complete reference for the main `Shadai` client class.

## Class: Shadai

Main entry point for interacting with Shadai services.

### Constructor

```python
Shadai(
    name: str = None,
    temporal: bool = False,
    api_key: str = None,
    base_url: str = "http://localhost",
    timeout: int = 30
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | `None` | Session name (required if not temporal) |
| `temporal` | `bool` | `False` | Create temporary session (auto-deleted) |
| `api_key` | `str` | `None` | API key (reads from env if not provided) |
| `base_url` | `str` | `"http://localhost"` | Shadai server URL |
| `timeout` | `int` | `30` | Request timeout in seconds |

**Examples:**

```python
# Named session
async with Shadai(name="my-project") as shadai:
    pass

# Temporal session
async with Shadai(temporal=True) as shadai:
    pass

# Custom configuration
async with Shadai(
    name="custom",
    api_key="your-key",
    base_url="https://api.shadai.com",
    timeout=60
) as shadai:
    pass
```

## Methods

### ingest()

Ingest documents from a folder into the session.

```python
async def ingest(folder_path: str) -> dict
```

**Parameters:**
- `folder_path` (str): Path to folder containing documents

**Returns:**
```python
{
    "total_files": int,
    "successful_count": int,
    "failed_count": int,
    "skipped_count": int,
    "successful": List[dict],
    "failed": List[dict],
    "skipped": List[dict]
}
```

**Example:**
```python
results = await shadai.ingest(folder_path="./documents")
print(f"Ingested {results['successful_count']} files")
```

### query()

Query the knowledge base.

```python
async def query(
    query: str,
    use_memory: bool = True
) -> AsyncIterator[str]
```

**Parameters:**
- `query` (str): Question to ask
- `use_memory` (bool): Enable conversation memory (default: True)

**Returns:** Async iterator of response chunks

**Example:**
```python
async for chunk in shadai.query("What are the terms?"):
    print(chunk, end="")
```

### summarize()

Generate summary of all documents.

```python
async def summarize(use_memory: bool = True) -> AsyncIterator[str]
```

**Parameters:**
- `use_memory` (bool): Enable conversation memory (default: True)

**Returns:** Async iterator of summary chunks

**Example:**
```python
async for chunk in shadai.summarize():
    print(chunk, end="")
```

### web_search()

Search the web for information.

```python
async def web_search(
    prompt: str,
    use_web_search: bool = True,
    use_memory: bool = True
) -> AsyncIterator[str]
```

**Parameters:**
- `prompt` (str): Search query
- `use_web_search` (bool): Enable web search (default: True)
- `use_memory` (bool): Enable conversation memory (default: True)

**Returns:** Async iterator of response chunks

**Example:**
```python
async for chunk in shadai.web_search("Latest AI news"):
    print(chunk, end="")
```

### engine()

Multi-tool orchestration.

```python
async def engine(
    prompt: str,
    use_knowledge_base: bool = False,
    use_summary: bool = False,
    use_web_search: bool = False,
    use_memory: bool = True
) -> AsyncIterator[str]
```

**Parameters:**
- `prompt` (str): Query or task
- `use_knowledge_base` (bool): Query documents (default: False)
- `use_summary` (bool): Include summary (default: False)
- `use_web_search` (bool): Search web (default: False)
- `use_memory` (bool): Enable memory (default: True)

**Returns:** Async iterator of response chunks

**Example:**
```python
async for chunk in shadai.engine(
    prompt="Compare docs with trends",
    use_knowledge_base=True,
    use_web_search=True
):
    print(chunk, end="")
```

### agent()

Execute custom tool workflow.

```python
async def agent(
    prompt: str,
    tools: List[Callable]
) -> AsyncIterator[str]
```

**Parameters:**
- `prompt` (str): Task description
- `tools` (List[Callable]): List of custom tools

**Returns:** Async iterator of response chunks

**Example:**
```python
from shadai import tool

@tool
def my_tool(param: str) -> str:
    return "result"

async for chunk in shadai.agent(
    prompt="Execute task",
    tools=[my_tool]
):
    print(chunk, end="")
```

### get_session_history()

Retrieve conversation history.

```python
async def get_session_history(
    page: int = 1,
    page_size: int = 5
) -> dict
```

**Parameters:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Messages per page (default: 5, max: 10)

**Returns:**
```python
{
    "count": int,
    "next": int | None,
    "previous": int | None,
    "results": [
        {
            "uuid": str,
            "role": str,
            "content": str,
            "created_at": str,
            "token_usage": dict
        }
    ]
}
```

**Example:**
```python
history = await shadai.get_session_history(page=1, page_size=10)
for msg in history["results"]:
    print(f"{msg['role']}: {msg['content']}")
```

### clear_session_history()

Clear all conversation history.

```python
async def clear_session_history() -> dict
```

**Returns:**
```python
{
    "message": "Session history cleared successfully"
}
```

**Example:**
```python
await shadai.clear_session_history()
```

## Context Manager

`Shadai` supports async context manager protocol:

```python
async with Shadai(name="session") as shadai:
    # Automatic initialization
    await shadai.ingest(folder_path="./docs")
    # Automatic cleanup on exit
```

**Equivalent to:**
```python
shadai = Shadai(name="session")
await shadai.__aenter__()
try:
    await shadai.ingest(folder_path="./docs")
finally:
    await shadai.__aexit__(None, None, None)
```

## Next Steps

- [Tool-Specific APIs](query-tool.md)
- [Exceptions Reference](exceptions.md)
