import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai import Shadai
from shadai.timing import timed


@timed
async def main() -> None:
    input_dir = os.path.join(os.path.dirname(__file__), "data")

    async with Shadai(name="test 6") as shadai:
        await shadai.ingest(folder_path=input_dir)

        async for chunk in shadai.query(query="De qué habla la quinta enmienda?"):
            print(chunk, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
