# Tool Orchestration

Master the art of orchestrating multiple tools for complex workflows.

## Orchestration Patterns

### Sequential Execution

```python
@tool
def step1(input: str) -> str:
    return "step1 result"

@tool
def step2(input: str) -> str:
    return "step2 result"

@tool
def step3(input: str) -> str:
    return "step3 result"

# Agent automatically chains
async for chunk in shadai.agent(
    prompt="Execute step1, then step2, then step3",
    tools=[step1, step2, step3]
):
    print(chunk, end="")
```

### Conditional Logic

```python
@tool
def check_condition(param: str) -> str:
    """Check if condition is met."""
    return "condition: met"

@tool
def action_if_true(data: str) -> str:
    """Execute if condition is true."""
    return "action completed"

@tool
def action_if_false(data: str) -> str:
    """Execute if condition is false."""
    return "alternative action"

# Agent decides which path
async for chunk in shadai.agent(
    prompt="Check condition, execute appropriate action",
    tools=[check_condition, action_if_true, action_if_false]
):
    print(chunk, end="")
```

### Parallel Execution

```python
@tool
def fetch_source_a() -> str:
    return "data from A"

@tool
def fetch_source_b() -> str:
    return "data from B"

@tool
def merge_data(data_a: str, data_b: str) -> str:
    return f"Merged: {data_a} + {data_b}"

# Agent can fetch in parallel
async for chunk in shadai.agent(
    prompt="Fetch from A and B, then merge",
    tools=[fetch_source_a, fetch_source_b, merge_data]
):
    print(chunk, end="")
```

## Complex Workflows

### ETL Pipeline

```python
@tool
def extract(source: str) -> str:
    """Extract data from source."""
    return "raw data"

@tool
def transform(data: str, format: str) -> str:
    """Transform data to format."""
    return "transformed data"

@tool
def load(data: str, destination: str) -> str:
    """Load data to destination."""
    return "loaded successfully"

@tool
def validate(destination: str) -> str:
    """Validate loaded data."""
    return "validation passed"

async for chunk in shadai.agent(
    prompt="Extract from DB, transform to JSON, load to warehouse, validate",
    tools=[extract, transform, load, validate]
):
    print(chunk, end="")
```

## See Also

- [Custom Tools](custom-tools.md)
- [Intelligent Agent](../core-concepts/intelligent-agent.md)
