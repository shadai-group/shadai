"""
Web Search Example
------------------
Demonstrates how to search the web for current information.
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
    print("WEB SEARCH EXAMPLE: Real-time Web Search")
    print("=" * 70)
    print()

    prompt = "Cuanto quedó el partido del Bayern Munchen esta semana contra Frankfurt?"

    print(f"Prompt: {prompt}")
    print("-" * 70)
    print()

    async with Shadai(name="test 6") as shadai:
        async for chunk in shadai.web_search(prompt=prompt, use_web_search=True):
            print(chunk, end="", flush=True)

    print("\n\n")


if __name__ == "__main__":
    asyncio.run(main())
