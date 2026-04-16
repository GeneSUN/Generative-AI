"""
Shared pytest fixtures for point agent tests.

Each fixture returns a DataFrame with columns [timestamp, value] that matches
the point agent input contract (time_col + value_col).  Fixtures are designed
to stress-test specific detection scenarios.
"""

import numpy as np
import pandas as pd
import pytest

# ── Constants ──────────────────────────────────────────────────────────────────

TIME_COL  = "timestamp"
VALUE_COL = "value"
RNG       = np.random.default_rng(42)   # fixed seed → reproducible tests


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_df(values: np.ndarray, start: str = "2024-01-01", freq: str = "h") -> pd.DataFrame:
    """Wrap a value array in a DataFrame with a datetime index column."""
    ts = pd.date_range(start=start, periods=len(values), freq=freq)
    return pd.DataFrame({TIME_COL: ts, VALUE_COL: values})


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def stationary_series():
    """
    Clean, stationary, roughly Gaussian series — no anomalies injected.
    Expected: zero or very few flags at medium sensitivity.
    """
    values = RNG.normal(loc=10.0, scale=1.0, size=200)
    return _make_df(values)


@pytest.fixture
def series_with_spike():
    """
    Stationary series with one large positive spike at index 100.
    Expected: exactly the spike flagged as is_anomaly=True.
    """
    values = RNG.normal(loc=10.0, scale=1.0, size=200)
    values[100] = 50.0          # clear upper outlier
    return _make_df(values)


@pytest.fixture
def series_with_dip():
    """
    Stationary series with one large negative dip at index 150.
    Expected: exactly the dip flagged as is_anomaly=True.
    """
    values = RNG.normal(loc=10.0, scale=1.0, size=200)
    values[150] = -30.0         # clear lower outlier
    return _make_df(values)


@pytest.fixture
def series_with_trend():
    """
    Upward-trending series with one spike injected in the test horizon.
    Useful for verifying that ARIMA handles trend correctly.
    """
    t = np.arange(200)
    values = 0.05 * t + RNG.normal(loc=0.0, scale=1.0, size=200)
    values[180] = values[180] + 30.0    # spike in the last 24-point horizon
    return _make_df(values)


@pytest.fixture
def seasonal_series():
    """
    Daily-seasonal series (period=24) over 10 days with one spike.
    Useful for verifying that ARIMA / STL handle seasonality correctly.
    """
    t = np.arange(240)
    values = (
        10.0
        + 3.0 * np.sin(2 * np.pi * t / 24)     # daily cycle
        + RNG.normal(loc=0.0, scale=0.5, size=240)
    )
    values[220] = 30.0                           # spike in test horizon
    return _make_df(values)


@pytest.fixture
def short_series():
    """
    Series with fewer than 30 points — below the minimum for ARIMA / STL.
    Used to verify that tools which require more data raise or return gracefully.
    """
    values = RNG.normal(loc=10.0, scale=1.0, size=20)
    return _make_df(values)


@pytest.fixture
def series_with_nan():
    """
    Series where some value_col entries are NaN.
    Expected: NaN rows → is_anomaly=False, anomaly_score=NaN, anomaly_reason='missing value'.
    """
    values = RNG.normal(loc=10.0, scale=1.0, size=200).astype(float)
    values[[10, 50, 99]] = np.nan
    return _make_df(values)


@pytest.fixture
def skewed_series():
    """
    Right-skewed series (log-normal) — mean >> median.
    Expected: IQR method preferred over Z-score in the statistical tool.
    """
    values = RNG.lognormal(mean=0.0, sigma=1.5, size=200)
    return _make_df(values)
