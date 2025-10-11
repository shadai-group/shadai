"""
Ingest Example
--------------
Demonstrates how to ingest files from a folder into a RAG session.
Recursively processes all PDF and image files (up to 35MB each).
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
    print("INGEST EXAMPLE: Folder Ingestion")
    print("=" * 70)
    print()

    input_dir = os.path.join(os.path.dirname(__file__), "data")

    print(f"Ingesting files from: {input_dir}")
    print("Supported formats: PDF, JPG, JPEG, PNG, WEBP")
    print("Maximum file size: 35 MB")
    print("-" * 70)
    print()

    async with Shadai(name="test 6") as shadai:
        results = await shadai.ingest(folder_path=input_dir)

        print()
        print("=" * 70)
        print("INGESTION RESULTS")
        print("=" * 70)
        print(f"Total files: {results['total_files']}")
        print(f"✓ Successful: {results['successful_count']}")
        print(f"✗ Failed: {results['failed_count']}")
        print(f"⊘ Skipped (>35MB): {results['skipped_count']}")
        print()

        if results["successful"]:
            print("Successfully ingested files:")
            for file_info in results["successful"]:
                size_mb = int(file_info["size"]) / (1024 * 1024)
                print(f"  • {file_info['filename']} ({size_mb:.2f} MB)")

        if results["failed"]:
            print("\nFailed files:")
            for file_info in results["failed"]:
                print(f"  • {file_info['filename']}: {file_info['error']}")

        if results["skipped"]:
            print("\nSkipped files (>35MB):")
            for file_info in results["skipped"]:
                print(f"  • {file_info['filename']}: {file_info['size_mb']}")

    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
