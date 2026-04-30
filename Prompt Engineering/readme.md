# Prompt Engineering

A prompt is a conversation. Like any good conversation, it works best when you establish who you're talking to, give them the right context, tell them clearly what you want, show them how to think, and provide examples. Each of these is a distinct lever — and together they compose a complete prompt.

---

## 1. Who You Are — Role Prompting

<details>
<summary>

</summary>

Before asking anything, tell the model who it is. A well-defined role anchors tone, expertise level, and behavior throughout the conversation. Without it, the model defaults to a generic assistant.

```python
messages=[
    {"role": "system", "content": "You are a senior telecom network engineer specializing in 5G RAN troubleshooting."},
    {"role": "user",   "content": "Why is my handover failure rate spiking?"},
]
```

Role prompting is most effective when the role is specific and domain-relevant — not just "you are an expert" but "you are an expert in X who cares about Y."

</details>

---

## 2. Why You Care — Add Context

<details>
<summary>

</summary>

A role tells the model *who* it is; context tells it *why this matters*. Context shapes relevance: the same question answered differently for a beginner vs. an expert, for a quick decision vs. a deep investigation.

What to include:
- Background on the situation or system
- Constraints (time, audience, format)
- What has already been tried
- What "good" looks like for this task

```
Context: I'm debugging a production 5G network. The handover failure rate jumped from 2% to 18% after last night's config push. I've already checked RSSI and it looks normal.
```

Good context eliminates wrong answers before they happen.

</details>

---

## 3. What You Want — Instruction Prompting

<details>
<summary>

</summary>

Now tell the model exactly what to do — and what not to do. Explicit instructions reduce ambiguity and prevent the model from filling gaps with guesses.

```
- Identify the most likely root cause
- List the top 3 diagnostic steps in order of priority
- Do not speculate beyond the provided data
- If uncertain, say "I don't know" rather than guessing
- Keep the response under 200 words
```

Negative instructions ("do not", "avoid") are just as important as positive ones. They define the boundaries of acceptable behavior.

</details>

---

## 4. How to Think — Chain of Thought

<details>
<summary>

</summary>

For complex or multi-step tasks, tell the model to reason step by step before answering. This is chain-of-thought (CoT) prompting. It reduces errors by forcing intermediate reasoning to be explicit — and explicit reasoning can be checked.

```
Think step by step:
1. What does the symptom pattern suggest?
2. What are the possible causes?
3. Which cause best fits all the observed data?
Then give your final answer.
```

CoT is especially effective for math, logic, diagnosis, and any task where the answer depends on a chain of inferences. Without it, models often skip steps and hallucinate confident-sounding conclusions.

Variant — **zero-shot CoT**: simply append `"Think step by step."` to any prompt. Surprisingly effective with no examples needed.

</details>

---

## 5. Show, Don't Just Tell — Few-Shot Examples

<details>
<summary>

</summary>

After defining role, context, instructions, and reasoning style, examples lock in the exact format and behavior you want. One well-chosen example is often worth a paragraph of instruction.

```
Example input:  "Handover failure rate: 18%, RSSI: -72 dBm, Airtime util: 85%"
Example output: "Root cause: radio congestion. Primary suspect: high airtime utilization driving retransmissions. Recommended action: load balancing to adjacent cell."

Now analyze: "Handover failure rate: 22%, RSSI: -68 dBm, Airtime util: 43%"
```

- **Zero-shot**: no examples — relies on instruction alone
- **One-shot**: one example — establishes format
- **Few-shot**: 2–5 examples — establishes pattern and edge cases

Choose examples that cover the range of inputs you expect, including edge cases.

→ [Few-shot notebook](https://colab.research.google.com/drive/1DwfVi6N9wDOLUNC0uVTI18BCHy-w0k51#scrollTo=b_Cq1tfrEAWS)

</details>

---

## 6. Keep It Organized — XML Tags

<details>
<summary>

</summary>

As prompts grow in complexity — multiple sections, long context, nested instructions — plain text becomes hard to parse for both humans and models. XML tags provide explicit structure that the model can reliably reference.

```xml
<system>
  You are a senior telecom engineer.
</system>

<context>
  Handover failure rate spiked after config push.
</context>

<instructions>
  - Identify root cause
  - List top 3 diagnostic steps
  - Do not speculate
</instructions>

<examples>
  <example>
    <input>...</input>
    <output>...</output>
  </example>
</examples>

<question>
  Why is my handover failure rate at 18%?
</question>
```

Benefits:
- Prevents instructions from bleeding into context
- Makes long prompts maintainable
- Reduces model confusion on where one section ends and another begins

</details>

---

## Putting It Together

<details>
<summary>

</summary>

A complete, well-structured prompt follows this anatomy:

```
[Role]         → Who the model is
[Context]      → Why this matters and what's known
[Instructions] → What to do (and not do)
[Reasoning]    → How to think through it
[Examples]     → What good output looks like
[Question]     → The actual task
```

Not every prompt needs all six. Simple tasks may only need instructions and a question. Complex, high-stakes tasks benefit from the full structure.

</details>

---

## Reference

- [Claude Prompt Engineering Guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
- [Console Prompting Tools](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-tools)
- [Few-shot notebook](https://colab.research.google.com/drive/1DwfVi6N9wDOLUNC0uVTI18BCHy-w0k51#scrollTo=b_Cq1tfrEAWS)
