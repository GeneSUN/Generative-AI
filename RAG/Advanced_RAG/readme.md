# Advanced RAG

Traditional RAG follows a fixed pipeline: chunk → embed → retrieve → generate. It works well for simple, single-hop questions over clean document sets. But it breaks down when queries are ambiguous, knowledge is relational, tasks require multi-step reasoning, or retrieval itself needs to be dynamic.

This section covers techniques that go beyond the baseline.

---

## Why Traditional RAG Falls Short

| Limitation | Example | Solution |
|---|---|---|
| Poor query quality → poor retrieval | User asks "it" without context | Query optimization |
| Flat document chunks miss relationships | "Who works with whom?" across entities | Graph RAG |
| Static one-shot retrieval | Multi-hop reasoning fails | Agentic RAG |
| Single retriever, single index | Mixed data types (text, tables, code) | Hybrid / Modular RAG |

---

## Techniques

### 1. Query Optimization
*The query is often the weakest link.*

Even with a perfect index, a poorly formed query returns irrelevant chunks. Query optimization sits between the user's question and the retrieval engine, transforming the input before search.

Key techniques:
- **Query Rewriting** — rephrase into retrieval-friendly form
- **Multi-Query Retrieval** — generate multiple query variants, union results
- **HyDE** — generate a hypothetical answer and embed that instead of the query
- **Question Decomposition** — break complex multi-hop questions into sub-queries
- **Conversational Reformulation** — resolve pronouns and references in chat context
- **RAG Fusion** — multi-query + reciprocal rank fusion for better ranking

> In many production systems, 50–70% of RAG performance gains come from query engineering, not embedding changes.

→ [Query Optimization](../rag_query_optimization_readme.md)

---

### 2. Graph RAG
*When knowledge is relational, not just similar.*

Vector search retrieves semantically similar chunks — but it doesn't understand structure. Graph RAG builds a knowledge graph over the document corpus, where entities are nodes and relationships are edges. Retrieval becomes graph traversal: follow edges, aggregate community summaries, answer questions that span multiple entities.

When to use:
- Questions involving relationships ("How does X connect to Y?")
- Multi-hop reasoning across entities
- Structured domains (medical, legal, technical specifications)

Key concepts:
- **Entity extraction** — identify nodes from documents
- **Relationship extraction** — build edges between entities
- **Community detection** — cluster related entities for summarization
- **Global vs. local search** — traverse graph vs. vector search over summaries

Reference: [Microsoft GraphRAG](https://arxiv.org/pdf/2404.16130)

---

### 3. Agentic RAG
*When retrieval itself needs to reason.*

Standard RAG retrieves once and answers. Agentic RAG treats retrieval as a tool that an agent can call repeatedly, adaptively, and with a plan. The agent decides *what* to retrieve, *when*, and *how many times* based on what it has found so far.

Patterns:
- **Iterative retrieval** — retrieve, evaluate gaps, retrieve again
- **Retrieval planning** — generate a structured search plan before any retrieval
- **Self-correcting RAG** — if retrieved context is insufficient, reformulate and retry
- **Tool-augmented retrieval** — combine vector search with SQL, APIs, web search

```
User Question
     ↓
Planner LLM → Search Plan
     ↓
Retriever (called multiple times)
     ↓
Synthesizer LLM
     ↓
Answer
```

Reference: [Agentic RAG Survey](https://arxiv.org/pdf/2501.09136)

---

### 4. Hybrid & Modular RAG
*Not all content is equal; not all retrievers are equal.*

Hybrid retrieval combines dense (vector) and sparse (BM25/keyword) search, then merges results via reranking. Different content types — structured tables, code, long documents, real-time data — benefit from different retrieval strategies.

Key techniques:
- **Hybrid search** — BM25 + vector, merged with reciprocal rank fusion
- **Cross-encoder reranking** — re-score top-k results with a more expensive model
- **Routing** — direct query to the right retriever based on intent
- **Multi-index RAG** — separate vector DBs per content type, merged at query time

```
User Query
     ↓
Intent Router
     ├── Vector DB (semantic search)
     ├── BM25 (keyword search)
     └── SQL / API (structured data)
          ↓
     Reranker
          ↓
         LLM
```

---

## How These Techniques Relate

```
Query Optimization   →  better input to retrieval
Graph RAG            →  better structure for relational knowledge
Agentic RAG          →  dynamic, multi-step retrieval
Hybrid / Modular RAG →  better retrieval infrastructure
```

They are composable. A production system might use query rewriting (optimization) → intent routing → hybrid retrieval → cross-encoder reranking → iterative agentic loop.

---

## Files

| File | Description |
|---|---|
| [Query Optimization](../rag_query_optimization_readme.md) | Rewriting, HyDE, decomposition, RAG Fusion |

---

## References

- [Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG](https://arxiv.org/pdf/2501.09136)
- [From Local to Global: A Graph RAG Approach to Query-Focused Summarization](https://arxiv.org/pdf/2404.16130)
- [Blended RAG: Improving RAG Accuracy with Semantic Search and Hybrid Query-Based Retrievers](https://arxiv.org/pdf/2404.07220)
- [A Systematic Framework for Enterprise Knowledge Retrieval](https://arxiv.org/pdf/2512.05411)
