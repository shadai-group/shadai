# Multi-Document Analysis

Examples for analyzing multiple documents together.

## Example: Comparative Analysis

```python
async def compare_contracts():
    async with Shadai(name="comparison") as shadai:
        # Ingest multiple contracts
        await shadai.ingest(folder_path="./contracts")

        # Comparative queries
        queries = [
            "What are the common terms across all contracts?",
            "What are the key differences?",
            "Which contract has the most favorable terms?"
        ]

        for q in queries:
            print(f"\n## {q}\n")
            async for chunk in shadai.query(q):
                print(chunk, end="")
```

## Example: Synthesis Report

```python
async def generate_synthesis():
    async with Shadai(name="synthesis") as shadai:
        await shadai.ingest(folder_path="./research-papers")

        # Get overview
        print("# Executive Summary\n")
        async for chunk in shadai.summarize():
            print(chunk, end="")

        # Key findings
        print("\n\n# Key Findings\n")
        async for chunk in shadai.query("What are the main conclusions?"):
            print(chunk, end="")
```

## See Also
- [Knowledge Synthesis](../use-cases/knowledge-synthesis.md)
