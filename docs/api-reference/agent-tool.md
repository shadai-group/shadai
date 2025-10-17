# Agent Tool API

Execute custom workflows with your own tools.

## Method Signature

```python
async def agent(prompt: str, tools: List[Callable]) -> AsyncIterator[str]
```

## Parameters

- **prompt** (str, required): Task description
- **tools** (List[Callable], required): List of tool functions

## Returns

Async iterator yielding response chunks (strings)

## Creating Tools

### Using @tool Decorator

```python
from shadai import tool

@tool
def my_function(param: str, count: int = 10) -> str:
    """Tool description.

    Args:
        param: Parameter description
        count: Count parameter

    Returns:
        Result as string
    """
    return "result"
```

### Tool Requirements

- Must use `@tool` decorator
- Must have docstring
- Must have type hints
- Must return string

## Example

```python
from shadai import tool

@tool
def search_database(query: str) -> str:
    """Search user database."""
    return "User1, User2..."

async for chunk in shadai.agent(
    prompt="Find top users and generate report",
    tools=[search_database]
):
    print(chunk, end="")
```

## See Also
- [Intelligent Agent](../core-concepts/intelligent-agent.md)
- [Custom Tools Guide](../advanced/custom-tools.md)
