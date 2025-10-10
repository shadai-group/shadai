import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai import Shadai
from shadai.timing import timed


@timed
async def main() -> None:
    # Engine combines multiple capabilities for comprehensive answers
    prompt = """
    Based on the documents in this session:
    1. What are the main topics covered?
    2. How do they relate to current industry trends and recent developments?
    3. Are there any contradictions between the document content and latest information?

    Provide a comprehensive analysis combining document insights with current information.
    """

    async with Shadai(name="test 6") as shadai:
        async for chunk in shadai.engine(
            prompt=prompt,
            use_knowledge_base=True,  # Query specific content from documents
            use_summary=True,  # Get overview of all documents
            use_web_search=True,  # Get latest trends and information
            use_memory=False,  # Use memory to store and retrieve information
        ):
            print(chunk, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
