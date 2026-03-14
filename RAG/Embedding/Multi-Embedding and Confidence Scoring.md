
<img width="9632" height="5954" alt="image" src="https://github.com/user-attachments/assets/872c3e31-17c5-4765-ac3e-8393b981cfed" />


## Introduction:

### 1. Why RAG important?
LLM has limitation of domain knowledge or out-date information
  
### 2. Limitation of RAG: different embedding models operate within their own prior domains
Though RAG is used to cover the limiation of domain knowledge by storage/encode them.
However, Due to variations in training data and architecture, different embedding models capture semantic similarity in divergent ways.
> A model that excels on one type of mathematical problem may underperform on another, making the selection of a single optimal embedding model a difficult and uncertain choice. 

This is similiar to unsupervised learning outlier detection: to detect the right type of anomaly, you need to select the appropriate model; but find customized model isn't easy, even impossible.

for example, if you worked at telecom, 
- Mostly plain text + formulas already extracted as text/LaTeX
- PDFs with equations, tables, charts, screenshots
you should use
- Vertex with LLM parser + embeddings if you are already in Vertex AI, because the parser is explicitly designed to understand rich documents, charts, relationships between charts and text, and extract meaningful sections before retrieval.
- Cohere embed-v4.0 or Voyage multimodal/contextual options if your source documents are mixed text/images/PDF pages. Cohere says embed-v4.0 supports text, images, and mixed texts/images such as PDFs, and Voyage offers multimodal/document-oriented embeddings plus contextualized chunk embeddings.


**2.1. Current Alternative(Agentic retrieval-augmented generation)**

### 3. Ensemble model

Inspired by the stacking/bagging paradigms of ensemble learning, we can borrow the strength of multiple modeling



## PRELIMINARY AND RELATED WORK


A common paradigm of **vanilla Retrieval-Augmented Generation (RAG)** is illustrated as follows.

### Step 1 — Embeddings Chunks

1. Chunks
Given a question $q$, an external corpus $C$ is divided into chunks:

$$ C = [c_1, c_2, ..., c_m] $$

An embedding model $g(\cdot)$ is used to generate embeddings for both the **question** and each **corpus chunk**.

2. Embeddings

The embedding representations are computed as:

$$
e_q = g(q)
$$

$$
e_{c_j} = g(c_j)
$$

where:

- $e_q$ = embedding of the question  
- $e_{c_j}$ = embedding of chunk $c_j$  
- $e_q, e_{c_j} \in \mathbb{R}^{d_g}$  
- $d_g$ = embedding dimension produced by the model $g(\cdot)$


### Step 2 — Compute Similarity

Based on the intuition that **semantically similar sentences produce similar embeddings**, we compute the similarity between the query and each chunk using **cosine similarity**:

$$
s_{q,c_j} =
\frac{e_q \cdot e_{c_j}}
{\|e_q\| \, \|e_{c_j}\|}
$$

where:

- $s_{q,c_j}$ = cosine similarity between query $q$ and chunk $c_j$
- $\cdot$ = dot product
- $\|\cdot\|$ = Euclidean norm



### Step 3 — Retrieve Top-k Chunks

Finally, we select the **top $k$** chunks with the highest similarity scores and incorporate them into the prompt:

$$
h(t, q, c_j \mid j \in K)
$$

where $K$ denotes the indices of the selected **top-k relevant chunks**.

These retrieved chunks are then used as **context** for the language model to generate the final answer.

---

## Confidence

“How sure is the LLM about the answer it is currently generating?”

1. an LLM generates one token at a time from a probability distribution over the vocabulary,
2. and they interpret a higher chosen-token probability or a more concentrated distribution as higher confidence.

> this is not truth, it is self-confidence. The model’s probability distribution tells you: how sure the model feels, not whether it is actually correct.


### Next Token Confidence Illustration

```
                           Prompt
                 "The capital of France is"
                              │
                              │
                     Predict next token
                              │
                ┌─────────────┴─────────────┐
                │                           │
        Very Confident Prediction     Uncertain Prediction
                │                           │
   France   0.93                      Paris   0.24
   Paris    0.02                      London  0.20
   London   0.01                      Berlin  0.18
   Berlin   0.01                      Rome    0.16
   Others   0.03                      Madrid  0.12
                                      Others  0.10
                │                           │
        Distribution is peaked        Distribution is flat
                │                           │
           Low uncertainty             High uncertainty
           High confidence             Low confidence
```


### sequence confidence across a whole sentence

Step i:
P(token 1), P(token 2), ..., P(token |V|)

assume each sentence contains three words/token

confident answer
token 1: [0.90, 0.05, 0.03, 0.02]
token 2: [0.85, 0.10, 0.03, 0.02]
token 3: [0.88, 0.07, 0.03, 0.02]


DP = (1/n) * Σ exp( - Σ p(vj|x,y<i) log p(vj|x,y<i) )
H1​=−(0.90log0.90+0.05log0.05+0.03log0.03+0.02log0.02) = 0.42805
DP1​=exp(0.42805)≈1.53426

H2 =−(0.85log0.85+0.10log0.10+0.03log0.03+0.02log0.02)=0.55184
DP2=exp(0.55184)≈1.73644

H3=−(0.88log0.88+0.07log0.07+0.03log0.03+0.02log0.02)=0.48208
DP3=exp(0.48208)≈1.61944

DP=(1.53426+1.73644+1.61944)/3
𝐷𝑃≈1.63005


uncertain answer
token 1: [0.30, 0.25, 0.23, 0.22]
token 2: [0.28, 0.27, 0.23, 0.22]
token 3: [0.35, 0.25, 0.20, 0.20]

DP1​=exp(1.37890)≈3.97053
DP2​=exp(1.38108)≈3.97921
DP3​=exp(1.35779)≈3.88758
DP=(3.97053+3.97921+3.88758)/3
𝐷𝑃≈3.94577

So the second sequence has a much larger DP, which means it is much less confident.


Self-certainty = -(1 / (n|V|)) * ΣΣ log( |V| * p(vj|x,y<i) )

<img width="627" height="551" alt="Screenshot 2026-03-13 at 6 04 24 PM" src="https://github.com/user-attachments/assets/a3954c1c-1053-4a9a-8edf-3c5236d28775" />

Example A
SC2 =−1/4(−4.33851)≈1.08463
SC3​=−41​(−4.66050)≈1.16512
SC=31.24363+1.08463+1.16512​≈1.16446

Example B
SC1​=−41​(−0.02889)≈0.00722
SC2​=−41​(−0.02092)≈0.00523
SC3​=−41​(−0.10981)≈0.02745
SC=30.00722+0.00523+0.02745​≈0.01330

Final summary table

```
Example A
Step self-certainty: 1.244, 1.085, 1.165
Final self-certainty: 1.164

Example B
Step self-certainty: 0.007, 0.005, 0.027
Final self-certainty: 0.013
```
So Example A has much higher self-certainty, which means the model is much more confident across the sequence.


Using above method, each chunk is assigned a DP score or Self-Certainty Score

## Workflow Overview

## Mixture-Embedding RAG



query -> embedding Model 1-> e_q,1 = g_1(q) , embedding chunk e_c_j,i = g(c_j),   top 3 most similiar [g1(c_1), g1(c_2), g1(c_3)]
query -> embedding Model 2-> e_q,2 = g_2(q) , embedding chunk e_c_j,i = g(c_j),   top 3 most similiar [g2(c_2), g2(c_3), g2(c_4)]
query -> embedding Model 3-> e_q,3 = g_3(q) , embedding chunk e_c_j,i = g(c_j),   top 3 most similiar [g3(c_1), g3(c_3), g3(c_4)] 

after calculate the similiarity score of each model-chunk, assume chunk_2, chunk_3, chunk_4 are the top 3.

because you use multiple embedding model to select the top 3 performed chunk. 
then what embedding model you use for RAG query and chunk? You only select chunk candidate, but there are multiple embedding model you used. which one you used for production?
" This table illustrates the performance when using retrieved information from 2 to 4 different embedding models randomly (denoted as 2 Embs to 4 Embs)," does this mean, when in production, you randomly select the embedding model?



### Confident RAG

query -> embedding Model 1-> e_q,1 = g_1(q) , embedding chunk e_c_j,i = g(c_j),   top 3 most similiar [g1(c_1), g1(c_2), g1(c_3)] -> answer [ token1(pr_1), token2(pr_2), ...token_i(pri) -> Confidence(Answer_1)

query -> embedding Model 2 -> ... -> Confidence(Answer_2)
query -> embedding Model 3 -> ... -> Confidence(Answer_3)


Max(Confidence(Answer_1), Confidence(Answer_2), Confidence(Answer_3))


### Summary

The ensemble is at different level for two methods. 
- Mixture-embedding is conducted at Top-k chunk level
- Confident embedding is conducted at answer selection level


I had a feeling that confident RAG works better when you had one embedding which is familiar with the topic(in this case, mathematics), and the confident answer is dominated by this embedding. Other embedding may compensate its weakness, there might be question where dominate embedding not as competitive as ususal; other "supporting-role" embedding can assist.

for mixture embedding, because you normalized the similarity. therefore, even bad performance embedding could still vote. It is kind of like random forest where it ignore dominate features, let other features not overshadowed by the dominated one.  it is kind of like a show, where main actor and supporting actor compete at the same level.
Therefore, this kind of method is even slightly worse the dominate embedding. especially when it works with math-specialized llm model(Qwen2.5-Math-7B)

> if you do not normalize similiarity, would the mixture-embedding perform worse than confident rag?

But I wouldn't simply consider mixture embedding is worse than confident modeling. 

what if right now, you are dealing with a complicated corpus, not just math, but ambiguous corpus. There is no dominated embedding which overshadowed other candidates. In this unknown case, maybe mixture embedding works better. 























