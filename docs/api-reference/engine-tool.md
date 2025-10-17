# Engine Tool API

Orchestrate multiple AI capabilities (knowledge base, web search, summarization) for comprehensive analysis.

## Method Signature

```python
async def engine(
    prompt: str,
    use_knowledge_base: bool = True,
    use_summary: bool = True,
    use_web_search: bool = True,
    use_memory: bool = True
) -> AsyncIterator[str]
```

## Parameters

- **prompt** (str, required): Query or analysis task
- **use_knowledge_base** (bool, optional): Query uploaded documents (default: **True**)
- **use_summary** (bool, optional): Include document summary context (default: **True**)
- **use_web_search** (bool, optional): Search web for current information (default: **True**)
- **use_memory** (bool, optional): Enable conversation context/memory (default: **True**)

## Returns

Async iterator yielding response chunks (strings) for streaming display.

## Examples

### Basic Usage (All Features Enabled)

```python
from shadai import Shadai

async with Shadai(name="analysis-session") as shadai:
    # Uses all capabilities by default
    async for chunk in shadai.engine(
        prompt="Compare my documents with current market trends"
    ):
        print(chunk, end="", flush=True)
```

### Selective Feature Control

```python
# Only use knowledge base and web search (no summary)
async with Shadai(name="research") as shadai:
    async for chunk in shadai.engine(
        prompt="What are the latest AI developments?",
        use_knowledge_base=True,
        use_summary=False,
        use_web_search=True
    ):
        print(chunk, end="", flush=True)
```

### LLM-Only Mode

```python
# Disable all tools for pure LLM response
async with Shadai(name="simple") as shadai:
    async for chunk in shadai.engine(
        prompt="Explain quantum computing",
        use_knowledge_base=False,
        use_summary=False,
        use_web_search=False
    ):
        print(chunk, end="", flush=True)
```

### Market Analysis with Full Context

```python
async with Shadai(name="market-research") as shadai:
    # Upload market reports first
    await shadai.ingest("/path/to/reports")

    # Comprehensive analysis with all tools
    async for chunk in shadai.engine(
        prompt="Analyze market trends and compare with our documents"
    ):
        print(chunk, end="", flush=True)
```

## Use Cases

### 1. Research & Analysis

Combine documents with web search for comprehensive research:

```python
async with Shadai(name="research") as shadai:
    await shadai.ingest("/research-papers")

    async for chunk in shadai.engine(
        prompt="Compare these papers with recent developments in the field"
    ):
        print(chunk, end="")
```

### 2. Document-Grounded Q&A

Query documents without external information:

```python
async with Shadai(name="qa") as shadai:
    async for chunk in shadai.engine(
        prompt="Summarize key findings from uploaded documents",
        use_web_search=False  # Only use documents
    ):
        print(chunk, end="")
```

### 3. Real-Time Information

Get current information without document context:

```python
async with Shadai(name="news") as shadai:
    async for chunk in shadai.engine(
        prompt="What's happening in tech today?",
        use_knowledge_base=False,  # No documents
        use_summary=False
    ):
        print(chunk, end="")
```

## Behavior

### Tool Selection

The engine intelligently decides which tools to use based on your query and enabled capabilities:

- **Knowledge Base**: Retrieves relevant document chunks
- **Summary**: Provides document overview for context
- **Web Search**: Searches web for current information
- **Memory**: Maintains conversation context across queries

### Tool Orchestration

1. **Planning**: Analyzes query to determine tool needs
2. **Parallel Execution**: Runs applicable tools concurrently
3. **Synthesis**: Combines results into coherent response
4. **Streaming**: Delivers response as it's generated

### Memory & Context

With `use_memory=True` (default):
- Remembers previous queries in session
- Maintains conversation context
- Allows follow-up questions

```python
async with Shadai(name="conversation") as shadai:
    # First query
    async for chunk in shadai.engine("What is machine learning?"):
        print(chunk, end="")

    # Follow-up remembers context
    async for chunk in shadai.engine("What are its applications?"):
        print(chunk, end="")  # Knows "its" = machine learning
```

## Performance Considerations

### Enabling All Tools (Default)

- **Pros**: Most comprehensive answers, combines multiple sources
- **Cons**: Slower response time, higher token usage
- **Best for**: Research, analysis, complex queries

### Selective Tools

- **Pros**: Faster responses, lower costs
- **Cons**: May miss relevant information
- **Best for**: Simple queries, known information needs

```python
# Fast, focused query
async for chunk in shadai.engine(
    prompt="What's the definition of RAG?",
    use_knowledge_base=False,
    use_summary=False,
    use_web_search=False
):
    print(chunk, end="")
```

## Error Handling

```python
from shadai import (
    Shadai,
    ConfigurationError,
    LLMProviderError,
    KnowledgePointsLimitExceededError
)

try:
    async with Shadai(name="analysis") as shadai:
        async for chunk in shadai.engine("Analyze this"):
            print(chunk, end="")

except ConfigurationError as e:
    print(f"Setup required: {e.context['config_key']}")
    # Configure LLM or embedding model

except KnowledgePointsLimitExceededError as e:
    print(f"Quota exceeded: {e.context['current_value']}/{e.context['max_allowed']}")
    # Upgrade plan or wait

except LLMProviderError as e:
    if e.is_retriable:
        # Retry after delay
        await asyncio.sleep(5)
```

## Comparison with Other Tools

### Engine vs Query

| Feature | Engine | Query |
|---------|--------|-------|
| Knowledge Base | Optional | Always |
| Web Search | Optional | No |
| Summary | Optional | No |
| Use Case | Flexible analysis | Document Q&A |

### Engine vs Agent

| Feature | Engine | Agent |
|---------|--------|-------|
| Built-in Tools | Knowledge base, web, summary | Custom tools |
| Orchestration | Automated | Planned & executed |
| Use Case | Standard workflows | Custom workflows |

## Tips & Best Practices

### 1. Start with Defaults

```python
# Let engine decide what's needed
async for chunk in shadai.engine("Your query"):
    print(chunk, end="")
```

### 2. Disable Unused Features

```python
# No documents? Disable knowledge base
async for chunk in shadai.engine(
    prompt="General knowledge question",
    use_knowledge_base=False
):
    print(chunk, end="")
```

### 3. Use Memory for Conversations

```python
# Keep memory enabled for follow-ups
async for chunk in shadai.engine("Initial question"):
    print(chunk, end="")

async for chunk in shadai.engine("Follow-up question"):
    print(chunk, end="")  # Remembers context
```

### 4. Disable Memory for Independent Queries

```python
# Each query independent
async for chunk in shadai.engine(
    prompt="Standalone question",
    use_memory=False
):
    print(chunk, end="")
```

## See Also

- [Query Tool](query-tool.md) - Simpler document Q&A
- [Agent Tool](agent-tool.md) - Custom tool workflows
- [Tools Overview](../core-concepts/tools-overview.md) - All available tools
- [Shadai Client](shadai-client.md) - Main client interface
