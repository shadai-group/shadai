# Custom Tools

Create powerful custom tools for your Shadai agents.

## Tool Basics

### Minimum Requirements

```python
from shadai import tool

@tool
def my_tool(param: str) -> str:
    """Tool description.

    Args:
        param: Parameter description
    """
    return "result"
```

**Required:**
1. `@tool` decorator
2. Type hints
3. Docstring
4. Return string

## Tool Design Principles

### Single Responsibility

✅ **Good:**
```python
@tool
def get_user_email(user_id: str) -> str:
    """Get user email address."""
    return "user@example.com"

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send email."""
    return "Email sent"
```

❌ **Bad:**
```python
@tool
def get_user_and_send_email(user_id: str, subject: str) -> str:
    """Get user and send email."""
    # Too many responsibilities
    pass
```

### Clear Descriptions

✅ **Good:**
```python
@tool
def search_products(
    category: str,
    min_price: float = 0.0,
    max_price: float = None,
    in_stock: bool = True
) -> str:
    """Search products by category and price range.

    Searches the product catalog for items matching the specified
    category and price constraints. Only returns available items
    unless in_stock is set to False.

    Args:
        category: Product category (e.g., 'electronics', 'books')
        min_price: Minimum price in dollars (default: 0.0)
        max_price: Maximum price in dollars (optional)
        in_stock: Only show available items (default: True)

    Returns:
        Formatted list of matching products with prices
    """
    # Implementation
    return "Product listings..."
```

### Type Safety

```python
from typing import List, Optional

@tool
def batch_lookup(ids: List[str], include_details: bool = False) -> str:
    """Lookup multiple items by ID."""
    return "Results..."

@tool
def get_record(id: str, fields: Optional[List[str]] = None) -> str:
    """Get record with optional field filtering."""
    return "Record data..."
```

## Advanced Patterns

### Error Handling

```python
@tool
def safe_api_call(endpoint: str) -> str:
    """Make API call with error handling."""
    try:
        # Your API logic
        return "Success: data"
    except ConnectionError:
        return "Error: Could not connect to API"
    except Exception as e:
        return f"Error: {str(e)}"
```

### Data Formatting

```python
@tool
def get_financial_data(company: str, format: str = "summary") -> str:
    """Get company financial data.

    Args:
        company: Company name or ticker
        format: Output format ('summary', 'detailed', 'json')
    """
    if format == "summary":
        return "Revenue: $1.5B, Profit: $200M"
    elif format == "detailed":
        return "Detailed breakdown:\n- Revenue: $1.5B\n- Expenses: $1.3B..."
    else:
        return '{"revenue": 1500000000, "profit": 200000000}'
```

### Async Tools

```python
import asyncio

@tool
async def fetch_remote_data(url: str) -> str:
    """Fetch data from remote URL asynchronously."""
    await asyncio.sleep(0.1)  # Simulated async operation
    return "Remote data..."
```

## Testing Tools

```python
import pytest
from shadai import tool

@tool
def calculator(operation: str, a: float, b: float) -> str:
    """Perform calculation."""
    if operation == "add":
        return str(a + b)
    elif operation == "multiply":
        return str(a * b)
    return "Unknown operation"

# Test
def test_calculator():
    result = calculator("add", 5.0, 3.0)
    assert result == "8.0"
```

## Integration Examples

### Database Tool

```python
@tool
def query_database(sql: str, limit: int = 10) -> str:
    """Execute SQL query.

    Args:
        sql: SQL SELECT statement
        limit: Maximum rows to return
    """
    # Your database logic
    return "Row1, Row2, Row3..."
```

### API Tool

```python
import requests

@tool
def call_rest_api(endpoint: str, method: str = "GET") -> str:
    """Call REST API endpoint.

    Args:
        endpoint: API endpoint path
        method: HTTP method (GET, POST, etc.)
    """
    try:
        response = requests.request(method, endpoint, timeout=10)
        return response.text
    except Exception as e:
        return f"API Error: {e}"
```

### File System Tool

```python
from pathlib import Path

@tool
def list_files(directory: str, extension: str = "*") -> str:
    """List files in directory.

    Args:
        directory: Directory path
        extension: File extension filter (e.g., '*.pdf')
    """
    path = Path(directory)
    files = list(path.glob(f"**/{extension}"))
    return "\n".join(str(f) for f in files[:50])  # Limit results
```

## Best Practices

### ✅ Do This

```python
# Clear names
@tool
def get_customer_by_email(email: str) -> str:
    """Find customer by email address."""
    pass

# Comprehensive docstrings
@tool
def calculate_roi(investment: float, returns: float, period_years: int) -> str:
    """Calculate return on investment.

    Calculates annualized ROI based on initial investment,
    total returns, and investment period.

    Args:
        investment: Initial investment amount in dollars
        returns: Total returns received in dollars
        period_years: Investment period in years

    Returns:
        Annualized ROI as percentage string
    """
    pass

# Handle edge cases
@tool
def divide(a: float, b: float) -> str:
    """Divide two numbers."""
    if b == 0:
        return "Error: Division by zero"
    return str(a / b)
```

### ❌ Don't Do This

```python
# Vague names
@tool
def process(x):  # What does it process?
    pass

# Missing docstrings
@tool
def calc(a: float, b: float) -> str:
    pass

# Complex return types
@tool
def fetch_data() -> dict:  # Should return str
    return {"data": "value"}
```

## See Also

- [Intelligent Agent](../core-concepts/intelligent-agent.md)
- [Tool Orchestration](tool-orchestration.md)
- [Custom Agent Examples](../examples/custom-agent.md)
