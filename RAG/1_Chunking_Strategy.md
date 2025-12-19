

## How to build Vector Database:

<img width="549" height="288" alt="Screenshot 2025-12-18 at 9 02 05 AM" src="https://github.com/user-attachments/assets/dc409400-b700-4cde-86dd-ff911655bb74" />

### Chunk

- https://colab.research.google.com/drive/1uwZ-B-E_I4kmCbnAk53wzJr_ZS88Jedc#scrollTo=ItDGN5zk69E_

**Why Chunk? Challenge of RAG**

1. Efficiency/LLM context/latency limits:
2. Granularity/Semantic precision:



**Factors affecting chunking strategies**

1. Nature of the content

| Content Type            | Typical Chunking             |
| ----------------------- | ---------------------------- |
| Tweets / short messages | Often no chunking or grouped |
| Articles / docs         | Paragraph or section-based   |
| Research papers         | Section-based                |
| Code                    | Function / class-based       |
| Logs / telemetry        | Time-window-based            |
| FAQs                    | One Q–A per chunk            |


2. Preprocessing data

3. Evaluating and comparing different chunk sizes

4. LLM and the associated embedding model
  —The LLM and the associated embedding model can also affect the chunking strategy.
  - For instance, some models may be more efficient at processing smaller chunks or


5. Query characteristics (often overlooked)

  Chunking should match how users ask questions.
  
  Examples:
  
  - Fact lookup → smaller chunks
  - “Explain how X works” → larger chunks
  - Troubleshooting → procedure-sized chunks
  
  > Chunking is query-driven, not just document-driven.

6. Retrieval strategy (sparse, dense, hybrid)

| Retriever Type | Chunk Preference         |
| -------------- | ------------------------ |
| Sparse (BM25)  | Larger chunks OK         |
| Dense (vector) | Smaller, coherent chunks |
| Hybrid         | Middle ground            |

7. Overlap strategy (boundary effects)


| Chunking Strategy          | How It Splits Text                | Main Advantage                   | Main Limitation           | When to Use             |
| -------------------------- | --------------------------------- | -------------------------------- | ------------------------- | ----------------------- |
| **Sentence/Punctuation splitting**     | By sentence boundaries            | Preserves full meaning per chunk | Context may be too narrow | Short text, QA tasks    |
| **Fixed-length splitting** | Every *N* characters/tokens       | Simple, fast                     | Cuts sentences            | Baseline, prototyping   |
| **Token-based splitting**  | Every *N* tokens                  | Aligns with model limits         | Can break ideas           | Embedding-aware systems |
| **Sliding window**         | Fixed-size chunks with overlap    | Preserves boundary context       | Redundancy, higher cost   | Dense retrieval, QA     |
| **Semantic/Adaptive chunking**      | By topic / paragraph meaning      | High semantic coherence          | More complex              | High-quality RAG        |
| **Hierarchical chunking**  | Chapters → sections → subsections | Preserves structure              | Needs structured docs     | Manuals, papers         |

> The most common chunking strategy in real-world RAG systems is: Token-based fixed-size chunking with a sliding window (overlap).


### Chunking sentences

Split sentence function

```python
def split_sentences(text):
  # Splits the sentence at every occurrence of these characters
  sentences = re.split('[.!?]', text)
  sentences = [sentence.strip() for sentence in sentences if sentence]
  return sentences
```

```python
import textwrap
def split_sentences_by_textwrap(text):
    max_chunk_size = 2048
    chunks = textwrap.wrap(text,
    width=max_chunk_size,
    break_long_words=False,
    break_on_hyphens=False)
    return chunks
```

#### natural language processing

> NLTK enables sentence-level semantic preservation, which can be composed into higher-level semantic chunks.

```
def split_sentences_by_nltk(text):
    chunks = []
    for sentence in nltk.sent_tokenize(text):
        chunks.append(sentence)
    return chunks
```


### HANDLING TABLES AND IMAGES IN PDF
