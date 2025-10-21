"""
Ejemplo de Ingesta
------------------
Demuestra cómo ingerir archivos de una carpeta en una sesión RAG.
Procesa recursivamente todos los archivos PDF e imágenes (hasta 35MB cada uno).
"""

import asyncio
import os
import sys

from shadai import EmbeddingModel, LLMModel, Shadai

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai.timing import timed


@timed
async def main() -> None:
    input_dir = os.path.join(os.path.dirname(__file__), "data")

    async with Shadai(
        name="test",
        llm_model=LLMModel.GOOGLE_GEMINI_2_0_FLASH,
        embedding_model=EmbeddingModel.GOOGLE_GEMINI_EMBEDDING_001,
    ) as shadai:
        await shadai.ingest(folder_path=input_dir)


if __name__ == "__main__":
    asyncio.run(main())
