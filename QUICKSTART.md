# Shadai Client - Quick Start Guide

## Installation

### From PyPI (when published)

```bash
pip install shadai-client
```

### From Source

```bash
# Clone or navigate to the client directory
cd client

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

## Your First Query

Create a file `my_first_query.py`:

```python
import asyncio
import os
from shadai import Shadai

async def main():
    # Get your API key from environment variable
    api_key = os.getenv("SHADAI_API_KEY")

    # Initialize client
    shadai = Shadai(api_key=api_key)

    # Check health
    health = await shadai.health()
    print(f"Server status: {health['status']}")

    # Query your documents
    session_uuid = "your-session-uuid-here"
    query = shadai.query(session_uuid=session_uuid)

    print("\nAsking: What is machine learning?\n")
    async for chunk in query("What is machine learning?"):
        print(chunk, end="", flush=True)

    print("\n")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
export SHADAI_API_KEY="your-api-key"
python my_first_query.py
```

## Next Steps

1. **Explore Examples**
   ```bash
   python -m shadai.examples.query_example
   python -m shadai.examples.planner_example
   python -m shadai.examples.complete_workflow
   ```

2. **Read the Full README**
   - Check `README.md` for comprehensive documentation
   - Learn about all available tools
   - See advanced usage patterns

3. **Try Different Tools**
   - Query: Search your documents
   - Summarize: Get document overviews
   - Web Search: Find current information
   - Planner: Let AI select the right tools
   - Synthesizer: Combine multiple tool outputs

## Common Patterns

### Basic Query
```python
query = shadai.query(session_uuid="...")
async for chunk in query("Your question?"):
    print(chunk, end="")
```

### With Memory
```python
async for chunk in query("Follow-up question", use_memory=True):
    print(chunk, end="")
```

### Multi-Tool Engine
```python
engine = shadai.engine(session_uuid="...")
async for chunk in engine(
    "Complex question",
    use_knowledge_base=True,
    use_web_search=True
):
    print(chunk, end="")
```

### Plan & Execute
```python
# Plan
planner = shadai.planner()
plan = await planner(prompt="Task", available_tools=tools)

# Execute based on plan
for tool in plan["tool_plan"]:
    # Your execution logic
    pass
```

## Getting Help

- 📖 **Documentation**: See `README.md`
- 💡 **Examples**: Check `shadai/examples/`
- 🐛 **Issues**: Report bugs on GitHub
- 💬 **Support**: Contact support@shadai.com

Happy coding with Shadai! 🚀
