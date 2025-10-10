import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai import Session, Shadai
from shadai.timing import timed


@timed
async def main() -> None:
    shadai = Shadai()

    async with Session(name="test 6") as session:
        async for chunk in shadai.summarize(session=session):
            print(chunk, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
