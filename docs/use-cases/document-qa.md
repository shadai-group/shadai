# Document Q&A

Build intelligent document Q&A systems with Shadai. Perfect for customer support, internal knowledge bases, and documentation search.

## Use Case Overview

**Problem**: Users need quick, accurate answers from large document collections

**Solution**: RAG-powered Q&A that searches documents and provides contextual answers

**Benefits**:
- ⚡ Instant answers
- 📚 Search thousands of documents
- 🎯 Accurate, cited responses
- 💬 Natural conversation

## Basic Implementation

### Simple Q&A System

```python
import asyncio
from shadai import Shadai

async def document_qa():
    """Simple document Q&A system."""

    # Initialize session
    async with Shadai(name="docs-qa") as shadai:
        # Ingest documentation
        print("📥 Loading documents...")
        results = await shadai.ingest(folder_path="./documentation")
        print(f"✅ Loaded {results['successful_count']} documents\n")

        # Interactive Q&A loop
        while True:
            question = input("Ask a question (or 'quit' to exit): ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                break

            if not question:
                continue

            print("\n💬 Answer: ", end="")
            async for chunk in shadai.query(question):
                print(chunk, end="", flush=True)
            print("\n")

if __name__ == "__main__":
    asyncio.run(document_qa())
```

## Advanced Implementation

### Customer Support Bot

```python
from shadai import Shadai
from datetime import datetime

class SupportBot:
    def __init__(self, docs_folder: str):
        self.docs_folder = docs_folder
        self.session_name = f"support-{datetime.now().strftime('%Y%m%d')}"

    async def initialize(self):
        """Load support documentation."""
        self.shadai = Shadai(name=self.session_name)
        await self.shadai.__aenter__()

        print("Loading support documentation...")
        results = await self.shadai.ingest(folder_path=self.docs_folder)
        print(f"✅ Loaded {results['successful_count']} documents")

    async def answer_question(self, question: str, customer_context: str = None):
        """Answer customer question with optional context."""

        # Add context if provided
        if customer_context:
            full_prompt = f"Customer context: {customer_context}\n\nQuestion: {question}"
        else:
            full_prompt = question

        response = ""
        async for chunk in self.shadai.query(full_prompt):
            response += chunk

        return response

    async def cleanup(self):
        """Cleanup resources."""
        await self.shadai.__aexit__(None, None, None)

# Usage
async def main():
    bot = SupportBot(docs_folder="./support-docs")
    await bot.initialize()

    # Example questions
    answer = await bot.answer_question(
        question="How do I reset my password?",
        customer_context="Premium plan user"
    )
    print(answer)

    await bot.cleanup()

asyncio.run(main())
```

### Multi-Language Support

```python
async def multilingual_qa(docs_folder: str, language: str = "en"):
    """Q&A system with language detection."""

    async with Shadai(name=f"qa-{language}") as shadai:
        await shadai.ingest(folder_path=docs_folder)

        # Language-specific prompt
        language_prompts = {
            "en": "Answer in English:",
            "es": "Responde en español:",
            "fr": "Répondez en français:"
        }

        while True:
            question = input(f"Question ({language}): ").strip()
            if not question:
                break

            # Add language instruction
            full_prompt = f"{language_prompts.get(language, '')} {question}"

            async for chunk in shadai.query(full_prompt):
                print(chunk, end="", flush=True)
            print("\n")
```

## Production Patterns

### Pattern 1: Cached Sessions

```python
from typing import Dict
import asyncio

class QASessionManager:
    def __init__(self):
        self.sessions: Dict[str, Shadai] = {}

    async def get_or_create_session(self, session_id: str, docs_folder: str = None):
        """Get existing session or create new one."""

        if session_id not in self.sessions:
            shadai = Shadai(name=session_id)
            await shadai.__aenter__()

            if docs_folder:
                await shadai.ingest(folder_path=docs_folder)

            self.sessions[session_id] = shadai

        return self.sessions[session_id]

    async def query(self, session_id: str, question: str):
        """Query a session."""
        shadai = await self.get_or_create_session(session_id)

        response = ""
        async for chunk in shadai.query(question):
            response += chunk

        return response

    async def cleanup_session(self, session_id: str):
        """Remove session from cache."""
        if session_id in self.sessions:
            await self.sessions[session_id].__aexit__(None, None, None)
            del self.sessions[session_id]

    async def cleanup_all(self):
        """Cleanup all sessions."""
        for shadai in self.sessions.values():
            await shadai.__aexit__(None, None, None)
        self.sessions.clear()
```

### Pattern 2: Confidence Scoring

```python
async def qa_with_confidence(question: str):
    """Answer with confidence indication."""

    async with Shadai(name="qa-confidence") as shadai:
        response = ""
        async for chunk in shadai.query(question):
            response += chunk

        # Heuristic confidence
        confidence = "high" if len(response) > 100 else "medium"

        return {
            "answer": response,
            "confidence": confidence,
            "question": question
        }
```

### Pattern 3: Source Attribution

```python
async def qa_with_sources(question: str):
    """Provide answer with source documents."""

    async with Shadai(name="qa-sources") as shadai:
        # Get answer
        answer = ""
        async for chunk in shadai.query(question):
            answer += chunk

        # Note: Source attribution would come from backend
        # This is a client-side approximation

        return {
            "answer": answer,
            "question": question,
            "metadata": {
                "session": "qa-sources",
                "timestamp": datetime.now().isoformat()
            }
        }
```

## Integration Examples

### Web API (FastAPI)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Initialize global session manager
qa_manager = QASessionManager()

class QuestionRequest(BaseModel):
    question: str
    session_id: str = "default"

class AnswerResponse(BaseModel):
    answer: str
    session_id: str

@app.on_event("startup")
async def startup():
    # Initialize default session
    await qa_manager.get_or_create_session(
        session_id="default",
        docs_folder="./docs"
    )

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    try:
        answer = await qa_manager.query(
            session_id=request.session_id,
            question=request.question
        )
        return AnswerResponse(
            answer=answer,
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
async def shutdown():
    await qa_manager.cleanup_all()
```

### Slack Bot

```python
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

app = AsyncApp(token="YOUR_BOT_TOKEN")
qa_bot = SupportBot(docs_folder="./support-docs")

@app.event("app_mention")
async def handle_mention(event, say):
    question = event["text"].split(maxsplit=1)[1] if len(event["text"].split()) > 1 else ""

    if not question:
        await say("Ask me a question about our documentation!")
        return

    answer = await qa_bot.answer_question(question)
    await say(answer)

async def main():
    await qa_bot.initialize()
    handler = AsyncSocketModeHandler(app, "YOUR_APP_TOKEN")
    await handler.start_async()

asyncio.run(main())
```

### Discord Bot

```python
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

qa_bot = None

@bot.event
async def on_ready():
    global qa_bot
    qa_bot = SupportBot(docs_folder="./docs")
    await qa_bot.initialize()
    print(f"Bot ready as {bot.user}")

@bot.command()
async def ask(ctx, *, question: str):
    """Ask a question: !ask How do I reset password?"""
    async with ctx.typing():
        answer = await qa_bot.answer_question(question)
        await ctx.send(answer[:2000])  # Discord message limit

bot.run("YOUR_BOT_TOKEN")
```

## Best Practices

### Optimize for Speed

```python
# Pre-load documents at startup
async def initialize_qa_system():
    shadai = Shadai(name="production-qa")
    await shadai.__aenter__()
    await shadai.ingest(folder_path="./docs")
    return shadai

# Reuse session
qa_system = await initialize_qa_system()

# Fast queries
answer = ""
async for chunk in qa_system.query("question"):
    answer += chunk
```

### Handle Edge Cases

```python
async def robust_qa(question: str):
    if not question or len(question) < 3:
        return "Please ask a more specific question."

    if len(question) > 500:
        return "Question too long. Please be more concise."

    try:
        async with Shadai(name="qa") as shadai:
            answer = ""
            async for chunk in shadai.query(question):
                answer += chunk

            if not answer:
                return "I couldn't find relevant information."

            return answer

    except Exception as e:
        return f"Error processing question: {str(e)}"
```

### Monitor Performance

```python
import time

async def timed_qa(question: str):
    start = time.time()

    async with Shadai(name="qa") as shadai:
        answer = ""
        async for chunk in shadai.query(question):
            answer += chunk

    duration = time.time() - start

    return {
        "answer": answer,
        "duration_seconds": duration,
        "timestamp": datetime.now().isoformat()
    }
```

## Troubleshooting

### Slow Responses

**Problem**: Queries take too long

**Solutions**:
- Pre-load documents
- Use smaller document collections
- Clear conversation history
- Disable memory for independent queries

### Irrelevant Answers

**Problem**: Answers don't match questions

**Solutions**:
- Make questions more specific
- Add context to queries
- Verify documents are relevant
- Check document quality

### Memory Issues

**Problem**: Bot confuses topics

**Solutions**:
```python
# Clear history between topics
await shadai.clear_session_history()

# Or disable memory
async for chunk in shadai.query(question, use_memory=False):
    print(chunk, end="")
```

## Next Steps

- [Research Assistant](research-assistant.md) - Advanced research workflows
- [Knowledge Synthesis](knowledge-synthesis.md) - Multi-document analysis
- [Custom Workflows](custom-workflows.md) - Build specialized systems

---

**Ready to build?** Start with the basic implementation and scale as needed!
