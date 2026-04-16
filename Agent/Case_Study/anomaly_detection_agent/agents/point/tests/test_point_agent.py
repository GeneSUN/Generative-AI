"""
Integration tests for agents/point/point_agent.py

These tests exercise the full agent loop end-to-end:
  - Input validation (Step 1 of skill.md procedure)
  - Tool selection (Step 3) — verify the agent picks the right tool for each series type
  - Output contract — the returned DataFrame must satisfy all guarantees in skill.md
  - Error paths — bad inputs must surface clear error messages

Tests here are stubs.  Fill in the bodies once point_agent.py is implemented.

NOTE: Integration tests call the Anthropic API.  Use pytest-vcr or a mock
client to avoid live API calls in CI.  Mark live tests with @pytest.mark.live
and skip them by default:
    pytest -m "not live"
"""

import pytest

# from agents.point.point_agent import run_point_agent

TIME_COL  = "timestamp"
VALUE_COL = "value"


# ── Input validation (skill.md Step 1) ────────────────────────────────────────

class TestInputValidation:

    def test_missing_time_col_raises(self, stationary_series):
        """Agent must return a clear error if time_col does not exist in the DataFrame."""
        pytest.skip("Implement after point_agent.py is built")

    def test_missing_value_col_raises(self, stationary_series):
        pytest.skip("Implement after point_agent.py is built")

    def test_non_numeric_value_col_raises(self, stationary_series):
        pytest.skip("Implement after point_agent.py is built")

    def test_fewer_than_10_points_raises(self, short_series):
        """Fewer than 10 non-NaN values is below the minimum for meaningful detection."""
        pytest.skip("Implement after point_agent.py is built")


# ── Tool selection (skill.md Step 3) ──────────────────────────────────────────

class TestToolSelection:
    """
    Verify the agent selects the tool prescribed by the decision tree in skill.md.

    These tests inspect which tool_use block the agent emits, not the final result.
    They are inherently coupled to the LLM — use a mock client or recorded fixture.
    """

    def test_short_series_selects_statistical(self, short_series):
        """Series with < 30 points → agent must call statistical_anomaly_detector."""
        pytest.skip("Implement after point_agent.py is built")

    def test_seasonal_series_selects_stl(self, seasonal_series):
        """Series with known regular seasonality → agent must call stl_anomaly_detector."""
        pytest.skip("Implement after point_agent.py is built")

    def test_trending_series_selects_arima_or_stl(self, series_with_trend):
        """Trending series → agent must call arima or stl detector (not statistical)."""
        pytest.skip("Implement after point_agent.py is built")

    def test_stationary_series_selects_statistical(self, stationary_series):
        """Default path: stationary, no clear pattern → statistical (Z-score)."""
        pytest.skip("Implement after point_agent.py is built")

    def test_skewed_series_selects_iqr(self, skewed_series):
        """Clearly skewed distribution → agent must choose IQR over Z-score."""
        pytest.skip("Implement after point_agent.py is built")


# ── Output contract (skill.md Step 6) ─────────────────────────────────────────

class TestOutputContract:

    def test_row_count_preserved(self, stationary_series):
        pytest.skip("Implement after point_agent.py is built")

    def test_original_columns_preserved(self, stationary_series):
        pytest.skip("Implement after point_agent.py is built")

    def test_three_anomaly_columns_added(self, stationary_series):
        """is_anomaly (bool), anomaly_score (float), anomaly_reason (str)."""
        pytest.skip("Implement after point_agent.py is built")

    def test_id_col_untouched(self):
        """If id_col is provided, it must be carried through unchanged."""
        pytest.skip("Implement after point_agent.py is built")

    def test_nan_value_rows_handled(self, series_with_nan):
        """NaN rows → is_anomaly=False, anomaly_score=NaN, anomaly_reason='missing value'."""
        pytest.skip("Implement after point_agent.py is built")


# ── Sensitivity end-to-end ─────────────────────────────────────────────────────

class TestSensitivityE2E:

    def test_high_sensitivity_flags_more_than_low(self, series_with_spike):
        pytest.skip("Implement after point_agent.py is built")


# ── Summary (skill.md Step 7) ─────────────────────────────────────────────────

class TestSummary:

    def test_summary_reports_anomaly_count(self, series_with_spike):
        """The agent's final text response must mention how many points were flagged."""
        pytest.skip("Implement after point_agent.py is built")

    def test_summary_names_tool_used(self, stationary_series):
        """The summary must state which tool was selected and why."""
        pytest.skip("Implement after point_agent.py is built")
