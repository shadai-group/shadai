import asyncio
import os
import sys

# Agregar el directorio padre a sys.path para acceder al paquete shadai
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai.core.agents import Agent
from shadai.core.enums import AIModels
from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")


def add(a: float, b: float) -> float:
    """Suma dos números.

    Args:
        a (float): El primer número
        b (float): El segundo número

    Returns:
        float: La suma de los dos números
    """
    return a + b


def multiply(a: float, b: float) -> float:
    """Multiplica dos números.

    Args:
        a (float): El primer número
        b (float): El segundo número

    Returns:
        float: El producto de los dos números
    """
    return a * b


def web_search(query: str) -> str:
    """Busca información en la web (dummy implementation).

    Args:
        query (str): La consulta para buscar en la web

    Returns:
        str: El resultado de la búsqueda web
    """
    return (
        "Aquí están los recuentos de empleados para cada una de las empresas FAANG en 2024:\n"
        "1. **Facebook (Meta)**: 67,317 empleados.\n"
        "2. **Apple**: 164,000 empleados.\n"
        "3. **Amazon**: 1,551,000 empleados.\n"
        "4. **Netflix**: 14,000 empleados.\n"
        "5. **Google (Alphabet)**: 181,269 empleados."
    )


async def call_calculator_agent():
    async with Session(
        llm_model=AIModels.GEMINI_2_0_FLASH,
        type="standard",
        delete=True,
    ) as session:
        await session.ingest(input_dir=input_dir)
        agent = Agent(
            name="Calculadora",
            description="Una calculadora simple que puede sumar y multiplicar dos números",
            agent_prompt="""
            Eres una calculadora simple que puede sumar y multiplicar dos números.
            Realiza los cálculos utilizando herramientas y devuelve el resultado de manera amigable.
            """,
            session=session,
            use_history=True,
        )
        await agent.add_tools(tools=[add, multiply])

        # Uso de ambas herramientas
        await agent.run(input="¿Puedes calcular 2 + 2 * (2 + 2)?")


async def call_web_search_agent():
    async with Session(
        llm_model=AIModels.GEMINI_2_0_FLASH,
        type="standard",
        delete=True,
    ) as session:
        await session.ingest(input_dir=input_dir)
        agent = Agent(
            name="experto_investigador",
            description="Un agente que puede buscar información en la web y resolver problemas matemáticos sencillos.",
            agent_prompt="""
            Eres un investigador experto con acceso a búsqueda web y una calculadora simple.
            """,
            session=session,
            use_history=True,
        )
        await agent.add_tools(tools=[add, multiply, web_search])

        await agent.run(
            # Esto debería activar las herramientas de suma y multiplicación
            input="¿Puedes calcular 6 * (2 + 2 * 8)?"  # Resultado esperado: 108
        )

        await agent.run(
            # Esto debería activar la herramienta de búsqueda web
            input="¿Cuál es el número total de empleados de las empresas FAANG en 2024?"
        )


if __name__ == "__main__":
    asyncio.run(call_calculator_agent())
    asyncio.run(call_web_search_agent())
