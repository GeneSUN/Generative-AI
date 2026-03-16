## 2. Two Evaluation Modes
### (1) Retrieval Evaluation

Evaluate the documents retrieved before generation.

Goal:

check if the retriever returns the correct context

Typical use:

tuning chunking

tuning embedding models

tuning vector search

### (2) End-to-End RAG Evaluation (Retrieve + Generate)

Evaluate the final answer produced by the LLM using retrieved context.

Metrics include:

- Correctness, Does the answer match the expected fact?
- Faithfulness (Hallucination detection)

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

### Ground-Truth vs Reference-Free Evaluation
