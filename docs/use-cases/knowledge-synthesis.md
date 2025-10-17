# Knowledge Synthesis

Combine information from multiple documents to generate comprehensive insights and identify patterns.

## Overview

**Best for:**
- Cross-document analysis
- Pattern identification
- Comprehensive reporting
- Strategic insights

## Implementation

```python
async def synthesize_knowledge(docs_folder: str, synthesis_query: str):
    async with Shadai(name="knowledge-synthesis") as shadai:
        # Ingest all documents
        await shadai.ingest(folder_path=docs_folder)

        # Multi-source synthesis
        async for chunk in shadai.engine(
            prompt=synthesis_query,
            use_knowledge_base=True,
            use_summary=True,
            use_web_search=True
        ):
            print(chunk, end="")
```

## Real-World Example

```python
class KnowledgeSynthesizer:
    async def analyze_market(self, internal_docs: str, competitors: List[str]):
        """Synthesize market intelligence."""
        async with Shadai(name="market-intel") as shadai:
            await shadai.ingest(folder_path=internal_docs)

            synthesis = {}

            # Internal analysis
            response = ""
            async for chunk in shadai.query("What are our strengths and weaknesses?"):
                response += chunk
            synthesis["internal"] = response

            # Competitive landscape
            response = ""
            async for chunk in shadai.engine(
                prompt=f"Analyze competitive landscape: {', '.join(competitors)}",
                use_knowledge_base=True,
                use_web_search=True
            ):
                response += chunk
            synthesis["competitive"] = response

            return synthesis
```

## Best Practices

- Use engine tool for multi-source synthesis
- Enable all relevant capabilities
- Ask broad synthesis questions
- Combine internal + external data

## Next Steps

- [Custom Workflows](custom-workflows.md)
- [Advanced Patterns](../examples/advanced-patterns.md)
