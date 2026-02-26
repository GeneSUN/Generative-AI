# Generative-AI

## ⭐ Situation
**1. At Verizon, I worked on a project to build a hierarchical Wi-Fi Metrics system to represent customer network performance.**

The system had multiple layers of metrics:

- Top level: Overall Wi-Fi Score (customer experience)
- Mid level: Speed/Coverage/Reliability
- Low level metrics: Latency/Upload/download throughput

While the scoring system successfully quantified network performance, stakeholders struggled to interpret the results.


**2. While the scoring system successfully quantified network performance, stakeholders struggled to interpret the results.**

For example: A customer might report unstable network experience, Analysts would see dozens of metrics changing

It was unclear:
- Which metrics were actually degraded?
- Which ones were symptoms vs root causes?
- Which metric engineers should investigate first?

**3. Another major challenge was domain knowledge complexity.**
Telecom metrics are highly specialized:
- Low SNR → may indicate interference
- High steering → may indicate poor coverage
- Reboot spikes → device instability

Non-experts — including product managers and analysts — could not translate metrics into actionable insights.

As a result:
- The Wi-Fi Score system was technically correct
- But difficult to operate.
Interpretability became a critical bottleneck.


## ⭐ Task

My task was to make the Wi-Fi Score system explainable and actionable so that:
- Analysts could quickly diagnose problems
- Engineers could identify root causes
- Product teams could understand customer experience drivers

Traditional dashboards and metric tables were insufficient, So I proposed building an **LLM-based explanation system using Retrieval-Augmented Generation (RAG).**
The goal was to enable users to ask questions like:
- "Why is this customer’s Wi-Fi score low?"
- "Is poor coverage causing reliability issues?"
- "Which metric should we fix first?"

RAG was ideal because it allows LLMs to **leverage domain-specific knowledge and private datasets**, improving accuracy and interpretability.


## Action:

**1) Turned raw KPI tables into LLM-friendly “customer narratives”**
- I pulled a single customer’s Wi-Fi score + sub-scores + KPI snapshot via SQL (e.g., Wi-Fi score, coverage/speed/reliability, RSSI, SNR, packet loss, latency, retransmission).
- Then I converted the structured row into a natural-language performance summary, because LLMs reason more reliably over concise textual context than raw tables.

Why this matters: this step made explanations customer-specific instead of generic metric definitions.


**2) Built a retrieval layer that fetches the right domain knowledge per question**

**1. First, I created a domain-specific knowledge base to support retrieval.**
This included two main sources:

- Telecom engineering documentation, which describes technical concepts such as RSSI, SNR, retransmissions, latency, and steering behavior.
- Custom Wi-Fi Score documentation that I designed myself, which explains:
  - How the Wi-Fi Score hierarchy is constructed
  - How each metric is defined
  - What each metric means operationally
  - How metrics relate to each other
  - How low-level KPIs influence mid-level scores like speed, coverage, and reliability
This documentation became the primary retrieval corpus for the RAG system.

**2). I then implemented a retrieval function that:**
- Converts the user question into a retrieval-focused query (rag_query)
- Searches the knowledge base
- Returns the top-k most relevant snippets
- Formats them into a structured context block:

**3) Designed Intent-Based Prompts**

**1. Different questions require different types of answers.**

For example:
- Diagnosis questions → identify root causes
- Explanation questions → explain the metrics
- Recommendation questions → suggest actions

Using one generic prompt often produced confusing or inconsistent answers, such as diagnosing problems when the user only wanted an explanation.


**2. So I designed a simple intent-based prompt framework.**

First, I classified questions into a few types:
- Diagnosis
- Explanation
- Recommendation

Then each type used a different prompt template so the model would respond in the right way.


## Result

### Measurable Explanation Accuracy

Since ground-truth labels for root causes do not exist, we evaluated the system by measuring:

**KPI-grounding accuracy**

For sampled cases:

- 90% of explanations correctly referenced degraded KPIs
- <10% contained irrelevant metrics

This ensured explanations were consistent with actual network data.

### Faster Root-Cause Analysis

Before the system:
- Analysts manually reviewed 20–50 KPIs per customer
- Root-cause analysis typically took 15–30 minutes per case

After deployment:
- Analysts could identify likely causes in 1–3 minutes using the generated explanations.

This reduced investigation time by approximately:

**~70–85% per case**

This allowed teams to analyze many more problem cases in batch investigations.


