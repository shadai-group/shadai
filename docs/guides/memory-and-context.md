# Memory & Context

Shadai's memory system enables natural, context-aware conversations. This guide explains how memory works and how to control it effectively.

## What is Memory?

Memory allows Shadai to remember previous interactions within a session, enabling:

- 🔗 **Follow-up questions** without repeating context
- 💬 **Natural conversations** that flow logically
- 🧠 **Context accumulation** over multiple interactions
- 🎯 **More accurate answers** based on conversation history

## Memory is Enabled by Default

As of v0.1.29, all tools use memory by default:

```python
async with Shadai(name="chat") as shadai:
    # First question
    async for chunk in shadai.query("Who discovered penicillin?"):
        print(chunk, end="")
    # Answer: Alexander Fleming discovered penicillin in 1928

    # Follow-up - memory enabled automatically
    async for chunk in shadai.query("When did he discover it?"):
        print(chunk, end="")
    # Answer: He discovered it in 1928
    # (knows "he" refers to Alexander Fleming)
```

## How Memory Works

### Message Storage

Every interaction is stored:

```python
async with Shadai(name="research") as shadai:
    # User message stored
    async for chunk in shadai.query("What is machine learning?"):
        # AI response stored
        print(chunk, end="")

    # Both messages available for context in next query
    async for chunk in shadai.query("Give me an example"):
        print(chunk, end="")
```

Behind the scenes:
1. User question → Stored as "user" message
2. AI answer → Stored as "assistant" message
3. Next query → Retrieves recent messages for context
4. Continues building conversation thread

### Context Window

Shadai maintains a sliding window of recent messages:

```python
# Message 1
async for chunk in shadai.query("Question 1"):
    print(chunk, end="")

# Message 2
async for chunk in shadai.query("Question 2"):
    print(chunk, end="")

# Message 3 - has context from 1 & 2
async for chunk in shadai.query("Question 3"):
    print(chunk, end="")
```

Recent messages have more influence on responses.

## Controlling Memory

### Enable Memory (Default)

```python
async with Shadai(name="chat") as shadai:
    # Explicit (redundant since it's default)
    async for chunk in shadai.query("Question", use_memory=True):
        print(chunk, end="")

    # Implicit (recommended)
    async for chunk in shadai.query("Question"):
        print(chunk, end="")
```

### Disable Memory

Useful for independent queries:

```python
async with Shadai(name="chat") as shadai:
    # Independent query 1
    async for chunk in shadai.query(
        "What is Python?",
        use_memory=False
    ):
        print(chunk, end="")

    # Independent query 2 (no context from query 1)
    async for chunk in shadai.query(
        "What is JavaScript?",
        use_memory=False
    ):
        print(chunk, end="")
```

**When to disable memory:**
- Completely independent queries
- Testing specific prompts
- Avoiding context pollution
- Privacy-sensitive queries

## Memory Across Tools

All tools support memory:

### Query Tool

```python
async for chunk in shadai.query("What is AI?"):
    print(chunk, end="")

async for chunk in shadai.query("How is it different from ML?"):
    print(chunk, end="")  # Knows "it" means AI
```

### Summarize Tool

```python
async for chunk in shadai.summarize():
    print(chunk, end="")

async for chunk in shadai.query("Can you elaborate on the second point?"):
    print(chunk, end="")  # References summary
```

### Web Search Tool

```python
async for chunk in shadai.web_search("Latest AI news"):
    print(chunk, end="")

async for chunk in shadai.query("How does this compare to my documents?"):
    print(chunk, end="")  # Combines web search + docs
```

### Engine Tool

```python
async for chunk in shadai.engine(
    prompt="Compare my docs with current trends",
    use_knowledge_base=True,
    use_web_search=True
):
    print(chunk, end="")

async for chunk in shadai.query("What should we prioritize?"):
    print(chunk, end="")  # Builds on engine analysis
```

## Managing Conversation History

### View History

```python
async with Shadai(name="chat") as shadai:
    # Get recent messages
    history = await shadai.get_session_history(page=1, page_size=5)

    for msg in history["results"]:
        print(f"{msg['role']}: {msg['content'][:100]}...")
```

### Clear History

```python
async with Shadai(name="chat") as shadai:
    # Clear all messages
    await shadai.clear_session_history()

    # Start fresh conversation
    async for chunk in shadai.query("New topic"):
        print(chunk, end="")
```

**Important**: Clearing history doesn't delete ingested documents!

## Practical Patterns

### Pattern 1: Conversational Q&A

```python
async def conversational_qa():
    async with Shadai(name="support") as shadai:
        await shadai.ingest(folder_path="./docs")

        questions = [
            "What is our refund policy?",
            "What if the item is damaged?",
            "How long does the refund take?",
        ]

        for q in questions:
            print(f"\nQ: {q}")
            print("A: ", end="")
            async for chunk in shadai.query(q):
                print(chunk, end="")
```

Each question builds on previous answers naturally.

### Pattern 2: Topic Switching

```python
async with Shadai(name="research") as shadai:
    # Topic 1: AI
    async for chunk in shadai.query("Explain AI"):
        print(chunk, end="")

    # Switch topics - clear memory
    await shadai.clear_session_history()

    # Topic 2: Blockchain
    async for chunk in shadai.query("Explain blockchain"):
        print(chunk, end="")
```

### Pattern 3: Contextual Refinement

```python
async with Shadai(name="writing") as shadai:
    # Initial request
    async for chunk in shadai.query("Write a product description"):
        response = chunk

    # Refine (memory maintains context)
    async for chunk in shadai.query("Make it more technical"):
        response = chunk

    # Further refine
    async for chunk in shadai.query("Add benefits"):
        response = chunk
```

### Pattern 4: Memory-Less Batch Processing

```python
async with Shadai(name="batch") as shadai:
    questions = ["Q1", "Q2", "Q3"]

    for q in questions:
        # Independent processing
        async for chunk in shadai.query(q, use_memory=False):
            print(chunk, end="")
```

## Advanced Memory Techniques

### Selective Memory

```python
async with Shadai(name="selective") as shadai:
    # Important query - use memory
    async for chunk in shadai.query("Main analysis"):
        print(chunk, end="")

    # Quick lookup - no memory
    async for chunk in shadai.query("Quick fact check", use_memory=False):
        print(chunk, end="")

    # Continue main thread - memory preserved
    async for chunk in shadai.query("Based on the analysis..."):
        print(chunk, end="")
```

### Memory Pagination

```python
async def analyze_conversation_flow():
    async with Shadai(name="chat") as shadai:
        page = 1
        while True:
            history = await shadai.get_session_history(
                page=page,
                page_size=10
            )

            # Analyze conversation patterns
            for msg in history["results"]:
                if msg["role"] == "user":
                    print(f"User asked: {msg['content'][:50]}...")

            if not history["next"]:
                break
            page = history["next"]
```

### Periodic Memory Cleanup

```python
async with Shadai(name="long-running") as shadai:
    conversation_count = 0

    while True:
        query = get_user_input()

        async for chunk in shadai.query(query):
            print(chunk, end="")

        conversation_count += 1

        # Clear every 20 interactions
        if conversation_count >= 20:
            await shadai.clear_session_history()
            conversation_count = 0
            print("\n[Memory cleared - starting fresh]")
```

## Best Practices

### ✅ Do This

```python
# Use memory for conversations
async with Shadai(name="chat") as shadai:
    async for chunk in shadai.query("First question"):
        print(chunk, end="")
    async for chunk in shadai.query("Follow-up"):
        print(chunk, end="")

# Clear memory when switching topics
await shadai.clear_session_history()

# Disable memory for independent queries
async for chunk in shadai.query("Unrelated question", use_memory=False):
    print(chunk, end="")

# Monitor conversation length
history = await shadai.get_session_history()
if history["count"] > 50:
    await shadai.clear_session_history()
```

### ❌ Don't Do This

```python
# Don't disable memory for follow-ups
async for chunk in shadai.query("What is AI?"):
    print(chunk, end="")
async for chunk in shadai.query("Tell me more", use_memory=False):
    print(chunk, end="")  # Lost context!

# Don't let memory grow indefinitely
# (no cleanup strategy)

# Don't mix topics without clearing
async for chunk in shadai.query("About AI"):
    print(chunk, end="")
async for chunk in shadai.query("About cooking"):
    print(chunk, end="")  # Confused context
```

## Memory and Performance

### Token Usage

Memory increases token usage:

```python
# No memory: ~100 tokens
async for chunk in shadai.query("Short question", use_memory=False):
    pass

# With memory: ~300 tokens (includes history)
async for chunk in shadai.query("Short question", use_memory=True):
    pass
```

**Optimization**: Clear memory periodically to reduce token usage.

### Response Quality vs. Cost

```python
# Higher cost, better context
async for chunk in shadai.query("Complex question", use_memory=True):
    pass  # Uses full conversation history

# Lower cost, no context
async for chunk in shadai.query("Complex question", use_memory=False):
    pass  # Standalone query
```

## Troubleshooting

### Memory Not Working

```python
# ❌ Wrong - memory disabled
async for chunk in shadai.query("Question", use_memory=False):
    print(chunk, end="")

# ✅ Correct - memory enabled (default)
async for chunk in shadai.query("Question"):
    print(chunk, end="")
```

### Context Confusion

If responses seem confused:

```python
# Solution: Clear and restart
async with Shadai(name="chat") as shadai:
    await shadai.clear_session_history()
    # Start fresh
```

### Memory Overflow

If context becomes too large:

```python
history = await shadai.get_session_history()
if history["count"] > 100:
    await shadai.clear_session_history()
```

## Next Steps

- [Session Management](session-management.md) - Organize your work
- [Streaming Responses](streaming-responses.md) - Handle real-time data
- [Error Handling](error-handling.md) - Robust applications
- [Performance Optimization](../advanced/performance-optimization.md) - Scale efficiently

---

**Pro Tip**: Let memory work for you by default. Only disable it when you have a specific reason.
