# Prompt Chaining Workflow Pattern

## 1. Definition

Prompt chaining decomposes a complex task into a sequence of serial steps, where:


**Sequential Workflow**
- Steps are executed in a fixed order, one after another

**Independent LLM Calls**
- Each step invokes the model separately
- The task is not solved within a single prompt

**Explicit Information Flow**
- Outputs from one step are clearly passed forward
- Intermediate steps can include programmatic validation, such as:
  - Checking if the output is valid JSON
  - Verifying format or constraints
- Only after passing validation does the process proceed to the next step


```
Input
  │
  ▼
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  Step 1 │────▶│  Gate   │────▶│  Step 2 │────▶│  Step 3 │────▶ Output
│ LLM Call│     │Validate?│     │ LLM Call│     │ LLM Call│
└─────────┘     └────┬────┘     └─────────┘     └─────────┘
                     │ fail
                     ▼
                   Exit / Retry
```

---

## 2. Trade-offs (Why Use Prompt Chaining Instead of a Single LLM Call)

Analyzed across three dimensions: quality, cost, and speed.

**Quality**
- Single-call: reasoning is hidden (black box); early errors propagate undetected
- Chaining: breaks the black box into a transparent pipeline; intermediate outputs can be inspected, validated, and corrected; critical errors caught early

**Speed**
- Chaining introduces higher latency due to multiple calls
- However, this trade-off typically yields better accuracy

**Cost**
- Single-call: requires a large, expensive model for the entire task
- Chaining: allows task decomposition; simple steps use smaller models, complex steps use more powerful ones; overall cost becomes more controllable


---

## 3. When to Apply It (advantage)


Suitable when:
- The task can be decomposed into well-defined sub-tasks
- The sequence and responsibilities of these sub-tasks are stable
- There is no need for dynamic decision-making during execution


**Low error-cost scenarios** *(e.g., personal use, small-team content generation)*
- Prefer a single LLM call for efficiency

**High error-cost scenarios** *(e.g., enterprise branding, production systems)*
- Single-call reasoning happens inside a black box, making it hard to interpret or debug; prompt chaining breaks the task into steps, so the quality of each intermediate output is inspectable
- Processing too much information in a single call risks overlooking critical details; prompt chaining narrows the model's focus to one component at a time, reducing that risk

**when not use it**
- If the task requires holistic reasoning — where context and interdependencies span the entire problem — decomposing it into steps causes each call to lose sight of the whole, potentially producing a worse result than a single comprehensive call


> Try both one-call and prompt-chaining, compare their cost/speed and error

---


## *. Is agentic-Rag prompt chaining?



In a prompt chaining workflow, a task is decomposed into a fixed sequence of sub-tasks defined ahead of time. The pipeline is rigid — each step is predetermined, and the flow does not adapt based on intermediate outputs.

Agentic RAG, by contrast, is dynamic. The number of retrieval and reasoning iterations is not fixed but determined by the complexity of the task at hand. Because the agent continuously evaluates whether it has gathered sufficient information before proceeding, it more closely resembles an evaluator-optimizer pattern than a traditional prompt chaining workflow.
