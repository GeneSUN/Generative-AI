[Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#output-and-formatting)

[Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)

1. tell the story use "STAR": 
- situation as system prompt, 
- Task include main question, and few-shot examples
- Action may give guidance of specific direction, or provide tools as agent
- Result specify what type of reponse, such as number, image, text, or probability; also include output formation
2. Refine with LLM,  [claude workbench](https://platform.claude.com/workbench/4ad89ea2-aa38-410d-86b3-563ccecaa68f?tab=prompt)
3. Evaluation

# Prompt Evaluation: A Machine Learning Perspective

<details>
<summary>## Comparison between Classical ML Pipeline and LLM</summary>

### Starting Point: The Classical ML Pipeline

A typical ML deployment pipeline looks like this:

```
Raw Data → Model Hyperparamter → Model → Prediction
```

During deployment (not training), the **model weights are frozen**. The only levers you control are upstream — how you clean, transform, and engineer your features before they reach the model.


### Mapping LLM to the ML Pipeline

An LLM pipeline mirrors this structure exactly:

```
Raw Question → Prompt Template → Claude (frozen) → Response
```

| ML Concept | LLM Equivalent |
|---|---|
| Raw data | User's question |
| Preprocessing / feature engineering | Prompt template |
| Frozen model | Claude (weights don't change) |
| Prediction | Claude's response |

The **prompt is your preprocessing step** — it transforms the raw input before it reaches the model. Just as different scalers or encoders produce different model outputs, different prompt designs produce different Claude responses.

---

### Prompt Engineering = Hyperparameter Tuning

In classical ML, once the model is trained, you do **hyperparameter tuning** — searching over configurations (learning rate, depth, regularization) to maximize a validation metric, while the model itself stays fixed.

**Prompt engineering is exactly this**, applied to LLMs:

- The model weights are frozen (you don't retrain Claude)
- You search over prompt configurations to maximize an eval score
- Each prompt variant is one "hyperparameter configuration"
- Your eval pipeline is your "validation loop"

Tools like **DSPy** even automate this search — the same way **Optuna** or **GridSearchCV** automates hyperparameter search in classical ML.

</details>

---

## The Evaluation Pipeline

### Step 1 — Build a Test Dataset

Before comparing prompt variants, you need a held-out test set. Each record contains:

- **Input (X):** the user question
- **Reference answer (y):** the ideal / ground truth response

```python
eval_dataset = [
    {"question": "What's 2+2?",          "ideal_answer": "4"},
    {"question": "How do I make oatmeal?","ideal_answer": "Boil water, add oats..."},
    {"question": "How far is the Moon?",  "ideal_answer": "~384,400 km from Earth"},
]
```

### Step 2 — Generate Predictions

Feed the test set through each prompt variant to collect predicted responses (ŷ):

```
prompt_v1(question) → Claude → response_v1
prompt_v2(question) → Claude → response_v2
```

Now for each record you have: **reference answer** and **predicted answer** — the same setup as classical model evaluation.

### Step 3 — Calculate Metrics

This is where LLM evaluation diverges from classical ML.

In classical ML, metrics are **deterministic formulas**:

| Task | Metric |
|---|---|
| Regression | MSE, RMSE, MAE |
| Classification | Precision, Recall, F1 |
| Ranking | NDCG, MAP |

In LLM evaluation, the metric computation itself involves a model — introducing a second layer of uncertainty:

| Evaluation Method | When to Use |
|---|---|
| **Manual (human) scoring** | Gold standard; slow and expensive |
| **LLM-as-a-judge** | Scalable; Claude grades Claude against a rubric |
| **Unit tests** | For code generation — does it run? Does it pass? |
| **RAGAS** | Standard framework for RAG pipelines |
| **Exact match / F1** | For structured outputs with deterministic answers |

> ⚠️ **Important caveat:** Unlike MSE which always returns the same value, LLM-as-a-judge is stochastic — the same response graded twice may get different scores. The grader also has its own biases (e.g. preferring longer answers). This means you need **multiple grading runs and averaging** to get stable scores — making LLM evaluation fundamentally noisier than classical evaluation.

### Step 4 — Compare and Decide

Assign a score to each prompt variant, then pick the best:

```
prompt_v1 → avg score: 7.66 / 10
prompt_v2 → avg score: 8.20 / 10  ← better
prompt_v3 → avg score: 8.70 / 10  ← best → ship this
```

This removes guesswork. You're making decisions from numbers, not intuition.

---

## Two Major Challenges:

1. Build test dataset
- LLM as generator
2. Define Success crtiria or Metrics
- Rarely measure correctness between reference answer and predicted answer, such as Q&A
- LLM as judge is risky
- Depend on each project. Some common task has standard metrcs, RAG use RAGAS
- Decompose the overall metrics into different critieria: Format, Valid Syntax
