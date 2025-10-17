# Market Research Examples

Use Shadai for comprehensive market research.

## Example: Competitive Analysis

```python
async def competitive_analysis():
    async with Shadai(name="competitive") as shadai:
        # Internal docs
        await shadai.ingest(folder_path="./internal-analysis")

        # Compare with market
        async for chunk in shadai.engine(
            prompt="How do our products compare to top 3 competitors?",
            use_knowledge_base=True,
            use_web_search=True
        ):
            print(chunk, end="")
```

## Example: Trend Analysis

```python
async def trend_analysis(industry: str):
    async with Shadai(name="trends") as shadai:
        await shadai.ingest(folder_path="./industry-reports")

        async for chunk in shadai.engine(
            prompt=f"What are the emerging trends in {industry}?",
            use_summary=True,
            use_web_search=True
        ):
            print(chunk, end="")
```

## See Also
- [Research Assistant](../use-cases/research-assistant.md)
