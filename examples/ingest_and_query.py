"""
Ingest and Query Example
------------------------
Demonstrates the complete workflow:
1. Ingest files from a folder
2. Query the ingested knowledge base
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadai import Shadai
from shadai.timing import timed


@timed
async def main() -> None:
    print("=" * 70)
    print("INGEST AND QUERY EXAMPLE: Complete Workflow")
    print("=" * 70)
    print()

    input_dir = os.path.join(os.path.dirname(__file__), "data")

    async with Shadai(name="test 7") as shadai:
        # Step 1: Ingest files
        print("STEP 1: Ingesting files")
        print("-" * 70)
        print(f"Folder: {input_dir}")
        print()

        results = await shadai.ingest(folder_path=input_dir)

        print(f"✓ Ingested {results['successful_count']} files")
        print()

        #TODO: this takes a couple of minutes to process we need to handle it

        # Step 2: Query the knowledge base
        print("STEP 2: Querying knowledge base")
        print("-" * 70)

        query = "De qué habla la quinta enmienda?"
        print(f"Query: {query}")
        print()

        async for chunk in shadai.query(query=query):
            print(chunk, end="", flush=True)

    print("\n\n")


if __name__ == "__main__":
    asyncio.run(main())
