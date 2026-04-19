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

## 2. Core Value: Separation of Concerns

Different types of inputs should not share the same optimization goal. Routing enables each path to focus on its own problem and avoids conflicts between competing objectives.

> This mirrors the case for prompt chaining: cramming all requirements into a single call dilutes the model's attention and risks important details being overlooked.

---

## 3. How Routing Is Implemented

Classification can be done using:
- An LLM
- Simple rules
- Traditional ML models

As long as the classification is reliable, the routing structure works.

---

## 4. When to Use Routing

Use routing only if all three conditions are true:
- Inputs can be clearly classified with high confidence
- Different categories require fundamentally different handling logic
- A single shared pipeline would cause conflicts or degraded performance

If these are not true, routing is likely over-engineering.

---

## 5. Relationship with Prompt Chaining

- **Routing** — decides which path to take
- **Prompt Chaining** — defines how that path is executed

> Routing and Prompt Chaining can be combined: routing selects the path, prompt chaining executes it.
