# Intelligent Agent

Shadai's intelligent agent enables autonomous workflows with custom tools through a powerful plan → execute → synthesize pattern.

## What is an Agent?

An agent is an AI system that can:
- **Plan**: Decide which tools to use
- **Execute**: Run tools autonomously
- **Synthesize**: Combine results into coherent answers

```python
@tool
def search_database(query: str) -> str:
    """Search user database."""
    return "results..."

async for chunk in shadai.agent(
    prompt="Find top 10 users and create report",
    tools=[search_database]
):
    print(chunk, end="")
```

The agent automatically:
1. Decides to use `search_database`
2. Infers arguments from prompt
3. Executes the tool
4. Synthesizes results

## Agent Workflow

### Traditional Approach (Manual)

```python
# You must explicitly:
results = search_database(query="top users", limit=10)
report = generate_report(data=results, format="pdf")
send_email(recipient="boss@company.com", body=report)
```

### Agent Approach (Autonomous)

```python
# Agent figures it out:
async for chunk in shadai.agent(
    prompt="Find top 10 users, create PDF report, email to boss@company.com",
    tools=[search_database, generate_report, send_email]
):
    print(chunk, end="")
```

Agent automatically:
- Determines tool sequence
- Infers all arguments
- Handles tool execution
- Combines outputs

## Creating Custom Tools

### Method 1: Using @tool Decorator

```python
from shadai import tool

@tool
def calculate_roi(investment: float, return_value: float) -> str:
    """Calculate return on investment percentage.

    Args:
        investment: Initial investment amount
        return_value: Final return value

    Returns:
        ROI percentage as formatted string
    """
    roi = ((return_value - investment) / investment) * 100
    return f"ROI: {roi:.2f}%"
```

**Key Points**:
- Use `@tool` decorator
- Add docstring (agent uses this!)
- Type hints required
- Return string

### Method 2: Manual Tool Definition

```python
from shadai import AgentTool

def calculate_roi(investment: float, return_value: float) -> str:
    roi = ((return_value - investment) / investment) * 100
    return f"ROI: {roi:.2f}%"

roi_tool = AgentTool(
    name="calculate_roi",
    description="Calculate return on investment percentage",
    implementation=calculate_roi,
    parameters={
        "type": "object",
        "properties": {
            "investment": {
                "type": "number",
                "description": "Initial investment amount"
            },
            "return_value": {
                "type": "number",
                "description": "Final return value"
            }
        },
        "required": ["investment", "return_value"]
    }
)
```

**Use `@tool` decorator** - it's simpler and automatically generates schemas!

## Tool Design Best Practices

### ✅ Good Tool

```python
@tool
def search_users_by_revenue(
    min_revenue: float,
    max_revenue: float = None,
    limit: int = 10
) -> str:
    """Search for users within a revenue range.

    Finds users whose revenue falls between min and max values.
    Results are sorted by revenue in descending order.

    Args:
        min_revenue: Minimum revenue threshold in dollars
        max_revenue: Maximum revenue threshold in dollars (optional)
        limit: Maximum number of results to return (default: 10)

    Returns:
        Formatted list of users with their revenue figures
    """
    # Implementation
    return "User1: $50k, User2: $75k..."
```

**Why Good:**
- Clear, descriptive name
- Detailed docstring
- Type hints
- Optional parameters
- Returns formatted string

### ❌ Bad Tool

```python
def search(query):  # No @tool, no types
    return db.query(query)  # Returns object, not string
```

**Why Bad:**
- No decorator
- No docstring
- No type hints
- Vague name
- Returns non-string

## Agent Capabilities

### 1. Tool Selection

Agent automatically chooses appropriate tools:

```python
@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Sunny, 72°F in {city}"

@tool
def get_stock_price(symbol: str) -> str:
    """Get current stock price."""
    return f"{symbol}: $150.25"

# Agent selects correct tool
async for chunk in shadai.agent(
    prompt="What's the weather in NYC?",
    tools=[get_weather, get_stock_price]
):
    print(chunk, end="")
# Uses get_weather only
```

### 2. Argument Inference

Agent infers arguments from prompt:

```python
@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return f"Email sent to {to}"

# No need to specify arguments!
async for chunk in shadai.agent(
    prompt="Email report to boss@company.com with subject 'Q4 Results'",
    tools=[send_email]
):
    print(chunk, end="")
# Agent infers: to="boss@company.com", subject="Q4 Results", body=<generated>
```

### 3. Multi-Step Execution

Agent chains tools automatically:

```python
@tool
def fetch_data(source: str) -> str:
    return "data..."

@tool
def analyze_data(data: str) -> str:
    return "analysis..."

@tool
def create_visualization(analysis: str) -> str:
    return "chart..."

async for chunk in shadai.agent(
    prompt="Fetch sales data, analyze it, and create a chart",
    tools=[fetch_data, analyze_data, create_visualization]
):
    print(chunk, end="")
# Agent executes: fetch → analyze → visualize
```

### 4. Result Synthesis

Agent combines tool outputs into coherent response:

```python
# Multiple tool results automatically synthesized
async for chunk in shadai.agent(
    prompt="Compare Q3 and Q4 revenue",
    tools=[get_q3_revenue, get_q4_revenue, calculate_growth]
):
    print(chunk, end="")
# Agent: "Q3 revenue was $1.2M, Q4 was $1.5M, showing 25% growth..."
```

## Real-World Examples

### Example 1: Customer Support

```python
@tool
def search_tickets(customer_id: str, status: str = "open") -> str:
    """Search support tickets for a customer."""
    return "Ticket #123: Login issue..."

@tool
def get_customer_info(customer_id: str) -> str:
    """Get customer account information."""
    return "Premium plan, joined 2023..."

@tool
def send_response(ticket_id: str, message: str) -> str:
    """Send response to support ticket."""
    return "Response sent"

async for chunk in shadai.agent(
    prompt="Check customer C123's open tickets and respond with account info",
    tools=[search_tickets, get_customer_info, send_response]
):
    print(chunk, end="")
```

### Example 2: Market Research

```python
@tool
def get_competitor_data(company: str) -> str:
    """Fetch competitor information."""
    return "Revenue: $5M, Growth: 20%..."

@tool
def get_market_trends(industry: str) -> str:
    """Get industry market trends."""
    return "AI market growing 40% YoY..."

@tool
def generate_report(data: str, format: str = "markdown") -> str:
    """Generate formatted report."""
    return "# Market Analysis\n..."

async for chunk in shadai.agent(
    prompt="Analyze top 3 AI competitors and create markdown report",
    tools=[get_competitor_data, get_market_trends, generate_report]
):
    print(chunk, end="")
```

### Example 3: Data Pipeline

```python
@tool
def extract_from_api(endpoint: str) -> str:
    """Extract data from API."""
    return "raw data..."

@tool
def transform_data(data: str, format: str) -> str:
    """Transform data to specified format."""
    return "transformed data..."

@tool
def load_to_database(data: str, table: str) -> str:
    """Load data into database table."""
    return "Data loaded successfully"

async for chunk in shadai.agent(
    prompt="Extract from /api/sales, transform to JSON, load to sales_table",
    tools=[extract_from_api, transform_data, load_to_database]
):
    print(chunk, end="")
```

## Advanced Patterns

### Pattern 1: Conditional Execution

```python
@tool
def check_inventory(product: str) -> str:
    """Check if product is in stock."""
    return "In stock: 5 units"

@tool
def order_from_supplier(product: str, quantity: int) -> str:
    """Order product from supplier."""
    return "Order placed"

@tool
def notify_customer(product: str, status: str) -> str:
    """Notify customer about order."""
    return "Customer notified"

# Agent decides: if in stock → notify, else → order then notify
async for chunk in shadai.agent(
    prompt="Check product X inventory. If low, order 100 units. Notify customer",
    tools=[check_inventory, order_from_supplier, notify_customer]
):
    print(chunk, end="")
```

### Pattern 2: Error Handling in Tools

```python
@tool
def fetch_user_data(user_id: str) -> str:
    """Fetch user data from database."""
    try:
        # Your implementation
        return "User data..."
    except Exception as e:
        return f"Error: {str(e)}"  # Agent handles gracefully
```

### Pattern 3: Async Tools

```python
import asyncio

@tool
async def async_api_call(endpoint: str) -> str:
    """Make asynchronous API call."""
    await asyncio.sleep(1)  # Simulated async operation
    return "API response..."

# Works seamlessly with agent
async for chunk in shadai.agent(
    prompt="Call /api/data endpoint",
    tools=[async_api_call]
):
    print(chunk, end="")
```

## Limitations

### 1. Tool Complexity

**Works Well:**
```python
@tool
def simple_calculation(a: int, b: int) -> str:
    return str(a + b)
```

**Challenging:**
```python
@tool
def complex_ml_pipeline(data, params, configs, ...):
    # Too many parameters, too complex
    pass
```

**Solution**: Break into smaller tools

### 2. Ambiguous Prompts

**Clear:**
```
"Search users with revenue > $50k, limit 10, email results to boss@company.com"
```

**Ambiguous:**
```
"Do something with users"
```

**Solution**: Be specific in prompts

### 3. Tool Count

**Optimal**: 3-10 tools

**Too Many**: 50+ tools (agent gets confused)

**Solution**: Group related functionality, provide clear descriptions

## Debugging Agents

### Check Tool Execution

```python
@tool
def debug_tool(param: str) -> str:
    print(f"Tool called with: {param}")  # Debug output
    return "result"

async for chunk in shadai.agent(
    prompt="test",
    tools=[debug_tool]
):
    print(chunk, end="")
```

### Validate Tool Descriptions

Make sure docstrings are clear:

```python
@tool
def ambiguous_tool(x):  # ❌ What does x mean?
    pass

@tool
def clear_tool(customer_id: str):  # ✅ Clear parameter
    """Fetch customer by ID."""
    pass
```

## Best Practices

### ✅ Do This

```python
# Clear tool names
@tool
def search_customers_by_email(email: str) -> str:
    """Find customer by email address."""
    pass

# Detailed docstrings
@tool
def calculate_discount(amount: float, percent: float) -> str:
    """Calculate discount amount.

    Args:
        amount: Original price in dollars
        percent: Discount percentage (0-100)

    Returns:
        Discounted price as formatted string
    """
    pass

# Type hints
@tool
def process_order(order_id: str, priority: int = 1) -> str:
    pass

# Return strings
@tool
def get_status() -> str:
    return "Status: Active"
```

### ❌ Don't Do This

```python
# Vague names
@tool
def do_thing(x):  # What thing?
    pass

# No docstrings
@tool
def process(data):  # How does it process?
    pass

# No type hints
@tool
def calc(a, b):  # Types?
    pass

# Return objects
@tool
def fetch() -> dict:  # Should return str
    return {"data": "value"}
```

## Next Steps

- [Custom Tools Deep Dive](../advanced/custom-tools.md)
- [Tool Orchestration](../advanced/tool-orchestration.md)
- [Custom Agent Examples](../examples/custom-agent.md)

---

**Key Takeaway**: Agents automate complex workflows. Design clear tools, write specific prompts, let the agent orchestrate!
