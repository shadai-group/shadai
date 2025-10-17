# Streaming Responses

Shadai streams all responses in real-time, delivering tokens as they're generated for the best user experience.

## Why Streaming?

**Without Streaming:**
```
User asks question → Wait 30 seconds → Get complete answer
```

**With Streaming:**
```
User asks question → Immediate first token → Tokens flow → Natural experience
```

Benefits:
- ⚡ **Instant feedback** - Users see responses immediately
- 🎯 **Better UX** - No long waits
- 🔄 **Interruptible** - Can stop if not useful
- 📊 **Progress indication** - Users know something is happening

## Basic Streaming

All Shadai tools support streaming:

```python
async with Shadai(name="chat") as shadai:
    async for chunk in shadai.query("What is AI?"):
        print(chunk, end="", flush=True)
```

**Key points:**
- `async for` - Iterate over chunks
- `chunk` - Individual text piece (could be word, sentence, or token)
- `end=""` - No newline between chunks
- `flush=True` - Display immediately

## Streaming All Tools

### Query

```python
async for chunk in shadai.query("Question"):
    print(chunk, end="", flush=True)
```

### Summarize

```python
async for chunk in shadai.summarize():
    print(chunk, end="", flush=True)
```

### Web Search

```python
async for chunk in shadai.web_search("Search query"):
    print(chunk, end="", flush=True)
```

### Engine

```python
async for chunk in shadai.engine(
    prompt="Complex query",
    use_knowledge_base=True,
    use_web_search=True
):
    print(chunk, end="", flush=True)
```

### Agent

```python
async for chunk in shadai.agent(prompt="Task", tools=[my_tool]):
    print(chunk, end="", flush=True)
```

## Collecting Full Response

### Method 1: Accumulate Chunks

```python
full_response = ""
async for chunk in shadai.query("Question"):
    full_response += chunk
    print(chunk, end="", flush=True)

print(f"\n\nFull response: {full_response}")
```

### Method 2: List Join

```python
chunks = []
async for chunk in shadai.query("Question"):
    chunks.append(chunk)
    print(chunk, end="", flush=True)

full_response = "".join(chunks)
```

## Practical Patterns

### Pattern 1: Terminal Output

```python
async def terminal_chat():
    async with Shadai(name="terminal") as shadai:
        while True:
            query = input("\nYou: ").strip()
            if not query:
                continue

            print("AI: ", end="", flush=True)
            async for chunk in shadai.query(query):
                print(chunk, end="", flush=True)
            print()
```

### Pattern 2: File Writing

```python
async def save_response_to_file(query: str, filename: str):
    async with Shadai(name="writer") as shadai:
        with open(filename, "w") as f:
            async for chunk in shadai.query(query):
                f.write(chunk)
                f.flush()  # Write immediately
```

### Pattern 3: Web Server (FastAPI)

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.get("/query")
async def query_endpoint(q: str):
    async def generate():
        async with Shadai(name="api") as shadai:
            async for chunk in shadai.query(q):
                yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
```

### Pattern 4: WebSocket

```python
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    async with Shadai(name="ws") as shadai:
        while True:
            query = await websocket.receive_text()

            async for chunk in shadai.query(query):
                await websocket.send_text(chunk)
```

### Pattern 5: Progress Indication

```python
import sys

async def query_with_spinner(query: str):
    spinner = ["|", "/", "-", "\\"]
    idx = 0

    async with Shadai(name="progress") as shadai:
        print("Thinking ", end="")
        started = False

        async for chunk in shadai.query(query):
            if not started:
                print("\rResponse: ", end="")
                started = True

            print(chunk, end="", flush=True)
```

## Error Handling

### Basic Error Handling

```python
from shadai import ServerError, AuthenticationError

try:
    async with Shadai(name="chat") as shadai:
        async for chunk in shadai.query("Question"):
            print(chunk, end="", flush=True)
except AuthenticationError:
    print("\n❌ Invalid API key")
except ServerError as e:
    print(f"\n❌ Server error: {e}")
except Exception as e:
    print(f"\n❌ Error: {e}")
```

### Mid-Stream Errors

```python
async with Shadai(name="chat") as shadai:
    try:
        async for chunk in shadai.query("Question"):
            print(chunk, end="", flush=True)
    except Exception as e:
        print(f"\n\n[Stream interrupted: {e}]")
        # Gracefully handle interruption
```

## Advanced Techniques

### Chunk Processing

```python
async def process_chunks(query: str):
    async with Shadai(name="processor") as shadai:
        word_count = 0

        async for chunk in shadai.query(query):
            # Count words
            word_count += len(chunk.split())

            # Display
            print(chunk, end="", flush=True)

        print(f"\n\nWord count: {word_count}")
```

### Rate Limiting

```python
import asyncio

async def rate_limited_stream(query: str, delay: float = 0.1):
    async with Shadai(name="limited") as shadai:
        async for chunk in shadai.query(query):
            print(chunk, end="", flush=True)
            await asyncio.sleep(delay)  # Artificial delay
```

### Buffered Streaming

```python
async def buffered_stream(query: str, buffer_size: int = 10):
    buffer = []

    async with Shadai(name="buffered") as shadai:
        async for chunk in shadai.query(query):
            buffer.append(chunk)

            if len(buffer) >= buffer_size:
                # Flush buffer
                print("".join(buffer), end="", flush=True)
                buffer.clear()

        # Flush remaining
        if buffer:
            print("".join(buffer), end="", flush=True)
```

### Multi-Stream Aggregation

```python
async def aggregate_multiple_queries():
    queries = ["Query 1", "Query 2", "Query 3"]

    async with Shadai(name="aggregate") as shadai:
        for i, query in enumerate(queries, 1):
            print(f"\n\n=== Query {i} ===\n")

            async for chunk in shadai.query(query):
                print(chunk, end="", flush=True)
```

## Performance Optimization

### Fast Display

```python
# ✅ Optimal
async for chunk in shadai.query("Question"):
    print(chunk, end="", flush=True)  # Immediate display

# ❌ Slower
full_response = ""
async for chunk in shadai.query("Question"):
    full_response += chunk
print(full_response)  # Delayed until complete
```

### Memory Efficiency

```python
# ✅ Memory efficient
async for chunk in shadai.query("Long response"):
    process(chunk)  # Process and discard

# ❌ Memory inefficient
chunks = []
async for chunk in shadai.query("Long response"):
    chunks.append(chunk)  # Accumulates in memory
```

## UI Integration

### React (Frontend)

```typescript
const response = await fetch('/api/query?q=question');
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    setResponse(prev => prev + chunk);  // Update UI
}
```

### Streamlit

```python
import streamlit as st

query = st.text_input("Ask a question")

if query:
    response_placeholder = st.empty()
    full_response = ""

    async with Shadai(name="streamlit") as shadai:
        async for chunk in shadai.query(query):
            full_response += chunk
            response_placeholder.markdown(full_response)
```

## Best Practices

### ✅ Do This

```python
# Display immediately
async for chunk in shadai.query("Question"):
    print(chunk, end="", flush=True)

# Handle errors gracefully
try:
    async for chunk in shadai.query("Question"):
        print(chunk, end="", flush=True)
except Exception as e:
    print(f"\n[Error: {e}]")

# Use async for
async for chunk in shadai.query("Question"):
    process(chunk)
```

### ❌ Don't Do This

```python
# Don't forget flush
async for chunk in shadai.query("Question"):
    print(chunk, end="")  # May not display immediately

# Don't block on accumulation
response = ""
async for chunk in shadai.query("Question"):
    response += chunk
print(response)  # Defeats streaming purpose

# Don't use synchronous iteration
for chunk in shadai.query("Question"):  # Wrong!
    print(chunk)
```

## Troubleshooting

### No Output Appearing

```python
# Problem: Missing flush
print(chunk, end="")

# Solution: Add flush
print(chunk, end="", flush=True)
```

### Delayed Output

```python
# Problem: Buffering
async for chunk in shadai.query("Question"):
    response += chunk  # Buffers first
    print(response)

# Solution: Print directly
async for chunk in shadai.query("Question"):
    print(chunk, end="", flush=True)
```

## Next Steps

- [Error Handling](error-handling.md) - Robust error management
- [Web Server Integration](../examples/advanced-patterns.md) - Production APIs
- [Performance Optimization](../advanced/performance-optimization.md) - Scale efficiently

---

**Pro Tip**: Always use `flush=True` for real-time display in terminals!
