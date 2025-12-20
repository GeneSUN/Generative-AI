

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

<img width="202" height="315" alt="Screenshot 2025-12-20 at 1 47 59 PM" src="https://github.com/user-attachments/assets/5a68d4ce-2fbe-44a3-8fb8-f1e16b658131" />

<img width="488" height="557" alt="Screenshot 2025-12-20 at 1 46 15 PM" src="https://github.com/user-attachments/assets/a9ddae50-da8c-4eb5-bcda-9f561dc0448f" />

<img width="541" height="588" alt="Untitled" src="https://github.com/user-attachments/assets/f7e4b6c8-5f5b-411f-b8d4-b5ceb93a2fc7" />

<img width="459" height="593" alt="Untitled" src="https://github.com/user-attachments/assets/4a7b1822-560c-484a-8e69-49335b57b1fc" />

