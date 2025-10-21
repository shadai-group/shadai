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
    timeout: int = 30,
    system_prompt: str = None,
    llm_model: LLMModel = None,
    embedding_model: EmbeddingModel = None
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
| `system_prompt` | `str` | `None` | Custom system prompt for the session |
| `llm_model` | `LLMModel` | `None` | LLM model to use (see Model Selection) |
| `embedding_model` | `EmbeddingModel` | `None` | Embedding model to use (see Model Selection) |

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

# With custom models and system prompt
from shadai import LLMModel, EmbeddingModel

async with Shadai(
    name="ai-analysis",
    llm_model=LLMModel.OPENAI_GPT_4O,
    embedding_model=EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_LARGE,
    system_prompt="You are an expert data analyst."
) as shadai:
    pass

# Mix providers (Google LLM + OpenAI embeddings)
async with Shadai(
    name="mixed-providers",
    llm_model=LLMModel.GOOGLE_GEMINI_2_0_FLASH,
    embedding_model=EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL
) as shadai:
    pass
```

## Model Selection

### Available LLM Models

```python
from shadai import LLMModel

# OpenAI Models
LLMModel.OPENAI_GPT_5
LLMModel.OPENAI_GPT_5_MINI
LLMModel.OPENAI_GPT_5_NANO
LLMModel.OPENAI_GPT_4_1
LLMModel.OPENAI_GPT_4_1_MINI
LLMModel.OPENAI_GPT_4O
LLMModel.OPENAI_GPT_4O_MINI

# Azure Models
LLMModel.AZURE_GPT_5
LLMModel.AZURE_GPT_5_MINI
LLMModel.AZURE_GPT_5_NANO
LLMModel.AZURE_GPT_4_1
LLMModel.AZURE_GPT_4_1_MINI
LLMModel.AZURE_GPT_4O
LLMModel.AZURE_GPT_4O_MINI

# Anthropic Models
LLMModel.ANTHROPIC_CLAUDE_SONNET_4_5
LLMModel.ANTHROPIC_CLAUDE_SONNET_4
LLMModel.ANTHROPIC_CLAUDE_3_7_SONNET
LLMModel.ANTHROPIC_CLAUDE_OPUS_4_1
LLMModel.ANTHROPIC_CLAUDE_OPUS_4
LLMModel.ANTHROPIC_CLAUDE_3_5_HAIKU

# Google Models
LLMModel.GOOGLE_GEMINI_2_5_PRO
LLMModel.GOOGLE_GEMINI_2_5_FLASH
LLMModel.GOOGLE_GEMINI_2_5_FLASH_LITE
LLMModel.GOOGLE_GEMINI_2_0_FLASH
LLMModel.GOOGLE_GEMINI_2_0_FLASH_LITE
```

### Available Embedding Models

```python
from shadai import EmbeddingModel

# OpenAI Embeddings
EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_LARGE
EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL

# Azure Embeddings
EmbeddingModel.AZURE_TEXT_EMBEDDING_3_LARGE
EmbeddingModel.AZURE_TEXT_EMBEDDING_3_SMALL

# Google Embeddings
EmbeddingModel.GOOGLE_GEMINI_EMBEDDING_001
```

### Model Selection Examples

```python
from shadai import Shadai, LLMModel, EmbeddingModel

# OpenAI GPT-4o with large embeddings
async with Shadai(
    name="premium-session",
    llm_model=LLMModel.OPENAI_GPT_4O,
    embedding_model=EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_LARGE
) as shadai:
    async for chunk in shadai.query("Detailed analysis"):
        print(chunk, end="")

# Fast and cost-effective (Google)
async with Shadai(
    name="fast-session",
    llm_model=LLMModel.GOOGLE_GEMINI_2_0_FLASH,
    embedding_model=EmbeddingModel.GOOGLE_GEMINI_EMBEDDING_001
) as shadai:
    async for chunk in shadai.query("Quick question"):
        print(chunk, end="")

# Claude for creative tasks
async with Shadai(
    name="creative-session",
    llm_model=LLMModel.ANTHROPIC_CLAUDE_SONNET_4_5,
    embedding_model=EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL,
    system_prompt="You are a creative writing assistant."
) as shadai:
    async for chunk in shadai.query("Write a story"):
        print(chunk, end="")

# Azure deployment
async with Shadai(
    name="enterprise-session",
    llm_model=LLMModel.AZURE_GPT_4O,
    embedding_model=EmbeddingModel.AZURE_TEXT_EMBEDDING_3_LARGE
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
