# Web Search Tool API

Search the internet for current information.

## Method Signature

```python
async def web_search(
    prompt: str,
    use_web_search: bool = True,
    use_memory: bool = True
) -> AsyncIterator[str]
```

## Parameters

- **prompt** (str, required): Search query
- **use_web_search** (bool, optional): Enable web search (default: True)
- **use_memory** (bool, optional): Enable conversation context (default: True)

## Returns

Async iterator yielding response chunks (strings)

## Example

```python
async for chunk in shadai.web_search("Latest AI developments 2024"):
    print(chunk, end="")
```

## See Also
- [Shadai Client](shadai-client.md)
