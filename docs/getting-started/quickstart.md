# Quick Start

Get productive with Shadai in 5 minutes. This guide covers the essential operations you'll use every day.

## Your First Shadai Application

Create a file `app.py`:

```python
import asyncio
from shadai import Shadai

async def main():
    # Create a session
    async with Shadai(name="quickstart") as shadai:
        # Ingest a document
        await shadai.ingest(folder_path="./docs")

        # Query your knowledge base
        async for chunk in shadai.query("What are the main topics?"):
            print(chunk, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python app.py
```

## Core Operations

### 1. Session Management

Sessions organize your documents and conversations:

```python
# Named session (persistent)
async with Shadai(name="my-project") as shadai:
    # Your code here
    pass

# Temporal session (auto-deleted)
async with Shadai(temporal=True) as shadai:
    # Great for one-off queries
    pass
```

### 2. Document Ingestion

Add documents to your knowledge base:

```python
async with Shadai(name="research") as shadai:
    # Ingest entire folder
    results = await shadai.ingest(folder_path="./documents")

    print(f"✅ Ingested {results['successful_count']} files")
    print(f"❌ Failed: {results['failed_count']}")
```

Supported formats:
- 📄 PDF
- 🖼️ Images (JPG, PNG, WEBP)
- Max size: 35MB per file

### 3. Query Knowledge Base

Ask questions about your documents:

```python
async with Shadai(name="research") as shadai:
    async for chunk in shadai.query("What are the key findings?"):
        print(chunk, end="")
```

### 4. Summarize Documents

Get an overview of all documents:

```python
async with Shadai(name="research") as shadai:
    async for chunk in shadai.summarize():
        print(chunk, end="")
```

### 5. Web Search

Search for current information:

```python
async with Shadai(name="research") as shadai:
    async for chunk in shadai.web_search("Latest AI developments 2024"):
        print(chunk, end="")
```

### 6. Unified Engine

Combine multiple capabilities:

```python
async with Shadai(name="research") as shadai:
    async for chunk in shadai.engine(
        prompt="Compare my documents with latest industry trends",
        use_knowledge_base=True,
        use_web_search=True,
        use_summary=True
    ):
        print(chunk, end="")
```

## Model Selection

Choose specific AI models for your session:

```python
from shadai import Shadai, LLMModel, EmbeddingModel

# Use Google models (fast and cost-effective)
async with Shadai(
    name="quick-analysis",
    llm_model=LLMModel.GOOGLE_GEMINI_2_0_FLASH,
    embedding_model=EmbeddingModel.GOOGLE_GEMINI_EMBEDDING_001
) as shadai:
    async for chunk in shadai.query("Quick question"):
        print(chunk, end="")

# Use OpenAI GPT-4o (premium quality)
async with Shadai(
    name="detailed-analysis",
    llm_model=LLMModel.OPENAI_GPT_4O,
    embedding_model=EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_LARGE
) as shadai:
    async for chunk in shadai.query("Complex analysis"):
        print(chunk, end="")

# Use Claude (excellent for creative tasks)
async with Shadai(
    name="creative-writing",
    llm_model=LLMModel.ANTHROPIC_CLAUDE_SONNET_4_5,
    embedding_model=EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL,
    system_prompt="You are a creative writing assistant."
) as shadai:
    async for chunk in shadai.query("Write a story about AI"):
        print(chunk, end="")
```

**Available Models:**
- **31 LLM models**: OpenAI, Azure, Anthropic (Claude), Google (Gemini)
- **5 embedding models**: OpenAI, Azure, Google

[See complete model list →](../api-reference/shadai-client.md#model-selection)

## Complete Example

Here's a realistic workflow with model selection:

```python
import asyncio
from shadai import Shadai, LLMModel, EmbeddingModel

async def analyze_market_research():
    """Analyze market research documents and compare with current trends."""

    # Use Google models for fast, cost-effective analysis
    async with Shadai(
        name="market-analysis",
        llm_model=LLMModel.GOOGLE_GEMINI_2_0_FLASH,
        embedding_model=EmbeddingModel.GOOGLE_GEMINI_EMBEDDING_001,
        system_prompt="You are a market research analyst."
    ) as shadai:
        print("📥 Ingesting documents...")
        results = await shadai.ingest(folder_path="./market-reports")
        print(f"✅ Processed {results['successful_count']} documents\n")

        print("📊 Generating summary...")
        async for chunk in shadai.summarize():
            print(chunk, end="")
        print("\n\n")

        print("🔍 Analyzing specific question...")
        async for chunk in shadai.query(
            "What are the top 3 market opportunities?"
        ):
            print(chunk, end="")
        print("\n\n")

        print("🌐 Comparing with current trends...")
        async for chunk in shadai.engine(
            prompt="How do our findings compare with latest Q4 2024 trends?",
            use_knowledge_base=True,
            use_web_search=True
        ):
            print(chunk, end="")

if __name__ == "__main__":
    asyncio.run(analyze_market_research())
```

## Memory & Context

By default, Shadai remembers your conversation:

```python
async with Shadai(name="chat") as shadai:
    # First question
    async for chunk in shadai.query("Who wrote The Great Gatsby?"):
        print(chunk, end="")

    # Follow-up (context maintained!)
    async for chunk in shadai.query("When was it published?"):
        print(chunk, end="")  # Knows we're still talking about The Great Gatsby
```

Disable memory if needed:

```python
async for chunk in shadai.query("New topic", use_memory=False):
    print(chunk, end="")
```

## Chat History

Retrieve and manage conversation history:

```python
async with Shadai(name="chat") as shadai:
    # Get history
    history = await shadai.get_session_history(page=1, page_size=10)

    for msg in history["results"]:
        print(f"{msg['role']}: {msg['content'][:50]}...")

    # Clear history
    await shadai.clear_session_history()
```

## Error Handling

Handle errors gracefully:

```python
from shadai import Shadai, AuthenticationError, ServerError

try:
    async with Shadai(name="test") as shadai:
        async for chunk in shadai.query("test"):
            print(chunk, end="")

except AuthenticationError:
    print("❌ Invalid API key")
except ServerError as e:
    print(f"❌ Server error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
```

## Best Practices

### ✅ Do This

```python
# Use context manager for automatic cleanup
async with Shadai(name="my-session") as shadai:
    async for chunk in shadai.query("query"):
        print(chunk, end="")

# Process streaming responses in real-time
async for chunk in shadai.query("query"):
    print(chunk, end="", flush=True)  # flush=True for real-time output

# Use named sessions for persistence
async with Shadai(name="project-alpha") as shadai:
    pass
```

### ❌ Don't Do This

```python
# Don't forget async context manager
shadai = Shadai(name="test")  # Missing async with
await shadai.query("test")  # Will fail

# Don't block streaming
response = ""
async for chunk in shadai.query("query"):
    response += chunk  # Defeats purpose of streaming

# Don't use temporal sessions for important data
async with Shadai(temporal=True) as shadai:
    await shadai.ingest(folder_path="important-docs")  # Will be deleted!
```

## Common Patterns

### Pattern 1: Batch Processing

```python
async def process_multiple_questions(questions):
    async with Shadai(name="batch") as shadai:
        for question in questions:
            print(f"\nQ: {question}")
            async for chunk in shadai.query(question):
                print(chunk, end="")
```

### Pattern 2: Incremental Ingestion

```python
async def add_new_documents():
    async with Shadai(name="knowledge-base") as shadai:
        # Add new documents to existing session
        await shadai.ingest(folder_path="./new-docs")
```

### Pattern 3: Multi-Modal Analysis

```python
async def comprehensive_analysis():
    async with Shadai(name="analysis") as shadai:
        # Combine all capabilities
        async for chunk in shadai.engine(
            prompt="Comprehensive analysis with all available information",
            use_knowledge_base=True,
            use_summary=True,
            use_web_search=True
        ):
            print(chunk, end="")
```

## Next Steps

🎉 You now know the basics! Here's what to explore next:

- [Session Management Deep Dive](../guides/session-management.md)
- [Memory & Context Guide](../guides/memory-and-context.md)
- [File Ingestion Guide](../guides/file-ingestion.md)
- [Use Cases](../use-cases/document-qa.md)

## Need Help?

- 📖 [Core Concepts](../core-concepts/architecture.md) - Understand how Shadai works
- 💡 [Examples](../examples/basic-query.md) - See more code examples
- 🚀 [Advanced Topics](../advanced/custom-tools.md) - Go deeper

---

Ready to learn more? → [Your First Query](first-query.md)
