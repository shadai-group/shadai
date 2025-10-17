# Advanced Patterns

Advanced techniques and patterns.

## Pattern: Retry Logic

```python
import asyncio

async def query_with_retry(shadai, query: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            response = ""
            async for chunk in shadai.query(query):
                response += chunk
            return response
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                raise
```

## Pattern: Parallel Processing

```python
async def parallel_queries(questions: List[str]):
    async def process_question(q: str):
        async with Shadai(name=f"q-{hash(q)}") as shadai:
            response = ""
            async for chunk in shadai.query(q):
                response += chunk
            return response

    results = await asyncio.gather(*[process_question(q) for q in questions])
    return results
```

## Pattern: Streaming to File

```python
async def stream_to_file(query: str, output_file: str):
    async with Shadai(name="file-stream") as shadai:
        with open(output_file, "w") as f:
            async for chunk in shadai.query(query):
                f.write(chunk)
                f.flush()
```

## See Also
- [Performance Optimization](../advanced/performance-optimization.md)
- [Best Practices](../advanced/best-practices.md)
