"""
Ejemplo de Consulta
--------------------
Demuestra cómo consultar la base de conocimiento usando RAG.
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai import EmbeddingModel, LLMModel, Shadai
from shadai.timing import timed


@timed
async def main() -> None:
    query = "De qué habla la quinta enmienda?"

    system_prompt = """
    Actua como un experto en el area de leyes y creatividad digital.
    """

    async with Shadai(
        name="test",
        llm_model=LLMModel.GOOGLE_GEMINI_2_0_FLASH,
        embedding_model=EmbeddingModel.GOOGLE_GEMINI_EMBEDDING_001,
        system_prompt=system_prompt,
    ) as shadai:
        async for chunk in shadai.query(query=query):
            print(chunk, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
