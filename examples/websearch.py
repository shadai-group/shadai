import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai import Shadai
from shadai.timing import timed


@timed
async def main() -> None:
    prompt = "Cuanto quedó el partido del Bayern Munchen esta semana contra Frankfurt?"

    async with Shadai(name="test 6") as shadai:
        async for chunk in shadai.web_search(prompt=prompt, use_web_search=True):
            print(chunk, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
