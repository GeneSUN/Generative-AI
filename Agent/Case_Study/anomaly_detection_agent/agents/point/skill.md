---
name: point-anomaly-agent
description: Detect point anomalies in a single univariate time series. A point anomaly is a single timestamp whose value is unusually high or low compared to the rest of the series. Use this agent when the user provides one series and asks to find spikes, dips, outliers, or unusual single values.
---

# Point Anomaly Agent

This agent detects point-level anomalies in one univariate time series.
It receives a single pandas DataFrame, inspects the series, selects the
appropriate tool, runs detection, and returns the original DataFrame with
anomaly labels appended.

---

## Input Contract

```
series_df : pd.DataFrame
    Required columns:
      time_col   — datetime, date string, or integer sequence index
      value_col  — numeric values (the signal to analyze)
    Optional column:
      id_col     — any identifier; carried through to output unchanged

time_col  : str   — name of the timestamp / sequence column
value_col : str   — name of the value column
id_col    : str | None — name of the ID column, or None

sensitivity : "low" | "medium" | "high"   (default: "medium")
    Controls how aggressively anomalies are flagged.
    low    → only extreme outliers flagged
    medium → standard threshold (default)
    high   → flag anything mildly unusual
```

**Input assumptions:**
- Exactly one series. Do not pass multiple series stacked in one DataFrame.
- The value column must be numeric. Raise an error if it is not.
- Missing values (NaN) in value_col: skip them in detection, carry them
  through to output with is_anomaly = False and anomaly_score = NaN.
- The series does not need to be sorted — sort by time_col on load.

---

## Step-by-Step Procedure

### Step 1 — Validate Input
Before doing anything else, verify:
- `time_col` and `value_col` exist in the DataFrame
- `value_col` is numeric
- At least 10 non-NaN values are present (minimum for meaningful detection)

If any check fails, return a clear error message. Do not attempt detection.

### Step 2 — Understand the User's Intent
Read the user's request and identify what kind of anomaly they care about.
This drives tool selection in Step 3.

| User intent | Signal phrases | Tool |
|---|---|---|
| New points deviate from historical temporal pattern | "unusual given the trend", "different from the forecast", "recent spike compared to pattern" | `arima.py` |
| New points are rare in the historical value distribution | "out of the historical range", "never seen before", "unusual value regardless of time" | `kde.py` |
| Both perspectives required | "make sure", "double check", "confirm from multiple angles" | both in parallel |

When the intent is ambiguous, default to `arima.py` if the series has visible
trend or seasonality, and `kde.py` if the series appears stationary.

### Step 3 — Select and Run Tool(s)

#### Case A — ARIMA only
Call `arima.py`. The tool trains AutoARIMA on the historical window and forecasts
a prediction interval for the new points. Points outside the interval are flagged.

- Pass: `time_col`, `value_col`, `split_idx`, `sensitivity`, `anomaly_direction`
- Score interpretation: `|actual − forecast| / half interval width`. Score > 1 = anomaly.
- Thresholding is handled internally. No separate threshold step needed.

#### Case B — KDE only
Call `kde.py`. The tool fits a Gaussian KDE on the historical distribution and
flags points whose density falls below the 1st-percentile training threshold
AND whose value lies in the specified tail.

- Pass: `time_col`, `value_col`, `split_idx`, `sensitivity`, `anomaly_direction`
- Score interpretation: `density_threshold / point_density`. Score > 1 = anomaly.
- Thresholding is handled internally. No separate threshold step needed.

#### Case C — Both in parallel (ensemble)
Call both `arima.py` and `kde.py` independently with the same inputs.
Combine results: flag a point as anomalous only if **both** tools flag it.

```
ensemble_is_anomaly = arima_is_anomaly AND kde_is_anomaly
```

Report both individual scores in the summary. The output DataFrame uses the
ensemble flag as `is_anomaly`. Include both tools' reasons in `anomaly_reason`.

State which tool(s) were selected and why before running.

### Step 4 — Build Output DataFrame
Append columns to the original DataFrame and return it.

### Step 5 — Summarize
After returning the DataFrame, provide a plain-language summary:
- How many points were flagged
- Which tool(s) were used and why
- What the flagged points have in common (all high? all low? clustered?)
- Any caveats (e.g., "series is short, ARIMA parameter estimates may be noisy")

---

## Output Contract

Returns the original DataFrame with these columns appended:

```
is_anomaly    : bool    — True if the point is flagged as anomalous
anomaly_score : float   — raw score from the detection tool (higher = more anomalous)
anomaly_reason: str     — plain-language explanation for flagged points,
                          empty string for normal points
```

**Output guarantees:**
- Row count and order are identical to input
- All original columns are preserved unchanged
- id_col (if provided) is untouched
- NaN values in value_col → is_anomaly = False, anomaly_score = NaN, anomaly_reason = "missing value"

**Example output:**

| time  | value | id | is_anomaly | anomaly_score | anomaly_reason     |
|-------|-------|----|------------|---------------|--------------------|
| 09:00 | 1.2   | A  | False      | 0.3           |                    |
| 09:01 | 98.7  | A  | True       | 8.1           | 8.1 std above mean |
| 09:02 | 1.1   | A  | False      | 0.2           |                    |

---

## Tool Reference

### `tools/arima.py`

**Question it answers:** *Given the historical temporal pattern, is this new point
surprising?*

Trains AutoARIMA on all rows except the last `split_idx` observations, then
forecasts `split_idx` steps ahead with a prediction interval. Points outside the
interval are flagged. The model captures trend, seasonality, and autocorrelation —
so the expected range shifts with the series structure.

| Parameter | Values | Effect |
|---|---|---|
| `split_idx` | integer ≥ 1 | Number of trailing points to score |
| `sensitivity` | low / medium / high | Interval width: 99% / 95% / 90% |
| `anomaly_direction` | both / upper / lower | Which tail to flag |
| `season_length` | integer | Seasonal period (e.g. 24 for hourly daily cycle) |
| `freq` | pandas freq string | Time index frequency (e.g. `'h'`, `'D'`) |

- **Score:** `|actual − forecast| / half interval width`. Score > 1 = outside interval.
- **Best for:** series with trend, seasonality, or complex autocorrelation.
- **Minimum data:** ≥ 50 training points for reliable parameter estimation.

---

### `tools/kde.py`

**Question it answers:** *Regardless of when it occurred, is this value rare in the
historical distribution?*

Fits a Gaussian KDE on the training data. Flags points whose density falls below
the 1st-percentile training threshold AND whose value lies in the specified tail.
Temporal order is irrelevant — the same value at any position would receive the
same score.

Two modes:
- **Outlier mode** (`split_idx=0`): trains and scores on the entire series.
  Use when looking for global outliers across the whole history.
- **Novelty mode** (`split_idx=N`): trains on all except last N rows, scores
  only the held-out window. Training rows are always marked normal.

| Parameter | Values | Effect |
|---|---|---|
| `split_idx` | 0 or integer ≥ 1 | 0 = outlier mode; N = novelty mode |
| `sensitivity` | low / medium / high | Directional tail: 99th / 97th / 95th percentile |
| `anomaly_direction` | both / upper / lower | Which value tail to flag |
| `bandwidth` | float | KDE smoothing width (default 0.5) |
| `filter_percentile` | float 0–100 | Trim training extremes before fitting (default 100 = keep all) |

- **Score:** `density_threshold / point_density`. Score > 1 = below density threshold.
- **Best for:** stationary or skewed series; distribution-based monitoring.
- **Minimum data:** ≥ 20 training points.

---

## Error Handling

---

## Examples

---

## Out of Scope

This agent does not:
- Detect subsequence anomalies (unusual segments or shapes)
- Accept more than one series at a time
- Use any external reference data
- Explain root causes of anomalies
- Impute or correct anomalous values
