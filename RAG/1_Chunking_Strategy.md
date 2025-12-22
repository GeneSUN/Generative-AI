
# How to build Vector Database:


<img width="1250" height="209" alt="Screenshot 2025-12-20 at 2 47 09 PM" src="https://github.com/user-attachments/assets/bcbcaaae-fbaf-4b61-b4cd-89d09e76b344" />

<img width="725" height="88" alt="Untitled" src="https://github.com/user-attachments/assets/9c02983e-634f-4ee9-826c-2caffb211ee6" />

As we discussed before, 
- the first step of using a RAG is to build a vector database;
- and the first step of building a vector database, is to chunk the big text document carefully into splits



---


## Why Chunking Matters

Before a document can be embedded and indexed, it must be split into smaller units. This is necessary because:

### 1. LLM Context and Latency Constraints
LLMs have limited context windows and non-trivial inference costs. Entire documents are too large to embed, retrieve, or pass to a model efficiently. Chunking allows the system to work with manageable units of information.

### 2. Retrieval Granularity and Semantic Precision
Retrieval works best when each chunk represents a **single, coherent idea**.  
- If chunks are too large, retrieval becomes noisy.  
- If chunks are too small, meaning is lost.

Chunking is therefore a trade-off between **context completeness** and **retrieval precision**.

---

## Common Chunking Strategies

| Strategy                    | How It Splits Text            | Advantage                         | Limitation                  | When to Use                |
|----------------------------|-------------------------------|-----------------------------------|-----------------------------|----------------------------|
| Sentence-based             | Sentence boundaries           | Preserves meaning                 | Context may be too narrow   | Short QA                   |
| Fixed-length               | Every N characters            | Simple and fast                   | Breaks semantics            | Baselines, prototyping     |
| Token-based                | Every N tokens                | Model-aware                       | Can cut ideas               | Embedding systems          |
| Sliding window             | Fixed size + overlap          | Preserves boundary context        | Redundant chunks            | Dense retrieval            |
| Semantic         | Topic-based                   | High coherence                    | More complex                | High-quality RAG           |
| Hierarchical               | Sections → subsections        | Preserves structure               | Needs structured docs       | Manuals, papers            |

> In practice, the most common real-world strategy is **token-based chunking with a sliding window**.

---

## A Practical Chunking Flow

This is illustrate in below notebook
- https://colab.research.google.com/drive/1uwZ-B-E_I4kmCbnAk53wzJr_ZS88Jedc#scrollTo=wvFBo0FS7X1o

The chunking flow follows two steps:
- firstly split the entire document into each sentence;
- then combine sentence or tokens together following certain rules.

### Token-based  
<img width="1707" height="749" alt="Untitled" src="https://github.com/user-attachments/assets/dfeb0468-2cb2-424a-8c28-964efd63aabc" />



### Semantic-based  
<img width="2128" height="392" alt="Untitled" src="https://github.com/user-attachments/assets/0382df3c-057f-47a5-a039-075686374435" />




## Factors That Affect Chunking Strategy

There is no universal chunk size or strategy. Chunking decisions depend on several interacting factors.

### 1. Nature of the Content

Different content types naturally suggest different chunk boundaries.

| Content Type            | Typical Chunking Strategy       |
|------------------------|---------------------------------|
| Tweets / short messages| Often no chunking or grouping   |
| Articles / docs        | Paragraph or section-based      |
| Research papers        | Section-based                   |
| Code                   | Function / class-based          |
| Logs / telemetry       | Time-window-based               |
| FAQs                   | One Q–A pair per chunk          |

Chunking should respect the **natural structure** of the content whenever possible.

---

### 2. Preprocessing Quality

Before chunking, text often needs cleanup:
- removing boilerplate
- fixing encoding issues
- normalizing whitespace
- stripping headers/footers

Bad preprocessing leads to bad chunks, which leads to bad retrieval.

---

### 3. Chunk Size Evaluation

Chunk size is not theoretical—it must be **measured and compared**.

Common evaluation signals include:
- retrieval relevance
- answer faithfulness
- latency and cost
- redundancy in retrieved results

Chunk size should be treated as a **tunable parameter**, not a fixed rule.

---

### 4. Embedding Model and LLM Constraints

Different models behave differently:
- Some embedding models perform better on shorter, focused chunks
- Others tolerate longer inputs
- Token limits directly influence feasible chunk sizes

Chunking must be compatible with the **embedding model**, not just the LLM.

---

### 5. Query Characteristics (Often Overlooked)

Chunking should match **how users ask questions**, not just how documents are written.

Examples:
- Fact lookup → smaller chunks
- “Explain how X works” → larger chunks
- Troubleshooting → procedure-sized chunks

> Chunking is query-driven, not only document-driven.

---

### 6. Retrieval Strategy

Different retrievers prefer different chunk sizes.

| Retriever Type | Chunk Preference               |
|---------------|--------------------------------|
| Sparse (BM25) | Larger chunks are acceptable   |
| Dense (Vector)| Smaller, coherent chunks work best |
| Hybrid        | A balanced middle ground       |

Chunking must align with the retrieval method you plan to use.

---

### 7. Overlap Strategy (Boundary Effects)

Chunk boundaries can cut important context. Overlap mitigates this by allowing adjacent chunks to share content.

Overlap improves recall but increases:
- storage size
- embedding cost
- retrieval redundancy

It should be used deliberately.

---


## Evaluating Chunking Quality

Chunking is a design decision, and like any design decision, it must be evaluated.  
Good chunking balances **semantic coherence**, **retrieval effectiveness**, and **system efficiency**.

Below are two practical, model-agnostic criteria for evaluating chunk quality.

---

### Embedding-Space Metrics (Cheap & Fast)

- https://github.com/GeneSUN/Generative-AI/blob/main/RAG/evaluation.py

#### 1. Intra-Chunk Coherence: Chunk Length Distribution

**Question:** How internally consistent is each chunk?

A well-formed chunk should represent a single, coherent idea. One simple way to assess this is by examining the **chunk length distribution**.

**Red flags include:**
- Large variance in chunk sizes
- Many chunks close to the maximum token limit
- Many very small or fragmented chunks

These patterns often indicate suboptimal chunking rules.

**Practical adjustments:**
- If the number of chunks is excessively high → increase `max_tokens` to reduce fragmentation.
- If the average chunk size is too large → reduce `max_tokens` to maintain LLM compatibility.
- If chunks feel disconnected → increase overlap to preserve context.

The goal is a balanced distribution: neither too fragmented nor too dense.

---

#### 2. Inter-Chunk Redundancy: Similarity Between Adjacent Chunks



Chunk boundaries should preserve continuity without introducing excessive redundancy.  
This can be evaluated by measuring **cosine similarity between embeddings of adjacent chunks**.

**What this metric captures well:**
- Context continuity across chunk boundaries
- Whether overlap is too weak or too aggressive
- Whether chunk boundaries align with topic changes

**How to interpret similarity scores:**

| Similarity Range | Interpretation |
|------------------|----------------|
| 0.9 – 1.0        | Highly redundant chunks |
| 0.7 – 0.9        | Healthy continuity |
| 0.5 – 0.7        | Weak continuity |
| < 0.5            | Over-fragmented chunks |

**Practical tuning guidance:**
- If similarity is consistently below ~0.7 → increase overlap or chunk size.
- If similarity is consistently above ~0.95 → reduce overlap to avoid redundancy.
- Sharp drops in similarity often indicate topic boundaries, which can be desirable.

---

### Retrieval-Centered Metrics (Most Common & Practical)

#### Retrieval Precision / Recall @ k

Question: Are the right chunks being retrieved?

- Precision@k: how many retrieved chunks are actually relevant
- Recall@k: whether relevant chunks appear in the top-k results

**not realistic, because Requires relevance labels (manual or heuristic)**

---

### LLM-Based Evaluation (Higher Signal, Higher Cost)


#### Answer Faithfulness / Groundedness

Question: Does the LLM’s answer stay grounded in retrieved chunks?

- Ask an LLM to check whether answers are supported by context

Often phrased as: ```“Is this answer fully supported by the provided context?”```


---

### End-to-End Task Metrics (Gold Standard)

These evaluate chunking only through final system performance.

#### QA Accuracy / Task Success Rate

Question: Does better chunking improve final answers?

- Compare different chunking strategies, Keep everything else fixed
- Measure task success (QA accuracy, troubleshooting resolution, etc.)
