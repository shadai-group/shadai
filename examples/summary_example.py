import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from shadai import Shadai
from shadai.timing import timed

load_dotenv()


@timed
async def main() -> None:
    shadai = Shadai(api_key=os.getenv("SHADAI_API_KEY"))

    session_uuid = "8d42d113-db82-48d3-943c-1ebef8c401f0"

    async for chunk in shadai.summarize(session_uuid=session_uuid):
        print(chunk, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
