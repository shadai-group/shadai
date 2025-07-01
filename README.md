# SHADAI Intelligence Client

A Python client for interacting with the SHADAI API. This client provides a simple interface for document processing, querying, and session management.

## Installation

```bash
pip install shadai
```

## Requirements

- Python >= 3.9
- Environment Variables:
  - `SHADAI_API_KEY`: Your SHADAI API key

## Features

- Asynchronous API interactions
- Automatic session management
- File ingestion with progress tracking
- Interactive query interface
- Robust error handling and retries
- Rich console output

## Getting Started with SHADAI

SHADAI Intelligence Client is a powerful tool for document processing, querying, and AI-assisted analysis. This guide will walk you through various use cases and show you how to leverage the full capabilities of the platform.

### Session Configuration

When working with SHADAI, you'll always start by creating a Session. Here are the configuration options available:

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| type | str | Processing type ("light", "standard", "deep") | "standard" |
| llm_model | str | Language model to use | AIModels.GEMINI_2_0_FLASH |
| llm_temperature | float | Model temperature | 0.7 |
| llm_max_tokens | int | Maximum tokens for response | 4096 |
| query_mode | str | Query processing mode | hybrid |
| language | str | Response language | es |
| delete | bool | Auto-delete session on exit | True |

## Working with Documents

### Ingesting Documents

The first step in most SHADAI workflows is ingesting documents. SHADAI can process various document formats and extract relevant information.

```python
# examples/ingest_data.py
import asyncio
import os
import sys

# Add the parent directory to sys.path to access the shadai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai.core.enums import AIModels
from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")


async def ingest_with_alias(alias: str) -> None:
    """
    This function ingests a directory of documents into a session with a given alias.
    """
    async with Session(
        llm_model=AIModels.GEMINI_2_0_FLASH, alias=alias, type="standard", delete=True
    ) as session:
        await session.ingest(input_dir=input_dir)


async def ingest_without_alias() -> None:
    """
    This function ingests a directory of documents into a session without a given alias.
    """
    async with Session(
        llm_model=AIModels.GEMINI_2_0_FLASH, type="standard", delete=False
    ) as session:
        await session.ingest(input_dir=input_dir)


async def main():
    await ingest_with_alias(alias="my_alias")
    await ingest_without_alias()


if __name__ == "__main__":
    asyncio.run(main())
```

### Managing Sessions

SHADAI provides tools for managing your sessions, including creating, listing, retrieving, and deleting them.

```python
# examples/handle_sessions.py
import asyncio
import os
import sys
from typing import List, Optional

# Add the parent directory to sys.path to access the shadai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from shadai.core.enums import AIModels, QueryMode
from shadai.core.manager import Manager
from shadai.core.schemas import SessionResponse
from shadai.core.session import Session


async def create_session(alias: Optional[str] = None) -> Session:
    """
    This function creates a new session with specific parameters.
    You can customize model, temperature, tokens, and query mode.
    If you set delete to False, you need to manually delete the session.

    Returns:
        Session: The session object.
    """
    async with Session(
        alias=alias,
        type="standard",
        llm_model=AIModels.GEMINI_2_0_FLASH,
        llm_temperature=0.7,
        llm_max_tokens=4096,
        query_mode=QueryMode.HYBRID,
        delete=False,
    ) as session:
        return session


async def get_existing_session_with_session_id(session_id: str) -> Session:
    """
    This function gets a session by its ID.

    Args:
        session_id (str): The ID of the session to get.

    Returns:
        Session: The session object.
    """
    async with Session(session_id=session_id, type="standard", delete=False) as session:
        return session


async def get_existing_session_with_alias(alias: str) -> Session:
    """
    This function gets a session by its alias.

    Args:
        session_id (str): The ID of the session to get.

    Returns:
        Session: The session object.
    """
    async with Session(alias=alias, type="standard", delete=False) as session:
        return session


async def list_sessions() -> List[SessionResponse]:
    """
    This function lists all the sessions in the current namespace.
    Returns:
        List[SessionResponse]: A list of session responses.
    """
    async with Manager() as manager:
        sessions = await manager.list_sessions(show_in_console=True)
        return sessions


async def cleanup_namespace() -> None:
    """
    This function cleans up the namespace of the current session.
    """
    async with Manager() as manager:
        await manager.cleanup_namespace()


async def delete_session(
    session_id: Optional[str] = None, alias: Optional[str] = None
) -> None:
    """
    This function deletes a session by its ID.

    Args:
        session_id (str): The ID of the session to delete.
    """
    async with Manager() as manager:
        await manager.delete_session(session_id=session_id, alias=alias)


async def main():
    session_created = await create_session(alias="test-session")
    session_id = session_created.id
    session_retrieved = await get_existing_session_with_session_id(
        session_id=session_id
    )
    await delete_session(session_id=session_retrieved.id)
    await list_sessions()
    await cleanup_namespace()


if __name__ == "__main__":
    asyncio.run(main())
```

## Querying and Analysis

### Making a Single Query

The most basic way to interact with your documents is through a single query:

```python
# examples/make_single_query.py
import asyncio
import os
import sys

# Add the parent directory to sys.path to access the shadai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai.core.enums import AIModels
from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")


async def main():
    async with Session(
        llm_model=AIModels.GEMINI_2_0_FLASH,
        type="standard",
        delete=False,
    ) as session:
        await session.ingest(input_dir=input_dir)
        await session.query(
            query="¿De qué habla la quinta enmienda de la constitución?",
            # You decide whether you want to add a role or not. This affects the response.
            role="Eres un abogado experto de harvard",
            display_in_console=True,
        )


if __name__ == "__main__":
    asyncio.run(main())
```

### Making Multiple Queries

For more complex analysis, you might want to ask multiple related questions:

```python
# examples/make_multiple_queries.py
import asyncio
import os
import sys
from typing import List

# Add the parent directory to sys.path to access the shadai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai.core.enums import AIModels
from shadai.core.schemas import Query
from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")

queries: List[Query] = [
    Query(
        query="¿De qué habla la quinta enmienda de la constitución?",
        role="Eres un abogado experto de harvard",
        display_in_console=True,
    ),
    Query(
        query="""
        ¿Cómo se detalla en el Artículo I, Sección 2 el mecanismo de asignación de representantes a
        los estados, y qué implicaciones podría tener la fórmula de prorrateo
        (incluyendo consideraciones como "las tres quintas partes" y la exclusión de indígenas)
        en términos de representación política y distribución de poder?
        """,
        display_in_console=True,
    ),
    Query(
        query="""
        El Artículo I, Sección 3 describe la organización y elección de senadores, incluyendo
        la división en tres clases. ¿Qué ventajas y desventajas podría presentar este sistema
        de renovación escalonada para la estabilidad y la continuidad de la representación estatal?
        """,
        display_in_console=True,
    ),
    Query(
        query="""
        Basándote en el Artículo I, Sección 7, analiza el proceso legislativo que incluye la
        intervención del Presidente. ¿Cómo se equilibra el poder entre el Ejecutivo y
        el Congreso cuando se trata de la aprobación de leyes, y cuáles son las implicaciones
        del proceso de veto con objeciones detalladas?
        """,
        display_in_console=True,
    ),
    Query(
        query="""
        En el Artículo III se define el poder y la jurisdicción de la Corte Suprema.
        ¿Cuáles son las implicaciones de otorgar a la Corte Suprema jurisdicción
        original en casos que involucran a embajadores y estados, y cómo afecta esto
        el equilibrio entre poderes?
        """,
        display_in_console=True,
    ),
    Query(
        query="""
        Con base en el Artículo II, analiza los límites impuestos al Presidente,
        especialmente en lo referente a la designación de funcionarios y la duración
        del mandato, y discute cómo estos límites buscan prevenir abusos de poder.
        """,
        display_in_console=True,
    ),
    Query(
        query="""
        Considerando las Enmiendas I al X (la Carta de Derechos), ¿cómo se aseguran y
        se limitan los poderes gubernamentales en relación con las libertades individuales,
        y qué desafíos se podrían plantear en la aplicación práctica de estos derechos?
        """,
        display_in_console=True,
    ),
    Query(
        query="""
        El Artículo V establece un mecanismo para modificar la Constitución.
        ¿Qué dificultades prácticas y políticas podrían derivarse de la necesidad de ratificar
        en tres cuartas partes de los estados, y cómo podría esto afectar la adaptabilidad de la
        Constitución a cambios sociales?
        """,
        display_in_console=True,
    ),
    Query(
        query="""
        Analiza el Artículo IV en el contexto del principio de "plena fe y crédito".
        ¿Cómo se garantiza la uniformidad en el reconocimiento de leyes y registros judiciales
        entre estados, y qué problemas podría surgir en casos de discrepancias legales
        entre jurisdicciones?
        """,
        display_in_console=True,
    ),
    Query(
        query="""
        En la Sección 10 del Artículo I se imponen restricciones a los estados en términos de política
        exterior, emisión de moneda y tratados con naciones extranjeras.
        ¿Cómo se justifica constitucionalmente esta limitación y qué conflictos podría
        generar en la relación entre el gobierno federal y los estados?
        """,
        display_in_console=True,
    ),
    Query(
        query="""
        Las Enmiendas del XIII al XXVII introducen cambios significativos en temas como la
        abolición de la esclavitud, el sufragio, y la limitación de mandatos presidenciales.
        ¿Cómo refleja esta evolución los cambios sociales y políticos en la historia de los Estados Unidos,
        y de qué manera impactan en la interpretación y aplicación de la Constitución original?
        """,
        display_in_console=True,
    ),
]


async def main():
    async with Session(
        llm_model=AIModels.GEMINI_2_0_FLASH, type="standard", delete=True
    ) as session:
        await session.ingest(input_dir=input_dir)
        await session.multiple_queries(queries=queries)


if __name__ == "__main__":
    asyncio.run(main())
```

### Getting a Session Summary

SHADAI can generate concise summaries of the documents in your session:

```python
# examples/get_session_summary.py
import asyncio
import os
import sys

# Add the parent directory to sys.path to access the shadai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai.core.enums import AIModels
from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")


async def main():
    async with Session(
        llm_model=AIModels.GEMINI_2_0_FLASH,
        type="standard",
        language="es",
        delete=False,
    ) as session:
        await session.ingest(input_dir=input_dir)
        await session.summarize(display_in_console=True)


if __name__ == "__main__":
    asyncio.run(main())
```

### Creating an Article

SHADAI can generate comprehensive articles on topics related to the documents in your session:

```python
# examples/create_article.py
import asyncio
import os
import sys

# Add the parent directory to sys.path to access the shadai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai.core.enums import AIModels
from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")


async def create_article():
    async with Session(
        llm_model=AIModels.GEMINI_2_0_FLASH, type="standard", delete=True
    ) as session:
        await session.ingest(input_dir=input_dir)
        await session.article(
            topic="Análisis de las enmiendas de la constitución y su impacto social",
            display_in_console=True,
        )


if __name__ == "__main__":
    asyncio.run(create_article())
```

## Advanced Interactions

### Simple LLM Completion

Sometimes you just need a direct answer from the language model:

```python
# examples/llm_call.py
import asyncio
import os
import sys

# Add the parent directory to sys.path to access the shadai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai.core.enums import AIModels
from shadai.core.session import Session

media_dir = os.path.join(os.path.dirname(__file__), "media")


async def call_llm_with_media():
    """
    This function calls the LLM with the media.
    """
    async with Session(
        llm_model=AIModels.GEMINI_2_0_FLASH,
        type="standard",
        delete=True,
    ) as session:
        await session.llm_call(
            prompt="""
            Dame toda la información que puedas obtener de estos archivos multimedia
            en detalle y por separado para cada tipo de archivo.
            """,
            media_path=media_dir,
            display_prompt=True,
            display_in_console=True,
        )


async def call_llm_without_media():
    """
    This function calls the LLM without media.
    """
    async with Session(
        llm_model=AIModels.GEMINI_2_0_FLASH, type="standard", delete=True
    ) as session:
        await session.llm_call(
            prompt="¿Cual es el estado con la mayor economía en los Estados Unidos?",
            display_prompt=True,
            display_in_console=True,
        )


if __name__ == "__main__":
    asyncio.run(call_llm_with_media())
    asyncio.run(call_llm_without_media())
```

### Chat with Data and History

For interactive conversations that maintain context:

```python
# examples/chat_with_data_and_history.py
import asyncio
import os
import sys

# Add the parent directory to sys.path to access the shadai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai.core.enums import AIModels
from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")


async def chat_with_data():
    """
    This function chats with the data and history.
    """
    async with Session(
        llm_model=AIModels.GEMINI_2_0_FLASH, type="standard", delete=True
    ) as session:
        await session.ingest(input_dir=input_dir)
        await session.chat(
            message="¿Qué dice la constitución sobre la libertad de expresión?",
            system_prompt="Eres un experto en derecho constitucional y tienes acceso a la constitución.",
            display_in_console=True,
        )
        # This is optional to run, it cleans up the chat history
        await session.cleanup_chat()


async def chat_without_data():
    """
    This function chats only with the history.
    """
    async with Session(
        llm_model=AIModels.GEMINI_2_0_FLASH, type="standard", delete=True
    ) as session:
        await session.chat(
            message="¿Qué dice la constitución sobre la libertad de expresión?",
            system_prompt="Eres un experto en derecho constitucional y tienes acceso a la constitución.",
            display_in_console=True,
        )
        # This is optional to run, it cleans up the chat history
        await session.cleanup_chat()


if __name__ == "__main__":
    asyncio.run(chat_with_data())
    asyncio.run(chat_without_data())
```

### Creating a Smart Agent

For more complex AI-powered workflows, you can create a Smart Agent that can use custom functions as tools:

```python
# examples/create_smart_agent.py
import asyncio
import os
import sys

# Add the parent directory to sys.path to access the shadai package
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
```

### Creating a Naive Agent

For specialized analytical workflows that need contextual knowledge, you can create a Naive Agent that uses a custom function to provide information:

```python
# examples/create_naive_agent.py
import asyncio
import os
import sys
from typing import Dict

# Add the parent directory to sys.path to access the shadai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai.core.agents import ToolAgent
from shadai.core.enums import AIModels
from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")


def get_constitutional_article(article_id: str) -> str:
    articles: Dict[str, Dict[str, str]] = {
        "1": {
            "title": "Primera Enmienda",
            "description": "Libertad de expresión, religión, prensa y reunión",
            "content": "El Congreso no hará ley alguna con respecto al establecimiento de religión, ni prohibiendo la libre práctica de la misma; ni limitando la libertad de expresión, ni de prensa; ni el derecho del pueblo a reunirse pacíficamente.",
        },
        "2": {
            "title": "Segunda Enmienda",
            "description": "Derecho a portar armas",
            "content": "Siendo necesaria una milicia bien ordenada para la seguridad de un Estado libre, no se violará el derecho del pueblo a poseer y portar armas.",
        },
    }

    if article_id not in articles:
        return "Artículo no encontrado"

    article = articles[article_id]
    return f"Título: {article['title']}\nDescripción: {article['description']}\nContenido: {article['content']}"


async def main():
    async with Session(
        llm_model=AIModels.GEMINI_2_0_FLASH, type="standard", language="es", delete=True
    ) as session:
        await session.ingest(input_dir=input_dir)
        agent = ToolAgent(
            session=session,
            prompt="""
                Analiza la relación entre la Primera Enmienda y las empresas digitales:

                Enmienda Constitucional:
                {function_output}

                Contexto de documentos:
                {summary}

                Considerando la Primera Enmienda y el contexto histórico, analiza:
                1. Cómo se aplican los principios de libertad de expresión en el entorno digital
                2. Desafíos y oportunidades para las empresas digitales en relación con estos derechos
                3. Recomendaciones para equilibrar la innovación tecnológica con los derechos constitucionales
            """,
            use_summary=True,
            function=get_constitutional_article,
        )
        await agent.call(article_id="1")


if __name__ == "__main__":
    asyncio.run(main())
```

## Error Handling

The SHADAI client includes comprehensive error handling for:
- Configuration errors
- API communication issues
- File processing problems
- Session management failures

## Author

SHADAI GROUP <jaisir@shadai.ai>
