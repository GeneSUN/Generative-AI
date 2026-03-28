Firstly, when RAG perform bad, it is important to diagnose what causes the failure, it is because of chunking? embedding? or retrival? generation.
therefore, set different metrics at each step is critical.

<details>
<summary>RAG metrics</summary>

<img width="867" height="1383" alt="Untitled" src="https://github.com/user-attachments/assets/cda68775-f876-4483-bf51-102a5e923845" />

**Check prompt / grounding behavior**

Question:
Is the model forced to use context?

Symptoms:
- model ignores retrieved context
- injects prior knowledge

Fix:
- stronger instructions:
  “Answer ONLY based on the provided context”
- add citations requirement
- add refusal rule:
  “If not in context, say ‘I don’t know’”


</details>

### Common Question

<details>

<summary>When would you rewrite the user query before retrieval? </summary>

Expected points

Ambiguous or conversational questions
Pronouns / missing nouns
Need to expand shorthand to domain terminology
Multi-hop or decomposed questions
LangChain documents query rephrasing as a retriever-side preprocessing step to improve retrieval quality.

</details>

<details>
<summary>How would you prevent “lost in the middle” when many chunks are retrieved? </summary>

Expected points

Retrieve fewer, better chunks
Rerank
Compress/summarize context
Group by source document
Order evidence strategically
Use answer planning before final generation

</details>

<details>

<summary>How would you build RAG for PDFs, slides, and tables rather than plain text only? </summary>

Expected points

Multimodal / layout-aware parsing
Preserve page structure, section titles, captions, tables
Possibly OCR or vision parsing for figures/slides
Store modality-aware metadata
OpenAI’s cookbook specifically discusses parsing PDFs for RAG, including using both extracted text and image-based analysis for rich documents.

</details>
