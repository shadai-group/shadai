# File Ingestion

Transform your documents into queryable knowledge with Shadai's intelligent ingestion system.

## Quick Start

```python
async with Shadai(name="docs") as shadai:
    results = await shadai.ingest(folder_path="./documents")
    print(f"✅ Ingested: {results['successful_count']}")
```

## Supported Formats

| Format | Extension | Max Size | Notes |
|--------|-----------|----------|-------|
| **PDF** | `.pdf` | 35 MB | Text extraction + OCR |
| **Images** | `.jpg`, `.jpeg` | 35 MB | OCR with vision models |
| **Images** | `.png`, `.webp` | 35 MB | OCR with vision models |

## How Ingestion Works

```
Your Files → Parse → Chunk → Embed → Vector Store
                ↓        ↓       ↓          ↓
           Extract   Smart    Create    PostgreSQL
            Text     Split  Embeddings   +pgvector
```

### Step 1: Parsing
- Extracts text from PDFs
- OCR for images
- Preserves structure and metadata

### Step 2: Chunking
- Intelligent text splitting (4000 chars/chunk)
- Maintains semantic coherence
- Overlapping chunks for context

### Step 3: Embedding
- Converts chunks to vector embeddings
- Uses configured embedding model
- Optimized for semantic search

### Step 4: Storage
- Stores in PostgreSQL with pgvector
- Indexed for fast retrieval
- Linked to session

## Basic Ingestion

### Single Folder

```python
async with Shadai(name="project") as shadai:
    results = await shadai.ingest(folder_path="./documents")
```

### Nested Folders

```python
# Recursively processes all subdirectories
async with Shadai(name="project") as shadai:
    results = await shadai.ingest(folder_path="./all-docs")
```

Example structure:
```
all-docs/
├── reports/
│   ├── q1-2024.pdf
│   └── q2-2024.pdf
├── research/
│   ├── paper1.pdf
│   └── paper2.pdf
└── images/
    ├── chart1.png
    └── diagram.jpg
```

All files ingested automatically!

## Ingestion Results

```python
results = await shadai.ingest(folder_path="./docs")

# Result structure
{
    "total_files": 10,
    "successful_count": 8,
    "failed_count": 1,
    "skipped_count": 1,

    "successful": [
        {"name": "report.pdf", "size": 1024000, "uuid": "..."},
        ...
    ],

    "failed": [
        {"filename": "corrupt.pdf", "error": "Unable to parse PDF"}
    ],

    "skipped": [
        {"filename": "huge.pdf", "size_mb": 40, "reason": "Exceeds 35MB limit"}
    ]
}
```

### Handling Results

```python
results = await shadai.ingest(folder_path="./docs")

# Success summary
if results["successful_count"] > 0:
    print(f"✅ Successfully ingested {results['successful_count']} files")
    for file in results["successful"]:
        size_mb = file["size"] / (1024 * 1024)
        print(f"  • {file['name']} ({size_mb:.2f} MB)")

# Failed files
if results["failed_count"] > 0:
    print(f"\n❌ Failed to ingest {results['failed_count']} files")
    for file in results["failed"]:
        print(f"  • {file['filename']}: {file['error']}")

# Skipped files
if results["skipped_count"] > 0:
    print(f"\n⊘ Skipped {results['skipped_count']} files (too large)")
    for file in results["skipped"]:
        print(f"  • {file['filename']} ({file['size_mb']} MB)")
```

## Incremental Ingestion

Add documents to existing sessions:

```python
# Initial ingestion
async with Shadai(name="research") as shadai:
    await shadai.ingest(folder_path="./batch-1")

# Later: add more documents
async with Shadai(name="research") as shadai:
    await shadai.ingest(folder_path="./batch-2")

# All documents available for queries
async with Shadai(name="research") as shadai:
    async for chunk in shadai.query("Analyze all documents"):
        print(chunk, end="")
```

## Best Practices

### ✅ Do This

```python
# Organize files before ingestion
documents/
├── contracts/
├── reports/
└── research/

# Check results
results = await shadai.ingest(folder_path="./documents")
if results["failed_count"] > 0:
    handle_failures(results["failed"])

# Use descriptive session names
async with Shadai(name="q4-financial-docs") as shadai:
    await shadai.ingest(folder_path="./finance")

# Wait for ingestion before querying
await shadai.ingest(folder_path="./docs")
async for chunk in shadai.query("question"):
    print(chunk, end="")
```

### ❌ Don't Do This

```python
# Don't ingest files > 35MB
# (will be skipped)

# Don't query immediately after starting ingestion
task = asyncio.create_task(shadai.ingest(folder_path="./docs"))
async for chunk in shadai.query("question"):  # Too soon!
    print(chunk, end="")

# Don't ingest to temporal sessions
async with Shadai(temporal=True) as shadai:
    await shadai.ingest(folder_path="./important-docs")  # Lost on exit!
```

## Performance

### Ingestion Speed

| File Size | Processing Time | Notes |
|-----------|-----------------|-------|
| < 1 MB | 5-10 seconds | Fast |
| 1-5 MB | 10-30 seconds | Typical |
| 5-20 MB | 30-120 seconds | Slower |
| 20-35 MB | 2-5 minutes | Maximum size |

**Factors affecting speed:**
- File size
- Document complexity
- Number of pages
- Image content
- Server load

### Parallel Ingestion

```python
import asyncio

async def ingest_multiple_folders():
    folders = ["./folder1", "./folder2", "./folder3"]

    tasks = []
    for folder in folders:
        async with Shadai(name=f"session-{folder}") as shadai:
            task = shadai.ingest(folder_path=folder)
            tasks.append(task)

    results = await asyncio.gather(*tasks)
    return results
```

## Troubleshooting

### File Not Ingested

**Check file size:**
```bash
ls -lh ./documents/*.pdf | awk '{print $5, $9}'
```

**Check file format:**
```bash
file ./documents/*
```

### Parse Errors

**Corrupted PDFs:**
```python
# Result will show in failed list
results = await shadai.ingest(folder_path="./docs")
for failed in results["failed"]:
    print(f"Fix: {failed['filename']}")
```

### Slow Ingestion

**Optimize:**
- Reduce file sizes
- Compress PDFs
- Remove unnecessary pages
- Ingest in batches

## Advanced Usage

### Progress Tracking

```python
import os

async def ingest_with_progress(folder_path: str):
    # Count files first
    total_files = sum(1 for _ in Path(folder_path).rglob("*.pdf"))

    async with Shadai(name="progress") as shadai:
        print(f"Ingesting {total_files} files...")
        results = await shadai.ingest(folder_path=folder_path)

        progress = (results["successful_count"] / total_files) * 100
        print(f"Progress: {progress:.1f}% complete")
```

### Selective Ingestion

```python
from pathlib import Path

async def ingest_recent_files(folder_path: str, days: int = 7):
    """Ingest only files modified in last N days."""
    import time

    cutoff = time.time() - (days * 24 * 60 * 60)
    recent_files = []

    for file in Path(folder_path).rglob("*.pdf"):
        if file.stat().st_mtime > cutoff:
            recent_files.append(file)

    # Create temp folder with recent files
    # Then ingest
    async with Shadai(name="recent") as shadai:
        await shadai.ingest(folder_path="./recent-files")
```

## Next Steps

- [Streaming Responses](streaming-responses.md) - Handle query results
- [Session Management](session-management.md) - Organize documents
- [Performance Optimization](../advanced/performance-optimization.md) - Scale ingestion

---

**Ready to query?** → [Your First Query](../getting-started/first-query.md)
