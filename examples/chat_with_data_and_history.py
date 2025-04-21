import asyncio
import os
import sys

# Add the parent directory to sys.path to access the shadai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")


async def main():
    async with Session(type="standard", delete=True) as session:
        await session.ingest(input_dir=input_dir)
        await session.chat(
            message="¿Qué dice la constitución sobre la libertad de expresión?",
            system_prompt="Eres un experto en derecho constitucional y tienes acceso a la constitución.",
            use_history=True,
            display_in_console=True,
        )
        # This is optional to run, it cleans up the chat history
        await session.cleanup_chat()


if __name__ == "__main__":
    asyncio.run(main())
