

- https://github.com/thuml/Time-Series-Library


- https://colab.research.google.com/drive/1PpGaOkm81ceO38s5uzlPeeTv0wlsXw2_

  ```
  think time series as sentence ──┬── Text-Transformer ──────────────── Chronos/TimeGPT
                                  └── Text-LLM ────────┬── Prompt Engineering
                                                       └── Fine-tuning / Change Embedding

  think time series as 2D-figure ─┬── Image-Transformer ─────────────── TimesNet
                                  └── Image-Multimodal LLM ────────────── TAMA
  ```

---

## Image

### Image-Transformer-TIMESNET:

<details>
  
- TIMESNET: TEMPORAL 2D-VARIATION MODELING FOR GENERAL TIME SERIES ANALYSIS

1. The model discovers multiple **periodic** patterns via FFT (not strictly frequency-domain features) — real-world signals often have several overlapping periodicities simultaneously.

2. For each period, it reshapes the 1D time series into a 2D tensor,
   where one axis represents intra-period variation (the shape within one cycle) and the other represents inter-period variation (how the same phase compares across cycles).

3. This 2D representation is then processed like an image using CNN
   (specifically inception-style convolution blocks) to extract temporal patterns and perform forecasting.

<img width="1173" height="369" alt="image" src="https://github.com/user-attachments/assets/1b032e1d-a7f5-417b-ab3d-d2eb3964c60d" />

Applying CNN-Inception blocks across different frequencies

<img width="1144" height="427" alt="image" src="https://github.com/user-attachments/assets/241900af-e349-48a3-832d-75229c588868" />


</details>

### image-multi-modal LLM 

<details>

- See it, Think it, Sorted: Large Multimodal Models are Few-shot Time Series Anomaly Analyzers
- Can Multimodal LLMs Perform Time Series Anomaly Detection?

Core idea: render time series as line charts and feed them into a multimodal LLM, which detects anomalies and generates a natural language explanation of *why*.

Two major challenges in TSAD:
1. **Model heterogeneity / dataset-dependence** — traditional detectors must be retrained for each domain; a multimodal LLM can transfer across domains with only a few in-context examples.
2. **Interpretability** — conventional detectors output a score or binary label with no explanation; multimodal LLMs produce a human-readable diagnosis alongside the detection result.

</details>

---

## Text



### Text-Transformer: Chronos

- https://github.com/GeneSUN/Generative-AI/blob/main/TimeSeries/Chronos.md
- https://www.nixtla.io/docs/introduction/why_timegpt


### Text-LLM forecasters

<details>

#### LLM Prompt Engineering
  
- [Large language models can be zero-shot anomaly detectors for time series?](https://arxiv.org/pdf/2405.14755v3)
- PromptCast: A New Prompt-based Learning Paradigm for Time Series Forecasting

LLMTIME does NOT pre-train or fine-tune an LLM on time series data. Instead, it transforms time series into tokens, feeds them into a general-purpose LLM, and extracts the result.
- **How tokenization works**: values are rescaled and serialized as plain-text decimal strings; each digit becomes a separate token, so scaling and precision choices are critical.
- **How outputs are converted back**: the LLM's token probability distribution over digits is decoded and parsed back into a scalar.



#### Fine-tuning pretrained LLMs
**Time-LLM**: Time series forecasting by reprogramming large language models — learns a lightweight reprogramming layer that translates time series patches into text-like tokens, while keeping the LLM backbone frozen.

#### Criticism
1. **No real gain over simple models**
  - Well-tuned linear models (e.g., DLinear) often match or outperform LLM-based forecasters on standard benchmarks
  - Weak evidence that LLMs truly "understand" time series — shuffling the numeric serialization barely degrades performance
  - Poor uncertainty calibration — GPT-4 even performs worse than GPT-3 on some benchmarks
2. **Extremely inefficient** — uses billions of parameters for a regression task that a lightweight model handles comparably

</details>

---


## Appendix

### Example of Fine-tuning pretrained LLMs

### Example of Prompt Time series
https://nixtlaverse.nixtla.io/neuralforecast/models.timellm.html

```
prompt_prefix = "The dataset contains data on monthly air passengers. There is a yearly seasonality"

timellm = TimeLLM(h=12,
                 input_size=36,
                 llm='openai-community/gpt2',
                 prompt_prefix=prompt_prefix,
                 batch_size=16,
                 valid_batch_size=16,
                 windows_batch_size=16)

nf = NeuralForecast(
    models=[timellm],
    freq='ME'
)

```


```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

# --- Step 1: Raw time series data ---
dates = ["Aug 16", "Aug 17", "Aug 18", "Aug 19", "Aug 20"]
temps = [78, 81, 83, 84, 84]
target_date = "Aug 21"

# --- Step 2: Convert to natural language prompt ---
values_str = ", ".join(str(t) for t in temps)

user_prompt = (
    f"From {dates[0]} to {dates[-1]}, the average temperature "
    f"was {values_str} degrees on each day. "
    f"What is the temperature going to be on {target_date}? "
    f"Reply only in this format: 'The temperature will be X degree.'"
)

# --- Step 3: Call OpenAI ---
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a time series forecasting assistant. "
                "Given historical data as a sentence, predict the next value. "
                "Always respond in the format: 'The temperature will be X degree.'"
            )
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ],
    temperature=0  # deterministic output for forecasting
)

prediction = response.choices[0].message.content
print("Prediction:", prediction)
# → "The temperature will be 82 degree."

# --- Step 4: Parse the number out if needed ---
import re
match = re.search(r"[\d.]+", prediction)
predicted_value = float(match.group()) if match else None
print("Parsed value:", predicted_value)  # → 82.0
```




## Reference

- [Chronos: Learning the Language of Time Series](https://arxiv.org/pdf/2403.07815)
- [See it, Think it, Sorted: Large Multimodal Models are Few-shot Time Series Anomaly Analyzers](https://arxiv.org/pdf/2411.02465)

- [Can Multimodal LLMs Perform Time Series Anomaly Detection?](https://arxiv.org/pdf/2502.17812)

- [MMAD: A COMPREHENSIVE BENCHMARK FOR MULTIMODAL LARGE LANGUAGE MODELS IN INDUSTRIAL ANOMALY DETECTION](https://arxiv.org/pdf/2410.09453?)
- [Anomaly Detection of Tabular Data Using LLMs](https://arxiv.org/pdf/2406.16308)
- [RATFM: Retrieval-augmented Time Serie Foundation Model for Anomaly Detection](https://arxiv.org/pdf/2506.02081)  (weak)
- [OpenRCA: Can Large Language Models Locate the Root Cause of Software Failures?](https://openreview.net/forum?id=M4qNIzQYpd)
