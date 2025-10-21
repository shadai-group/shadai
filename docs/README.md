# Shadai Client Documentation

Welcome to the complete documentation for the Shadai Python client! This documentation will help you build powerful AI applications with document understanding, intelligent agents, and RAG technology.

## 📚 Documentation Structure

### [Index →](index.md)
Main documentation hub with complete navigation

## 🚀 Quick Links

### New to Shadai?
Start here to get up and running:
- [Installation](getting-started/installation.md) - Install Shadai in 60 seconds
- [Authentication](getting-started/authentication.md) - Set up your API key
- [Quick Start](getting-started/quickstart.md) - Core operations in 5 minutes
- [Your First Query](getting-started/first-query.md) - Step-by-step tutorial

### Building Applications?
Learn the essentials:
- [Session Management](guides/session-management.md) - Organize your work
- [Memory & Context](guides/memory-and-context.md) - Conversational AI
- [File Ingestion](guides/file-ingestion.md) - Process documents
- [Streaming Responses](guides/streaming-responses.md) - Real-time output
- [Error Handling](guides/error-handling.md) - Robust applications

### Understanding Shadai?
Deep dive into concepts:
- [Architecture](core-concepts/architecture.md) - How Shadai works
- [RAG System](core-concepts/rag-system.md) - Retrieval-Augmented Generation
- [Tools Overview](core-concepts/tools-overview.md) - All available tools
- [Intelligent Agent](core-concepts/intelligent-agent.md) - Autonomous workflows

### Real-World Use Cases?
Practical applications:
- [Document Q&A](use-cases/document-qa.md) - Build Q&A systems
- [Research Assistant](use-cases/research-assistant.md) - Analyze research
- [Knowledge Synthesis](use-cases/knowledge-synthesis.md) - Multi-document analysis
- [Custom Workflows](use-cases/custom-workflows.md) - Build specialized systems

### API Reference?
Complete technical reference:
- [Shadai Client](api-reference/shadai-client.md) - Main client class
- [Query Tool](api-reference/query-tool.md) - Document queries
- [Summarize Tool](api-reference/summarize-tool.md) - Document summaries
- [Web Search Tool](api-reference/web-search-tool.md) - Internet search
- [Engine Tool](api-reference/engine-tool.md) - Multi-tool orchestration
- [Agent Tool](api-reference/agent-tool.md) - Custom workflows
- [Exceptions](api-reference/exceptions.md) - Error handling

### Code Examples?
Ready-to-use examples:
- [Basic Query](examples/basic-query.md) - Simple queries
- [Multi-Document Analysis](examples/multi-document-analysis.md) - Multiple docs
- [Custom Agent](examples/custom-agent.md) - Build agents
- [Market Research](examples/market-research.md) - Research workflows
- [Advanced Patterns](examples/advanced-patterns.md) - Pro techniques

### Advanced Topics?
Take it to the next level:
- [Custom Tools](advanced/custom-tools.md) - Build your own tools
- [Tool Orchestration](advanced/tool-orchestration.md) - Complex workflows
- [Performance Optimization](advanced/performance-optimization.md) - Speed & efficiency
- [Best Practices](advanced/best-practices.md) - Production-ready patterns

## 🎯 Common Tasks

### I want to...

**Query documents**
```python
async with Shadai(name="docs") as shadai:
    await shadai.ingest(folder_path="./documents")
    async for chunk in shadai.query("What are the terms?"):
        print(chunk, end="")
```
→ [Document Q&A Guide](use-cases/document-qa.md)

**Choose specific AI models** ✨ NEW
```python
from shadai import Shadai, LLMModel, EmbeddingModel

async with Shadai(
    name="premium-analysis",
    llm_model=LLMModel.OPENAI_GPT_4O,
    embedding_model=EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_LARGE,
    system_prompt="You are an expert analyst."
) as shadai:
    async for chunk in shadai.query("Detailed analysis"):
        print(chunk, end="")
```
→ [Model Selection Guide](guides/session-management.md#model-configuration)

**Build a chatbot**
```python
async with Shadai(name="chat") as shadai:
    while True:
        question = input("You: ")
        async for chunk in shadai.query(question):
            print(chunk, end="")
```
→ [Quick Start](getting-started/quickstart.md)

**Create custom tools**
```python
from shadai import tool

@tool
def my_tool(param: str) -> str:
    """Tool description."""
    return "result"

async for chunk in shadai.agent(
    prompt="Execute task",
    tools=[my_tool]
):
    print(chunk, end="")
```
→ [Custom Tools Guide](advanced/custom-tools.md)

**Analyze multiple documents**
```python
async with Shadai(name="analysis") as shadai:
    await shadai.ingest(folder_path="./reports")
    async for chunk in shadai.engine(
        prompt="Compare all reports",
        use_knowledge_base=True,
        use_summary=True
    ):
        print(chunk, end="")
```
→ [Knowledge Synthesis](use-cases/knowledge-synthesis.md)

## 📖 Learning Paths

### Path 1: Build a Q&A System (30 minutes)
1. [Installation](getting-started/installation.md) (5 min)
2. [Authentication](getting-started/authentication.md) (5 min)
3. [Your First Query](getting-started/first-query.md) (10 min)
4. [Document Q&A Use Case](use-cases/document-qa.md) (10 min)

### Path 2: Master Core Features (1 hour)
1. [Quick Start](getting-started/quickstart.md) (15 min)
2. [Session Management](guides/session-management.md) (15 min)
3. [Memory & Context](guides/memory-and-context.md) (15 min)
4. [Tools Overview](core-concepts/tools-overview.md) (15 min)

### Path 3: Build Custom Agents (2 hours)
1. [Intelligent Agent Concepts](core-concepts/intelligent-agent.md) (30 min)
2. [Custom Tools Guide](advanced/custom-tools.md) (45 min)
3. [Custom Agent Examples](examples/custom-agent.md) (30 min)
4. [Tool Orchestration](advanced/tool-orchestration.md) (15 min)

### Path 4: Production Deployment (1.5 hours)
1. [Error Handling](guides/error-handling.md) (20 min)
2. [Performance Optimization](advanced/performance-optimization.md) (40 min)
3. [Best Practices](advanced/best-practices.md) (30 min)

## 🔍 Search by Topic

### RAG & Document Processing
- [RAG System Explained](core-concepts/rag-system.md)
- [File Ingestion Guide](guides/file-ingestion.md)
- [Multi-Document Analysis](examples/multi-document-analysis.md)

### Agents & Tools
- [Intelligent Agent](core-concepts/intelligent-agent.md)
- [Custom Tools](advanced/custom-tools.md)
- [Tool Orchestration](advanced/tool-orchestration.md)
- [Custom Agent Examples](examples/custom-agent.md)

### Memory & Conversations
- [Memory & Context Guide](guides/memory-and-context.md)
- [Session Management](guides/session-management.md)
- [Chat History API](api-reference/shadai-client.md#get_session_history)

### Performance & Optimization
- [Streaming Responses](guides/streaming-responses.md)
- [Performance Optimization](advanced/performance-optimization.md)
- [Best Practices](advanced/best-practices.md)

### Integration & Production
- [Document Q&A System](use-cases/document-qa.md)
- [Error Handling](guides/error-handling.md)
- [Best Practices](advanced/best-practices.md)

## 💡 Tips

- **Start Simple**: Begin with basic queries, add complexity as needed
- **Use Memory**: Enable memory by default for natural conversations
- **Stream Responses**: Always stream for better user experience
- **Handle Errors**: Use try/except for robust applications
- **Reuse Sessions**: Keep sessions alive for better performance

## 🆘 Need Help?

- 📧 **Email**: support@shadai.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/shadai/shadai-client/issues)
- 📖 **API Reference**: [Complete API Docs](api-reference/shadai-client.md)

## 🆕 What's New in v0.1.31

- **🎯 Model Selection** - Choose from 31 LLM models and 5 embedding models across OpenAI, Azure, Anthropic (Claude), and Google (Gemini)
- **⚡ Automatic Error Handling** - Clean, user-friendly error messages without verbose tracebacks
- **🎨 System Prompts** - Customize your session's behavior with custom system prompts
- **🔧 Provider Flexibility** - Mix and match providers (e.g., Google LLM + OpenAI embeddings)

### Previous Release (v0.1.29)

- **🧠 Memory Enabled by Default** - All tools now use conversation memory automatically
- **💬 Chat History Management** - New methods to retrieve and clear session history
- **📖 Complete Documentation** - This comprehensive documentation site!

[See full changelog →](https://github.com/shadai/shadai-client/releases)

## 📄 License

MIT License - see LICENSE file for details.

---

**Ready to start?** → [Installation Guide](getting-started/installation.md)

**Have questions?** → [Core Concepts](core-concepts/architecture.md)

**Building something specific?** → [Use Cases](use-cases/document-qa.md)
