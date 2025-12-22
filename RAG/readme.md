# RAG Fundamentals: Retrieve, Read, and Synthesize with LLMs

## Overview

This repository demonstrates how to build a **Retrieval-Augmented Generation (RAG)** system on top of large language models (LLMs).

At its core, RAG follows a simple idea:

**retrieve → read → synthesize**

Instead of asking an LLM to answer questions purely from its internal knowledge, RAG first retrieves relevant external information and then asks the model to reason over that context. This design makes LLM-based systems more accurate, more transparent, and far more useful for real-world, domain-specific applications.

---


## Why RAG? Limitation of Direct LLM Question-Answering

<img width="584" height="88" alt="Untitled" src="https://github.com/user-attachments/assets/9a8b0f5b-2b26-495e-bc8e-f75d864ffcf9" />

A standalone LLM is excellent at reasoning and explanation, but it has two fundamental limitations:

- Its knowledge is fixed at training time and can become outdated.
- It cannot directly access your private documents, internal wikis, or proprietary data.

RAG addresses these limitations by separating **knowledge access** from **reasoning**. The system retrieves the most relevant information at query time and provides it to the LLM as context, allowing the model to focus on synthesis rather than memorization.

---

## RAG-Enhanced Question-Answering

RAG addresses these limitations by extends the direct workflow with introducing a retrieval step before generation.
Instead of answering in isolation, the LLM is given relevant external context and asked to reason over it.

<img width="1129" height="187" alt="RAG Workflow" src="https://github.com/user-attachments/assets/ed3733bd-011a-4cd7-8eb3-25661061e720" />

The high-level flow is:

1. **User Question** – A user submits a question.
2. **Retrieve** – The system searches for relevant information related to the question.
3. **Knowledge Store** – Matching content is fetched from an external document collection.
4. **Augment** – The retrieved content is combined with the original question.
5. **Generate** – The LLM produces an answer using the augmented input.
6. **Answer** – A grounded, context-aware response is returned.

---

## Intuition: Librarian and Professor


<table>
  <tr>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/51066285-2c27-417a-a311-824bf93eccfb"
           width="1200" />
      <br/>
      <b>Figure 1.</b> Baseline LLM Inference Workflow
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/801aed3e-b215-4a55-8bb2-7c7bf637e5c7"
           width="1200" />
      <br/>
      <b>Figure 2.</b> Retrieval-Augmented Generation (RAG) Workflow
    </td>
  </tr>
</table>


A helpful way to think about RAG is as a collaboration between two roles:

- **The Professor (LLM):**  
  Excellent at reasoning, explaining, and synthesizing ideas, but with imperfect and static memory.

- **The Librarian (Retriever):**  
  Knows how to search a large collection of documents and find the most relevant information.

When a question is asked:
1. The librarian searches the library (your document collection).
2. The most relevant passages are selected.
3. The professor receives the question along with those passages.
4. The professor produces a clear, contextual answer grounded in the provided material.

---

## What This Repository Focuses On

<img width="1860" height="277" alt="Untitled" src="https://github.com/user-attachments/assets/5ff2b085-bcca-46ff-8b38-b997f61f4fbe" />


This project focuses on the **foundational building blocks** required to implement a RAG system effectively:

- **Chunking**  
  Breaking raw documents into small, retrievable units that preserve meaning.

- **Embedding**  
  Converting each chunk into a vector representation suitable for similarity search.

- **Indexing**  
  Storing embeddings in a vector database for efficient retrieval.

- **Retrieval**  
  Selecting the most relevant chunks to support a given query.

Together, these steps enable the retrieval layer that powers the RAG workflow.





