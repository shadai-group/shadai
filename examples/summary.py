"""
Ejemplo de Resumen
-------------------
Demuestra cómo resumir todos los documentos en una sesión.
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai import Shadai
from shadai.timing import timed


@timed
async def main() -> None:
    async with Shadai(name="test") as shadai:
        async for chunk in shadai.summarize():
            print(chunk, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
