# Basic Query Examples

Simple, practical examples for querying documents.

## Example 1: Single Question

```python
import asyncio
from shadai import Shadai

async def main():
    async with Shadai(name="simple") as shadai:
        await shadai.ingest(folder_path="./documents")

        async for chunk in shadai.query("What is the refund policy?"):
            print(chunk, end="")

asyncio.run(main())
```

## Example 2: Multiple Questions

```python
async def main():
    questions = [
        "What are the payment terms?",
        "What is the delivery timeframe?",
        "Are there any warranties?"
    ]

    async with Shadai(name="multiple") as shadai:
        await shadai.ingest(folder_path="./contracts")

        for q in questions:
            print(f"\nQ: {q}")
            print("A: ", end="")
            async for chunk in shadai.query(q):
                print(chunk, end="")
            print("\n")

asyncio.run(main())
```

## Example 3: Interactive Q&A

```python
async def main():
    async with Shadai(name="interactive") as shadai:
        await shadai.ingest(folder_path="./docs")
        print("Ready! Ask questions (type 'quit' to exit)\n")

        while True:
            question = input("You: ").strip()
            if question.lower() in ['quit', 'exit']:
                break

            print("AI: ", end="")
            async for chunk in shadai.query(question):
                print(chunk, end="")
            print("\n")

asyncio.run(main())
```

## See Also
- [Document Q&A Use Case](../use-cases/document-qa.md)
- [Query Tool API](../api-reference/query-tool.md)
