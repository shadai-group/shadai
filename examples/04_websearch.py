"""
Ejemplo de Búsqueda Web
------------------------
Demuestra cómo buscar en la web información actual.
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai import EmbeddingModel, LLMModel, Shadai
from shadai.timing import timed


@timed
async def main() -> None:
    prompt = "Cuánto quedó el partido del Bayern Múnich la última vez contra Frankfurt?"

    system_prompt = """
    Actua como un analista de deportivo.
    """

    async with Shadai(
        name="test_websearch",
        llm_model=LLMModel.GOOGLE_GEMINI_2_0_FLASH,
        embedding_model=EmbeddingModel.GOOGLE_GEMINI_EMBEDDING_001,
        system_prompt=system_prompt,
        temporal=True,
    ) as shadai:
        async for chunk in shadai.web_search(prompt=prompt, use_memory=False):
            print(chunk, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    asyncio.run(main())
