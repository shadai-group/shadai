import asyncio
import os

from intelligence.core.session import Session

input_dir = os.path.join(os.path.dirname(__file__), "data")

async def main():
    async with Session(type="standard", delete_session=True) as session:
        await session.ingest(input_dir=input_dir)
        await session.query(query="¿De qué habla la quinta enmienda?", display_in_console=True)

if __name__ == "__main__":
    asyncio.run(main())
