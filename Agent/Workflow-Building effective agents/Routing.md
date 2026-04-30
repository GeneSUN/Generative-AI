# Routing Pattern

## 1. Definition

Routing is a system design pattern that classifies inputs before processing and directs them to different execution paths. It does not solve the task itself — it only decides which path should handle the input.

```
                            Type A
                         ┌──────────────────▶ [Path A: LLM Call] ──▶ (Out A)
                         │  Type B
(In) ──▶ [Classifier] ───┼──────────────────▶ [Path B: LLM Call] ──▶ (Out B)
                         │  Type C
                         └──────────────────▶ [Path C: LLM Call] ──▶ (Out C)
```


---


## 2. When to Use Routing (when not)

Use routing only if all three conditions are true:
- Inputs can be clearly classified with high confidence
- Different categories require fundamentally different handling logic
- A single shared pipeline would cause conflicts or degraded performance

**Advantage**
- **Distribution**: If you compact different requirment into one prompt, llm may lost its attention, or over-focus on certain categories, for example:
    - to improve performance on category A, you add constraint, which may degrade performance on category B
- **Debuggable**: Easy to debug which type of case cause low performance

**When not to use**: 
- **over-engineering**: if inputs are homogeneous and a single pipeline handles them well, routing is over-engineering

> This mirrors the case for prompt chaining: cramming all requirements into a single call dilutes the model's attention and risks important details being overlooked.


---

## 3. Relationship with Prompt Chaining

- **Routing** — decides which path to take
- **Prompt Chaining** — defines how that path is executed

> Routing and Prompt Chaining can be combined: routing selects the path, prompt chaining executes it.
