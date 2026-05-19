"""
tests/test_monte_carlo.py
-------------------------
Property-based tests untuk modules/monte_carlo.py menggunakan Hypothesis.

Properties yang diuji:
- Property 29: Monte Carlo output length equals iteration count  (Validates: Requirements 8.5)
- Property 30: Simulation summary statistics match numpy         (Validates: Requirements 8.7)
- Property 31: Sensitivity analysis matches scipy Spearman       (Validates: Requirements 8.10)
"""

import numpy as np
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays
from scipy.stats import spearmanr

from modules.monte_carlo import (
    run_monte_carlo,
    compute_sim_stats,
    compute_sensitivity,
)

# ---------------------------------------------------------------------------
# Strategi / Generator
# ---------------------------------------------------------------------------

# Jumlah iterasi simulasi: antara 100 dan 1000 (dibatasi untuk efisiensi)
n_iterations_strategy = st.integers(min_value=100, max_value=1000)

# Nilai float terbatas, tidak NaN/Inf
finite_floats = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
)

# Array output simulasi: minimal 10 elemen
output_array_strategy = arrays(
    dtype=np.float64,
    shape=st.integers(min_value=10, max_value=500),
    elements=finite_floats,
)


def make_normal_variable(name: str = "x") -> dict:
    """Buat variabel simulasi Normal sederhana dengan parameter tetap."""
    return {
        "name": name,
        "dist_type": "Normal",
        "params": {"mean": 0.0, "std": 1.0},
    }


def input_matrix_and_output_strategy(n_rows: int, n_cols: int):
    """
    Buat strategi pasangan (input_matrix, output) dengan shape yang konsisten.
    input_matrix: shape (n_rows, n_cols)
    output: shape (n_rows,)
    """
    matrix = arrays(
        dtype=np.float64,
        shape=(n_rows, n_cols),
        elements=finite_floats,
    )
    output = arrays(
        dtype=np.float64,
        shape=(n_rows,),
        elements=finite_floats,
    )
    return st.tuples(matrix, output)


# ---------------------------------------------------------------------------
# Property 29: Monte Carlo output length equals iteration count
# Validates: Requirements 8.5
# ---------------------------------------------------------------------------

@settings(max_examples=30)
@given(n_iterations_strategy)
def test_property_29_output_length_equals_iteration_count(n):
    """
    **Validates: Requirements 8.5**

    Property 29: Untuk sembarang n dalam [100, 1000], run_monte_carlo dengan
    satu variabel Normal dan ekspresi "x" harus mengembalikan output dengan
    len == n.
    """
    variables = [make_normal_variable("x")]
    result = run_monte_carlo(variables, expr="x", n=n)

    assert len(result["output"]) == n, (
        f"Panjang output harus sama dengan jumlah iterasi n={n}, "
        f"dapat {len(result['output'])}"
    )
    assert result["n_iterations"] == n, (
        f"n_iterations dalam MCResult harus == n={n}, "
        f"dapat {result['n_iterations']}"
    )
    assert result["input_matrix"].shape == (n, 1), (
        f"input_matrix harus shape ({n}, 1), dapat {result['input_matrix'].shape}"
    )


# ---------------------------------------------------------------------------
# Property 30: Simulation summary statistics match numpy
# Validates: Requirements 8.7
# ---------------------------------------------------------------------------

@settings(max_examples=30)
@given(output_array_strategy)
def test_property_30_sim_stats_match_numpy(output):
    """
    **Validates: Requirements 8.7**

    Property 30: Untuk sembarang array float, compute_sim_stats harus
    mengembalikan:
    - mean  == np.mean(output)
    - std   == np.std(output)
    - p5    == np.percentile(output, 5)
    - p95   == np.percentile(output, 95)
    - min   == np.min(output)
    - max   == np.max(output)
    """
    assume(np.isfinite(output).all() and len(output) >= 2)

    stats = compute_sim_stats(output)

    np.testing.assert_allclose(
        stats["mean"], np.mean(output), rtol=1e-10, atol=1e-10,
        err_msg="stats['mean'] harus sama dengan np.mean(output)"
    )
    np.testing.assert_allclose(
        stats["std"], np.std(output), rtol=1e-10, atol=1e-10,
        err_msg="stats['std'] harus sama dengan np.std(output)"
    )
    np.testing.assert_allclose(
        stats["p5"], np.percentile(output, 5), rtol=1e-10, atol=1e-10,
        err_msg="stats['p5'] harus sama dengan np.percentile(output, 5)"
    )
    np.testing.assert_allclose(
        stats["p95"], np.percentile(output, 95), rtol=1e-10, atol=1e-10,
        err_msg="stats['p95'] harus sama dengan np.percentile(output, 95)"
    )
    np.testing.assert_allclose(
        stats["min"], np.min(output), rtol=1e-10, atol=1e-10,
        err_msg="stats['min'] harus sama dengan np.min(output)"
    )
    np.testing.assert_allclose(
        stats["max"], np.max(output), rtol=1e-10, atol=1e-10,
        err_msg="stats['max'] harus sama dengan np.max(output)"
    )

    # Pastikan semua key yang diharapkan ada
    expected_keys = {"mean", "std", "p5", "p95", "min", "max"}
    assert expected_keys.issubset(stats.keys()), (
        f"compute_sim_stats harus mengembalikan key: {expected_keys}, "
        f"dapat {set(stats.keys())}"
    )


# ---------------------------------------------------------------------------
# Property 31: Sensitivity analysis matches scipy Spearman
# Validates: Requirements 8.10
# ---------------------------------------------------------------------------

@settings(max_examples=30)
@given(
    st.integers(min_value=20, max_value=200).flatmap(
        lambda n_rows: st.integers(min_value=1, max_value=5).flatmap(
            lambda n_cols: input_matrix_and_output_strategy(n_rows, n_cols).map(
                lambda pair: (pair[0], pair[1], n_cols)
            )
        )
    )
)
def test_property_31_sensitivity_matches_scipy_spearman(args):
    """
    **Validates: Requirements 8.10**

    Property 31: Untuk sembarang input_matrix dan output array,
    compute_sensitivity harus mengembalikan nilai yang sama dengan
    scipy.stats.spearmanr untuk setiap pasangan (kolom input, output).
    """
    input_matrix, output, n_cols = args

    assume(np.isfinite(input_matrix).all())
    assume(np.isfinite(output).all())
    # Pastikan output tidak konstan (spearmanr membutuhkan variasi)
    assume(np.std(output) > 0)
    # Pastikan setiap kolom input tidak konstan
    for j in range(n_cols):
        assume(np.std(input_matrix[:, j]) > 0)

    var_names = [f"x{i}" for i in range(n_cols)]
    result = compute_sensitivity(input_matrix, output, var_names)

    assert set(result.keys()) == set(var_names), (
        f"compute_sensitivity harus mengembalikan key {var_names}, "
        f"dapat {list(result.keys())}"
    )

    for i, name in enumerate(var_names):
        expected_corr = float(spearmanr(input_matrix[:, i], output).correlation)
        np.testing.assert_allclose(
            result[name], expected_corr, rtol=1e-10, atol=1e-10,
            err_msg=(
                f"Korelasi Spearman untuk variabel '{name}' harus sama dengan "
                f"scipy.stats.spearmanr: expected {expected_corr}, "
                f"dapat {result[name]}"
            )
        )


# ---------------------------------------------------------------------------
# Unit tests tambahan untuk verifikasi contoh konkret
# ---------------------------------------------------------------------------

class TestRunMonteCarloConcrete:
    """Unit tests dengan contoh konkret untuk run_monte_carlo."""

    def test_output_shape_single_variable(self):
        """Output shape harus (n,) untuk satu variabel."""
        variables = [make_normal_variable("x")]
        result = run_monte_carlo(variables, expr="x", n=500)
        assert result["output"].shape == (500,)
        assert result["input_matrix"].shape == (500, 1)
        assert result["var_names"] == ["x"]
        assert result["n_iterations"] == 500

    def test_output_shape_multiple_variables(self):
        """Output shape harus (n,) untuk beberapa variabel."""
        variables = [
            {"name": "revenue", "dist_type": "Normal", "params": {"mean": 100.0, "std": 10.0}},
            {"name": "cost",    "dist_type": "Uniform", "params": {"min": 50.0, "max": 80.0}},
        ]
        result = run_monte_carlo(variables, expr="revenue - cost", n=300)
        assert result["output"].shape == (300,)
        assert result["input_matrix"].shape == (300, 2)
        assert result["var_names"] == ["revenue", "cost"]
        assert result["n_iterations"] == 300

    def test_spearman_corrs_shape(self):
        """spearman_corrs harus shape (k,) di mana k = jumlah variabel."""
        variables = [
            make_normal_variable("a"),
            make_normal_variable("b"),
            make_normal_variable("c"),
        ]
        result = run_monte_carlo(variables, expr="a + b + c", n=200)
        assert result["spearman_corrs"].shape == (3,)

    def test_default_n_iterations(self):
        """Default n harus 10.000."""
        variables = [make_normal_variable("x")]
        result = run_monte_carlo(variables, expr="x")
        assert result["n_iterations"] == 10_000
        assert len(result["output"]) == 10_000

    def test_triangular_distribution(self):
        """Sampling dari distribusi Triangular harus menghasilkan output dalam [min, max]."""
        variables = [{
            "name": "x",
            "dist_type": "Triangular",
            "params": {"min": 0.0, "mode": 5.0, "max": 10.0},
        }]
        result = run_monte_carlo(variables, expr="x", n=500)
        assert np.all(result["output"] >= 0.0), "Semua sampel Triangular harus >= min"
        assert np.all(result["output"] <= 10.0), "Semua sampel Triangular harus <= max"


class TestComputeSimStatsConcrete:
    """Unit tests dengan contoh konkret untuk compute_sim_stats."""

    def test_known_array(self):
        """Verifikasi statistik untuk array yang diketahui."""
        output = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        stats = compute_sim_stats(output)
        assert abs(stats["mean"] - 3.0) < 1e-10
        assert abs(stats["min"] - 1.0) < 1e-10
        assert abs(stats["max"] - 5.0) < 1e-10

    def test_all_keys_present(self):
        """Semua key yang diharapkan harus ada dalam hasil."""
        output = np.random.normal(0, 1, 100)
        stats = compute_sim_stats(output)
        for key in ["mean", "std", "p5", "p95", "min", "max"]:
            assert key in stats, f"Key '{key}' harus ada dalam compute_sim_stats"

    def test_p5_less_than_p95(self):
        """p5 harus selalu <= p95 untuk array dengan variasi."""
        output = np.random.normal(0, 1, 1000)
        stats = compute_sim_stats(output)
        assert stats["p5"] <= stats["p95"], "p5 harus <= p95"

    def test_min_max_bounds(self):
        """min harus <= semua nilai, max harus >= semua nilai."""
        output = np.random.uniform(-10, 10, 500)
        stats = compute_sim_stats(output)
        assert stats["min"] <= output.min() + 1e-10
        assert stats["max"] >= output.max() - 1e-10


class TestComputeSensitivityConcrete:
    """Unit tests dengan contoh konkret untuk compute_sensitivity."""

    def test_perfect_positive_correlation(self):
        """Variabel yang identik dengan output harus memiliki korelasi = 1.0."""
        n = 200
        x = np.random.normal(0, 1, n)
        input_matrix = x.reshape(-1, 1)
        output = x.copy()  # output identik dengan input
        result = compute_sensitivity(input_matrix, output, ["x"])
        assert abs(result["x"] - 1.0) < 1e-10, (
            f"Korelasi Spearman untuk variabel identik harus = 1.0, dapat {result['x']}"
        )

    def test_perfect_negative_correlation(self):
        """Variabel yang berlawanan tanda dengan output harus memiliki korelasi = -1.0."""
        n = 200
        x = np.random.normal(0, 1, n)
        input_matrix = x.reshape(-1, 1)
        output = -x  # output berlawanan tanda
        result = compute_sensitivity(input_matrix, output, ["x"])
        assert abs(result["x"] - (-1.0)) < 1e-10, (
            f"Korelasi Spearman untuk variabel berlawanan harus = -1.0, dapat {result['x']}"
        )

    def test_returns_all_variable_names(self):
        """Hasil harus mengandung semua nama variabel yang diberikan."""
        n = 100
        k = 4
        input_matrix = np.random.normal(0, 1, (n, k))
        output = np.random.normal(0, 1, n)
        var_names = ["a", "b", "c", "d"]
        result = compute_sensitivity(input_matrix, output, var_names)
        assert set(result.keys()) == set(var_names)

    def test_correlation_range(self):
        """Semua nilai korelasi Spearman harus dalam rentang [-1, 1]."""
        n = 150
        k = 3
        input_matrix = np.random.normal(0, 1, (n, k))
        output = np.random.normal(0, 1, n)
        var_names = ["x1", "x2", "x3"]
        result = compute_sensitivity(input_matrix, output, var_names)
        for name, corr in result.items():
            assert -1.0 - 1e-10 <= corr <= 1.0 + 1e-10, (
                f"Korelasi Spearman untuk '{name}' harus dalam [-1, 1], dapat {corr}"
            )
