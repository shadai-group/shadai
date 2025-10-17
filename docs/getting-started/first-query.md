# Your First Query

Learn by doing! This step-by-step tutorial will take you from zero to your first successful query.

## What You'll Build

A simple document Q&A application that:
1. Ingests PDF documents
2. Answers questions about them
3. Maintains conversation context

**Time to complete**: ~10 minutes

## Prerequisites

- ✅ Shadai installed ([Installation Guide](installation.md))
- ✅ API key configured ([Authentication Guide](authentication.md))
- ✅ Python 3.10+ with async support

## Step 1: Prepare Your Documents

Create a folder with some PDF files:

```bash
mkdir ./my-documents
# Add some PDF files to ./my-documents/
```

For this tutorial, you can use any PDF - research papers, reports, books, etc.

## Step 2: Create Your Script

Create `first_query.py`:

```python
import asyncio
from shadai import Shadai

async def main():
    # Step 1: Create a session
    print("🚀 Starting Shadai session...")
    async with Shadai(name="my-first-query") as shadai:

        # Step 2: Ingest documents
        print("📥 Ingesting documents...")
        results = await shadai.ingest(folder_path="./my-documents")

        print(f"✅ Successfully ingested: {results['successful_count']}")
        print(f"❌ Failed: {results['failed_count']}")
        print(f"⊘ Skipped (too large): {results['skipped_count']}\n")

        # Step 3: Ask a question
        print("🔍 Asking question...")
        print("Q: What are the main topics covered in these documents?\n")
        print("A: ", end="")

        async for chunk in shadai.query(
            "What are the main topics covered in these documents?"
        ):
            print(chunk, end="", flush=True)

        print("\n")

if __name__ == "__main__":
    asyncio.run(main())
```

## Step 3: Run Your First Query

```bash
python first_query.py
```

You should see output like:

```
🚀 Starting Shadai session...
📥 Ingesting documents...
✅ Successfully ingested: 3
❌ Failed: 0
⊘ Skipped (too large): 0

🔍 Asking question...
Q: What are the main topics covered in these documents?

A: Based on the documents provided, the main topics include:
1. Machine learning algorithms and their applications
2. Data preprocessing techniques
3. Model evaluation metrics...
```

## Step 4: Add Follow-Up Questions

The magic of Shadai is context! Let's add a follow-up:

```python
import asyncio
from shadai import Shadai

async def main():
    async with Shadai(name="my-first-query") as shadai:
        # Ingest documents
        print("📥 Ingesting documents...")
        await shadai.ingest(folder_path="./my-documents")

        # First question
        print("\n🔍 Question 1:")
        print("Q: What are the main topics?\n")
        print("A: ", end="")

        async for chunk in shadai.query("What are the main topics?"):
            print(chunk, end="", flush=True)

        # Follow-up question (context maintained!)
        print("\n\n🔍 Question 2 (follow-up):")
        print("Q: Can you elaborate on the first topic?\n")
        print("A: ", end="")

        async for chunk in shadai.query("Can you elaborate on the first topic?"):
            print(chunk, end="", flush=True)

        print("\n")

if __name__ == "__main__":
    asyncio.run(main())
```

Notice how the second question doesn't need to repeat context - Shadai remembers "the first topic" from the previous answer!

## Understanding the Code

### The Context Manager

```python
async with Shadai(name="my-first-query") as shadai:
    # Your code here
```

- `async with` - Ensures proper cleanup
- `name="my-first-query"` - Creates a persistent session
- Session stores: documents, chat history, context

### Ingestion

```python
results = await shadai.ingest(folder_path="./my-documents")
```

What happens behind the scenes:
1. 🔍 Scans folder recursively
2. 📄 Extracts text from PDFs
3. ✂️ Chunks documents intelligently
4. 🧠 Creates embeddings
5. 💾 Stores in vector database

### Querying

```python
async for chunk in shadai.query("Your question"):
    print(chunk, end="", flush=True)
```

What happens:
1. 🧠 Converts question to embedding
2. 🔍 Finds relevant document chunks
3. 🤖 Generates answer with context
4. ⚡ Streams tokens in real-time

## Troubleshooting

### No documents ingested

**Problem**: `Successfully ingested: 0`

**Solutions**:
- Check folder path is correct
- Ensure PDFs are under 35MB
- Verify PDFs aren't corrupted

### Slow ingestion

**Problem**: Ingestion takes a long time

**Explanation**:
- First ingestion is slower (processing + embedding)
- Large files take longer
- This is normal! Subsequent queries are fast

### Generic answers

**Problem**: Answers don't reference your documents

**Solutions**:
- Check documents were actually ingested
- Make questions more specific
- Verify documents contain relevant information

### Authentication errors

**Problem**: `AuthenticationError`

**Solution**:
```bash
# Verify API key is set
echo $SHADAI_API_KEY

# Or check .env file
cat .env | grep SHADAI_API_KEY
```

## Next Level: Interactive Q&A

Let's make it interactive:

```python
import asyncio
from shadai import Shadai

async def interactive_qa():
    async with Shadai(name="interactive") as shadai:
        # Ingest documents once
        print("📥 Loading documents...")
        await shadai.ingest(folder_path="./my-documents")
        print("✅ Ready! Ask your questions (type 'quit' to exit)\n")

        while True:
            # Get question from user
            question = input("You: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                break

            if not question:
                continue

            # Get answer
            print("AI: ", end="")
            async for chunk in shadai.query(question):
                print(chunk, end="", flush=True)
            print("\n")

if __name__ == "__main__":
    asyncio.run(interactive_qa())
```

Run it:

```bash
python first_query.py
```

Example interaction:

```
📥 Loading documents...
✅ Ready! Ask your questions (type 'quit' to exit)

You: What is this document about?
AI: This document discusses machine learning algorithms...

You: What are the key benefits?
AI: The key benefits mentioned include improved accuracy...

You: quit
```

## What You Learned

✅ How to create a Shadai session
✅ How to ingest documents
✅ How to query your knowledge base
✅ How streaming responses work
✅ How context is maintained automatically

## Next Steps

Now that you've run your first query, explore more:

### 📖 Learn More
- [Session Management](../guides/session-management.md) - Organize your data
- [Memory & Context](../guides/memory-and-context.md) - Control conversation flow
- [Streaming Responses](../guides/streaming-responses.md) - Handle real-time data

### 💡 See Examples
- [Document Q&A](../use-cases/document-qa.md) - Production-ready Q&A system
- [Research Assistant](../use-cases/research-assistant.md) - Advanced research workflows
- [Multi-Document Analysis](../examples/multi-document-analysis.md) - Analyze multiple sources

### 🚀 Go Advanced
- [Custom Tools](../advanced/custom-tools.md) - Build your own tools
- [Intelligent Agents](../core-concepts/intelligent-agent.md) - Orchestrate complex workflows
- [Performance Optimization](../advanced/performance-optimization.md) - Scale to production

## Need Help?

- 💬 Having issues? Check [Error Handling Guide](../guides/error-handling.md)
- 🐛 Found a bug? [Open an issue](https://github.com/shadai/shadai-client/issues)
- 💡 Have questions? Email support@shadai.com

---

🎉 **Congratulations!** You've completed your first query. Ready to build something amazing?
