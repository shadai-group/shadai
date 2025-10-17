# Query Tool API

Query your knowledge base with RAG-powered search.

## Method Signature

```python
async def query(query: str, use_memory: bool = True) -> AsyncIterator[str]
```

## Parameters

- **query** (str, required): Question to ask
- **use_memory** (bool, optional): Enable conversation context (default: True)

## Returns

Async iterator yielding response chunks (strings)

## Examples

### Basic Query
```python
async for chunk in shadai.query("What are the payment terms?"):
    print(chunk, end="")
```

### Without Memory
```python
async for chunk in shadai.query("Independent question", use_memory=False):
    print(chunk, end="")
```

### Collecting Full Response
```python
response = ""
async for chunk in shadai.query("Question"):
    response += chunk
print(response)
```

## See Also
- [Shadai Client](shadai-client.md)
- [Memory Guide](../guides/memory-and-context.md)
