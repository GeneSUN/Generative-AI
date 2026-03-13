

## Modern RAG Systems Improve Retrieval in 4 Ways

### 1. Hybrid search: vector search + keyword search (BM25)

### 2. Reranking
  ```
  retrieve top 20 chunks
  ↓
  rerank with cross-encoder
  ↓
  select top 5
  ```

### 3. Metadata filtering
```
filter: customer_id
filter: document_type
filter: date
```

### 4. Real Production Trick

Many companies improve RAG with query rewriting. Example:

User query:
> Why is my Wi-Fi slow?

System converts it to:
> wifi performance degradation causes
> RSSI SNR retransmission latency wifi

Then retrieval becomes much better.









