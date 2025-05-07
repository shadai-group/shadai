import asyncio
import os
import sys

# Add the parent directory to sys.path to access the shadai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai.core.enums import AIModels
from shadai.core.session import Session

media_dir = os.path.join(os.path.dirname(__file__), "media")


async def call_llm_with_media():
    """
    This function calls the LLM with the media.
    """
    async with Session(
        llm_model=AIModels.GEMINI_2_0_FLASH,
        type="standard",
        delete=True,
    ) as session:
        await session.llm_call(
            prompt="""
            Dame toda la información que puedas obtener de estos archivos multimedia
            en detalle y por separado para cada tipo de archivo.
            """,
            media_path=media_dir,
            display_prompt=True,
            display_in_console=True,
        )


async def call_llm_without_media():
    """
    This function calls the LLM without media.
    """
    async with Session(
        llm_model=AIModels.GEMINI_2_0_FLASH, type="standard", delete=True
    ) as session:
        await session.llm_call(
            prompt="¿Cual es el estado con la mayor economía en los Estados Unidos?",
            display_prompt=True,
            display_in_console=True,
        )


if __name__ == "__main__":
    asyncio.run(call_llm_with_media())
    asyncio.run(call_llm_without_media())
