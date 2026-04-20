# Generative AI: A Practitioner's Journey

This repository traces the evolution of applied AI from its earliest engineering challenges to the frontier of agentic systems — organized not as a textbook, but as a story.

---

## The Story

### Chapter 1 — Prompt Engineering: Learning to Talk to AI

When LLMs became publicly accessible around 2022, the first bottleneck wasn't the model — it was us. We didn't know how to ask. A poorly framed question produced a generic, unreliable answer; the same question, reframed with explicit instructions, few-shot examples, or a chain-of-thought scaffold, could dramatically improve output quality.

Prompt engineering formalized this intuition:

- **Instruction prompting** — tell the model what to do *and* what not to do
- **Role prompting** — anchor the model's persona and perspective
- **Few-shot learning** — show examples rather than describe behavior
- **Chain-of-thought** — make reasoning explicit step-by-step

This wasn't just a bag of tricks. It was the first recognition that *how information enters the model matters as much as the model itself*.

→ [Prompt Engineering](Prompt%20Engineering/readme.md)

---

### Chapter 2 — RAG: Giving AI a Library

A well-prompted model is still bounded by what it was trained on. It doesn't know your internal documentation, your product specs, or last quarter's reports. Its knowledge has a cutoff date. It cannot memorize everything.

Retrieval-Augmented Generation (RAG) addressed this cleanly: **separate knowledge access from reasoning**. At query time, retrieve the most relevant documents from an external store and inject them into the prompt. The model focuses on synthesis; the retrieval layer handles knowledge.

The pipeline is straightforward in concept but nuanced in execution:

1. **Chunking** — break documents into retrievable units without losing meaning
2. **Embedding** — encode chunks as vectors in semantic space
3. **Indexing** — store in a vector database for efficient similarity search
4. **Retrieval** — select the most relevant chunks per query

RAG extended this further into multi-source retrieval (domain corpora, monitoring data, case histories) and eventually into *Agentic RAG*, where the model decides dynamically what to retrieve and when.

→ [RAG](RAG/readme.md)

---

### Chapter 3 — Agents: Giving AI a Toolkit

Knowing things is not enough. An agent that can only read and write text cannot browse a website, execute code, query a database, or send an email. AI is not omnipotent — but it can be equipped.

The agent paradigm provides the model with **tools**: discrete, callable functions that extend what it can do. Given the right tools and clear instructions, an LLM learns to select and sequence them appropriately based on the task at hand.

Simple agents scale naturally into complex workflows:

- **Prompt chaining** — break multi-step tasks into sequential calls
- **Routing** — direct inputs to the appropriate specialist
- **Parallelization** — run independent subtasks concurrently
- **Orchestrator-worker** — a coordinating agent delegates to specialized sub-agents
- **Evaluator-optimizer** — one agent critiques and refines another's output

This is where AI stopped being a question-answering interface and started resembling a *collaborative system*.

→ [Agent](Agent/readme.md) · [Building Effective Agents](Agent/Building%20effective%20agents/Readme.md) · [Agent Skills](Agent/Skills/)

---

### Chapter 4 — Context Engineering: Managing What AI Remembers

As context windows grew from 4K to 128K tokens and beyond, a new problem emerged: more space doesn't automatically mean better performance. Models can "lose the middle" — attention degrades for information buried in long contexts. Long multi-turn conversations accumulate noise. Relevant history competes with irrelevant history.

Context engineering is the practice of **deliberately curating what occupies the model's context window** at each step:

- What from the conversation history is worth preserving vs. compressing?
- When should working memory be written to external storage and retrieved later?
- How do you structure long interactions so the model stays grounded?

The ACE framework (Agentic Context Engineering) formalizes this with three roles: a **Generator** that acts, a **Reflector** that extracts generalizable insights from each interaction, and a **Curator** that updates a structured playbook over time. Each question makes the next one smarter.

This is the natural extension of RAG: RAG manages static knowledge; context engineering manages dynamic, session-level memory.

→ [Context Engineering](Context_Engineering/readme.md) · [ACE Framework](Discussion/agentic_context_engineering.md)

---

### Chapter 5 — Evaluation & Harness Engineering: Defining What Good Means

Throughout all of this, one question persisted: *how do you know if it's working?* AI can be fluent without being correct. It can be confident while being wrong. Without a standard, iteration is guesswork.

Evaluation is not just testing — it's defining the contract:

- What constitutes a correct answer for this task?
- What failure modes matter most?
- How do you measure quality across multi-step, non-deterministic behavior?

Harness engineering goes one step further: it **embeds evaluation and constraints directly into the system design**. Rather than auditing outputs after the fact, harnesses encode the standards — output format, safety boundaries, quality thresholds, orchestration rules — as first-class system components. Anthropic's Claude Code is a direct example: hooks, permission layers, and behavioral constraints are structural, not advisory.

This is the discipline that turns a capable model into a reliable product.

→ [Evaluation](Evaluation/readme.md) · [Anthropic](Anthropic/readme.md)

---

## The Unifying Framework

Looking back, the past three years produced many terms — but the underlying challenges reduce to three:

### Information — *AI is not omniscient*

Models have knowledge cutoffs. They don't know your data. They can't remember every conversation. The response: **RAG** extends knowledge externally at query time; **context engineering** manages memory dynamically within a session. Both are answers to the same question: *what does the model need to know, right now?*

### Tools — *AI is not omnipotent*

Models can reason, but they can't act without affordances. **Agents** provide those affordances. **Multi-agent systems** distribute capability: let the right agent, with the right tools, handle the right subtask. The orchestrator doesn't do everything — it delegates intelligently.

### Guardrails — *AI is not infallible*

Models hallucinate, drift, and optimize for the wrong objective. The answer is feedback: tight evaluation loops, adversarial test sets, iterative refinement. For multi-agent systems, this means explicit orchestration rules. For production systems, it means harness engineering — constraints baked in, not bolted on.

```
┌───────────────────────────────────────────────────────────────┐
│                     Generative AI Landscape                   │
├────────────────────┬──────────────────┬───────────────────────┤
│    Information     │      Tools       │      Guardrails        │
├────────────────────┼──────────────────┼───────────────────────┤
│ Prompt Engineering │ Agents           │ Evaluation            │
│ RAG                │ Multi-Agent      │ Harness Engineering   │
│ Context Engineering│ Agent Skills     │ Orchestration Rules   │
└────────────────────┴──────────────────┴───────────────────────┘
```

---

## Repository Map

| Section | Description |
|---|---|
| [Prompt Engineering](Prompt%20Engineering/readme.md) | Instruction prompting, few-shot, chain-of-thought |
| [RAG](RAG/readme.md) | Chunking, embedding, retrieval, agentic RAG |
| [Agent](Agent/readme.md) | Tool use, workflows, multi-agent patterns |
| [Context Engineering](Context_Engineering/readme.md) | Memory management, ACE framework |
| [Evaluation](Evaluation/readme.md) | Evaluation design, agent evals |
| [Anthropic](Anthropic/readme.md) | Claude API, Claude Code, harness engineering |
| [TimeSeries](TimeSeries/readme.md) | LLM applied to time series: forecasting and anomaly detection |
| [Discussion](Discussion/) | Cross-cutting topics: API vs. local, agentic context, blogs |

---

## Key References

- [Anthropic: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Anthropic: Equipping Agents with Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Anthropic: Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Agentic Retrieval-Augmented Generation: A Survey](https://arxiv.org/pdf/2501.09136)
- [Agentic Context Engineering](Context_Engineering/AGENTIC%20CONTEXT%20ENGINEERING-%20EVOLVING%20CONTEXTS%20FOR%20SELF-IMPROVING%20LANGUAGE%20MODELS.pdf)
