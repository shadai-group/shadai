"""
Ejemplo de Resumen
-------------------
Demuestra cómo resumir todos los documentos en una sesión y hacer preguntas sobre el resumen.

Modos disponibles:
1. Resumen directo: Retorna el resumen consolidado
2. Preguntas y respuestas: Usa el resumen para responder preguntas específicas
"""

import asyncio
import os
import sys

from shadai.models import EmbeddingModel, LLMModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai import Shadai
from shadai.timing import timed


@timed
async def example_direct_summary() -> None:
    """Ejemplo 1: Obtener resumen directo (comportamiento por defecto)."""

    system_prompt = """
    Actua como un experto en el area de leyes y creatividad digital.
    """

    async with Shadai(
        name="test",
        llm_model=LLMModel.GOOGLE_GEMINI_2_0_FLASH,
        embedding_model=EmbeddingModel.GOOGLE_GEMINI_EMBEDDING_001,
        system_prompt=system_prompt,
    ) as shadai:
        async for chunk in shadai.summarize():
            print(chunk, end="", flush=True)
        print("\n")


@timed
async def example_question_answering() -> None:
    """Ejemplo 2: Hacer preguntas sobre el resumen."""

    system_prompt = """
    Actua como un experto en el area de leyes y creatividad digital.
    """

    async with Shadai(
        name="test",
        llm_model=LLMModel.GOOGLE_GEMINI_2_0_FLASH,
        embedding_model=EmbeddingModel.GOOGLE_GEMINI_EMBEDDING_001,
        system_prompt=system_prompt,
    ) as shadai:
        async for chunk in shadai.summarize(
            prompt="¿Cuáles son los temas principales discutidos en los documentos?",
            return_direct=False,
            use_memory=False,
        ):
            print(chunk, end="", flush=True)
        print("\n\n")

        async for chunk in shadai.summarize(
            prompt="¿Puedes profundizar más en el primer tema que mencionaste?",
            return_direct=False,
            use_memory=False,
        ):
            print(chunk, end="", flush=True)
        print("\n")


async def main() -> None:
    """Ejecuta todos los ejemplos."""
    await example_direct_summary()

    await example_question_answering()


if __name__ == "__main__":
    asyncio.run(main())
