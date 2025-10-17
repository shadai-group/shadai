# Tools Overview

Shadai provides five powerful tools for different use cases. This guide helps you choose the right tool for your needs.

## Available Tools

| Tool | Best For | Streaming | Memory |
|------|----------|-----------|--------|
| **Query** | Specific questions | ✅ | ✅ |
| **Summarize** | Document overview | ✅ | ✅ |
| **Web Search** | Current information | ✅ | ✅ |
| **Engine** | Multi-source analysis | ✅ | ✅ |
| **Agent** | Custom workflows | ✅ | ✅ |

## Query Tool

**Purpose**: Ask specific questions about your documents.

**Use When**:
- You have a specific question
- Need information from documents
- Want to cite sources

```python
async for chunk in shadai.query("What are the payment terms?"):
    print(chunk, end="")
```

**Examples**:
- "What's the refund policy?"
- "Who is the contract between?"
- "What are the main findings?"
- "List all requirements"

**Best Practices**:
✅ Be specific
✅ Use follow-up questions
✅ Enable memory for conversations

❌ Don't ask extremely broad questions
❌ Don't query without ingesting documents first

## Summarize Tool

**Purpose**: Get an executive summary of all documents in a session.

**Use When**:
- Starting a new project
- Need overview before deep dive
- Want to understand document scope
- Presenting to stakeholders

```python
async for chunk in shadai.summarize():
    print(chunk, end="")
```

**What It Provides**:
- Main topics covered
- Key themes
- Important entities
- Document structure
- Overall insights

**Best Practices**:
✅ Run after ingesting all documents
✅ Use as conversation starter
✅ Follow up with specific queries

❌ Don't use for detailed analysis
❌ Don't use with no documents

## Web Search Tool

**Purpose**: Find current information from the internet.

**Use When**:
- Need latest news/data
- Checking current trends
- Verifying recent information
- Researching live topics

```python
async for chunk in shadai.web_search("Latest AI developments 2024"):
    print(chunk, end="")
```

**Examples**:
- "Current stock price of Tesla"
- "Latest COVID-19 guidelines"
- "Recent AI breakthroughs"
- "Today's weather in NYC"

**Best Practices**:
✅ Use for time-sensitive queries
✅ Be specific with dates
✅ Combine with document queries

❌ Don't use for historical data
❌ Don't use for private information

## Engine Tool

**Purpose**: Orchestrate multiple tools for comprehensive analysis.

**Use When**:
- Need multi-source insights
- Comparing documents with trends
- Comprehensive research
- Complex analysis

```python
async for chunk in shadai.engine(
    prompt="Compare my contracts with industry standards",
    use_knowledge_base=True,  # Query documents
    use_summary=True,          # Include overview
    use_web_search=True        # Check current standards
):
    print(chunk, end="")
```

**Capabilities**:
- Combines document knowledge
- Adds web search results
- Includes summaries
- Synthesizes information

**Examples**:
- "How do our policies compare to competitors?"
- "Analyze documents and check current market trends"
- "What's missing from our strategy based on industry best practices?"

**Best Practices**:
✅ Use for complex questions
✅ Enable relevant capabilities
✅ Let it synthesize information

❌ Don't use for simple queries
❌ Don't enable all features unnecessarily

## Agent Tool

**Purpose**: Execute custom workflows with your own tools.

**Use When**:
- Need custom functionality
- Integrating with your systems
- Automating complex workflows
- Building specialized applications

```python
from shadai import tool

@tool
def search_database(query: str) -> str:
    """Search internal database."""
    return "results..."

async for chunk in shadai.agent(
    prompt="Find users and generate report",
    tools=[search_database]
):
    print(chunk, end="")
```

**How It Works**:
1. **Plans**: Determines which tools to use
2. **Executes**: Runs tools with inferred arguments
3. **Synthesizes**: Combines results into answer

**Examples**:
- Database queries + report generation
- API calls + data analysis
- Multi-step workflows
- Custom business logic

**Best Practices**:
✅ Provide clear tool descriptions
✅ Use type hints
✅ Keep tools focused

❌ Don't create overlapping tools
❌ Don't make tools too complex

## Tool Comparison

### Query vs. Summarize

**Use Query When:**
- Have specific question
- Need detailed answer
- Want to cite specific sections

**Use Summarize When:**
- Need overview
- Starting research
- Want big picture

### Query vs. Web Search

**Use Query When:**
- Information in your documents
- Need private/internal data
- Historical information

**Use Web Search When:**
- Need current data
- Public information
- Live updates

### Query vs. Engine

**Use Query When:**
- Simple, direct question
- Single source sufficient
- Fast answer needed

**Use Engine When:**
- Complex analysis
- Multiple sources needed
- Synthesis required

### Engine vs. Agent

**Use Engine When:**
- Standard capabilities sufficient
- Document + web + summary
- No custom logic needed

**Use Agent When:**
- Custom tools required
- Specialized workflows
- Integration with systems

## Combining Tools

### Pattern 1: Overview → Deep Dive

```python
# Start with summary
async for chunk in shadai.summarize():
    print(chunk, end="")

# Then ask specific questions
async for chunk in shadai.query("Tell me more about section 3"):
    print(chunk, end="")
```

### Pattern 2: Documents + Current Data

```python
# Combine internal docs with external data
async for chunk in shadai.engine(
    prompt="How do our Q3 results compare to market trends?",
    use_knowledge_base=True,
    use_web_search=True
):
    print(chunk, end="")
```

### Pattern 3: Custom Workflow

```python
@tool
def get_sales_data() -> str:
    return "sales data..."

# Agent uses custom tool + built-in capabilities
async for chunk in shadai.agent(
    prompt="Analyze sales and compare with documents",
    tools=[get_sales_data]
):
    print(chunk, end="")
```

## Tool Selection Guide

**Start Here:**

```
Do you need custom functionality?
    ├─ Yes → Agent
    └─ No ↓

Do you need current/live data?
    ├─ Yes → Web Search
    └─ No ↓

Do you need multi-source analysis?
    ├─ Yes → Engine
    └─ No ↓

Do you need overview of documents?
    ├─ Yes → Summarize
    └─ No → Query
```

## Common Patterns

### Research Workflow

```python
# 1. Ingest documents
await shadai.ingest(folder_path="./research")

# 2. Get overview
async for chunk in shadai.summarize():
    print(chunk, end="")

# 3. Deep dive
async for chunk in shadai.query("What are the key findings?"):
    print(chunk, end="")

# 4. Compare with current
async for chunk in shadai.engine(
    prompt="How does this compare to latest research?",
    use_knowledge_base=True,
    use_web_search=True
):
    print(chunk, end="")
```

### Due Diligence Workflow

```python
# 1. Ingest contracts
await shadai.ingest(folder_path="./contracts")

# 2. Summary
async for chunk in shadai.summarize():
    print(chunk, end="")

# 3. Specific checks
queries = [
    "What are the payment terms?",
    "Are there any termination clauses?",
    "What are the liability limits?"
]

for q in queries:
    async for chunk in shadai.query(q):
        print(f"\n{q}\n{chunk}\n")
```

### Market Analysis Workflow

```python
# 1. Internal docs
await shadai.ingest(folder_path="./internal-reports")

# 2. Comprehensive analysis
async for chunk in shadai.engine(
    prompt="Analyze market position and competitive landscape",
    use_knowledge_base=True,
    use_summary=True,
    use_web_search=True
):
    print(chunk, end="")
```

## Performance Tips

### Fast Queries

```python
# Disable memory for independent queries
async for chunk in shadai.query("Quick fact", use_memory=False):
    print(chunk, end="")
```

### Complex Analysis

```python
# Use engine for multi-faceted questions
async for chunk in shadai.engine(
    prompt="Complex analysis needed",
    use_knowledge_base=True,
    use_summary=True
):
    print(chunk, end="")
```

### Batch Processing

```python
# Process multiple queries efficiently
questions = ["Q1", "Q2", "Q3"]

for q in questions:
    async for chunk in shadai.query(q, use_memory=False):
        print(chunk, end="")
```

## Next Steps

- [Intelligent Agent](intelligent-agent.md) - Deep dive into agents
- [Use Cases](../use-cases/document-qa.md) - Practical examples
- [API Reference](../api-reference/shadai-client.md) - Complete documentation

---

**Remember**: Start simple with Query, add complexity as needed!
