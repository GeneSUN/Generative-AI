
## Common Embedding Failures

This is where many RAG systems break.

### 1️⃣ Domain mismatch

Example:

> Embedding model trained on general text

But your data:

> telecom KPI metrics

### 3️⃣ Query vs document mismatch

User asks:
> Why is my Wi-Fi slow?

Document says:
> High retransmission rate indicates packet errors.

Embedding must recognize:
> slow wifi ≈ retransmission ≈ packet errors

Bad embedding models miss this.


### Chunking mismatch



Many companies improve RAG with query rewriting.















