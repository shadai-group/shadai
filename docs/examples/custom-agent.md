# Custom Agent Examples

Build intelligent agents with custom tools.

## Example: Business Intelligence Agent

```python
from shadai import Shadai, tool

@tool
def get_sales_data(period: str) -> str:
    """Fetch sales data for period."""
    return "Q4 Sales: $1.5M, Growth: 25%"

@tool
def get_customer_metrics(metric: str) -> str:
    """Get customer metrics."""
    return "Churn: 5%, Satisfaction: 85%"

@tool
def generate_executive_summary(data: str) -> str:
    """Generate executive summary."""
    return f"Summary: {data}"

async def main():
    async with Shadai(name="bi-agent") as shadai:
        async for chunk in shadai.agent(
            prompt="Analyze Q4 performance and generate executive summary",
            tools=[get_sales_data, get_customer_metrics, generate_executive_summary]
        ):
            print(chunk, end="")
```

## Example: Automation Agent

```python
@tool
def check_system_status(system: str) -> str:
    """Check if system is running."""
    return f"{system}: Running"

@tool
def send_alert(message: str, urgency: str = "normal") -> str:
    """Send alert notification."""
    return f"Alert sent: {message}"

async def monitoring_agent():
    async with Shadai(name="monitor") as shadai:
        async for chunk in shadai.agent(
            prompt="Check all systems and alert if any issues",
            tools=[check_system_status, send_alert]
        ):
            print(chunk, end="")
```

## See Also
- [Intelligent Agent](../core-concepts/intelligent-agent.md)
- [Custom Tools](../advanced/custom-tools.md)
