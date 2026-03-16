

## Evaluating Chunking Quality

Chunking is a design decision, and like any design decision, it must be evaluated.  
Good chunking balances **semantic coherence**, **retrieval effectiveness**, and **system efficiency**.

Below are two practical, model-agnostic criteria for evaluating chunk quality.


- https://github.com/GeneSUN/Generative-AI/blob/main/RAG/evaluation.py

### 1. Intra-Chunk Coherence: Chunk Length Distribution

```
Chunk 1:  sentence1 ←→ sentence2 ←→ sentence3
                    all pairs averaged
```

It embeds every sentence inside the chunk, builds a full similarity matrix of all sentence pairs, and averages the upper triangle.

- High score → all sentences in the chunk are about the same topic — the chunk is coherent and focused
- Low score → sentences inside the chunk are jumping between topics — the chunk is incoherent and will confuse retrieval


#### Messy Chunk

```
=======================================================
Metric                  Min    Mean    Max     Std
=======================================================
Chars                     1  2362.0  82215  6078.6
Words                     1   412.1  14090  1043.0
Tokens                    1   526.5  18038  1341.5


⚠️  Chunks < 50 tokens  : 455
⚠️  Chunks > 600 tokens : 177

Shortest 3 chunks:
  [4] 1 tokens | '.'
  [6] 1 tokens | '.'
  [8] 1 tokens | '.'
```
<img width="1489" height="396" alt="image" src="https://github.com/user-attachments/assets/784c55c0-4de1-467b-862c-c091b686377c" />


#### Clean Chunk

```
=======================================================
Metric                  Min    Mean    Max     Std
=======================================================
Chars                   180  1425.5   2716   841.9
Words                    32   248.5    499   145.4
Tokens                   50   317.1    854   188.4
```
<img width="1489" height="396" alt="image" src="https://github.com/user-attachments/assets/887b3ad5-3165-48b1-bd25-3e4acb013a7c" />



### 2. Inter-Chunk Redundancy: Similarity Between Adjacent Chunks


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




## Retrieval Precision / Recall @ k

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



## Best Practices & Implementation Guidelines

### 0. Define Evaluation Strategy

### 1. Begin with Baseline Testing

Start simple (e.g., **fixed-size chunking** with different **chunk** and **overlap sizes**). Gather metrics to establish a reference point before introducing complexity.


### 2. Optimize Chunk Size & Overlap

- General text: 200–500 tokens, 10–20% overlap.
- Code or very technical content: 100–200 tokens, 15–25% overlap.
- Narrative content: 500–1000 tokens to preserve context.


### 3. Add Metadata to Chunks
Storing metadata (e.g., section title, document type, date) helps with filtering and contextual retrieval.

