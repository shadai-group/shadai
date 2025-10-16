"""
Ejemplo del Motor
-----------------
Demuestra el Motor de Shadai que orquesta múltiples capacidades RAG:
- Base de Conocimiento: Consulta contenido específico de documentos
- Resumen: Obtiene vista general de todos los documentos
- Búsqueda Web: Obtiene últimas tendencias e información
- Memoria: Almacena y recupera contexto de conversación
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai import Shadai
from shadai.timing import timed


@timed
async def main() -> None:
    prompt = """
    Basándote en los documentos de esta sesión:
    1. ¿Cuáles son los temas principales cubiertos?
    2. ¿Cómo se relacionan con las tendencias actuales de la industria y desarrollos recientes?
    3. ¿Hay alguna contradicción entre el contenido de los documentos y la información más reciente?

    Proporciona un análisis integral combinando conocimientos de los documentos con información actual.
    """

    async with Shadai(name="test") as shadai:
        async for chunk in shadai.engine(
            prompt=prompt,
            use_knowledge_base=True,
            use_summary=True,
            use_web_search=True,
        ):
            print(chunk, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
