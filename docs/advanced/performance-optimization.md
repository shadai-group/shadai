# Performance Optimization

Optimize your Shadai applications for speed and efficiency.

## Client-Side Optimization

### 1. Session Reuse

```python
# ❌ Slow: Create new session each time
async def slow_approach():
    for query in queries:
        async with Shadai(name="temp") as shadai:
            await shadai.ingest(folder_path="./docs")
            async for chunk in shadai.query(query):
                print(chunk, end="")

# ✅ Fast: Reuse session
async def fast_approach():
    async with Shadai(name="reusable") as shadai:
        await shadai.ingest(folder_path="./docs")  # Once
        for query in queries:
            async for chunk in shadai.query(query):
                print(chunk, end="")
```

### 2. Parallel Queries

```python
import asyncio

async def parallel_processing():
    queries = ["Q1", "Q2", "Q3"]

    async def process(q: str):
        async with Shadai(name=f"parallel-{hash(q)}") as shadai:
            result = ""
            async for chunk in shadai.query(q):
                result += chunk
            return result

    results = await asyncio.gather(*[process(q) for q in queries])
    return results
```

### 3. Disable Memory When Not Needed

```python
# Independent queries don't need memory
for query in independent_queries:
    async for chunk in shadai.query(query, use_memory=False):
        print(chunk, end="")
```

### 4. Stream Processing

```python
# ✅ Process as you receive
async for chunk in shadai.query("Question"):
    process_chunk(chunk)  # Real-time processing

# ❌ Don't accumulate then process
response = ""
async for chunk in shadai.query("Question"):
    response += chunk  # Waits for all chunks
process_all(response)
```

## Memory Management

### Clear History Periodically

```python
conversation_count = 0
async with Shadai(name="long-running") as shadai:
    while True:
        query = get_user_input()
        async for chunk in shadai.query(query):
            print(chunk, end="")

        conversation_count += 1
        if conversation_count >= 20:
            await shadai.clear_session_history()
            conversation_count = 0
```

### Monitor History Size

```python
history = await shadai.get_session_history()
if history["count"] > 50:
    await shadai.clear_session_history()
```

## Best Practices

- Reuse sessions when possible
- Disable memory for independent queries
- Process streams in real-time
- Clear history periodically
- Use parallel processing for multiple queries

## See Also

- [Best Practices](best-practices.md)
- [Streaming Responses](../guides/streaming-responses.md)
