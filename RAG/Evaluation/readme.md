# RAG Evaluation Overview

## 2. Two Evaluation Modes
### (1) Retrieval Evaluation
tuning chunking
tuning embedding models
tuning vector search

metrics:
- Context Precision
- Context Recall
- Context Entities Recall

### (2) End-to-End RAG Evaluation (Retrieve + Generate)

metrics:
- Faithfulness
- Response Relevancy
- Correctness
- Answer Similarity

## Ground-Truth vs Reference-Free Evaluation

## Ground-Truth vs Reference-Free Evaluation

### Ground-Truth Evaluation

Use a dataset with:

- question
- reference answer

Metrics:

- Correctness
- Answer Similarity

---

### Reference-Free Evaluation

No reference answer needed.

Use:

- question
- retrieved context
- generated answer

Metrics:

- Faithfulness
- Context Precision
- Context Recall
- Response Relevancy


**Correctness/accuracy is rarely used directly in RAG evaluation**

1. Creating Ground Truth Is Extremely Expensive
2. ground-truth answers are usually unavailable, ambiguous,
   for example, i would ask "how to become a data scientist"; you would end up with all kinds of answer, It is hard to define “wrong answer” problems, 

3. RAG Evaluation Is Usually Decomposed
   Assume now, you find one answer "you need to practice coding to become a data scientist", and you regard this a wrong answer.<p>
   However, why it come up with this answer? it could be

  - Retriever failure
  - Hallucination
  - Missing context

  This is why we rarely use correctness, the overall metrics, but decomposed metrics.

> Correctness Is Still Used — But Only in Special Cases, such as mathematics. 
