import asyncio
import os
from typing import Dict

from shadai.core.agents import ToolAgent
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
    async with Session(type="standard", delete_session=True) as session:
        await session.ingest(input_dir=input_dir)

        await session.query(
            query="¿De qué habla la quinta enmienda?", display_in_console=True
        )

        await session.summarize(display_in_console=True)

        await session.create_article(
            topic="Enmiendas de la constitución y su impacto social",
            display_in_console=True,
        )

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
