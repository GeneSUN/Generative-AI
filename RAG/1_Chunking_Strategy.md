
# How to build Vector Database:


- https://github.com/GeneSUN/Generative-AI/blob/main/src/rag/chunk_strategy.py
- https://colab.research.google.com/drive/1uwZ-B-E_I4kmCbnAk53wzJr_ZS88Jedc#scrollTo=XgS3Yx_57TPu

As we discussed before, 
- the first step of using a RAG is to build a vector database;
  <img width="1250" height="209" alt="Screenshot 2025-12-20 at 2 47 09 PM" src="https://github.com/user-attachments/assets/bcbcaaae-fbaf-4b61-b4cd-89d09e76b344" />

- and the first step of building a vector database, is to chunk the big text document carefully into splits
  <img width="725" height="88" alt="Untitled" src="https://github.com/user-attachments/assets/767ba798-f487-4283-a7f4-548be5e5cb0a" />

  
## Table of Contents


- [1. Why Chunking Matters](#why-chunking-matters)
- [2. Common Chunking Strategies](#common-chunking-strategies)
  - [Token-based Chunking](#token-based)
  - [Semantic-based Chunking](#semantic-based)
  - [Overlap Strategy](#7-overlap-strategy-boundary-effects)
- [3. Factors That Affect Chunking Strategy](#factors-that-affect-chunking-strategy)
  - [Nature of the Content](#1-nature-of-the-content)
  - [Query Characteristics](#2-query-characteristics-often-overlooked)
  - [Embedding Model and LLM Constraints](#4-embedding-model-and-llm-constraints)
  - [Retrieval Strategy](#6-retrieval-strategy)
- [4. Evaluating Chunking Quality](#evaluating-chunking-quality)
  - [1. Embedding-Space Metrics](#embedding-space-metrics-cheap--fast)
    - [Intra-Chunk Coherence](#1-intra-chunk-coherence-chunk-length-distribution)
    - [Inter-Chunk Redundancy](#2-inter-chunk-redundancy-similarity-between-adjacent-chunks)
  - [2. Retrieval-Centered Metrics](#retrieval-centered-metrics-most-common--practical)
    - [LLM-Based Evaluation](#llm-based-evaluation-higher-signal-higher-cost)
  - [3. RAGAS](#end-to-end-task-metrics-gold-standard)




---


## Why Chunking Matters

Before a document can be embedded and indexed, it must be split into smaller units. This is necessary because:

### 1.1. LLM Context and Latency Constraints
LLMs have limited context windows and non-trivial inference costs. Entire documents are too large to embed, retrieve, or pass to a model efficiently. Chunking allows the system to work with manageable units of information.

### 1.2. Retrieval Granularity and Semantic Precision
Retrieval works best when each chunk represents a **single, coherent idea**.  
- If chunks are too large, retrieval becomes noisy.  
- If chunks are too small, meaning is lost.

Chunking is therefore a trade-off between **context completeness** and **retrieval precision**.

---

## Common Chunking Strategies

- https://community.databricks.com/t5/technical-blog/the-ultimate-guide-to-chunking-strategies-for-rag-applications/ba-p/113089




> In practice, the most common real-world strategy is **token-based chunking with a sliding window**.

**A Practical Chunking Flow**

<img width="733" height="287" alt="Screenshot 2026-03-12 at 6 46 02 PM" src="https://github.com/user-attachments/assets/74b522b8-7255-4587-97e1-56599bec847f" />


The chunking flow follows two steps:
- firstly split the entire document into each sentence;
- then combine sentence or tokens together following certain rules.
- This is illustrate in below [notebook](https://colab.research.google.com/drive/1uwZ-B-E_I4kmCbnAk53wzJr_ZS88Jedc) 



### Token-based  
<img width="1707" height="749" alt="Untitled" src="https://github.com/user-attachments/assets/dfeb0468-2cb2-424a-8c28-964efd63aabc" />



### Semantic-based  
<img width="2128" height="392" alt="Untitled" src="https://github.com/user-attachments/assets/0382df3c-057f-47a5-a039-075686374435" />


### *. Overlap Strategy (Boundary Effects)

Chunk boundaries can cut important context. Overlap mitigates this by allowing adjacent chunks to share content.

Overlap improves recall but increases:
- storage size
- embedding cost
- retrieval redundancy

It should be used deliberately.

---


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



### 2. Query Characteristics (Often Overlooked)

Chunking should match **how users ask questions**, not just how documents are written.

Examples:
- Fact lookup → smaller chunks
- “Explain how X works” → larger chunks
- Troubleshooting → procedure-sized chunks

> Chunking is query-driven, not only document-driven.


### 3. Embedding Model and LLM Constraints

Different models behave differently:
- Some embedding models perform better on shorter, focused chunks
- Others tolerate longer inputs
- Token limits directly influence feasible chunk sizes

Chunking must be compatible with the **embedding model**, not just the LLM.


### 6. Retrieval Strategy

Different retrievers prefer different chunk sizes.

| Retriever Type | Chunk Preference               |
|---------------|--------------------------------|
| Sparse (BM25) | Larger chunks are acceptable   |
| Dense (Vector)| Smaller, coherent chunks work best |
| Hybrid        | A balanced middle ground       |

Chunking must align with the retrieval method you plan to use.




---


## Evaluating Chunking Quality

Chunking is a design decision, and like any design decision, it must be evaluated.  
Good chunking balances **semantic coherence**, **retrieval effectiveness**, and **system efficiency**.

Below are two practical, model-agnostic criteria for evaluating chunk quality.


### Embedding-Space Metrics (Cheap & Fast)

- https://github.com/GeneSUN/Generative-AI/blob/main/RAG/evaluation.py

#### 1. Intra-Chunk Coherence: Chunk Length Distribution

```
Chunk 1:  sentence1 ←→ sentence2 ←→ sentence3
                    all pairs averaged
```

It embeds every sentence inside the chunk, builds a full similarity matrix of all sentence pairs, and averages the upper triangle.

- High score → all sentences in the chunk are about the same topic — the chunk is coherent and focused
- Low score → sentences inside the chunk are jumping between topics — the chunk is incoherent and will confuse retrieval



#### 2. Inter-Chunk Redundancy: Similarity Between Adjacent Chunks


```
Chunk 1 ←→ Chunk 2 ←→ Chunk 3 ←→ Chunk 4
         sim1       sim2       sim3
```

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

### Retrieval Precision / Recall @ k

Question: Are the right chunks being retrieved?

- Precision@k: how many retrieved chunks are actually relevant
- Recall@k: whether relevant chunks appear in the top-k results

```
Imagine your resume is split into 6 chunks:

Chunk 1: Summary — "Data Scientist with expertise in Fraud Detection..."
Chunk 2: Verizon experience — "Developed ETL pipelines, churn prediction..."
Chunk 3: Walmart experience — "Conducted Causal Inference, self-checkout ads..."
Chunk 4: Wi-Fi/5G scoring project — "Designed scoring systems, 82% accuracy..."
Chunk 5: Anomaly detection project — "Built global anomaly detection model..."
Chunk 6: Skills — "Python, Scala, SQL, Spark, TensorFlow, AWS..."

Relevant = {Chunk 2, Chunk 4, Chunk 5}   ← all Verizon-related ML work


Retrieved = [Chunk 2, Chunk 6, Chunk 4]
              ✅ relevant  ❌ wrong  ✅ relevant
Precision@3 = 2/3 = 0.67
```

**not realistic, because Requires relevance labels (manual or heuristic)**



### LLM-Based Evaluation (Higher Signal, Higher Cost)

```
Relevant = {Chunk 2, Chunk 4, Chunk 5}   ← all Verizon-related ML work

Chunk 2  -LLM→  RELEVANT     (was retrieved ✅)
Chunk 6  -LLM→  NOT RELEVANT (was retrieved ❌)
Chunk 4  -LLM→  RELEVANT     (was retrieved ✅)
```

---

### RAGAS

- https://arxiv.org/pdf/2309.15217

**1. What RAGAS measures**

```
1. faithfulness        — Is the answer grounded in the retrieved context?
                         (catches hallucination)

2. answer_relevancy    — Does the answer actually address the question?
                         (catches vague or off-topic answers)

3. context_precision   — Are the retrieved chunks relevant to the question?
                         (equivalent to Precision@k with LLM judge)

4. context_recall      — Did retrieval find all the information needed?
                         (equivalent to Recall@k — requires ground truth answer)
```

**2. RAGAS needs a dataset of:**

```
{
    "question":         the question you ask
    "answer":           what your RAG pipeline actually returned
    "contexts":         the chunks your retriever returned (list of strings)
    "ground_truth":     the ideal answer (needed for context_recall only)
}
```

```
question:
"What machine learning work did this person do at Verizon?"

answer:
"At Verizon, this person developed ETL pipelines and predictive 
models for churn prediction and anomaly detection across Wi-Fi 
and 5G services. They also built a 5G Home Churn prediction model 
using Time Series Classification methods including CNN, ResNets, 
and KNN, achieving 78% accuracy. Additionally, they developed a 
global anomaly detection model using probabilistic time series 
forecasting for 5G network stations."

contexts: [
    "Data Scientist, Verizon Contract (09/2023 - Present)
     Developed ETL pipelines and predictive models for churn 
     prediction and anomaly detection across Verizon Wi-Fi and 
     5G services. Delivered scalable solutions using Spark, 
     forecasting models, and ML/DL techniques.",

    "Wi-Fi and 5G Home Internet Scoring System (Verizon, 2024)
     Designed scoring systems aggregating KPIs using statistical 
     and domain expertise. Built an Extender Recommendation Model 
     with 82% accuracy, 78% precision, 82% recall. Developed 5G 
     Home Churn model using Time Series Classification 
     (CNN, ResNets, KNN).",

    "5G Network Station Anomaly Detection (Verizon, 2024)
     Built a global anomaly detection model using probabilistic 
     time series forecasting. Enabled early detection of 5G 
     station anomalies, reducing downtime during 4G to 5G 
     transition.",
]

ground_truth:
"At Verizon, this person developed churn prediction models, 
anomaly detection for Wi-Fi and 5G stations, and a 5G Home 
Churn prediction model using Time Series Classification."
```

**3. Example output:**
```
{
    "faithfulness":      0.92,
    "answer_relevancy":  0.87,
    "context_precision": 0.71,
    "context_recall":    0.65,
}
```

**How to interpret each score:**
```
faithfulness = 0.92  ✅ Good
→ 92% of claims in the answers are supported by retrieved chunks.
  The LLM is not hallucinating much.

answer_relevancy = 0.87  ✅ Good  
→ Answers are mostly on-topic and address the question directly.
  Some answers may be slightly verbose or drift off topic.

context_precision = 0.71  ⚠️ Needs work
→ Only 71% of retrieved chunks were actually useful.
  29% of what was retrieved was noise — wrong chunks being pulled in.
  Fix: try smaller chunk size, better embedding model, or hybrid search.

context_recall = 0.65  ❌ Problem
→ Retriever is only finding 65% of the information needed.
  It is missing relevant chunks for some questions.
  Fix: increase k, try MMR retrieval, or check chunk boundaries.

```

```
question                              faith  ans_rel  ctx_prec  ctx_rec
"What ML work at Verizon?"            1.00    0.91     0.83      0.80
"What big data tools?"                0.95    0.88     0.67      0.67
"Accuracy of Extender model?"         1.00    0.95     1.00      1.00
"Where was the internship?"           0.75    0.82     0.50      0.50
"Educational background?"             0.90    0.79     0.67      0.50
```



