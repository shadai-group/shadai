import asyncio
import os
import sys

# Add the parent directory to sys.path to access the shadai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai.core.enums import AIModels
from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")


async def create_article():
    async with Session(
        llm_model=AIModels.GEMINI_2_0_FLASH, type="standard", delete=True
    ) as session:
        await session.ingest(input_dir=input_dir)
        await session.article(
            topic="Análisis de las enmiendas de la constitución y su impacto social",
            display_in_console=True,
        )


if __name__ == "__main__":
    asyncio.run(create_article())
