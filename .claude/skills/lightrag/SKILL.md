---
name: lightrag
description: "Build and query knowledge graphs with LightRAG (lightrag-hku). This skill should be used when inserting documents into a LightRAG knowledge graph, querying with any of the 5 search modes (naive, local, global, hybrid, mix), or setting up a new LightRAG instance. Covers initialization, storage lifecycle, query modes, and best practices."
---

# LightRAG Knowledge Graph

Build graph-based RAG pipelines using the `lightrag-hku` Python package. LightRAG extracts entities and relationships from documents into a knowledge graph, then retrieves context using graph structure + vector similarity for more accurate answers than flat-chunk RAG.

**Package:** `pip install lightrag-hku`
**Import:** `from lightrag import LightRAG, QueryParam`

---

## Python Quickstart

```python
import asyncio
import os
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed

# Ensure API key is set
# os.environ["OPENAI_API_KEY"] = "sk-..."

WORKING_DIR = os.path.expanduser("~/thecalltaker/lightrag_storage")
os.makedirs(WORKING_DIR, exist_ok=True)


async def main():
    # 1. Instantiate
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=gpt_4o_mini_complete,
        embedding_func=openai_embed,
    )

    # 2. Initialize storages (REQUIRED before any insert/query)
    await rag.initialize_storages()

    try:
        # 3. Insert documents
        await rag.ainsert("The Call Taker is an AI receptionist SaaS for service businesses.")
        await rag.ainsert([
            "HVAC companies lose $2K-$10K/month in missed calls.",
            "The Call Taker offers plans at $97, $297, and $497 per month.",
        ])

        # 4. Query with different modes
        result = await rag.aquery(
            "How does The Call Taker help HVAC businesses?",
            param=QueryParam(mode="hybrid"),
        )
        print(result)

    finally:
        # 5. Finalize storages (REQUIRED for clean shutdown)
        await rag.finalize_storages()


asyncio.run(main())
```

---

## Storage Lifecycle

**Critical:** LightRAG requires explicit storage initialization and cleanup.

```python
rag = LightRAG(working_dir=WORKING_DIR, ...)

# MUST call before any insert or query
await rag.initialize_storages()

# ... do work ...

# MUST call on cleanup to flush data and release locks
await rag.finalize_storages()
```

Failing to call `initialize_storages()` before insert/query raises errors. Failing to call `finalize_storages()` risks data corruption. Always use a `try/finally` block or async context manager pattern.

---

## Inserting Documents

### Single Document

```python
await rag.ainsert("Your document text here.")
```

### Multiple Documents (Batch)

```python
await rag.ainsert([
    "Document one text.",
    "Document two text.",
    "Document three text.",
])
```

### With File Path Tracking

```python
await rag.ainsert(
    "Contents of the file...",
    file_paths="path/to/source.txt",
)
```

### Synchronous Insert

```python
rag.insert("Your document text here.")
```

### Key Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `input` | `str \| list[str]` | Document text(s) to insert |
| `split_by_character` | `str \| None` | Custom split delimiter (default: None, uses token-based chunking) |
| `ids` | `str \| list[str] \| None` | Custom document IDs |
| `file_paths` | `str \| list[str] \| None` | Source file paths for attribution |

---

## Query Modes

LightRAG supports 5 query modes via `QueryParam(mode=...)`. Each mode retrieves context differently from the knowledge graph.

### Mode Comparison

| Mode | What It Searches | Best For | Speed |
|------|-----------------|----------|-------|
| `naive` | Raw text chunks only (no graph) | Simple factual lookups, baseline comparison | Fastest |
| `local` | Entities + their immediate relationships | Specific entity details, "tell me about X" | Fast |
| `global` | High-level community summaries from graph | Broad themes, "what are the main topics?" | Medium |
| `hybrid` | Local + global combined | Balanced depth + breadth, general-purpose | Medium |
| `mix` | Local + global + naive chunks | Maximum recall, complex multi-hop questions | Slowest |

### When to Use Each Mode

**`naive`** -- Use when the question is a simple keyword lookup or when graph extraction hasn't been done. Equivalent to traditional vector-chunk RAG. Good for benchmarking against graph-enhanced modes.

**`local`** -- Use for entity-centric questions: "What is X?", "How does X relate to Y?", "List all properties of X." Searches the immediate neighborhood of matched entities in the graph.

**`global`** -- Use for high-level summarization: "What are the main themes?", "Give an overview of the domain." Leverages community detection summaries across the full graph.

**`hybrid`** -- Use as the default for most questions. Combines local entity details with global thematic context. Good balance of precision and coverage.

**`mix`** (default) -- Use for complex questions requiring maximum context. Combines graph-based retrieval (local + global) with raw chunk retrieval (naive). Highest recall but uses the most tokens.

### Query Examples

```python
from lightrag import QueryParam

# Naive -- raw chunks only
result = await rag.aquery(
    "What is the pricing?",
    param=QueryParam(mode="naive"),
)

# Local -- entity-focused
result = await rag.aquery(
    "What does the Max engine do?",
    param=QueryParam(mode="local"),
)

# Global -- thematic overview
result = await rag.aquery(
    "What are the main components of the system?",
    param=QueryParam(mode="global"),
)

# Hybrid -- balanced (recommended default)
result = await rag.aquery(
    "How does the demo follow-up sequence work?",
    param=QueryParam(mode="hybrid"),
)

# Mix -- maximum recall
result = await rag.aquery(
    "Explain the full lead lifecycle from cold outreach to paid customer.",
    param=QueryParam(mode="mix"),
)
```

### Synchronous Query

```python
result = rag.query("Your question", param=QueryParam(mode="hybrid"))
```

---

## QueryParam Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | `str` | `"mix"` | Query mode: `naive`, `local`, `global`, `hybrid`, `mix` |
| `only_need_context` | `bool` | `False` | Return retrieved context only (no LLM answer) |
| `only_need_prompt` | `bool` | `False` | Return the constructed prompt only (no LLM call) |
| `response_type` | `str` | `"Multiple Paragraphs"` | Desired response format hint |
| `stream` | `bool` | `False` | Stream the response |
| `top_k` | `int` | `40` | Number of top entities/relations to retrieve |
| `chunk_top_k` | `int` | `20` | Number of top chunks to retrieve (naive/mix modes) |
| `max_total_tokens` | `int` | `30000` | Max tokens for combined context |
| `hl_keywords` | `list[str]` | `[]` | High-level keywords to boost in global search |
| `ll_keywords` | `list[str]` | `[]` | Low-level keywords to boost in local search |
| `conversation_history` | `list` | `[]` | Prior conversation turns for context |
| `history_turns` | `int` | `0` | Number of history turns to include |
| `include_references` | `bool` | `False` | Include source references in response |

---

## LightRAG Constructor Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `working_dir` | `str` | `"./rag_storage"` | Directory for all storage files |
| `llm_model_func` | `Callable` | `None` | LLM function (e.g., `gpt_4o_mini_complete`) |
| `embedding_func` | `EmbeddingFunc` | `None` | Embedding function (e.g., `openai_embed`) |
| `llm_model_name` | `str` | `"gpt-4o-mini"` | Model name for tokenization |
| `chunk_token_size` | `int` | `1200` | Tokens per chunk |
| `chunk_overlap_token_size` | `int` | `100` | Overlap between chunks |
| `max_parallel_insert` | `int` | `2` | Concurrent insert operations |
| `llm_model_max_async` | `int` | `4` | Max concurrent LLM calls |
| `embedding_batch_num` | `int` | `10` | Embeddings per batch |
| `enable_llm_cache` | `bool` | `True` | Cache LLM responses |
| `kv_storage` | `str` | `"JsonKVStorage"` | Key-value storage backend |
| `vector_storage` | `str` | `"NanoVectorDBStorage"` | Vector storage backend |
| `graph_storage` | `str` | `"NetworkXStorage"` | Graph storage backend |
| `top_k` | `int` | `40` | Default top-k for retrieval |
| `cosine_threshold` | `float` | `0.2` | Min cosine similarity for vector matches |
| `entity_extract_max_gleaning` | `int` | `1` | Extra extraction passes per chunk |

---

## Known Pitfalls

- **Must call `await rag.initialize_storages()`**: Instantiating `LightRAG()` does NOT initialize storage. Inserting or querying without initialization raises errors or silently fails.
- **Must call `await rag.finalize_storages()`**: Skipping finalization risks data loss. Storage files may not be flushed to disk. Always use `try/finally`.
- **Both lifecycle methods are async**: `initialize_storages()` and `finalize_storages()` are coroutines. They must be awaited.
- **`insert` vs `ainsert`**: `insert()` is the synchronous wrapper, `ainsert()` is the native async version. In async code, always use `ainsert`/`aquery`.
- **Working directory must exist**: `LightRAG` does not create the `working_dir`. Create it with `os.makedirs(dir, exist_ok=True)` before instantiation.
- **OpenAI key required**: When using `gpt_4o_mini_complete` and `openai_embed`, the `OPENAI_API_KEY` environment variable must be set.
- **Large document batches**: For many documents, insert in batches and increase `max_parallel_insert` (default 2) to control throughput vs. rate limits.
- **Mode affects token usage**: `mix` mode retrieves from all sources and uses the most tokens. Use `local` or `naive` for cost-sensitive queries.
- **Graph extraction is LLM-intensive**: Inserting documents triggers entity/relationship extraction via the LLM. This is the most expensive operation. Insert once, query many times.
- **Default storage is file-based**: `JsonKVStorage` + `NanoVectorDBStorage` + `NetworkXStorage` store everything as local files in `working_dir`. Fine for development; consider database-backed storage for production.
- **Re-inserting same text**: LightRAG deduplicates by content hash. Re-inserting identical text is a no-op.

---

## Quick Reference

| Operation | Method | Key Args |
|-----------|--------|----------|
| Create instance | `LightRAG(...)` | `working_dir`, `llm_model_func`, `embedding_func` |
| Initialize storage | `await rag.initialize_storages()` | None |
| Insert (async) | `await rag.ainsert(text)` | `input`, `file_paths` |
| Insert (sync) | `rag.insert(text)` | `input`, `file_paths` |
| Query (async) | `await rag.aquery(q, param=QueryParam(...))` | `query`, `param` |
| Query (sync) | `rag.query(q, param=QueryParam(...))` | `query`, `param` |
| Finalize storage | `await rag.finalize_storages()` | None |
| Get context only | `QueryParam(only_need_context=True)` | No LLM answer |
| Stream response | `QueryParam(stream=True)` | Returns async iterator |
| Keyword boost | `QueryParam(hl_keywords=[...], ll_keywords=[...])` | Guide retrieval |

---

## Storage Files

After inserting documents, `working_dir` contains:

```
lightrag_storage/
├── graph_chunk_entity_relation.graphml   # NetworkX knowledge graph
├── kv_store_full_docs.json               # Full document store
├── kv_store_text_chunks.json             # Chunked text store
├── kv_store_community_reports.json       # Community summaries
├── vdb_entities.json                     # Entity vector DB
├── vdb_relationships.json                # Relationship vector DB
├── vdb_chunks.json                       # Chunk vector DB
└── llm_response_cache.json              # LLM response cache
```
