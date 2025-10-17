# Custom Workflows

Build specialized AI workflows tailored to your business needs using Shadai's agent system.

## Overview

Create workflows that:
- Integrate with your systems
- Automate complex processes
- Execute multi-step logic
- Combine multiple data sources

## Example: Sales Intelligence Workflow

```python
from shadai import Shadai, tool

@tool
def get_crm_data(company: str) -> str:
    """Fetch company data from CRM."""
    # Your CRM integration
    return "Company: TechCorp, Industry: SaaS..."

@tool
def get_recent_news(company: str) -> str:
    """Get recent news about company."""
    # News API integration
    return "TechCorp raised $10M Series A..."

@tool
def generate_brief(data: str, format: str = "markdown") -> str:
    """Generate sales brief."""
    return f"# Sales Brief\n\n{data}"

async def sales_intelligence(company: str):
    async with Shadai(name="sales-intel") as shadai:
        async for chunk in shadai.agent(
            prompt=f"Research {company}, analyze their needs, generate sales brief",
            tools=[get_crm_data, get_recent_news, generate_brief]
        ):
            print(chunk, end="")
```

## Example: Compliance Workflow

```python
@tool
def scan_document(doc_path: str) -> str:
    """Scan document for compliance issues."""
    return "Found 3 potential issues..."

@tool
def check_regulations(issue: str, jurisdiction: str) -> str:
    """Check relevant regulations."""
    return "Regulation XYZ applies..."

@tool
def generate_report(findings: str) -> str:
    """Generate compliance report."""
    return f"Compliance Report:\n{findings}"

async def compliance_check(doc_path: str):
    async with Shadai(name="compliance") as shadai:
        async for chunk in shadai.agent(
            prompt=f"Scan {doc_path}, check regulations, generate report",
            tools=[scan_document, check_regulations, generate_report]
        ):
            print(chunk, end="")
```

## Best Practices

- Keep tools focused and simple
- Provide clear tool descriptions
- Use type hints
- Test workflows iteratively
- Handle errors in tools

## Next Steps

- [Custom Tools Guide](../advanced/custom-tools.md)
- [Custom Agent Examples](../examples/custom-agent.md)
