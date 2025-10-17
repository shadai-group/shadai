# Session Management

Sessions are the foundation of Shadai. They organize your documents, maintain conversation context, and enable powerful multi-document workflows.

## What is a Session?

A session is a container that holds:
- 📚 **Documents** - Your ingested files
- 💬 **Chat history** - All questions and answers
- 🧠 **Context** - Conversation memory
- ⚙️ **Configuration** - Session-specific settings

Think of a session as a workspace for a specific project or topic.

## Session Types

### Named Sessions (Persistent)

Perfect for ongoing projects:

```python
async with Shadai(name="market-research-q4") as shadai:
    # Documents and history persist
    await shadai.ingest(folder_path="./reports")
    async for chunk in shadai.query("What are the trends?"):
        print(chunk, end="")

# Later, reconnect to same session
async with Shadai(name="market-research-q4") as shadai:
    # All previous documents and history available
    async for chunk in shadai.query("Any updates on those trends?"):
        print(chunk, end="")
```

**Use named sessions when:**
- Working on ongoing projects
- Building up knowledge over time
- Need to preserve history
- Collaborating with team members

### Temporal Sessions (Auto-Delete)

Perfect for one-off queries:

```python
async with Shadai(temporal=True) as shadai:
    # Session deleted automatically on exit
    async for chunk in shadai.query("Quick question"):
        print(chunk, end="")
```

**Use temporal sessions when:**
- One-time queries
- Testing or experiments
- Privacy-sensitive data
- No need to persist data

## Creating Sessions

### Basic Session Creation

```python
from shadai import Shadai

# Named session
async with Shadai(name="my-project") as shadai:
    pass

# Temporal session
async with Shadai(temporal=True) as shadai:
    pass

# With custom configuration
async with Shadai(
    name="my-project",
    api_key="your-key",
    base_url="https://api.shadai.com",
    timeout=60
) as shadai:
    pass
```

### Session Naming Best Practices

✅ **Good Names:**
```python
Shadai(name="q4-financial-analysis")
Shadai(name="product-roadmap-2024")
Shadai(name="customer-feedback-march")
Shadai(name="legal-contracts-review")
```

❌ **Bad Names:**
```python
Shadai(name="test")  # Too vague
Shadai(name="session123")  # No context
Shadai(name="my session")  # Spaces not recommended
Shadai(name="临时")  # Use English for consistency
```

## Session Lifecycle

### 1. Session Creation

```python
async with Shadai(name="research") as shadai:
    # Session created (or existing one loaded)
    print("Session ready!")
```

What happens:
- 🔍 Checks if session exists
- ✨ Creates new if doesn't exist
- 📂 Loads existing data if exists

### 2. Adding Documents

```python
async with Shadai(name="research") as shadai:
    # Initial ingestion
    await shadai.ingest(folder_path="./docs")

    # Add more documents later
    await shadai.ingest(folder_path="./new-docs")
```

Documents are cumulative - new ingestions add to existing documents.

### 3. Querying

```python
async with Shadai(name="research") as shadai:
    async for chunk in shadai.query("What are the findings?"):
        print(chunk, end="")
```

Each query:
- Searches ALL documents in session
- Maintains conversation history
- Updates context

### 4. Session Cleanup

```python
# Automatic cleanup
async with Shadai(name="research") as shadai:
    # Do work
    pass
# Session resources released (but data persists)

# Temporal sessions are deleted
async with Shadai(temporal=True) as shadai:
    pass
# Session completely deleted
```

## Working with Multiple Sessions

### Pattern 1: Sequential Processing

```python
async def process_departments():
    # Finance department
    async with Shadai(name="finance-2024") as shadai:
        await shadai.ingest(folder_path="./finance")
        async for chunk in shadai.query("Revenue trends?"):
            print(chunk, end="")

    # Marketing department
    async with Shadai(name="marketing-2024") as shadai:
        await shadai.ingest(folder_path="./marketing")
        async for chunk in shadai.query("Campaign performance?"):
            print(chunk, end="")
```

### Pattern 2: Parallel Processing

```python
import asyncio

async def analyze_finance():
    async with Shadai(name="finance-2024") as shadai:
        async for chunk in shadai.query("Revenue trends?"):
            return chunk

async def analyze_marketing():
    async with Shadai(name="marketing-2024") as shadai:
        async for chunk in shadai.query("Campaign performance?"):
            return chunk

# Run in parallel
results = await asyncio.gather(
    analyze_finance(),
    analyze_marketing()
)
```

### Pattern 3: Hierarchical Sessions

```python
async def company_analysis():
    # Master session for company-wide analysis
    async with Shadai(name="company-2024") as company:
        await company.ingest(folder_path="./company-reports")

        # Department-specific sessions
        async with Shadai(name="finance-2024") as finance:
            await finance.ingest(folder_path="./finance")

        async with Shadai(name="marketing-2024") as marketing:
            await marketing.ingest(folder_path="./marketing")
```

## Session Management Operations

### Get Session History

```python
async with Shadai(name="research") as shadai:
    # Get paginated history
    history = await shadai.get_session_history(
        page=1,
        page_size=10  # Max: 10
    )

    print(f"Total messages: {history['count']}")
    print(f"Current page: {history['page']}")

    for message in history["results"]:
        role = message["role"]
        content = message["content"]
        timestamp = message["created_at"]
        print(f"[{timestamp}] {role}: {content[:100]}...")
```

Response format:

```python
{
    "count": 42,  # Total messages
    "next": 2,    # Next page number (or None)
    "previous": None,  # Previous page number (or None)
    "results": [
        {
            "uuid": "...",
            "role": "user",
            "content": "What are the trends?",
            "created_at": "2024-01-15T10:30:00Z",
            "token_usage": {}
        },
        {
            "uuid": "...",
            "role": "assistant",
            "content": "Based on the documents...",
            "created_at": "2024-01-15T10:30:05Z",
            "token_usage": {"prompt_tokens": 1500, "completion_tokens": 300}
        }
    ]
}
```

### Clear Session History

```python
async with Shadai(name="research") as shadai:
    # Clear all messages (documents remain!)
    result = await shadai.clear_session_history()
    print(result["message"])  # "Session history cleared successfully"
```

**Important**: This clears chat history but keeps documents!

### Pagination Example

```python
async def print_all_history(session_name: str):
    async with Shadai(name=session_name) as shadai:
        page = 1
        while True:
            history = await shadai.get_session_history(
                page=page,
                page_size=10
            )

            for msg in history["results"]:
                print(f"{msg['role']}: {msg['content']}")

            if not history["next"]:
                break

            page = history["next"]
```

## Memory Management

### Memory Enabled (Default)

```python
async with Shadai(name="chat") as shadai:
    # Question 1
    async for chunk in shadai.query("What is quantum computing?"):
        print(chunk, end="")

    # Question 2 - remembers previous context
    async for chunk in shadai.query("What are its applications?"):
        print(chunk, end="")  # Knows "its" refers to quantum computing
```

### Memory Disabled

```python
async with Shadai(name="chat") as shadai:
    # Independent query
    async for chunk in shadai.query("What is AI?", use_memory=False):
        print(chunk, end="")

    # Another independent query
    async for chunk in shadai.query("What is ML?", use_memory=False):
        print(chunk, end="")
```

Use `use_memory=False` when:
- Queries are completely independent
- Want to avoid context pollution
- Testing specific prompts

## Best Practices

### ✅ Do This

```python
# Use descriptive session names
async with Shadai(name="q4-2024-financial-review") as shadai:
    pass

# Reuse sessions for related work
async with Shadai(name="project-alpha") as shadai:
    await shadai.ingest(folder_path="./docs")

# Later...
async with Shadai(name="project-alpha") as shadai:
    # Previous documents still available
    async for chunk in shadai.query("Update?"):
        print(chunk, end="")

# Clear history when starting fresh topics
async with Shadai(name="research") as shadai:
    await shadai.clear_session_history()
    async for chunk in shadai.query("New topic"):
        print(chunk, end="")
```

### ❌ Don't Do This

```python
# Don't use temporal sessions for persistent work
async with Shadai(temporal=True) as shadai:
    await shadai.ingest(folder_path="./important-docs")  # Lost on exit!

# Don't create too many sessions
for i in range(1000):
    async with Shadai(name=f"session-{i}") as shadai:
        pass  # Hard to manage!

# Don't forget to use context manager
shadai = Shadai(name="test")  # Missing async with!
```

## Common Patterns

### Pattern: Session Per Project

```python
projects = ["alpha", "beta", "gamma"]

for project in projects:
    async with Shadai(name=f"project-{project}") as shadai:
        await shadai.ingest(folder_path=f"./projects/{project}")
        async for chunk in shadai.query(f"Status of {project}?"):
            print(chunk, end="")
```

### Pattern: Session Per User

```python
async def user_session(user_id: str, query: str):
    async with Shadai(name=f"user-{user_id}") as shadai:
        async for chunk in shadai.query(query):
            yield chunk

# Each user gets their own isolated session
async for chunk in user_session("user123", "My question"):
    print(chunk, end="")
```

### Pattern: Session Per Topic

```python
async def topic_based_research():
    topics = {
        "ai-trends": "./ai-papers",
        "market-analysis": "./market-reports",
        "tech-reviews": "./tech-docs"
    }

    for topic, folder in topics.items():
        async with Shadai(name=topic) as shadai:
            await shadai.ingest(folder_path=folder)
            async for chunk in shadai.summarize():
                print(f"\n{topic.upper()}:\n{chunk}")
```

## Troubleshooting

### Session Not Found

```python
# First time - creates new session
async with Shadai(name="new-session") as shadai:
    await shadai.ingest(folder_path="./docs")

# Second time - loads existing session
async with Shadai(name="new-session") as shadai:
    # All previous data available
    pass
```

### Lost Session Data

If using temporal sessions, data is deleted on exit:

```python
# ❌ Data lost
async with Shadai(temporal=True) as shadai:
    await shadai.ingest(folder_path="./docs")
# Session deleted here!

# ✅ Data persists
async with Shadai(name="persistent") as shadai:
    await shadai.ingest(folder_path="./docs")
# Data still available
```

### Memory Overflow

If conversation history gets too long:

```python
async with Shadai(name="long-conversation") as shadai:
    # Clear history periodically
    await shadai.clear_session_history()

    # Continue with fresh context
    async for chunk in shadai.query("New topic"):
        print(chunk, end="")
```

## Next Steps

- [Memory & Context](memory-and-context.md) - Deep dive into conversation memory
- [File Ingestion](file-ingestion.md) - Advanced document processing
- [Performance Optimization](../advanced/performance-optimization.md) - Scale your sessions

---

**Questions?** Check out the [API Reference](../api-reference/shadai-client.md) for complete documentation.
