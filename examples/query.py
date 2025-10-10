import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai import Shadai
from shadai.timing import timed


@timed
async def main() -> None:
    query = "De qué habla la quinta enmienda?"

    async with Shadai(name="test 6") as shadai:
        async for chunk in shadai.query(query=query):
            print(chunk, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
