"""
Ejemplo del Engine
-----------------
Demuestra el Engine de Shadai que orquesta múltiples capacidades RAG (Opcionales):
- Base de Conocimiento: Consulta contenido específico de documentos (Opcional)
- Búsqueda Web: Obtiene últimas tendencias e información (Opcional)
- Memoria: Almacena y recupera contexto de conversación (siempre habilitada)

Nota: La memoria (use_memory) está siempre habilitada internamente para garantizar contexto de conversación.
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai import EmbeddingModel, LanguageCode, LLMModel, Shadai
from shadai.timing import timed


@timed
async def main() -> None:
    prompt = """
    Quiero saber cual es mi estado de salud.
    """

    system_prompt = """
    Actua como un Medico.
    Proporciona un análisis integral sobre la salud del paciente.
    """

    async with Shadai(
        name="new-session",
        llm_model=LLMModel.GOOGLE_GEMINI_2_5_PRO,
        embedding_model=EmbeddingModel.GOOGLE_GEMINI_EMBEDDING_001,
        system_prompt=None,
    ) as shadai:
        async for chunk in shadai.engine(
            prompt=prompt,
            use_knowledge_base=True,
            use_web_search=False,
            system_prompt=system_prompt,
            response_language=LanguageCode.ENGLISH,
        ):
            print(chunk, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    asyncio.run(main())
