"""
Ejemplo de Búsqueda Web
------------------------
Demuestra cómo buscar en la web información actual.
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai import Shadai
from shadai.timing import timed


@timed
async def main() -> None:
    prompt = "Cuánto quedó el partido del Bayern Múnich esta semana contra Frankfurt?"

    async with Shadai(name="test") as shadai:
        async for chunk in shadai.web_search(prompt=prompt, use_web_search=True):
            print(chunk, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
