# Summarize Tool API

Generate comprehensive summaries of all session documents with optional question-answering capability.

## Overview

The Summarize Tool supports two operating modes:

1. **Direct Summary** (`return_direct=True`): Returns the consolidated summary
2. **Question Answering** (`return_direct=False`): Uses the summary to answer specific questions

## Method Signature

```python
async def summarize(
    prompt: str | None = None,
    return_direct: bool = True,
    use_memory: bool = True
) -> AsyncIterator[str]
```

## Parameters

- **prompt** (str | None, optional): Question to answer using the summary (default: None)
- **return_direct** (bool, optional): If True, return summary directly; if False, answer the prompt (default: True)
- **use_memory** (bool, optional): Enable conversation context (default: True)

## Parameter Rules

The `prompt` and `return_direct` parameters are mutually exclusive:

| `prompt` | `return_direct` | Behavior |
|----------|----------------|----------|
| `None` | `True` | ✅ Returns summary directly |
| `"question"` | `False` | ✅ Answers question using summary |
| `None` | `False` | ❌ Raises `InvalidParameterError` |
| `"question"` | `True` | ❌ Raises `InvalidParameterError` |

## Returns

Async iterator yielding text chunks (strings)

## Raises

- **InvalidParameterError**: If `prompt`/`return_direct` mutual exclusivity is violated
- **ValueError**: If Shadai instance is not used as a context manager

## Examples

### Mode 1: Direct Summary (Default)

Get the consolidated summary of all documents:

```python
from shadai import Shadai

# Default behavior - returns summary directly
async with Shadai(name="my-session") as shadai:
    async for chunk in shadai.summarize():
        print(chunk, end="")
```

### Mode 2: Question Answering

Ask specific questions about the documents:

```python
from shadai import Shadai

async with Shadai(name="my-session") as shadai:
    # Ask a question
    async for chunk in shadai.summarize(
        prompt="What are the main topics discussed?",
        return_direct=False
    ):
        print(chunk, end="")
```

### Mode 3: Multi-turn Conversation

Maintain conversation context across questions:

```python
from shadai import Shadai

async with Shadai(name="my-session") as shadai:
    # First question
    async for chunk in shadai.summarize(
        prompt="What are the key findings?",
        return_direct=False,
        use_memory=True
    ):
        print(chunk, end="")

    print("\n\n")

    # Follow-up question (remembers previous context)
    async for chunk in shadai.summarize(
        prompt="Can you elaborate on the first finding?",
        return_direct=False,
        use_memory=True
    ):
        print(chunk, end="")
```

### Disable Memory

For independent requests without conversation history:

```python
async with Shadai(name="my-session") as shadai:
    async for chunk in shadai.summarize(use_memory=False):
        print(chunk, end="")
```

## Important Notes

1. **Summary Source**: Answers are based strictly on the consolidated summary, not the original documents
2. **No External Knowledge**: The tool only uses information from the session's document summaries
3. **Memory Persistence**: When `use_memory=True`, conversation context is preserved across calls
4. **Streaming**: Both modes stream responses in real-time for better UX
5. **Backward Compatible**: Existing code using only `use_memory` continues to work

## Error Handling

```python
from shadai import Shadai, InvalidParameterError

async with Shadai(name="my-session") as shadai:
    try:
        # This will raise InvalidParameterError
        async for chunk in shadai.summarize(
            prompt=None,
            return_direct=False  # Invalid: prompt is None but return_direct is False
        ):
            print(chunk, end="")
    except InvalidParameterError as e:
        print(f"Parameter error: {e.message}")
        print(f"Error code: {e.error_code}")
```

## See Also

- [Shadai Client](shadai-client.md)
- [Query Tool](query-tool.md)
- [Engine Tool](engine-tool.md)
- [Exceptions Reference](exceptions.md)
