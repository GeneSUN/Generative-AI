

Think of the LLM as a brilliant professor who’s excellent at explaining and synthesizing ideas, but:

- their “memory” is imperfect and not up-to-date, and
- they can’t open your company wiki or read today’s new paper unless you give it to them.

So when you ask a hard or domain-specific question, you use a librarian (the retriever) first:

1. You ask your question.
2. The librarian searches the library (your document collection) and returns the most relevant pages/sections.
3. You hand the professor the question + those passages.
4. The professor reads them and produces a clear, contextual answer — ideally with citations back to the passages.

That’s RAG: retrieve → read → synthesize.

```
Raw documents
 → Chunking
 → Embedding (vectorization)
 → Indexing in a vector database
 → Retrieval
```



