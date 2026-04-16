from sklearn.neighbors import KernelDensity
import pandas as pd
import numpy as np

# ── Tool schema ────────────────────────────────────────────────────────────────

TOOL_SCHEMA = {
    "name": "kde_anomaly_detector",
    "description": (
        "Detect point anomalies in a univariate time series using Kernel Density "
        "Estimation (KDE). Fits a Gaussian KDE on training data, computes a density "
        "threshold from the 1st percentile of training densities, and flags test "
        "points whose density falls below this threshold AND whose value lies in the "
        "specified tail direction. "
        "Supports two modes: "
        "(1) outlier mode (split_idx=0) — trains and scores the entire series, "
        "useful for finding global outliers in a stationary distribution; "
        "(2) novelty mode (split_idx=N) — trains on all but the last N points, "
        "scores only the held-out window, useful for monitoring recent values. "
        "Best for: non-Gaussian or multimodal distributions, skewed series, "
        "or when you want a density-based rather than interval-based score. "
        "Requires ≥ 20 training observations."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "time_col": {
                "type": "string",
                "description": "Name of the timestamp or sequence-index column.",
            },
            "value_col": {
                "type": "string",
                "description": "Name of the numeric value column to analyze.",
            },
            "split_idx": {
                "type": "integer",
                "description": (
                    "0 → outlier mode: train and score on all data. "
                    "N → novelty mode: train on all except last N rows, "
                    "score only the last N rows. Default 0."
                ),
                "default": 0,
            },
            "bandwidth": {
                "type": "number",
                "description": (
                    "Bandwidth for the Gaussian KDE. Larger values produce a "
                    "smoother density estimate. Default 0.5."
                ),
                "default": 0.5,
            },
            "filter_percentile": {
                "type": "number",
                "description": (
                    "Trim extreme values from training data before fitting KDE. "
                    "100 = keep all (default). 95 = remove the outer 5% (2.5% each tail). "
                    "Useful when the training set itself contains outliers that would "
                    "distort the density estimate."
                ),
                "default": 100,
            },
            "sensitivity": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": (
                    "Controls the directional value threshold: "
                    "low → 99th percentile tail (fewest flags), "
                    "medium → 97th percentile tail (default), "
                    "high → 95th percentile tail (most flags)."
                ),
                "default": "medium",
            },
            "anomaly_direction": {
                "type": "string",
                "enum": ["both", "upper", "lower"],
                "description": (
                    "'both' flags values in either tail (default), "
                    "'upper' flags only unusually high values, "
                    "'lower' flags only unusually low values."
                ),
                "default": "both",
            },
        },
        "required": ["time_col", "value_col"],
    },
}

# Maps sensitivity → directional percentile threshold.
# A point must be both low-density AND in the specified value tail to be flagged.
# Higher percentile → stricter tail → fewer flags.
_SENSITIVITY_TO_PERCENTILE = {
    "low":    99,
    "medium": 97,
    "high":   95,
}


class KDEAnomalyDetector:
    """
    Point anomaly detection using Kernel Density Estimation.

    Two detection modes:
      - Outlier mode (split_idx=0): fits and scores on the same data.
        Training rows can be flagged. Useful for global outlier detection.
      - Novelty mode (split_idx=N): fits on all except last N rows, scores
        only the held-out window. Training rows are always normal.

    A point is flagged when:
      (1) its density under the fitted KDE is below the 1st percentile of
          training densities  AND
      (2) its value lies in the specified tail (controlled by sensitivity
          and anomaly_direction).

    Parameters
    ----------
    series_df : pd.DataFrame
        Input DataFrame. Must contain time_col and value_col.
    time_col : str
        Name of the timestamp or sequence index column.
    value_col : str
        Name of the numeric value column to analyze.
    split_idx : int
        0 = outlier mode; N = novelty mode (score last N rows only).
    bandwidth : float
        KDE bandwidth. Larger = smoother density estimate.
    filter_percentile : float
        Percentile for trimming extremes from training data before fitting.
        100 = keep all. 95 = remove outer 5%.
    sensitivity : str
        One of 'low', 'medium', 'high'. Maps to the directional tail threshold.
    anomaly_direction : str
        Which tail to flag: 'both', 'upper', or 'lower'.
    """

    def __init__(
        self,
        series_df: pd.DataFrame,
        time_col: str,
        value_col: str,
        split_idx: int = 0,
        bandwidth: float = 0.5,
        filter_percentile: float = 100,
        sensitivity: str = "medium",
        anomaly_direction: str = "both",
    ):
        self.series_df = series_df.sort_values(time_col).reset_index(drop=True)
        self.time_col = time_col
        self.value_col = value_col
        self.split_idx = split_idx
        self.bandwidth = bandwidth
        self.filter_percentile = filter_percentile
        self.sensitivity = sensitivity
        self.anomaly_direction = anomaly_direction
        self.threshold_percentile = _SENSITIVITY_TO_PERCENTILE[sensitivity]

    # ── Private helpers ────────────────────────────────────────────

    def _split(self) -> tuple[np.ndarray, np.ndarray]:
        """Return (train_values, test_values). In outlier mode both are the full series."""
        values = self.series_df[self.value_col].values.astype(float)
        if self.split_idx == 0:
            return values, values
        return values[: -self.split_idx], values[-self.split_idx :]

    def _filter_train(self, train: np.ndarray) -> np.ndarray:
        """Trim extreme values from training data before fitting KDE."""
        if self.filter_percentile >= 100:
            return train
        lower_p = (100 - self.filter_percentile) / 2
        upper_p = 100 - lower_p
        lo = np.percentile(train, lower_p)
        hi = np.percentile(train, upper_p)
        return train[(train >= lo) & (train <= hi)]

    def _build_reasons(
        self,
        test_vals: np.ndarray,
        is_anomaly: np.ndarray,
        lower_bound: float,
        upper_bound: float,
    ) -> list[str]:
        reasons = [""] * len(test_vals)
        for i, (val, flag) in enumerate(zip(test_vals, is_anomaly)):
            if not flag:
                continue
            if val < lower_bound:
                reasons[i] = (
                    f"Value ({round(val, 4)}) is unusually low "
                    f"(below {self.threshold_percentile}th-percentile bound "
                    f"{round(lower_bound, 4)}) and falls in a low-density region"
                )
            else:
                reasons[i] = (
                    f"Value ({round(val, 4)}) is unusually high "
                    f"(above {self.threshold_percentile}th-percentile bound "
                    f"{round(upper_bound, 4)}) and falls in a low-density region"
                )
        return reasons

    # ── Public API ─────────────────────────────────────────────────

    def run(self) -> pd.DataFrame:
        """
        Run the full detection pipeline.

        Returns
        -------
        pd.DataFrame
            Original series_df with three columns appended:
              is_anomaly    : bool   — True for flagged points
              anomaly_score : float  — density_threshold / density;
                                       > 1 means density is below threshold (anomaly)
              anomaly_reason: str    — plain-language explanation; empty for normal points

        In novelty mode (split_idx > 0), training rows always have
        is_anomaly=False and anomaly_score=NaN.
        """
        train_raw, test_vals = self._split()
        train_filtered = self._filter_train(train_raw)

        # Fit KDE on (filtered) training data
        kde = KernelDensity(kernel="gaussian", bandwidth=self.bandwidth)
        kde.fit(train_filtered.reshape(-1, 1))

        # Density threshold: 1st percentile of training densities
        train_densities = np.exp(kde.score_samples(train_filtered.reshape(-1, 1)))
        density_threshold = np.quantile(train_densities, 0.01)

        # Score test points
        test_densities = np.exp(kde.score_samples(test_vals.reshape(-1, 1)))
        low_density_mask = test_densities < density_threshold

        # Directional value thresholds derived from training distribution
        lower_bound = np.percentile(train_filtered, 100 - self.threshold_percentile)
        upper_bound = np.percentile(train_filtered, self.threshold_percentile)

        if self.anomaly_direction == "lower":
            direction_mask = test_vals < lower_bound
        elif self.anomaly_direction == "upper":
            direction_mask = test_vals > upper_bound
        else:
            direction_mask = (test_vals < lower_bound) | (test_vals > upper_bound)

        is_anomaly = low_density_mask & direction_mask

        # Score: density_threshold / density → >1 = anomalous, <1 = normal
        with np.errstate(divide="ignore", invalid="ignore"):
            score = np.where(
                test_densities > 0,
                density_threshold / test_densities,
                np.nan,
            )

        reasons = self._build_reasons(test_vals, is_anomaly, lower_bound, upper_bound)

        # Assemble output DataFrame
        result = self.series_df.copy().reset_index(drop=True)
        result["is_anomaly"]     = False
        result["anomaly_score"]  = np.nan
        result["anomaly_reason"] = ""

        if self.split_idx == 0:
            # Outlier mode: all rows scored
            result["is_anomaly"]     = is_anomaly
            result["anomaly_score"]  = score
            result["anomaly_reason"] = reasons
        else:
            # Novelty mode: only test rows scored
            n_train = len(self.series_df) - self.split_idx
            result.loc[n_train:, "is_anomaly"]     = is_anomaly
            result.loc[n_train:, "anomaly_score"]  = score
            result.loc[n_train:, "anomaly_reason"] = reasons

        return result


# ── Tool executor ──────────────────────────────────────────────────────────────

def run_tool(series_df: pd.DataFrame, tool_input: dict) -> dict:
    """
    Execute KDEAnomalyDetector and return a JSON-serialisable result.

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
          anomaly_count  — number of flagged points
          total_points   — total number of rows
          scored_points  — number of rows that were actually scored
                           (= total in outlier mode, = split_idx in novelty mode)
    """
    detector = KDEAnomalyDetector(series_df=series_df, **tool_input)
    result_df = detector.run()
    split_idx = tool_input.get("split_idx", 0)
    scored = len(result_df) if split_idx == 0 else split_idx
    return {
        "records":       result_df.to_dict(orient="records"),
        "anomaly_count": int(result_df["is_anomaly"].sum()),
        "total_points":  len(result_df),
        "scored_points": scored,
    }
