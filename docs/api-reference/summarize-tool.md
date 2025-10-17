# Summarize Tool API

Generate comprehensive summaries of all session documents.

## Method Signature

```python
async def summarize(use_memory: bool = True) -> AsyncIterator[str]
```

## Parameters

- **use_memory** (bool, optional): Enable conversation context (default: True)

## Returns

Async iterator yielding summary chunks (strings)

## Example

```python
async for chunk in shadai.summarize():
    print(chunk, end="")
```

## See Also
- [Shadai Client](shadai-client.md)
