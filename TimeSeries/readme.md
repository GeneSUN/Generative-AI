- [Chronos: Learning the Language of Time Series](https://arxiv.org/pdf/2403.07815)
- [See it, Think it, Sorted: Large Multimodal Models are Few-shot Time Series Anomaly Analyzers](https://arxiv.org/pdf/2411.02465)

- [Can Multimodal LLMs Perform Time Series Anomaly Detection?](https://arxiv.org/pdf/2502.17812)

- [MMAD: A COMPREHENSIVE BENCHMARK FOR MULTIMODAL LARGE LANGUAGE MODELS IN INDUSTRIAL ANOMALY DETECTION](https://arxiv.org/pdf/2410.09453?)
- [Anomaly Detection of Tabular Data Using LLMs](https://arxiv.org/pdf/2406.16308)
- [RATFM: Retrieval-augmented Time Serie Foundation Model for Anomaly Detection](https://arxiv.org/pdf/2506.02081)  (weak)
- [OpenRCA: Can Large Language Models Locate the Root Cause of Software Failures?](https://openreview.net/forum?id=M4qNIzQYpd)

## LLM-based forecasters

### LLM Prompt Engineering
- [Large language models can be zero-shot anomaly detectors for time series?](https://arxiv.org/pdf/2405.14755v3)
- PromptCast: A New Prompt-based Learning Paradigm for Time Series Forecasting

LLMTIME does NOT pre-train or fine-tune an LLM for time series, It transforms time series → tokens → feeds into a general LLM → gets result
- how the tokenization actually works
- how outputs are converted back to continuous values

### Fine-tuning pretrained LLMs,
Time-LLM: Time series forecasting by reprogramming large language models

#### Criticize
1. No real gain over simple models,
  - Some studies show LLMs don’t meaningfully improve forecasting
  - Weak evidence LLM “understands” time series
  - Poor uncertainty calibration, GPT-4 performs worse than GPT-3
2. Extremely inefficient, Uses billions of parameters















- 



