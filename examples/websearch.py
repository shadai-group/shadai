import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai import Session, Shadai
from shadai.timing import timed


@timed
async def main() -> None:
    shadai = Shadai()
    prompt = "Cuanto quedó el partido del Bayern Munchen esta semana contra Frankfurt?"

    async with Session(name="test 6") as session:
        async for chunk in shadai.web_search(
            prompt=prompt,
            session=session,
            use_web_search=True,
        ):
            print(chunk, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
