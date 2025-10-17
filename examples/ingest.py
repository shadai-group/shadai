"""
Ejemplo de Ingesta
------------------
Demuestra cómo ingerir archivos de una carpeta en una sesión RAG.
Procesa recursivamente todos los archivos PDF e imágenes (hasta 35MB cada uno).
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai import Shadai
from shadai.timing import timed


@timed
async def main() -> None:
    input_dir = os.path.join(os.path.dirname(__file__), "data")

    async with Shadai(name="test_client") as shadai:
        results = await shadai.ingest(folder_path=input_dir)


if __name__ == "__main__":
    asyncio.run(main())
