# Research Assistant

Build an AI research assistant that analyzes documents, synthesizes findings, and stays current with latest developments.

## Overview

Perfect for:
- Academic research
- Market analysis
- Competitive intelligence
- Literature reviews
- Trend analysis

## Basic Research Workflow

```python
async def research_workflow(topic: str, docs_folder: str):
    async with Shadai(name=f"research-{topic}") as shadai:
        # 1. Ingest research materials
        await shadai.ingest(folder_path=docs_folder)

        # 2. Get overview
        print("📚 Document Overview:")
        async for chunk in shadai.summarize():
            print(chunk, end="")

        # 3. Deep analysis
        print("\n\n🔍 Key Findings:")
        async for chunk in shadai.query(
            "What are the key findings and methodologies?"
        ):
            print(chunk, end="")

        # 4. Current context
        print("\n\n🌐 Recent Developments:")
        async for chunk in shadai.engine(
            prompt=f"How do these findings compare to latest {topic} research?",
            use_knowledge_base=True,
            use_web_search=True
        ):
            print(chunk, end="")
```

## Advanced Implementation

```python
from dataclasses import dataclass
from typing import List

@dataclass
class ResearchQuery:
    question: str
    category: str

class ResearchAssistant:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.session_name = f"research-{project_name}"

    async def analyze_literature(self, papers_folder: str) -> dict:
        """Comprehensive literature analysis."""
        async with Shadai(name=self.session_name) as shadai:
            # Ingest papers
            results = await shadai.ingest(folder_path=papers_folder)

            # Systematic queries
            queries = [
                ResearchQuery("What are the main research questions?", "questions"),
                ResearchQuery("What methodologies were used?", "methods"),
                ResearchQuery("What are the key findings?", "findings"),
                ResearchQuery("What are the limitations?", "limitations"),
                ResearchQuery("What future research is suggested?", "future")
            ]

            analysis = {}
            for q in queries:
                response = ""
                async for chunk in shadai.query(q.question):
                    response += chunk
                analysis[q.category] = response

            return analysis

    async def compare_with_current(self, topic: str) -> str:
        """Compare findings with current research."""
        async with Shadai(name=self.session_name) as shadai:
            response = ""
            async for chunk in shadai.engine(
                prompt=f"Compare documented findings with latest {topic} research",
                use_knowledge_base=True,
                use_web_search=True
            ):
                response += chunk
            return response

# Usage
async def main():
    assistant = ResearchAssistant(project_name="ai-ethics")
    analysis = await assistant.analyze_literature("./papers")

    for category, findings in analysis.items():
        print(f"\n## {category.upper()}\n{findings}\n")
```

## Next Steps

- [Knowledge Synthesis](knowledge-synthesis.md)
- [Custom Workflows](custom-workflows.md)
