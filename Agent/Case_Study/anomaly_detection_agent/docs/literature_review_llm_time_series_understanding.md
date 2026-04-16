# Literature Review: How LLMs Understand Time Series

**Context:** This review was conducted to inform the design of `_describe_series()` in the Point Anomaly Agent — specifically, what representation of a time series should be passed to an LLM so it can make good tool-selection decisions.

---

## The Core Challenge

LLMs are trained on text. Time series are sequences of numbers. Bridging this gap is non-trivial: you cannot dump thousands of raw floats into a context window and expect meaningful reasoning. The question is: what representation of a time series is most useful for an LLM?

---

## Method 1 — Statistical / Numerical Representation

The most common baseline. Provide summary statistics + time-series-specific features.

**Sub-variants found in literature:**

- **Raw statistics**: mean, std, min, max, trend, lag — used in Time-LLM (ICLR 2024) and IJCAI 2024 surveys
- **Tokenization strategies**:
  - Round numbers as space-separated strings
  - CSV format (index + value per line)
  - Prompt-as-Prefix (PAP): include key statistics like mean, median, and trend in the prompt
  - Token-per-Digit (TPD): split floating-point numbers digit-by-digit to avoid tokenizer artifacts
- **ARIMA / model coefficients**: not widely adopted — LLMs do not reliably reason about AR/MA order or coefficient magnitudes
- **Integer-Decimal Decomposition** (Nature Scientific Reports, 2025): decomposes values into integer + decimal parts for better cross-modal alignment

**Verdict:** Statistics help, but are lossy. LLMs struggle with subtle numerical anomalies.

**Missing signals that matter for tool selection:**

| Signal | Why it matters |
|---|---|
| Trend | Drives ARIMA vs KDE choice |
| Seasonality / period | Determines `season_length` for ARIMA |
| Stationarity | Core decision signal |
| Autocorrelation | ARIMA fit quality |
| Skewness / heavy tails | KDE fit quality |
| Recent vs historical distribution shift | Novelty vs outlier mode |

---

## Method 2 — Text Description / Verbalization

Convert the series into natural language, e.g.:
> "The series shows a gradual upward trend with a sharp spike in the final 5 points."

- Used in **SIGLLM** and **Prompt-as-Prefix (PAP)** approaches
- Effective because it maps directly to the LLM's native modality
- Main challenge: how to generate the description reliably
  - Rule-based narrator (brittle but fast)
  - Another LLM pre-processing call (high quality but adds latency + cost)

---

## Method 3 — Image / Multimodal

Plot the series (e.g. with Matplotlib) and pass the image to a vision-capable LLM.

- **ICLR 2025 key finding** ("Can LLMs Understand Time Series Anomalies?"): **LLMs understand time series better as images than as text**
- LLMs can detect trivial/obvious anomalies visually, but struggle with subtle real-world ones
- Explicit chain-of-thought reasoning did not improve performance
- Requires a multimodal model (GPT-4V, Claude 3+)
- Used in AnomSeer, multimodal TSAD frameworks (MDPI 2025)

---

## Method 4 — Reprogramming / Embedding Alignment (fine-tuning)

- **Time-LLM** (ICLR 2024): reprograms time series patches into text-prototype embeddings more natural for the LLM, combined with declarative prompts
- Requires fine-tuning — not applicable in zero-shot / API-only settings

---

## Comparison for Zero-Shot Agent Use

| Method | Zero-shot | Works with Claude API | Quality |
|---|---|---|---|
| Extended statistics | Yes | Yes | Moderate |
| Text description (rule-based) | Yes | Yes | Good |
| Image (multimodal) | Yes | Yes (Claude 3+) | Best for obvious anomalies |
| Reprogramming | No (fine-tuning needed) | No | Best overall but heavy |

---

## Key Takeaways

1. **Images outperform text** for anomaly understanding in zero-shot settings (ICLR 2025).
2. **Statistics alone are insufficient** — trend, stationarity, and autocorrelation features should be added beyond mean/std.
3. **Text verbalization is promising** but requires a reliable description generator.
4. **LLMs can handle trivial anomalies** but fail on subtle real-world ones regardless of representation.
5. Fine-tuning approaches (Time-LLM) are strongest but out of scope for this agent's architecture.

---

## Relevance to This Project

The current `_describe_series()` function in `agents/point/point_agent.py` is a minimal Method 1 implementation. Based on this review, candidate improvements are:

- **Short-term**: Add trend, stationarity, and autocorrelation estimates to the statistical summary
- **Medium-term**: Add a rule-based text description (e.g. "series appears stationary with one recent spike")
- **Long-term**: Render a plot and pass it as an image for multimodal tool-selection decisions

---

## Sources

- [Large Language Models for Time Series: A Survey (IJCAI 2024)](https://arxiv.org/abs/2402.01801)
- [Time-LLM: Time Series Forecasting by Reprogramming LLMs (ICLR 2024)](https://arxiv.org/pdf/2310.01728)
- [Can LLMs Understand Time Series Anomalies? (ICLR 2025)](https://proceedings.iclr.cc/paper_files/paper/2025/file/05774fb74e863308c4b460c9f49f6918-Paper-Conference.pdf)
- [Can Multimodal LLMs Perform Time Series Anomaly Detection? (2025)](https://arxiv.org/pdf/2502.17812)
- [Multi-modal Time Series Analysis: A Tutorial and Survey (2025)](https://arxiv.org/html/2503.13709v1)
- [Empowering Time Series Analysis with LLMs: A Survey (IJCAI 2024)](https://www.ijcai.org/proceedings/2024/0895.pdf)
- [Integer-Decimal Decomposition for LLM Time Series Forecasting (Nature 2025)](https://www.nature.com/articles/s41598-025-06581-x)
- [Can LLMs Serve As Time Series Anomaly Detectors? (2024)](https://arxiv.org/html/2408.03475v1)
- [Exploring Multi-Modal LLMs for TSAD (MDPI 2025)](https://www.mdpi.com/2813-0324/11/1/22)
