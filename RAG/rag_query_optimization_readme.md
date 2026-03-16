
# Improving RAG Performance via Query Transformation

Improving **query quality** is one of the most effective ways to improve Retrieval-Augmented Generation (RAG) performance. 
Even with a strong embedding model and vector database, poor queries often lead to poor retrieval.

In many production RAG systems, a **query transformation layer** sits between the user question and the retrieval engine.

```
retrieval_quality ≈ f(query_quality, index_quality)
```

If the query is poorly formulated, even a perfect index will return irrelevant chunks.

---

# Query Optimization Techniques

## 1. Query Rewriting

Rewrite the user question into a **retrieval-friendly form**.

Example:

User query

```
Why did Louis XIV fight Spain?
```

Rewritten query

```
causes of Franco-Spanish war 1650s Louis XIV Spain war reason
```

Pipeline

```
User Query
     ↓
LLM Query Rewriter
     ↓
Improved Query
     ↓
Vector / Hybrid Retrieval
```

Purpose:
- Bridge vocabulary gap
- Match document wording better

---

## 2. Multi‑Query Retrieval

Generate multiple versions of the query.

Example:

```
Original:
What caused the French victory at Dunkirk?
```

Generated queries:

```
1. Battle of the Dunes causes French victory
2. Dunkirk 1658 battle outcome explanation
3. why Spain lost battle of the dunes
4. Louis XIV military strategy Dunkirk
```

Then retrieve for each query:

```
retrieve(query1)
retrieve(query2)
retrieve(query3)

union + deduplicate
```

Benefits:
- Handles vocabulary mismatch
- Improves recall

---

## 3. Query Expansion

Add related terms or synonyms.

Example:

Original:

```
5G handover anomaly
```

Expanded:

```
5G handover anomaly
5G fallback problem
5G → 4G switching issue
NSA interworking failure
```

Purpose:
- Capture documents using different terminology.

---

## 4. HyDE (Hypothetical Document Embedding)

Generate a **hypothetical answer**, then embed that answer instead of the query.

Example:

Query

```
What causes Wi‑Fi packet loss?
```

LLM generates:

```
Wi‑Fi packet loss is typically caused by interference, network congestion,
weak signal strength, and hardware issues.
```

Embed the generated paragraph and retrieve with it.

Why it works:

```
query embedding  → sparse semantic signal
hypothetical doc → richer semantic representation
```

---

## 5. Question Decomposition

Break complex questions into smaller queries.

Example:

```
Which team won more recently, Red Sox or Patriots?
```

Decompose:

```
1. When did Red Sox win championship?
2. When did Patriots win championship?
```

Used in **multi-hop reasoning systems**.

---

## 6. RAG Fusion

Combine multi-query retrieval with ranking.

Process:

```
generate multiple queries
retrieve documents for each
merge results
rerank documents
```

Benefits:
- Improves retrieval diversity
- Improves ranking quality

---

## 7. Conversational Query Reformulation

For chat-based systems, rewrite queries to remove context dependence.

Example:

Conversation:

```
User: When was it signed?
```

Rewrite to:

```
When was the Peace of the Pyrenees signed?
```

Purpose:
- Avoid missing context during retrieval

---

## 8. Intent Routing

Route different query types to different retrievers.

Example:

```
diagnostic question → troubleshooting retriever
definition question → knowledge base retriever
numerical question → database query
```

Purpose:
- Improve retrieval precision.

---

## 9. Planning / Agent Retrieval

Advanced RAG systems generate a **search plan**.

Example:

```
User Question
     ↓
Planner LLM

Plan:
1. retrieve history of Louis XIV wars
2. retrieve Franco-Spanish relations
3. combine results
```

Used in **agentic RAG architectures**.

---

## 10. Rewrite‑Retrieve‑Read Architecture

Traditional RAG:

```
Retrieve → LLM
```

Improved pipeline:

```
Rewrite
   ↓
Retrieve
   ↓
LLM
```

Benefits:
- Better retrieval alignment with user intent.

---

# Typical Production RAG Pipeline

Many modern systems use the following structure:

```
User Query
     ↓
Query Rewrite
     ↓
Multi‑Query Generation
     ↓
Hybrid Retrieval (BM25 + Vector)
     ↓
Reranker
     ↓
LLM Answer
```

---

# Recommended Improvements (Practical)

## Level 1 — Easy

Use:

```
MultiQueryRetriever
```

---

## Level 2 — Strong

```
Query rewrite
+
Hybrid retrieval
+
Cross‑encoder reranker
```

---

## Level 3 — Advanced

```
HyDE
+
RAG fusion
+
query decomposition
```

---

# Key Insight

In many production systems:

```
RAG performance improvements often come more from
query engineering than embedding changes.
```

Teams often spend **50–70% of optimization effort on query and retrieval engineering** rather than model changes.

