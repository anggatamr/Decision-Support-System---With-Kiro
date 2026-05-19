"""
tests/test_validators.py
------------------------
Unit tests dan property-based tests untuk utils/validators.py.

Covers:
  - Property 9:  validate_payoff_matrix (Req 3.4)
  - Property 11: validate_probabilities (Req 4.1)
  - Property 25: validate_distribution_params (Req 6.10)
  - Property 28: validate_sim_variable (Req 8.2)
  Plus unit tests untuk validate_file dan validate_sim_expression (Req 2.7, 2.8, 8.4)
"""

from __future__ import annotations

import io
import sys
import os

import pytest
from hypothesis import given, settings, strategies as st
from hypothesis import assume

# Tambahkan root project ke sys.path agar import berjalan
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.validators import (
    validate_file,
    validate_payoff_matrix,
    validate_probabilities,
    validate_distribution_params,
    validate_sim_variable,
    validate_sim_expression,
)


# ===========================================================================
# Helpers / Stubs
# ===========================================================================

class _FakeFile:
    """Stub untuk Streamlit UploadedFile."""

    def __init__(self, name: str, content: bytes):
        self.name = name
        self.size = len(content)
        self._buf = io.BytesIO(content)

    def read(self):
        return self._buf.read()

    def seek(self, pos):
        self._buf.seek(pos)


# ===========================================================================
# validate_file — unit tests (Req 2.7, 2.8)
# ===========================================================================

class TestValidateFile:
    def test_valid_csv(self):
        f = _FakeFile("data.csv", b"a,b\n1,2\n3,4\n")
        ok, msg = validate_file(f)
        assert ok is True
        assert msg == ""

    def test_valid_xlsx(self):
        f = _FakeFile("data.xlsx", b"\x50\x4b\x03\x04" + b"\x00" * 100)
        ok, msg = validate_file(f)
        assert ok is True
        assert msg == ""

    def test_invalid_extension_pdf(self):
        f = _FakeFile("report.pdf", b"%PDF-1.4 content")
        ok, msg = validate_file(f)
        assert ok is False
        assert "CSV" in msg or "XLSX" in msg

    def test_invalid_extension_txt(self):
        f = _FakeFile("notes.txt", b"hello world")
        ok, msg = validate_file(f)
        assert ok is False

    def test_empty_file(self):
        f = _FakeFile("empty.csv", b"")
        ok, msg = validate_file(f)
        assert ok is False
        assert "kosong" in msg.lower() or "data" in msg.lower()

    def test_file_too_large(self):
        # 51 MB
        big_content = b"x" * (51 * 1024 * 1024)
        f = _FakeFile("big.csv", big_content)
        ok, msg = validate_file(f)
        assert ok is False
        assert "50" in msg or "MB" in msg

    def test_exactly_50mb_is_valid(self):
        content = b"a" * (50 * 1024 * 1024)
        f = _FakeFile("limit.csv", content)
        ok, msg = validate_file(f)
        assert ok is True

    def test_none_file(self):
        ok, msg = validate_file(None)
        assert ok is False

    def test_no_extension(self):
        f = _FakeFile("noext", b"some data")
        ok, msg = validate_file(f)
        assert ok is False


# ===========================================================================
# validate_payoff_matrix — unit tests + property tests (Req 3.4, Property 9)
# ===========================================================================

class TestValidatePayoffMatrix:
    def test_all_valid_integers(self):
        matrix = [[1, 2, 3], [4, 5, 6]]
        ok, invalid = validate_payoff_matrix(matrix)
        assert ok is True
        assert invalid == []

    def test_all_valid_floats(self):
        matrix = [[1.5, -2.0], [0.0, 100.0]]
        ok, invalid = validate_payoff_matrix(matrix)
        assert ok is True
        assert invalid == []

    def test_all_valid_numeric_strings(self):
        matrix = [["10", "20"], ["30", "40"]]
        ok, invalid = validate_payoff_matrix(matrix)
        assert ok is True
        assert invalid == []

    def test_empty_string_cell(self):
        matrix = [["1", ""], ["3", "4"]]
        ok, invalid = validate_payoff_matrix(matrix)
        assert ok is False
        assert (0, 1) in invalid

    def test_none_cell(self):
        matrix = [[None, 2], [3, 4]]
        ok, invalid = validate_payoff_matrix(matrix)
        assert ok is False
        assert (0, 0) in invalid

    def test_text_cell(self):
        matrix = [["abc", 2], [3, 4]]
        ok, invalid = validate_payoff_matrix(matrix)
        assert ok is False
        assert (0, 0) in invalid

    def test_multiple_invalid_cells(self):
        matrix = [["x", 2], [3, "y"]]
        ok, invalid = validate_payoff_matrix(matrix)
        assert ok is False
        assert (0, 0) in invalid
        assert (1, 1) in invalid
        assert len(invalid) == 2

    def test_empty_matrix(self):
        ok, invalid = validate_payoff_matrix([])
        assert ok is True
        assert invalid == []

    def test_negative_values_valid(self):
        matrix = [[-100, -50], [-200, -10]]
        ok, invalid = validate_payoff_matrix(matrix)
        assert ok is True
        assert invalid == []


# Feature: dss-dashboard-streamlit, Property 9: Payoff matrix validation correctly identifies invalid cells
@settings(max_examples=100)
@given(
    rows=st.integers(min_value=1, max_value=5),
    cols=st.integers(min_value=1, max_value=5),
    values=st.lists(
        st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        min_size=1,
    ),
)
def test_property_9_valid_matrix_returns_empty_invalid(rows, cols, values):
    """
    Validates: Requirements 3.4
    Untuk matriks yang semua selnya berupa float valid, validate_payoff_matrix
    harus mengembalikan (True, []).
    """
    # Buat matriks dengan nilai float valid
    flat = [values[i % len(values)] for i in range(rows * cols)]
    matrix = [flat[i * cols:(i + 1) * cols] for i in range(rows)]
    ok, invalid = validate_payoff_matrix(matrix)
    assert ok is True
    assert invalid == []


@settings(max_examples=100)
@given(
    rows=st.integers(min_value=1, max_value=4),
    cols=st.integers(min_value=1, max_value=4),
    bad_row=st.integers(min_value=0, max_value=3),
    bad_col=st.integers(min_value=0, max_value=3),
    bad_value=st.one_of(
        st.just(""),
        st.just(None),
        st.just("abc"),
        st.just("  "),
    ),
)
def test_property_9_invalid_cell_detected(rows, cols, bad_row, bad_col, bad_value):
    """
    Validates: Requirements 3.4
    Jika ada satu sel tidak valid, posisinya harus ada dalam daftar invalid.
    """
    assume(bad_row < rows and bad_col < cols)

    # Buat matriks valid terlebih dahulu
    matrix = [[float(i * cols + j + 1) for j in range(cols)] for i in range(rows)]
    # Sisipkan sel tidak valid
    matrix[bad_row][bad_col] = bad_value

    ok, invalid = validate_payoff_matrix(matrix)
    assert ok is False
    assert (bad_row, bad_col) in invalid


# ===========================================================================
# validate_probabilities — unit tests + property tests (Req 4.1, Property 11)
# ===========================================================================

class TestValidateProbabilities:
    def test_valid_two_probs(self):
        ok, msg = validate_probabilities([0.3, 0.7])
        assert ok is True
        assert msg == ""

    def test_valid_three_probs(self):
        ok, msg = validate_probabilities([0.2, 0.5, 0.3])
        assert ok is True

    def test_sum_exactly_one(self):
        ok, msg = validate_probabilities([0.25, 0.25, 0.25, 0.25])
        assert ok is True

    def test_sum_within_tolerance(self):
        # 0.3334 + 0.3333 + 0.3333 = 1.0000
        ok, msg = validate_probabilities([0.3334, 0.3333, 0.3333])
        assert ok is True

    def test_sum_just_outside_tolerance(self):
        # sum = 0.998 → |1 - 0.998| = 0.002 > 0.001
        ok, msg = validate_probabilities([0.499, 0.499])
        assert ok is False
        assert "1.0" in msg or "jumlah" in msg.lower() or "sum" in msg.lower()

    def test_value_below_zero(self):
        ok, msg = validate_probabilities([-0.1, 1.1])
        assert ok is False
        assert "[0" in msg or "rentang" in msg.lower() or "range" in msg.lower()

    def test_value_above_one(self):
        ok, msg = validate_probabilities([0.5, 1.5])
        assert ok is False

    def test_empty_list(self):
        ok, msg = validate_probabilities([])
        assert ok is False

    def test_single_prob_one(self):
        ok, msg = validate_probabilities([1.0])
        assert ok is True

    def test_single_prob_zero(self):
        # sum = 0.0, bukan 1.0
        ok, msg = validate_probabilities([0.0])
        assert ok is False

    def test_tolerance_boundary_positive(self):
        # sum = 1.0009 → masih dalam toleransi? Tidak — 0.0009 < 0.001 → valid
        ok, msg = validate_probabilities([0.5005, 0.5004])
        assert ok is True

    def test_tolerance_boundary_negative(self):
        # sum = 0.9989 → |1 - 0.9989| = 0.0011 > 0.001 → tidak valid
        ok, msg = validate_probabilities([0.4994, 0.4995])
        assert ok is False


# Feature: dss-dashboard-streamlit, Property 11: Probability validation is correct
@settings(max_examples=100)
@given(
    n=st.integers(min_value=2, max_value=10),
    raw=st.lists(
        st.floats(min_value=0.01, max_value=1.0, allow_nan=False, allow_infinity=False),
        min_size=2,
        max_size=10,
    ),
)
def test_property_11_valid_probs_normalized(n, raw):
    """
    Validates: Requirements 4.1
    Probabilitas yang dinormalisasi (sum = 1.0) harus selalu valid.
    """
    assume(len(raw) >= 2)
    total = sum(raw)
    assume(total > 0)
    normalized = [p / total for p in raw]
    ok, msg = validate_probabilities(normalized)
    assert ok is True, f"Normalized probs failed: {normalized}, msg={msg}"


@settings(max_examples=100)
@given(
    probs=st.lists(
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        min_size=1,
        max_size=10,
    ),
)
def test_property_11_out_of_range_rejected(probs):
    """
    Validates: Requirements 4.1
    Jika ada nilai di luar [0,1], harus ditolak.
    """
    # Sisipkan nilai di luar range
    bad_probs = probs + [-0.5]
    ok, msg = validate_probabilities(bad_probs)
    assert ok is False


# ===========================================================================
# validate_distribution_params — unit tests + property tests (Req 6.10, Property 25)
# ===========================================================================

class TestValidateDistributionParams:
    # Normal
    def test_normal_valid(self):
        ok, msg = validate_distribution_params("Normal", {"mu": 0.0, "sigma": 1.0})
        assert ok is True

    def test_normal_sigma_zero(self):
        ok, msg = validate_distribution_params("Normal", {"mu": 0.0, "sigma": 0.0})
        assert ok is False
        assert "sigma" in msg.lower() or "σ" in msg

    def test_normal_sigma_negative(self):
        ok, msg = validate_distribution_params("Normal", {"mu": 5.0, "sigma": -2.0})
        assert ok is False

    # Binomial
    def test_binomial_valid(self):
        ok, msg = validate_distribution_params("Binomial", {"p": 0.5, "n_trials": 10})
        assert ok is True

    def test_binomial_p_zero(self):
        ok, msg = validate_distribution_params("Binomial", {"p": 0.0, "n_trials": 10})
        assert ok is False

    def test_binomial_p_one(self):
        ok, msg = validate_distribution_params("Binomial", {"p": 1.0, "n_trials": 10})
        assert ok is False

    def test_binomial_n_zero(self):
        ok, msg = validate_distribution_params("Binomial", {"p": 0.5, "n_trials": 0})
        assert ok is False

    def test_binomial_n_negative(self):
        ok, msg = validate_distribution_params("Binomial", {"p": 0.5, "n_trials": -5})
        assert ok is False

    # Poisson
    def test_poisson_valid(self):
        ok, msg = validate_distribution_params("Poisson", {"lambda": 3.0})
        assert ok is True

    def test_poisson_lambda_zero(self):
        ok, msg = validate_distribution_params("Poisson", {"lambda": 0.0})
        assert ok is False

    def test_poisson_lambda_negative(self):
        ok, msg = validate_distribution_params("Poisson", {"lambda": -1.0})
        assert ok is False

    # Exponential
    def test_exponential_valid(self):
        ok, msg = validate_distribution_params("Exponential", {"lambda": 0.5})
        assert ok is True

    def test_exponential_lambda_zero(self):
        ok, msg = validate_distribution_params("Exponential", {"lambda": 0.0})
        assert ok is False

    # Uniform
    def test_uniform_valid(self):
        ok, msg = validate_distribution_params("Uniform", {"a": 0.0, "b": 1.0})
        assert ok is True

    def test_uniform_a_equals_b(self):
        ok, msg = validate_distribution_params("Uniform", {"a": 5.0, "b": 5.0})
        assert ok is False

    def test_uniform_a_greater_than_b(self):
        ok, msg = validate_distribution_params("Uniform", {"a": 10.0, "b": 5.0})
        assert ok is False

    # Beta
    def test_beta_valid(self):
        ok, msg = validate_distribution_params("Beta", {"alpha": 2.0, "beta": 3.0})
        assert ok is True

    def test_beta_alpha_zero(self):
        ok, msg = validate_distribution_params("Beta", {"alpha": 0.0, "beta": 3.0})
        assert ok is False

    def test_beta_beta_negative(self):
        ok, msg = validate_distribution_params("Beta", {"alpha": 2.0, "beta": -1.0})
        assert ok is False

    def test_unknown_distribution(self):
        ok, msg = validate_distribution_params("Gamma", {"k": 2.0, "theta": 1.0})
        assert ok is False


# Feature: dss-dashboard-streamlit, Property 25: Distribution parameter validation is correct
@settings(max_examples=100)
@given(sigma=st.floats(min_value=0.001, max_value=1e6, allow_nan=False, allow_infinity=False))
def test_property_25_normal_valid_sigma(sigma):
    """Validates: Requirements 6.10 — Normal dengan sigma > 0 harus valid."""
    ok, _ = validate_distribution_params("Normal", {"mu": 0.0, "sigma": sigma})
    assert ok is True


@settings(max_examples=100)
@given(sigma=st.floats(max_value=0.0, allow_nan=False, allow_infinity=False))
def test_property_25_normal_invalid_sigma(sigma):
    """Validates: Requirements 6.10 — Normal dengan sigma ≤ 0 harus tidak valid."""
    ok, _ = validate_distribution_params("Normal", {"mu": 0.0, "sigma": sigma})
    assert ok is False


@settings(max_examples=100)
@given(
    p=st.floats(min_value=0.001, max_value=0.999, allow_nan=False, allow_infinity=False),
    n=st.integers(min_value=1, max_value=1000),
)
def test_property_25_binomial_valid(p, n):
    """Validates: Requirements 6.10 — Binomial dengan p ∈ (0,1) dan n > 0 harus valid."""
    ok, _ = validate_distribution_params("Binomial", {"p": p, "n_trials": n})
    assert ok is True


@settings(max_examples=100)
@given(lam=st.floats(min_value=0.001, max_value=1e6, allow_nan=False, allow_infinity=False))
def test_property_25_poisson_valid_lambda(lam):
    """Validates: Requirements 6.10 — Poisson dengan lambda > 0 harus valid."""
    ok, _ = validate_distribution_params("Poisson", {"lambda": lam})
    assert ok is True


@settings(max_examples=100)
@given(
    a=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
    diff=st.floats(min_value=0.001, max_value=1e6, allow_nan=False, allow_infinity=False),
)
def test_property_25_uniform_valid(a, diff):
    """Validates: Requirements 6.10 — Uniform dengan a < b harus valid."""
    b = a + diff
    ok, _ = validate_distribution_params("Uniform", {"a": a, "b": b})
    assert ok is True


@settings(max_examples=100)
@given(
    alpha=st.floats(min_value=0.001, max_value=100.0, allow_nan=False, allow_infinity=False),
    beta=st.floats(min_value=0.001, max_value=100.0, allow_nan=False, allow_infinity=False),
)
def test_property_25_beta_valid(alpha, beta):
    """Validates: Requirements 6.10 — Beta dengan alpha > 0 dan beta > 0 harus valid."""
    ok, _ = validate_distribution_params("Beta", {"alpha": alpha, "beta": beta})
    assert ok is True


# ===========================================================================
# validate_sim_variable — unit tests + property tests (Req 8.2, Property 28)
# ===========================================================================

class TestValidateSimVariable:
    # Normal
    def test_normal_valid(self):
        ok, msg = validate_sim_variable("X", "Normal", {"mean": 5.0, "std": 1.0})
        assert ok is True

    def test_normal_std_zero(self):
        ok, msg = validate_sim_variable("X", "Normal", {"mean": 5.0, "std": 0.0})
        assert ok is False
        assert "std" in msg.lower()

    def test_normal_std_negative(self):
        ok, msg = validate_sim_variable("X", "Normal", {"mean": 5.0, "std": -1.0})
        assert ok is False

    # Uniform
    def test_uniform_valid(self):
        ok, msg = validate_sim_variable("Y", "Uniform", {"min": 0.0, "max": 10.0})
        assert ok is True

    def test_uniform_min_equals_max(self):
        ok, msg = validate_sim_variable("Y", "Uniform", {"min": 5.0, "max": 5.0})
        assert ok is False

    def test_uniform_min_greater_than_max(self):
        ok, msg = validate_sim_variable("Y", "Uniform", {"min": 10.0, "max": 5.0})
        assert ok is False

    # Triangular
    def test_triangular_valid(self):
        ok, msg = validate_sim_variable("Z", "Triangular", {"min": 1.0, "mode": 3.0, "max": 5.0})
        assert ok is True

    def test_triangular_mode_at_min(self):
        ok, msg = validate_sim_variable("Z", "Triangular", {"min": 1.0, "mode": 1.0, "max": 5.0})
        assert ok is True  # min ≤ mode ≤ max → valid

    def test_triangular_mode_at_max(self):
        ok, msg = validate_sim_variable("Z", "Triangular", {"min": 1.0, "mode": 5.0, "max": 5.0})
        assert ok is True  # min ≤ mode ≤ max → valid

    def test_triangular_mode_below_min(self):
        ok, msg = validate_sim_variable("Z", "Triangular", {"min": 2.0, "mode": 1.0, "max": 5.0})
        assert ok is False

    def test_triangular_mode_above_max(self):
        ok, msg = validate_sim_variable("Z", "Triangular", {"min": 1.0, "mode": 6.0, "max": 5.0})
        assert ok is False

    # Nama variabel
    def test_empty_name(self):
        ok, msg = validate_sim_variable("", "Normal", {"mean": 0.0, "std": 1.0})
        assert ok is False

    def test_invalid_name_starts_with_digit(self):
        ok, msg = validate_sim_variable("1var", "Normal", {"mean": 0.0, "std": 1.0})
        assert ok is False

    def test_valid_name_with_underscore(self):
        ok, msg = validate_sim_variable("var_1", "Normal", {"mean": 0.0, "std": 1.0})
        assert ok is True

    def test_unknown_dist_type(self):
        ok, msg = validate_sim_variable("X", "Gamma", {"k": 2.0})
        assert ok is False


# Feature: dss-dashboard-streamlit, Property 28: Simulation variable validation is correct
@settings(max_examples=100)
@given(std=st.floats(min_value=0.001, max_value=1e6, allow_nan=False, allow_infinity=False))
def test_property_28_normal_valid_std(std):
    """Validates: Requirements 8.2 — Normal dengan std > 0 harus valid."""
    ok, _ = validate_sim_variable("x", "Normal", {"mean": 0.0, "std": std})
    assert ok is True


@settings(max_examples=100)
@given(std=st.floats(max_value=0.0, allow_nan=False, allow_infinity=False))
def test_property_28_normal_invalid_std(std):
    """Validates: Requirements 8.2 — Normal dengan std ≤ 0 harus tidak valid."""
    ok, _ = validate_sim_variable("x", "Normal", {"mean": 0.0, "std": std})
    assert ok is False


@settings(max_examples=100)
@given(
    mn=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
    diff=st.floats(min_value=0.001, max_value=1e6, allow_nan=False, allow_infinity=False),
)
def test_property_28_uniform_valid(mn, diff):
    """Validates: Requirements 8.2 — Uniform dengan min < max harus valid."""
    mx = mn + diff
    ok, _ = validate_sim_variable("x", "Uniform", {"min": mn, "max": mx})
    assert ok is True


@settings(max_examples=100)
@given(
    mn=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
    diff=st.floats(min_value=0.001, max_value=1e6, allow_nan=False, allow_infinity=False),
    mode_offset=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
def test_property_28_triangular_valid(mn, diff, mode_offset):
    """Validates: Requirements 8.2 — Triangular dengan min ≤ mode ≤ max harus valid."""
    mx = mn + diff
    mode = mn + mode_offset * diff  # mode ∈ [min, max]
    ok, _ = validate_sim_variable("x", "Triangular", {"min": mn, "mode": mode, "max": mx})
    assert ok is True


@settings(max_examples=100)
@given(
    mn=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
    diff=st.floats(min_value=0.001, max_value=1e6, allow_nan=False, allow_infinity=False),
    mode_excess=st.floats(min_value=0.001, max_value=1e6, allow_nan=False, allow_infinity=False),
)
def test_property_28_triangular_mode_above_max_invalid(mn, diff, mode_excess):
    """Validates: Requirements 8.2 — Triangular dengan mode > max harus tidak valid."""
    mx = mn + diff
    mode = mx + mode_excess  # mode > max
    ok, _ = validate_sim_variable("x", "Triangular", {"min": mn, "mode": mode, "max": mx})
    assert ok is False


# ===========================================================================
# validate_sim_expression — unit tests (Req 8.4)
# ===========================================================================

class TestValidateSimExpression:
    def test_simple_addition(self):
        ok, msg = validate_sim_expression("x + y", ["x", "y"])
        assert ok is True

    def test_multiplication(self):
        ok, msg = validate_sim_expression("price * quantity", ["price", "quantity"])
        assert ok is True

    def test_complex_expression(self):
        ok, msg = validate_sim_expression("a * b + c / 2", ["a", "b", "c"])
        assert ok is True

    def test_undefined_variable(self):
        ok, msg = validate_sim_expression("x + z", ["x", "y"])
        assert ok is False
        assert "z" in msg or "tidak terdefinisi" in msg.lower() or "undefined" in msg.lower()

    def test_syntax_error(self):
        ok, msg = validate_sim_expression("x +* y", ["x", "y"])
        assert ok is False
        assert "sintaks" in msg.lower() or "syntax" in msg.lower()

    def test_empty_expression(self):
        ok, msg = validate_sim_expression("", ["x"])
        assert ok is False

    def test_whitespace_only(self):
        ok, msg = validate_sim_expression("   ", ["x"])
        assert ok is False

    def test_single_variable(self):
        ok, msg = validate_sim_expression("revenue", ["revenue"])
        assert ok is True

    def test_no_variables_constant(self):
        ok, msg = validate_sim_expression("42", [])
        assert ok is True

    def test_division_by_zero_with_dummy(self):
        # Dengan dummy value 1.0, ini tidak akan zero-divide
        ok, msg = validate_sim_expression("x / y", ["x", "y"])
        assert ok is True

    def test_security_no_builtins(self):
        # __import__ tidak boleh bisa diakses
        ok, msg = validate_sim_expression("__import__('os')", [])
        assert ok is False

    def test_security_no_open(self):
        ok, msg = validate_sim_expression("open('file.txt')", [])
        assert ok is False

    def test_power_operator(self):
        ok, msg = validate_sim_expression("x ** 2 + y ** 2", ["x", "y"])
        assert ok is True

    def test_nested_arithmetic(self):
        ok, msg = validate_sim_expression("(a + b) * (c - d) / 4", ["a", "b", "c", "d"])
        assert ok is True
