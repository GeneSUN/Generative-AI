
## Ragas

### 1. Faithfulness

<details>

Faithfulness measures whether the answer is supported by the retrieved context. It detects hallucinations.

```
question (Where is the Eiffel Tower located?)
↓
retrieve context (The Eiffel Tower is located in Paris.)
↓
LLM answer (The Eiffel Tower is located in Paris and is the largest city in Europe.)

1. extract claims from answer: 1 Paris is location; 2 Paris is largest city in Europe ✘ unsupported
2. check if each claim is supported by context
3. compute ratio (supported_claims / total_claims = 1 / 2 = 0.5)
```

</details>

### 2. Response Relevancy 

<details>

It checks **semantic alignment** between question and answer.

1. LLM reads the answer, Eo 
2. LLM generates N questions the answer could answer, Egi
3. Compare those questions with the original question

<img width="366" height="80" alt="Screenshot 2026-03-16 at 8 50 34 AM" src="https://github.com/user-attachments/assets/c06261d2-7372-499d-8d40-cf4e68c66b97" />

</details>

### 3. Retrieval Precision @ k

<details>

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

Chunk 2  -LLM→  RELEVANT     (was retrieved ✅)
Chunk 6  -LLM→  NOT RELEVANT (was retrieved ❌)
Chunk 4  -LLM→  RELEVANT     (was retrieved ✅)
Retrieved = [Chunk 2, Chunk 6, Chunk 4]
         ✅ relevant  ❌ wrong  ✅ relevant

Precision@3 = 2/3 = 0.67
```

</details>

### 4. Retrieval Recall @ k


## Best Practices & Implementation Guidelines: The Evaluation Pipeline

### Step 1 — Build a Test Dataset (Synthetic QA dataset/Human dataset)

### Step 2 — Generate Predictions

### Step 3 — Calculate Metrics, Compare and Decide

### Step *. Collect, User Feedback

For example, wifi-Score can do:
- Diagnosis	“Why is my Wi-Fi score low?”
- Metric explanation	“What does SNR mean?”
- Recommendation	“How can I improve my Wi-Fi?”

when evaluate user feedback, I found Recommendation is really bad, because failure case is really diverse, and a lot of case, there is no Recommendation history.

---



## Evaluating Chunking Quality

Chunking is a design decision, and like any design decision, it must be evaluated.  
Good chunking balances **semantic coherence**, **retrieval effectiveness**, and **system efficiency**.

Below are two practical, model-agnostic criteria for evaluating chunk quality.


- https://github.com/GeneSUN/Generative-AI/blob/main/RAG/evaluation.py

### 1. Intra-Chunk Coherence: Chunk Length Distribution
<details>
```
Chunk 1:  sentence1 ←→ sentence2 ←→ sentence3
                    all pairs averaged
```

It embeds every sentence inside the chunk, builds a full similarity matrix of all sentence pairs, and averages the upper triangle.

- High score → all sentences in the chunk are about the same topic — the chunk is coherent and focused
- Low score → sentences inside the chunk are jumping between topics — the chunk is incoherent and will confuse retrieval

</details>

### 2. Inter-Chunk Redundancy: Similarity Between Adjacent Chunks

<details>

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

</details>

### Example of Messy Chunk

<details>

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

<img width="1389" height="789" alt="image" src="https://github.com/user-attachments/assets/9f0fcdc7-3592-4e5c-aab3-577d70012596" />


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
<img width="1390" height="789" alt="image" src="https://github.com/user-attachments/assets/82f6b979-700e-497c-a245-aa9006ad8ab0" />

### Post-Process

- Drop junk chunks (< 50 tokens or pure punctuation)
- Break up monster chunks (> 600 tokens)
- Re-run the length evaluation to confirm improvement

</details>


