"""
tests/test_formatters.py

Unit tests untuk utils/formatters.py
Mencakup semua fungsi: fmt_monetary, fmt_probability, fmt_stat, fmt_number.
"""

import math
import pytest
from utils.formatters import fmt_monetary, fmt_probability, fmt_stat, fmt_number


# ---------------------------------------------------------------------------
# fmt_monetary
# ---------------------------------------------------------------------------

class TestFmtMonetary:
    def test_positive_value(self):
        assert fmt_monetary(1234.5) == "1234.50"

    def test_zero(self):
        assert fmt_monetary(0) == "0.00"
        assert fmt_monetary(0.0) == "0.00"

    def test_negative_value(self):
        assert fmt_monetary(-50.0) == "-50.00"

    def test_rounds_to_2_decimal(self):
        # Python rounds half-to-even; 1.005 may round to 1.00 or 1.01 depending
        # on float representation — we just check the format length is correct
        result = fmt_monetary(1.005)
        assert len(result.split(".")[-1]) == 2

    def test_large_value(self):
        assert fmt_monetary(1_000_000.0) == "1000000.00"

    def test_none_returns_na(self):
        assert fmt_monetary(None) == "N/A"

    def test_nan_returns_nan(self):
        assert fmt_monetary(float("nan")) == "NaN"

    def test_positive_inf(self):
        assert fmt_monetary(float("inf")) == "∞"

    def test_negative_inf(self):
        assert fmt_monetary(float("-inf")) == "-∞"

    def test_integer_input(self):
        assert fmt_monetary(100) == "100.00"

    def test_small_decimal(self):
        assert fmt_monetary(0.1) == "0.10"


# ---------------------------------------------------------------------------
# fmt_probability
# ---------------------------------------------------------------------------

class TestFmtProbability:
    def test_zero(self):
        assert fmt_probability(0.0) == "0.00"

    def test_one(self):
        assert fmt_probability(1.0) == "1.00"

    def test_typical_probability(self):
        assert fmt_probability(0.75) == "0.75"

    def test_small_probability(self):
        assert fmt_probability(0.01) == "0.01"

    def test_none_returns_na(self):
        assert fmt_probability(None) == "N/A"

    def test_nan_returns_nan(self):
        assert fmt_probability(float("nan")) == "NaN"

    def test_positive_inf(self):
        assert fmt_probability(float("inf")) == "∞"

    def test_negative_inf(self):
        assert fmt_probability(float("-inf")) == "-∞"

    def test_rounds_to_2_decimal(self):
        result = fmt_probability(0.333333)
        assert result == "0.33"

    def test_integer_zero(self):
        assert fmt_probability(0) == "0.00"


# ---------------------------------------------------------------------------
# fmt_stat
# ---------------------------------------------------------------------------

class TestFmtStat:
    def test_zero(self):
        assert fmt_stat(0.0) == "0.0000"

    def test_positive_value(self):
        assert fmt_stat(0.9876543) == "0.9877"

    def test_negative_value(self):
        assert fmt_stat(-0.12345) == "-0.1235"

    def test_rounds_to_4_decimal(self):
        assert fmt_stat(0.123456789) == "0.1235"

    def test_p_value_small(self):
        assert fmt_stat(0.0001) == "0.0001"

    def test_correlation_one(self):
        assert fmt_stat(1.0) == "1.0000"

    def test_none_returns_na(self):
        assert fmt_stat(None) == "N/A"

    def test_nan_returns_nan(self):
        assert fmt_stat(float("nan")) == "NaN"

    def test_positive_inf(self):
        assert fmt_stat(float("inf")) == "∞"

    def test_negative_inf(self):
        assert fmt_stat(float("-inf")) == "-∞"

    def test_integer_input(self):
        assert fmt_stat(1) == "1.0000"


# ---------------------------------------------------------------------------
# fmt_number (dispatcher)
# ---------------------------------------------------------------------------

class TestFmtNumber:
    def test_monetary_dispatch(self):
        assert fmt_number(1234.5, "monetary") == "1234.50"

    def test_probability_dispatch(self):
        assert fmt_number(0.75, "probability") == "0.75"

    def test_stat_dispatch(self):
        assert fmt_number(0.9876, "stat") == "0.9876"

    def test_none_monetary(self):
        assert fmt_number(None, "monetary") == "N/A"

    def test_none_probability(self):
        assert fmt_number(None, "probability") == "N/A"

    def test_none_stat(self):
        assert fmt_number(None, "stat") == "N/A"

    def test_nan_monetary(self):
        assert fmt_number(float("nan"), "monetary") == "NaN"

    def test_nan_stat(self):
        assert fmt_number(float("nan"), "stat") == "NaN"

    def test_inf_probability(self):
        assert fmt_number(float("inf"), "probability") == "∞"

    def test_invalid_fmt_type_raises_value_error(self):
        with pytest.raises(ValueError, match="fmt_type tidak dikenali"):
            fmt_number(1.0, "unknown")

    def test_invalid_fmt_type_empty_string(self):
        with pytest.raises(ValueError):
            fmt_number(1.0, "")

    def test_invalid_fmt_type_case_sensitive(self):
        # fmt_type is case-sensitive; "Monetary" is not valid
        with pytest.raises(ValueError):
            fmt_number(1.0, "Monetary")

    def test_zero_monetary(self):
        assert fmt_number(0, "monetary") == "0.00"

    def test_zero_stat(self):
        assert fmt_number(0, "stat") == "0.0000"
