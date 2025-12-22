# Wi-Fi score data-augmented RAG pipeline

<img width="795" height="647" alt="Untitled" src="https://github.com/user-attachments/assets/1084ee12-b62a-4300-bca7-068bb8067dcf" />


# Step 1 - SQL data Input

## 1.1. Query data by customer ID

```
    {
        "customer_id": "CUST_002",
        "wifi_score": 55,
        "coverage_score": 60,
        "speed_score": 50,
        "reliability_score": 58,
        "avg_rssi": -71,
        "avg_snr": 18,
        "packet_loss_pct": 6.8,
        "latency_ms": 95,
        "retransmission_pct": 14.2
    }
```

## 1.2 Convert structured data → natural language

LLMs reason better over textual summaries than raw tables.

```python

              Customer Wi-Fi Performance Summary:

              Overall Wi-Fi Score: 55
              Coverage Score: 60
              Speed Score: 50
              Reliability Score: 58

              Network KPIs:
              - Average RSSI: -71 dBm
              - Average SNR: 18 dB
              - Packet Loss: 6.8 %
              - Latency: 95 ms
              - Retransmission Rate: 14.2 %


```


## Step 2 — Retrieve relevant KPI explanations from RAG




```python

def retrieve_kpi_context(query: str, retriever, top_k: int = 5) -> str:
    results = retriever.retrieve(query=query, top_k=top_k)

    context = "\n\n".join(
        f"[Source {i+1}]\n{r.text}"
        for i, r in enumerate(results)
    )
    return context

```

**rag_query != user_query, derive a retrieval query from the user question**

### Step 2.1 classify the user question

Before retrieval, determine what kind of question the user is asking.

| Question type      | Example                             |
| ------------------ | ----------------------------------- |
| Diagnosis          | “Why is my Wi-Fi score low?”        |
| Metric explanation | “What does SNR mean?”               |
| Score calculation  | “How is Wi-Fi score computed?”      |
| Comparison         | “Why is speed worse than coverage?” |
| Recommendation     | “How can I improve my Wi-Fi?”       |
| Trend / anomaly    | “Why did the score drop last week?” |




### Step 2.2 generate a retrieval-focused query



## Step 3 — LLM prompt + data + RAG context


### 3.1 Define a small set of prompt “modes”

Think in intent-driven templates, not free-form prompts.

```
PROMPT_TEMPLATES = {
    "diagnosis": "...",
    "explanation": "...",
    "recommendation": "...",
    "comparison": "...",
}
```


### 3.2 Route user questions to a mode

```python
def classify_question(user_query: str) -> str:
    q = user_query.lower()
    if "why" in q or "issue" in q or "problem" in q:
        return "diagnosis"
    if "what is" in q or "explain" in q:
        return "explanation"
    if "how to improve" in q or "recommend" in q:
        return "recommendation"
    if "compare" in q or "difference" in q:
        return "comparison"
    return "diagnosis"
```

### 3.3 Parameterize your prompt

```python
def build_prompt(
    intent: str,
    user_query: str,
    customer_metrics: str,
    rag_context: str
) -> str:
    intent_config = {
        "diagnosis": {
            "role": "You are a network performance engineer.",
            "task": [
                "Diagnose the root causes",
                "Tie each issue to specific KPIs",
                "Avoid speculation",
            ],
        },
        "explanation": {
            "role": "You are a Wi-Fi expert.",
            "task": [
                "Explain concepts clearly",
                "Do NOT diagnose the customer",
                "Use simple language",
            ],
        },
        "recommendation": {
            "role": "You are a Wi-Fi optimization specialist.",
            "task": [
                "Provide actionable recommendations",
                "Map each recommendation to KPIs",
            ],
        },
    }

    if intent not in intent_config:
        raise ValueError(f"Unsupported intent: {intent}")

    cfg = intent_config[intent]
    task_block = "\n".join(f"- {t}" for t in cfg["task"])

    return f"""
                {cfg["role"]}
                
                User question:
                {user_query}
                
                Customer Metrics:
                {customer_metrics}
                
                Reference Knowledge:
                {rag_context}
                
                Task:
                {task_block}
                """.strip()


```

## Step 4: Putting it all together (clean pipeline)
```python
def answer_user_question(customer_id: str, user_query: str, retriever, llm):
    # 1) Get structured data
    data = get_customer_row(customer_id)
    customer_text = format_customer_metrics(data)

    # 2) Classify intent
    intent = classify_question(user_query)

    # 3) Build retrieval query
    rag_query = build_rag_query(user_query)

    # 4) Retrieve reference knowledge
    rag_context = retrieve_kpi_context(rag_query, retriever)

    # 5) Build prompt dynamically
    prompt = build_prompt(
        intent=intent,
        user_query=user_query,
        customer_metrics=customer_text,
        rag_context=rag_context,
    )

    # 6) LLM inference
    return llm.generate(prompt)
```






