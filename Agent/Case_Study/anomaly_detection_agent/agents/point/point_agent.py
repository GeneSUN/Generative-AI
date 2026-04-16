"""
Point Anomaly Agent — main agent loop.

Follows the procedure defined in skill.md:

  Step 1  Validate input
  Step 2  Understand user intent  →  select tool(s)
  Step 3  Run tool(s) via Anthropic tool-use loop
  Step 4  Build output DataFrame
  Step 5  Return plain-language summary

Architecture
------------
                    ┌─────────────────────────┐
  user_request  ──► │   Claude (LLM)          │ ◄── system prompt (skill.md rules)
  series info   ──► │   decides which tool(s) │
                    └──────────┬──────────────┘
                               │ tool_use block(s)
                    ┌──────────▼──────────────┐
                    │  Dispatch loop          │
                    │  arima_run_tool()       │ ◄── series_df (Python memory)
                    │  kde_run_tool()         │
                    └──────────┬──────────────┘
                               │ compact result summary
                    ┌──────────▼──────────────┐
                    │   Claude (LLM)          │
                    │   final summary text    │
                    └─────────────────────────┘

Key design decisions
--------------------
- The series DataFrame never enters the API messages. Only scalar parameters
  travel through tool_use blocks; the DataFrame stays in Python memory.
- The tool result sent back to the model is a compact dict (counts + flagged
  indices), not the full records. This keeps the context window manageable.
- For ensemble (both tools), the Python layer combines results with AND logic
  after the loop ends. The model does not need to merge DataFrames.

Usage
-----
    from agents.point.point_agent import run_point_agent

    result_df, summary = run_point_agent(
        series_df=df,
        time_col="timestamp",
        value_col="value",
        user_request="Are there any recent spikes unusual given the historical trend?",
        sensitivity="medium",
    )
"""

import json
import os

import anthropic
import pandas as pd

from agents.point.tools.arima import TOOL_SCHEMA as ARIMA_SCHEMA
from agents.point.tools.arima import run_tool as arima_run_tool
from agents.point.tools.kde import TOOL_SCHEMA as KDE_SCHEMA
from agents.point.tools.kde import run_tool as kde_run_tool

# ── Constants ──────────────────────────────────────────────────────────────────

DEFAULT_MODEL = "claude-sonnet-4-6"

# Registry: tool name (as declared in TOOL_SCHEMA) → Python executor
_TOOL_EXECUTORS = {
    "arima_anomaly_detector": arima_run_tool,
    "kde_anomaly_detector":   kde_run_tool,
}

# All schemas passed to the API so the model knows what tools exist
_TOOL_SCHEMAS = [ARIMA_SCHEMA, KDE_SCHEMA]

# ── System prompt ──────────────────────────────────────────────────────────────
# Embeds the core rules from skill.md so the model knows how to behave.

_SYSTEM_PROMPT = """
You are the Point Anomaly Agent. You detect point-level anomalies in a single
univariate time series. Follow this procedure exactly.

## Step 2 — Understand User Intent

Identify what kind of anomaly the user cares about, then pick a tool:

| Intent | Tool |
|---|---|
| New point deviates from historical temporal pattern (trend, seasonality, autocorrelation) | arima_anomaly_detector |
| New point is rare in the historical value distribution, regardless of time | kde_anomaly_detector |
| Both perspectives required ("make sure", "confirm", "double check") | call both in parallel |

Ambiguous intent: use arima_anomaly_detector if the series has trend or
seasonality; use kde_anomaly_detector if the series appears stationary.

## Step 3 — Call Tool(s)

State which tool(s) you selected and why. Then call them.

The series DataFrame is held in Python memory — do NOT ask for raw data.
Only pass scalar parameters in the tool call (time_col, value_col, split_idx, etc).
The sensitivity parameter will be injected automatically if you omit it.

ARIMA: best for temporal pattern deviation. Score > 1 = outside prediction interval.
KDE:   best for distribution-based monitoring. Score > 1 = below density threshold.
       split_idx=0 scores all rows; split_idx=N scores only the last N rows.

For ensemble: call both tools. The Python layer will combine results with AND logic
(a point is anomalous only if both tools flag it).

## Step 5 — Summarize

After receiving tool results, provide a plain-language summary covering:
- How many points were flagged out of how many scored
- Which tool(s) were used and why
- What the flagged points have in common (all high? all low? clustered in time?)
- Any caveats (e.g. short series, possible false positives)
""".strip()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _validate(
    series_df: pd.DataFrame, time_col: str, value_col: str
) -> str | None:
    """Return an error string if validation fails, else None."""
    if time_col not in series_df.columns:
        return (
            f"time_col '{time_col}' not found. "
            f"Available columns: {list(series_df.columns)}"
        )
    if value_col not in series_df.columns:
        return (
            f"value_col '{value_col}' not found. "
            f"Available columns: {list(series_df.columns)}"
        )
    if not pd.api.types.is_numeric_dtype(series_df[value_col]):
        return (
            f"value_col '{value_col}' is not numeric "
            f"(dtype: {series_df[value_col].dtype})"
        )
    n_valid = series_df[value_col].notna().sum()
    if n_valid < 10:
        return f"Too few non-NaN values: {n_valid}. Minimum required: 10."
    return None


def _describe_series(
    series_df: pd.DataFrame, time_col: str, value_col: str
) -> str:
    """
    Build a compact text description of the series to include in the first
    user message. Gives the model enough context to pick the right tool
    without sending the raw data.
    """
    s = series_df[value_col].dropna()
    return (
        f"Series info:\n"
        f"  total rows   : {len(series_df)} ({s.notna().sum()} non-NaN)\n"
        f"  time_col     : '{time_col}'\n"
        f"  value_col    : '{value_col}'\n"
        f"  value range  : [{s.min():.4g}, {s.max():.4g}]\n"
        f"  mean / median: {s.mean():.4g} / {s.median():.4g}\n"
        f"  std          : {s.std():.4g}\n"
        f"  time range   : {series_df[time_col].iloc[0]} → {series_df[time_col].iloc[-1]}"
    )


def _compact_tool_result(
    raw: dict, result_df: pd.DataFrame, value_col: str
) -> dict:
    """
    Build the compact dict sent back to the model after a tool call.
    Sending full records would be too large; the model only needs counts
    and the details of flagged points to write a useful summary.
    """
    flagged = result_df[result_df["is_anomaly"]]
    return {
        "anomaly_count":   raw["anomaly_count"],
        "total_points":    raw["total_points"],
        "scored_points":   raw.get("scored_points", raw["total_points"]),
        "flagged_indices": flagged.index.tolist(),
        "flagged_values":  flagged[value_col].round(4).tolist(),
        "flagged_scores":  flagged["anomaly_score"].round(4).tolist(),
        "flagged_reasons": flagged["anomaly_reason"].tolist(),
    }


def _combine_ensemble(
    arima_df: pd.DataFrame, kde_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Combine two result DataFrames using AND logic:
    a point is anomalous only if BOTH tools flag it.
    ARIMA score is used as the primary anomaly_score.
    Both tools' reasons are merged into anomaly_reason.
    """
    result = arima_df.copy()
    result["is_anomaly"] = arima_df["is_anomaly"] & kde_df["is_anomaly"]

    reasons = []
    for a_flag, a_reason, k_flag, k_reason in zip(
        arima_df["is_anomaly"], arima_df["anomaly_reason"],
        kde_df["is_anomaly"],   kde_df["anomaly_reason"],
    ):
        if a_flag and k_flag:
            reasons.append(f"[ARIMA] {a_reason} | [KDE] {k_reason}")
        else:
            reasons.append("")

    result["anomaly_reason"] = reasons
    return result


# ── Main agent ─────────────────────────────────────────────────────────────────

def run_point_agent(
    series_df: pd.DataFrame,
    time_col: str,
    value_col: str,
    user_request: str,
    sensitivity: str = "medium",
    id_col: str | None = None,  # noqa: ARG001 — preserved by tools automatically
    model: str = DEFAULT_MODEL,
    api_key: str | None = None,
    max_iterations: int = 10,
) -> tuple[pd.DataFrame | None, str]:
    """
    Run the point anomaly agent.

    Parameters
    ----------
    series_df : pd.DataFrame
        Input series. Must contain time_col and value_col.
    time_col : str
        Name of the timestamp or sequence column.
    value_col : str
        Name of the numeric value column to analyze.
    user_request : str
        Plain-language description of what the user wants to detect.
    sensitivity : str
        'low', 'medium', or 'high'. Injected into every tool call.
    id_col : str | None
        Optional identifier column. Declared for API consistency — the tools
        preserve all original columns automatically, so no explicit handling
        is needed here.
    model : str
        Anthropic model ID.
    api_key : str | None
        Anthropic API key. Falls back to ANTHROPIC_API_KEY env var.
    max_iterations : int
        Safety cap on the tool-use loop (prevents infinite loops).

    Returns
    -------
    result_df : pd.DataFrame | None
        Original DataFrame with three columns appended:
          is_anomaly, anomaly_score, anomaly_reason.
        None if input validation failed.
    summary : str
        Plain-language summary from the agent, or an error message.
    """

    # ── Step 1: Validate ───────────────────────────────────────────────────────
    error = _validate(series_df, time_col, value_col)
    if error:
        return None, f"Input validation failed: {error}"

    # ── Build Anthropic client ─────────────────────────────────────────────────
    client = anthropic.Anthropic(
        api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
    )

    # ── Build the first user message ───────────────────────────────────────────
    # Include the user's request + a compact series description so the model
    # has enough context to pick the right tool without seeing raw data.
    first_message = (
        f"{user_request}\n\n"
        f"{_describe_series(series_df, time_col, value_col)}\n\n"
        f"sensitivity : {sensitivity}\n"
        f"time_col    : {time_col}\n"
        f"value_col   : {value_col}"
    )

    messages = [{"role": "user", "content": first_message}]

    # Accumulates result DataFrames keyed by tool name.
    # Used in Step 4 to build the final output DataFrame.
    tool_result_dfs: dict[str, pd.DataFrame] = {}

    # ── Step 3: Tool-use loop ──────────────────────────────────────────────────
    #
    # Each iteration:
    #   1. Send messages → model responds
    #   2. If stop_reason == "end_turn": model is done, collect summary text
    #   3. If stop_reason == "tool_use": dispatch each tool_use block,
    #      send tool_result(s) back, repeat
    #
    summary = "Agent did not produce a summary."

    for _ in range(max_iterations):

        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=_SYSTEM_PROMPT,
            tools=_TOOL_SCHEMAS,
            messages=messages,
        )

        # Append assistant turn to history
        messages.append({"role": "assistant", "content": response.content})

        # ── Agent finished ─────────────────────────────────────────────────────
        if response.stop_reason == "end_turn":
            summary = " ".join(
                block.text
                for block in response.content
                if hasattr(block, "text")
            )
            break

        # ── Dispatch tool calls ────────────────────────────────────────────────
        tool_results_content = []

        for block in response.content:
            if block.type != "tool_use":
                continue

            tool_name  = block.name
            tool_input = dict(block.input)   # mutable copy

            # Inject sensitivity so the model doesn't need to remember it
            tool_input.setdefault("sensitivity", sensitivity)

            executor = _TOOL_EXECUTORS.get(tool_name)

            if executor is None:
                payload = {"error": f"Unknown tool '{tool_name}'."}
            else:
                raw       = executor(series_df=series_df, tool_input=tool_input)
                result_df = pd.DataFrame(raw["records"])
                tool_result_dfs[tool_name] = result_df
                payload   = _compact_tool_result(raw, result_df, value_col)

            tool_results_content.append({
                "type":        "tool_result",
                "tool_use_id": block.id,
                "content":     json.dumps(payload),
            })

        messages.append({"role": "user", "content": tool_results_content})

    else:
        summary = (
            f"Agent reached the maximum of {max_iterations} iterations "
            "without completing. Returning partial results."
        )

    # ── Step 4: Build output DataFrame ────────────────────────────────────────
    if not tool_result_dfs:
        return None, summary

    if len(tool_result_dfs) == 2:
        # Ensemble: both tools ran — combine with AND logic
        result_df = _combine_ensemble(
            arima_df=tool_result_dfs["arima_anomaly_detector"],
            kde_df=tool_result_dfs["kde_anomaly_detector"],
        )
    else:
        result_df = next(iter(tool_result_dfs.values()))

    return result_df, summary
