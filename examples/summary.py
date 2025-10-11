"""
Summary Example
---------------
Demonstrates how to summarize all documents in a session.
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
    print("SUMMARY EXAMPLE: Document Summarization")
    print("=" * 70)
    print()
    print("Generating summary of all documents in the session...")
    print("-" * 70)
    print()

    async with Shadai(name="test 6") as shadai:
        async for chunk in shadai.summarize():
            print(chunk, end="", flush=True)

    print("\n\n")


if __name__ == "__main__":
    asyncio.run(main())
