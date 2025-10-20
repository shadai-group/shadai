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

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai import Shadai
from shadai.timing import timed


@timed
async def example_direct_summary() -> None:
    """Ejemplo 1: Obtener resumen directo (comportamiento por defecto)."""
    print("\n=== MODO 1: RESUMEN DIRECTO ===\n")

    async with Shadai(name="test") as shadai:
        async for chunk in shadai.summarize():
            print(chunk, end="", flush=True)
        print("\n")


@timed
async def example_question_answering() -> None:
    """Ejemplo 2: Hacer preguntas sobre el resumen."""
    print("\n=== MODO 2: PREGUNTAS Y RESPUESTAS ===\n")

    async with Shadai(name="test") as shadai:
        # Primera pregunta
        print("Pregunta: ¿Cuáles son los temas principales?\n")
        async for chunk in shadai.summarize(
            prompt="¿Cuáles son los temas principales discutidos en los documentos?",
            return_direct=False,
            use_memory=True,
        ):
            print(chunk, end="", flush=True)
        print("\n\n")

        # Segunda pregunta (con memoria de conversación)
        print("Pregunta de seguimiento: ¿Puedes profundizar en el primer tema?\n")
        async for chunk in shadai.summarize(
            prompt="¿Puedes profundizar más en el primer tema que mencionaste?",
            return_direct=False,
            use_memory=True,  # Mantiene el contexto de la pregunta anterior
        ):
            print(chunk, end="", flush=True)
        print("\n")


async def main() -> None:
    """Ejecuta todos los ejemplos."""
    # Ejemplo 1: Resumen directo
    await example_direct_summary()

    # Ejemplo 2: Preguntas y respuestas
    await example_question_answering()


if __name__ == "__main__":
    asyncio.run(main())
