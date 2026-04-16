from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA
import pandas as pd
import numpy as np

# ── Tool schema ────────────────────────────────────────────────────────────────
# Passed to the Anthropic API tools=[...] parameter so the agent can invoke
# this tool by name. The series DataFrame is held in agent state and NOT
# included here — only scalar parameters travel through the tool call JSON.

TOOL_SCHEMA = {
    "name": "arima_anomaly_detector",
    "description": (
        "Detect point anomalies in the trailing window of a univariate time series "
        "using AutoARIMA forecast prediction intervals (novelty / online detection). "
        "Trains on all rows except the last `split_idx` observations, forecasts "
        "`split_idx` steps ahead, and flags held-out points that fall outside the "
        "prediction interval as anomalies. Training rows are always marked normal. "
        "Best for series with trend, complex autocorrelation, or unknown / irregular "
        "seasonal period. Requires ≥ 50 non-NaN training observations."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "time_col": {
                "type": "string",
                "description": "Name of the timestamp or sequence-index column in the DataFrame.",
            },
            "value_col": {
                "type": "string",
                "description": "Name of the numeric value column to analyze.",
            },
            "split_idx": {
                "type": "integer",
                "description": (
                    "Number of trailing observations reserved for the forecast horizon. "
                    "These are the only rows that can be flagged as anomalies. Default 24."
                ),
                "default": 24,
            },
            "season_length": {
                "type": "integer",
                "description": (
                    "Seasonal period passed to AutoARIMA "
                    "(e.g. 24 for hourly data with daily seasonality, "
                    "7 for daily data with weekly seasonality). Default 24."
                ),
                "default": 24,
            },
            "freq": {
                "type": "string",
                "description": (
                    "Pandas-compatible frequency string for the time index "
                    "(e.g. 'h' for hourly, 'D' for daily, 'W' for weekly). Default 'h'."
                ),
                "default": "h",
            },
            "sensitivity": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": (
                    "Controls how aggressively anomalies are flagged via the "
                    "prediction interval width: "
                    "low → 99% interval (fewest flags), "
                    "medium → 95% interval (default), "
                    "high → 90% interval (most flags)."
                ),
                "default": "medium",
            },
            "anomaly_direction": {
                "type": "string",
                "enum": ["both", "upper", "lower"],
                "description": (
                    "'both' flags spikes and dips (default), "
                    "'upper' flags only unusually high values, "
                    "'lower' flags only unusually low values."
                ),
                "default": "both",
            },
        },
        "required": ["time_col", "value_col"],
    },
}

# Maps the agent's sensitivity parameter to ARIMA confidence level.
# Lower sensitivity → wider interval → fewer anomalies flagged.
_SENSITIVITY_TO_CONFIDENCE = {
    "low":    99,
    "medium": 95,
    "high":   90,
}


class ARIMAAnomalyDetector:
    """
    Point anomaly detection using AutoARIMA forecast prediction intervals
    (novelty / online detection).

    Trains on all rows except the last `split_idx` observations, forecasts
    `split_idx` steps ahead, and flags held-out points that fall outside the
    prediction interval.  Training rows are passed through unchanged with
    is_anomaly=False.

    Parameters
    ----------
    series_df : pd.DataFrame
        Input DataFrame. Must contain time_col and value_col.
    time_col : str
        Name of the timestamp or sequence index column.
    value_col : str
        Name of the numeric value column to analyze.
    split_idx : int
        Number of trailing observations reserved for the forecast horizon.
    season_length : int
        Seasonal period passed to AutoARIMA.
    freq : str
        Pandas-compatible frequency string (e.g. 'h', 'D', 'W').
    sensitivity : str
        One of 'low', 'medium', 'high'. Maps to the prediction interval width.
    anomaly_direction : str
        Which side to flag: 'both', 'upper', or 'lower'.
    """

    def __init__(
        self,
        series_df: pd.DataFrame,
        time_col: str,
        value_col: str,
        split_idx: int = 24,
        season_length: int = 24,
        freq: str = "h",
        sensitivity: str = "medium",
        anomaly_direction: str = "both",
    ):
        self.series_df = series_df.sort_values(time_col).reset_index(drop=True)
        self.time_col = time_col
        self.value_col = value_col
        self.split_idx = split_idx
        self.season_length = season_length
        self.freq = freq
        self.sensitivity = sensitivity
        self.anomaly_direction = anomaly_direction
        self.confidence_level = _SENSITIVITY_TO_CONFIDENCE[sensitivity]

        self._model = StatsForecast(
            models=[AutoARIMA(season_length=season_length)],
            freq=freq,
            n_jobs=-1,
        )
        self._train_df: pd.DataFrame | None = None
        self._test_df: pd.DataFrame | None = None
        self._forecast_df: pd.DataFrame | None = None

    # ── Private helpers ────────────────────────────────────────────

    def _prepare_data(self) -> None:
        """Reshape input and split into train / test."""
        df = self.series_df[[self.time_col, self.value_col]].copy()
        df = df.rename(columns={self.time_col: "ds", self.value_col: "y"})
        df["unique_id"] = "series_1"
        self._train_df = df.iloc[: -self.split_idx].copy()
        self._test_df  = df.iloc[-self.split_idx :].copy()

    def _fit_forecast(self) -> None:
        """Fit AutoARIMA on training data and forecast the test horizon."""
        self._forecast_df = self._model.forecast(
            df=self._train_df,
            h=self.split_idx,
            level=[self.confidence_level],
        ).reset_index()

    def _detect(self) -> pd.DataFrame:
        """
        Compare held-out actuals to forecast intervals.
        Returns a DataFrame aligned with the test rows, with anomaly columns.
        """
        forecast = self._forecast_df.copy()
        test     = self._test_df.reset_index(drop=True)

        lo_col = f"AutoARIMA-lo-{self.confidence_level}"
        hi_col = f"AutoARIMA-hi-{self.confidence_level}"

        # Align on position (both have split_idx rows in the same order)
        y       = test["y"].values
        lo      = forecast[lo_col].values
        hi      = forecast[hi_col].values
        fitted  = forecast["AutoARIMA"].values

        is_low  = y < lo
        is_high = y > hi

        if self.anomaly_direction == "lower":
            is_anomaly = is_low
        elif self.anomaly_direction == "upper":
            is_anomaly = is_high
        else:
            is_anomaly = is_low | is_high

        half_width = (hi - lo) / 2
        with np.errstate(invalid="ignore"):
            score = np.abs(y - fitted) / np.where(half_width == 0, np.nan, half_width)

        reasons = pd.array([""] * self.split_idx, dtype=object)
        for i in range(self.split_idx):
            if is_low[i]:
                reasons[i] = (
                    f"Value ({round(y[i], 4)}) is below the "
                    f"{self.confidence_level}% lower prediction bound ({round(lo[i], 4)})"
                )
            elif is_high[i]:
                reasons[i] = (
                    f"Value ({round(y[i], 4)}) is above the "
                    f"{self.confidence_level}% upper prediction bound ({round(hi[i], 4)})"
                )

        result = test.copy()
        result["is_anomaly"]     = is_anomaly
        result["anomaly_score"]  = score
        result["anomaly_reason"] = reasons
        return result

    # ── Public API ─────────────────────────────────────────────────

    def run(self) -> pd.DataFrame:
        """
        Run the full detection pipeline.

        Returns
        -------
        pd.DataFrame
            Original series_df with three columns appended:
              is_anomaly    : bool   — True only for test-horizon rows that are flagged
              anomaly_score : float  — >1 means outside prediction interval; NaN for train rows
              anomaly_reason: str    — plain-language explanation; empty for normal / train rows
        """
        self._prepare_data()
        self._fit_forecast()
        test_results = self._detect()

        # Build output: training rows marked normal, test rows carry detection results
        n_train = len(self.series_df) - self.split_idx

        result = self.series_df.copy().reset_index(drop=True)
        result["is_anomaly"]     = False
        result["anomaly_score"]  = np.nan
        result["anomaly_reason"] = ""

        result.loc[n_train:, "is_anomaly"]     = test_results["is_anomaly"].values
        result.loc[n_train:, "anomaly_score"]  = test_results["anomaly_score"].values
        result.loc[n_train:, "anomaly_reason"] = test_results["anomaly_reason"].values

        return result


# ── Tool executor ──────────────────────────────────────────────────────────────
# Called by the agent's tool-dispatch loop when the model emits a
# tool_use block with name == "arima_anomaly_detector".
#
# The series DataFrame lives in agent state (not in the tool call JSON) to
# avoid bloating the context window with raw data. Only scalar parameters
# travel through tool_input.

def run_tool(series_df: pd.DataFrame, tool_input: dict) -> dict:
    """
    Execute ARIMAAnomalyDetector and return a JSON-serialisable result.

    Parameters
    ----------
    series_df : pd.DataFrame
        The full input DataFrame held in agent state.
    tool_input : dict
        Parameter dict from the model's tool_use block. Must contain
        'time_col' and 'value_col'; all other keys are optional.

    Returns
    -------
    dict
        JSON-serialisable result with keys:
          records        — list of row dicts (original columns + anomaly columns)
          anomaly_count  — number of flagged points (test horizon only)
          total_points   — total number of rows
          horizon_points — number of rows in the scored test horizon
    """
    detector = ARIMAAnomalyDetector(series_df=series_df, **tool_input)
    result_df = detector.run()
    return {
        "records":        result_df.to_dict(orient="records"),
        "anomaly_count":  int(result_df["is_anomaly"].sum()),
        "total_points":   len(result_df),
        "horizon_points": tool_input.get("split_idx", 24),
    }
