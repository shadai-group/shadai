# Shadai Client Documentation

**Welcome to Shadai** - The most intuitive Python SDK for building intelligent, context-aware AI applications.

## What is Shadai?

Shadai is a production-ready Python client that transforms how you interact with AI. Built on cutting-edge RAG (Retrieval-Augmented Generation) technology, Shadai enables you to:

- 🧠 **Query your knowledge base** with natural language
- 📚 **Ingest and process documents** at scale
- 🤖 **Orchestrate intelligent agents** that reason and act
- 💬 **Maintain conversation context** across interactions
- 🔍 **Search the web** for real-time information
- ⚡ **Stream responses** in real-time

## Why Choose Shadai?

### 🚀 Developer First

```python
# It's this simple
async with Shadai(name="research") as shadai:
    async for chunk in shadai.query("What are the key findings?"):
        print(chunk, end="")
```

### 🧠 Intelligent by Default

- **Automatic context management** - Memory enabled out of the box
- **Smart agent orchestration** - Plan → Execute → Synthesize workflow
- **Multi-source synthesis** - Combines documents, web search, and more

### ⚡ Production Ready

- **Streaming responses** - Real-time token streaming for all operations
- **Type-safe** - Full type hints for better IDE support
- **Error handling** - Comprehensive exception hierarchy
- **Async-first** - Built on modern async/await patterns

### 🎯 Flexible & Powerful

- **Custom tools** - Define your own tools with automatic schema inference
- **Session management** - Organize conversations and documents
- **Chat history** - Full conversation history with pagination
- **Multiple LLM support** - Works with Gemini, Claude, OpenAI, and more

## Quick Navigation

### 🎓 Getting Started
Start here if you're new to Shadai:
- [Installation](getting-started/installation.md)
- [Quick Start](getting-started/quickstart.md)
- [Authentication](getting-started/authentication.md)
- [Your First Query](getting-started/first-query.md)

### 📖 Guides
Learn how to use Shadai's core features:
- [Session Management](guides/session-management.md)
- [Memory & Context](guides/memory-and-context.md)
- [File Ingestion](guides/file-ingestion.md)
- [Streaming Responses](guides/streaming-responses.md)
- [Error Handling](guides/error-handling.md)

### 🧩 Core Concepts
Understand how Shadai works:
- [Architecture](core-concepts/architecture.md)
- [RAG System](core-concepts/rag-system.md)
- [Tools Overview](core-concepts/tools-overview.md)
- [Intelligent Agent](core-concepts/intelligent-agent.md)

### 💼 Use Cases
See Shadai in action:
- [Document Q&A](use-cases/document-qa.md)
- [Research Assistant](use-cases/research-assistant.md)
- [Knowledge Synthesis](use-cases/knowledge-synthesis.md)
- [Custom Workflows](use-cases/custom-workflows.md)

### 📚 API Reference
Complete API documentation:
- [Shadai Client](api-reference/shadai-client.md)
- [Query Tool](api-reference/query-tool.md)
- [Summarize Tool](api-reference/summarize-tool.md)
- [Web Search Tool](api-reference/web-search-tool.md)
- [Engine Tool](api-reference/engine-tool.md)
- [Agent Tool](api-reference/agent-tool.md)
- [Exceptions](api-reference/exceptions.md)

### 💡 Examples
Ready-to-use code examples:
- [Basic Query](examples/basic-query.md)
- [Multi-Document Analysis](examples/multi-document-analysis.md)
- [Custom Agent](examples/custom-agent.md)
- [Market Research](examples/market-research.md)
- [Advanced Patterns](examples/advanced-patterns.md)

### 🚀 Advanced
Take your skills to the next level:
- [Custom Tools](advanced/custom-tools.md)
- [Tool Orchestration](advanced/tool-orchestration.md)
- [Performance Optimization](advanced/performance-optimization.md)
- [Best Practices](advanced/best-practices.md)

## What's New in v0.1.29

🎉 **Latest Release Highlights:**

- **🧠 Memory Enabled by Default** - All tools now maintain conversation context automatically
- **💬 Chat History Management** - New methods to retrieve and manage conversation history
- **📖 Enhanced Documentation** - This comprehensive documentation site!

[See full changelog →](https://github.com/shadai/shadai-client/releases)

## Quick Example

Here's a taste of what you can do with Shadai:

```python
import asyncio
from shadai import Shadai, tool

# Define custom tools
@tool
def get_customer_sentiment(product: str) -> str:
    """Analyze customer sentiment for a product."""
    return "92% positive feedback, customers love the ease of use"

# Use intelligent agent
async def main():
    async with Shadai(name="analysis") as shadai:
        # Ingest documents
        await shadai.ingest(folder_path="./reports")

        # Query with memory
        async for chunk in shadai.query(
            "What are the revenue trends?"
        ):
            print(chunk, end="")

        # Follow-up question (context maintained)
        async for chunk in shadai.query(
            "How does this compare to customer satisfaction?"
        ):
            print(chunk, end="")

        # Use custom agent
        async for chunk in shadai.agent(
            prompt="Analyze product performance and customer sentiment",
            tools=[get_customer_sentiment]
        ):
            print(chunk, end="")

asyncio.run(main())
```

## Support & Community

- 📧 **Email**: support@shadai.com
- 📖 **Documentation**: https://docs.shadai.com
- 🐛 **Issues**: https://github.com/shadai/shadai-client/issues

## License

MIT License - see LICENSE file for details.

---

**Ready to get started?** → [Installation Guide](getting-started/installation.md)
