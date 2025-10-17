# Architecture

Understanding Shadai's architecture helps you build better applications and troubleshoot effectively.

## High-Level Overview

```
Your Application
     ↓
Shadai Python Client (SDK)
     ↓
REST API (Shadai Server)
     ↓
┌──────────────────────────────────┐
│  RAG Engine                      │
│  ├─ Document Processing          │
│  ├─ Vector Search                │
│  ├─ LLM Integration              │
│  └─ Memory Management            │
└──────────────────────────────────┘
```

## Client-Server Architecture

### Python Client (Your Code)

The Shadai client is what you interact with:

```python
async with Shadai(name="my-session") as shadai:
    async for chunk in shadai.query("Question"):
        print(chunk, end="")
```

**Responsibilities:**
- Session management
- API communication
- Response streaming
- Error handling
- Type safety

### Shadai Server (Backend)

The server handles all heavy lifting:

**Document Processing:**
- PDF parsing
- Text extraction
- Intelligent chunking
- Embedding generation

**RAG Pipeline:**
- Vector similarity search
- Context retrieval
- LLM prompting
- Response generation

**State Management:**
- Session persistence
- Chat history
- Document storage
- Memory management

## Core Components

### 1. Sessions

Sessions are isolated workspaces:

```python
# Each session has its own:
async with Shadai(name="project-alpha") as shadai:
    # ✓ Documents
    # ✓ Chat history
    # ✓ Context/memory
    # ✓ Configuration
    pass
```

**Key Features:**
- Persistent by default
- Isolated from other sessions
- Shareable across runs
- Queryable independently

### 2. Tools

Tools are specialized capabilities:

| Tool | Purpose | Use Case |
|------|---------|----------|
| **Query** | Search documents | "What does the contract say?" |
| **Summarize** | Overview of all docs | "Give me the executive summary" |
| **Web Search** | Current information | "Latest industry news" |
| **Engine** | Multi-tool orchestration | "Compare docs with trends" |
| **Agent** | Custom tool execution | "Analyze with my tools" |

### 3. Memory System

Memory enables context-aware conversations:

```python
# Question 1
await shadai.query("Who is the CEO?")
# Answer: "John Smith"

# Question 2 (remembers context!)
await shadai.query("What's his background?")
# Knows "his" refers to John Smith
```

**How it works:**
- Stores user messages
- Stores AI responses
- Maintains conversation thread
- Provides context to LLM

### 4. Vector Store

Documents are converted to searchable vectors:

```
Your PDF → Text Chunks → Embeddings → Vector Database
```

When you query:
```
Your Question → Embedding → Vector Search → Relevant Chunks → LLM → Answer
```

## Data Flow

### Document Ingestion

```
1. Upload File
   ↓
2. Server Processes
   - Extracts text
   - Splits into chunks
   - Creates embeddings
   ↓
3. Stores Vectors
   ↓
4. Returns Success
```

Your code:
```python
results = await shadai.ingest(folder_path="./docs")
# File is now queryable
```

### Query Execution

```
1. Send Question
   ↓
2. Server Processes
   - Creates question embedding
   - Searches vectors
   - Retrieves top matches
   - Prompts LLM with context
   ↓
3. Streams Response
   ↓
4. Saves to Memory
```

Your code:
```python
async for chunk in shadai.query("Question"):
    print(chunk, end="")
# Response streamed token by token
```

## Communication Protocol

### Request/Response Flow

```python
# Your code makes request
async for chunk in shadai.query("Question"):
    # Server returns NDJSON stream
    # Each line is a chunk of the response
    print(chunk, end="")
```

**Benefits of Streaming:**
- Immediate feedback
- Lower perceived latency
- Interruptible
- Better UX

### Authentication

Every request includes your API key:

```python
Headers:
  X-API-Key: your_api_key_here
```

Server validates and processes request.

## Scalability & Performance

### Client-Side

**Fast:**
- Minimal dependencies
- Async/await for concurrency
- Efficient streaming
- Type-safe operations

**Example - Parallel Queries:**
```python
import asyncio

async def query1():
    async with Shadai(name="session1") as shadai:
        async for chunk in shadai.query("Q1"):
            return chunk

async def query2():
    async with Shadai(name="session2") as shadai:
        async for chunk in shadai.query("Q2"):
            return chunk

# Run in parallel
results = await asyncio.gather(query1(), query2())
```

### Server-Side

The server is optimized for:
- Fast vector search
- Efficient embedding generation
- LLM response streaming
- Concurrent request handling

**You don't need to worry about:**
- Database optimization
- Vector indexing
- LLM provider management
- Load balancing

## Security Model

### Authentication

- API key-based authentication
- Keys are account-specific
- Can be rotated anytime
- Revokable instantly

### Data Isolation

- Each session is isolated
- Documents not shared between accounts
- Chat history is private
- Embeddings are account-specific

### Transport Security

- HTTPS/TLS encryption
- Secure API communication
- No credentials in URLs
- Token-based auth

## Limitations & Constraints

### File Size

- Maximum: 35MB per file
- Larger files are skipped
- Compress if needed

### Session Limits

- No hard limit on sessions
- Organize sessions logically
- Use temporal sessions for one-off queries

### Rate Limiting

- Fair use policy applies
- Concurrent requests allowed
- Contact support for enterprise needs

### Memory

- Conversation history accumulates
- Clear periodically if needed
- Affects token usage

## Best Practices

### ✅ Do This

```python
# Use sessions to organize work
async with Shadai(name="project-specific") as shadai:
    pass

# Stream responses for best UX
async for chunk in shadai.query("Question"):
    print(chunk, end="", flush=True)

# Handle errors gracefully
try:
    async for chunk in shadai.query("Question"):
        print(chunk, end="")
except ShadaiError as e:
    handle_error(e)

# Use async/await properly
async def main():
    async with Shadai(name="app") as shadai:
        await shadai.ingest(folder_path="./docs")
```

### ❌ Don't Do This

```python
# Don't block streaming
response = ""
async for chunk in shadai.query("Question"):
    response += chunk  # Accumulates before displaying

# Don't forget error handling
async for chunk in shadai.query("Question"):
    print(chunk)  # No try/except

# Don't use synchronous code
def main():  # Should be async
    shadai = Shadai(name="app")  # Missing async with
```

## Troubleshooting

### Slow Responses

**Causes:**
- Large documents (more context to process)
- Complex queries
- High server load

**Solutions:**
- Reduce context size
- Simplify queries
- Use temporal sessions for quick queries

### Memory Issues

**Causes:**
- Long conversation history
- Many messages accumulated

**Solutions:**
```python
# Clear history periodically
await shadai.clear_session_history()

# Or disable memory for independent queries
async for chunk in shadai.query("Question", use_memory=False):
    print(chunk, end="")
```

### Connection Errors

**Causes:**
- Network issues
- Invalid API key
- Server maintenance

**Solutions:**
- Verify internet connection
- Check API key validity
- Implement retry logic
- Check status page

## Next Steps

- [RAG System](rag-system.md) - Deep dive into RAG
- [Tools Overview](tools-overview.md) - All available tools
- [Intelligent Agent](intelligent-agent.md) - Agent architecture

---

**Remember**: The client is your interface. The server handles all complexity. Focus on building great applications!
