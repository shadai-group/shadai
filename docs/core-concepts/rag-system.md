# RAG System

Retrieval-Augmented Generation (RAG) is the technology that powers Shadai's intelligent document querying capabilities.

## What is RAG?

RAG combines two powerful concepts:

**Retrieval**: Find relevant information from your documents
**Generation**: Use AI to create answers based on that information

```
Your Question → Search Documents → Find Relevant Parts → Generate Answer
```

## Why RAG?

### Traditional Approach (Without RAG)

**Ask AI:** "What's in my contract?"

**AI Response:** "I don't have access to your contract. I can only answer based on my training data."

### RAG Approach (With Shadai)

**Ask Shadai:** "What's in my contract?"

**Shadai:**
1. Searches your uploaded contract
2. Finds relevant clauses
3. Generates answer based on YOUR document

**Response:** "Your contract specifies a 30-day notice period and includes a non-compete clause valid for 12 months..."

## How RAG Works in Shadai

### Step 1: Document Ingestion

```python
await shadai.ingest(folder_path="./documents")
```

Behind the scenes:
1. **Parsing**: Extract text from PDFs/images
2. **Chunking**: Split into manageable pieces (~4000 characters)
3. **Embedding**: Convert text to numerical vectors
4. **Storage**: Save vectors for fast search

### Step 2: Query Processing

```python
async for chunk in shadai.query("What are the key terms?"):
    print(chunk, end="")
```

Behind the scenes:
1. **Embed Query**: Convert question to vector
2. **Search**: Find similar document chunks
3. **Retrieve**: Get top matching chunks
4. **Augment**: Add chunks to prompt
5. **Generate**: LLM creates answer with context

## RAG Pipeline in Detail

### Document Processing

```
PDF File (5 pages)
    ↓
Text Extraction
    ↓
Smart Chunking
    ├─ Chunk 1: "Introduction..."
    ├─ Chunk 2: "Key Terms..."
    ├─ Chunk 3: "Obligations..."
    └─ Chunk 4: "Termination..."
    ↓
Create Embeddings (vectors)
    ├─ [0.23, 0.45, -0.12, ...] (Chunk 1)
    ├─ [0.67, -0.23, 0.89, ...] (Chunk 2)
    └─ ...
    ↓
Store in Vector Database
```

### Query Execution

```
User: "What are the payment terms?"
    ↓
Create Query Embedding
    [0.61, -0.28, 0.77, ...]
    ↓
Vector Similarity Search
    ├─ Chunk 7: 95% similar ✅
    ├─ Chunk 3: 87% similar ✅
    ├─ Chunk 12: 82% similar ✅
    └─ Chunk 1: 45% similar ❌
    ↓
Retrieve Top 3 Chunks
    ↓
Build LLM Prompt:
    "Based on these excerpts:
     [Chunk 7 content]
     [Chunk 3 content]
     [Chunk 12 content]

     Answer: What are the payment terms?"
    ↓
LLM Generates Response
    ↓
Stream to User
```

## Embeddings Explained

Embeddings are numerical representations of text that capture semantic meaning.

### Example

**Text:** "The dog ran quickly"

**Embedding:** `[0.23, -0.45, 0.67, 0.12, -0.89, ...]` (1536 numbers)

**Similar Text:** "The canine sprinted fast"

**Embedding:** `[0.25, -0.43, 0.69, 0.10, -0.87, ...]` (very similar numbers!)

### Why This Matters

Embeddings allow semantic search:

```python
Query: "refund policy"

Finds chunks containing:
- "money-back guarantee"
- "return procedures"
- "customer reimbursement"

Even if they don't contain the word "refund"!
```

## Vector Similarity Search

How Shadai finds relevant chunks:

### Cosine Similarity

Measures how similar two vectors are:

```
Query Vector:     [0.5, 0.8, 0.3]
Document Vector:  [0.6, 0.7, 0.4]

Cosine Similarity: 0.95 (very similar!)
```

### Top-K Retrieval

Shadai retrieves the K most similar chunks:

```python
# Shadai automatically retrieves top chunks
async for chunk in shadai.query("contract terms"):
    # Uses top 5-10 most relevant chunks
    print(chunk, end="")
```

## Advantages of RAG

### 1. Accuracy

✅ **With RAG**: Answers based on your actual documents

❌ **Without RAG**: AI might hallucinate or guess

### 2. Up-to-Date

✅ **With RAG**: Always uses your latest documents

❌ **Without RAG**: Limited to AI's training cutoff date

### 3. Verifiable

✅ **With RAG**: Answers cite specific document sections

❌ **Without RAG**: No source attribution

### 4. Private

✅ **With RAG**: Your documents stay in your account

❌ **Without RAG**: Might need to paste sensitive info in prompts

### 5. Scalable

✅ **With RAG**: Query thousands of documents instantly

❌ **Without RAG**: Can't fit all documents in prompt

## RAG in Action

### Example 1: Legal Document Analysis

```python
# Upload contracts
await shadai.ingest(folder_path="./contracts")

# Ask specific questions
async for chunk in shadai.query(
    "What are the termination clauses?"
):
    print(chunk, end="")
```

**Result**: Finds and summarizes termination clauses from all contracts.

### Example 2: Research Paper Analysis

```python
# Upload research papers
await shadai.ingest(folder_path="./papers")

# Synthesize findings
async for chunk in shadai.query(
    "What are the common conclusions across all papers?"
):
    print(chunk, end="")
```

**Result**: Identifies patterns and commonalities across multiple papers.

### Example 3: Product Documentation

```python
# Upload manuals and docs
await shadai.ingest(folder_path="./product-docs")

# Customer support queries
async for chunk in shadai.query(
    "How do I reset the device?"
):
    print(chunk, end="")
```

**Result**: Provides exact instructions from official documentation.

## RAG vs. Fine-Tuning

| Aspect | RAG | Fine-Tuning |
|--------|-----|-------------|
| **Setup** | Upload documents | Train new model |
| **Time** | Minutes | Hours/Days |
| **Cost** | Low | High |
| **Updates** | Add new docs anytime | Retrain model |
| **Use Case** | Query documents | Change AI behavior |
| **Best For** | Document Q&A | Specialized tasks |

**Shadai uses RAG** because it's perfect for document querying!

## Optimizing RAG Performance

### Better Queries

✅ **Good**: "What are the payment terms in section 5?"

❌ **Vague**: "Tell me about money"

### Better Documents

✅ **Good**: Well-structured PDFs with clear sections

❌ **Poor**: Scanned images with poor quality

### Better Context

```python
# Use memory for follow-ups
async for chunk in shadai.query("What are the terms?"):
    print(chunk, end="")

# Follow-up (remembers context)
async for chunk in shadai.query("Are there exceptions?"):
    print(chunk, end="")
```

## Limitations

### 1. Chunk Boundaries

Sometimes relevant info spans multiple chunks:

**Document**: "The contract period is 12 months. Extensions require written approval."

**Chunking**: Might split into two chunks

**Solution**: Shadai uses overlapping chunks to minimize this

### 2. Vector Search Isn't Perfect

Occasionally misses exact keyword matches:

**Query**: "What's the SKU number?"

**Document**: Contains "Product ID: 12345" (not "SKU")

**Solution**: Try rephrasing: "What's the product identifier?"

### 3. Context Limits

Can only fit ~5-10 chunks in LLM context:

**Problem**: Very long or complex answers

**Solution**: Ask more specific questions or use summarize tool

## Advanced RAG Features

### Hybrid Search (Planned)

Combine vector search with keyword search:
- Vector: Semantic similarity
- Keyword: Exact matches
- Result: Best of both worlds

### Metadata Filtering (Available)

Filter by document properties:
- Date ranges
- Document types
- Specific sessions
- Authors/sources

### Re-ranking (Automatic)

Shadai automatically re-ranks results for better relevance.

## Next Steps

- [Tools Overview](tools-overview.md) - All RAG-powered tools
- [Intelligent Agent](intelligent-agent.md) - Advanced RAG workflows
- [Document Q&A Use Case](../use-cases/document-qa.md) - Practical examples

---

**Key Takeaway**: RAG enables AI to answer questions using YOUR documents. It's like giving AI a research assistant!
