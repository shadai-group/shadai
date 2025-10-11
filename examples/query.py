"""
Query Example
-------------
Demonstrates how to query the knowledge base using RAG.
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai import Shadai
from shadai.timing import timed


@timed
async def main() -> None:
    print("=" * 70)
    print("QUERY EXAMPLE: Knowledge Base RAG Query")
    print("=" * 70)
    print()

    query = "De qué habla la quinta enmienda?"

    print(f"Query: {query}")
    print("-" * 70)
    print()

    async with Shadai(name="test 6") as shadai:
        async for chunk in shadai.query(query=query):
            print(chunk, end="", flush=True)

    print("\n\n")


if __name__ == "__main__":
    asyncio.run(main())
