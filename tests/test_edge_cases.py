"""
tests/test_edge_cases.py
------------------------
Unit tests untuk edge cases pada fungsi komputasi DSS.

Mencakup:
- Equal payoffs (semua nilai sama)
- Single alternative / single state
- Negative payoffs
- Large values (overflow risk)
- Probability tolerance boundary
- Monte Carlo safe expression evaluator
- Validator edge cases
"""

from __future__ import annotations

import math
import numpy as np
import pytest

from modules.ev_eol import (
    compute_ev,
    compute_eol,
    compute_evpi,
    compute_opportunity_loss,
    get_optimal_indices,
)
from modules.uncertainty import (
    compute_maximax,
    compute_maximin,
    compute_minimax_regret,
    compute_laplace,
)
from modules.monte_carlo import (
    run_monte_carlo,
    compute_sim_stats,
    compute_sensitivity,
    safe_eval_expr,
)
from utils.validators import (
    validate_probabilities,
    validate_sim_variable,
    validate_sim_expression,
)


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def equal_payoff_matrix():
    """Matriks payoff di mana semua nilai identik."""
    return np.array([[5.0, 5.0, 5.0],
                     [5.0, 5.0, 5.0],
                     [5.0, 5.0, 5.0]])


@pytest.fixture
def uniform_probs_3():
    return np.array([1/3, 1/3, 1/3])


@pytest.fixture
def single_alt_matrix():
    """Matriks dengan satu alternatif, tiga kondisi alam."""
    return np.array([[10.0, 20.0, 30.0]])


@pytest.fixture
def single_state_matrix():
    """Matriks dengan tiga alternatif, satu kondisi alam."""
    return np.array([[10.0], [20.0], [30.0]])


@pytest.fixture
def negative_payoff_matrix():
    """Matriks payoff dengan nilai negatif."""
    return np.array([[-100.0, -50.0],
                     [-200.0, -10.0],
                     [-150.0, -80.0]])


@pytest.fixture
def large_payoff_matrix():
    """Matriks payoff dengan nilai sangat besar."""
    return np.array([[1e12, 2e12],
                     [3e12, 0.5e12]])


# ===========================================================================
# EV & EOL — Equal Payoffs
# ===========================================================================

class TestEqualPayoffs:
    """Ketika semua payoff sama, semua alternatif harus memiliki EV dan EOL yang sama."""

    def test_ev_all_equal(self, equal_payoff_matrix, uniform_probs_3):
        ev = compute_ev(equal_payoff_matrix, uniform_probs_3)
        assert np.allclose(ev, 5.0), f"EV harus semua 5.0, dapat: {ev}"

    def test_eol_all_zero(self, equal_payoff_matrix, uniform_probs_3):
        ol = compute_opportunity_loss(equal_payoff_matrix)
        eol = compute_eol(ol, uniform_probs_3)
        assert np.allclose(eol, 0.0), f"EOL harus semua 0.0, dapat: {eol}"

    def test_evpi_zero(self, equal_payoff_matrix, uniform_probs_3):
        evpi = compute_evpi(equal_payoff_matrix, uniform_probs_3)
        assert math.isclose(evpi, 0.0, abs_tol=1e-9), f"EVPI harus 0.0, dapat: {evpi}"

    def test_opportunity_loss_all_zero(self, equal_payoff_matrix):
        ol = compute_opportunity_loss(equal_payoff_matrix)
        assert np.allclose(ol, 0.0), f"OL harus semua 0.0, dapat: {ol}"

    def test_all_alternatives_optimal(self, equal_payoff_matrix, uniform_probs_3):
        ev = compute_ev(equal_payoff_matrix, uniform_probs_3)
        best = get_optimal_indices(ev, "max")
        assert len(best) == 3, f"Semua 3 alternatif harus optimal (tied), dapat: {best}"


# ===========================================================================
# EV & EOL — Single Alternative
# ===========================================================================

class TestSingleAlternative:
    """Dengan satu alternatif, ia selalu menjadi pilihan optimal."""

    def test_ev_single_alt(self, single_alt_matrix):
        probs = np.array([0.2, 0.5, 0.3])
        ev = compute_ev(single_alt_matrix, probs)
        expected = 10.0 * 0.2 + 20.0 * 0.5 + 30.0 * 0.3
        assert math.isclose(float(ev[0]), expected, rel_tol=1e-9)

    def test_eol_single_alt_is_zero(self, single_alt_matrix):
        probs = np.array([0.2, 0.5, 0.3])
        ol = compute_opportunity_loss(single_alt_matrix)
        eol = compute_eol(ol, probs)
        assert np.allclose(eol, 0.0), "EOL untuk satu alternatif harus 0"

    def test_evpi_single_alt_is_zero(self, single_alt_matrix):
        probs = np.array([0.2, 0.5, 0.3])
        evpi = compute_evpi(single_alt_matrix, probs)
        assert math.isclose(evpi, 0.0, abs_tol=1e-9), "EVPI untuk satu alternatif harus 0"

    def test_optimal_index_single_alt(self, single_alt_matrix):
        probs = np.array([0.2, 0.5, 0.3])
        ev = compute_ev(single_alt_matrix, probs)
        best = get_optimal_indices(ev, "max")
        assert best == [0]


# ===========================================================================
# EV & EOL — Single State
# ===========================================================================

class TestSingleState:
    """Dengan satu kondisi alam, probabilitas = 1.0 dan OL = 0 untuk alternatif terbaik."""

    def test_ev_single_state(self, single_state_matrix):
        probs = np.array([1.0])
        ev = compute_ev(single_state_matrix, probs)
        expected = np.array([10.0, 20.0, 30.0])
        assert np.allclose(ev, expected)

    def test_ol_single_state(self, single_state_matrix):
        ol = compute_opportunity_loss(single_state_matrix)
        # Alternatif terbaik (30.0) harus OL = 0
        assert math.isclose(float(ol[2, 0]), 0.0, abs_tol=1e-9)
        # Alternatif lain harus OL > 0
        assert float(ol[0, 0]) > 0
        assert float(ol[1, 0]) > 0

    def test_evpi_single_state_is_zero(self, single_state_matrix):
        probs = np.array([1.0])
        evpi = compute_evpi(single_state_matrix, probs)
        assert math.isclose(evpi, 0.0, abs_tol=1e-9)


# ===========================================================================
# EV & EOL — Negative Payoffs
# ===========================================================================

class TestNegativePayoffs:
    """Payoff negatif harus ditangani dengan benar (loss minimization context)."""

    def test_ev_negative(self, negative_payoff_matrix):
        probs = np.array([0.4, 0.6])
        ev = compute_ev(negative_payoff_matrix, probs)
        # EV alt 0: -100*0.4 + -50*0.6 = -40 - 30 = -70
        assert math.isclose(float(ev[0]), -70.0, rel_tol=1e-9)
        # EV alt 1: -200*0.4 + -10*0.6 = -80 - 6 = -86
        assert math.isclose(float(ev[1]), -86.0, rel_tol=1e-9)
        # EV alt 2: -150*0.4 + -80*0.6 = -60 - 48 = -108
        assert math.isclose(float(ev[2]), -108.0, rel_tol=1e-9)

    def test_ol_negative_payoffs_nonnegative(self, negative_payoff_matrix):
        ol = compute_opportunity_loss(negative_payoff_matrix)
        assert np.all(ol >= 0), "OL harus selalu >= 0 meskipun payoff negatif"

    def test_evpi_negative_payoffs_nonnegative(self, negative_payoff_matrix):
        probs = np.array([0.4, 0.6])
        evpi = compute_evpi(negative_payoff_matrix, probs)
        assert evpi >= 0, "EVPI harus selalu >= 0"

    def test_best_ev_negative(self, negative_payoff_matrix):
        probs = np.array([0.4, 0.6])
        ev = compute_ev(negative_payoff_matrix, probs)
        best = get_optimal_indices(ev, "max")
        # Alt 0 memiliki EV = -70 (tertinggi dari -70, -86, -108)
        assert 0 in best


# ===========================================================================
# EV & EOL — Large Values
# ===========================================================================

class TestLargeValues:
    """Nilai sangat besar tidak boleh menyebabkan overflow atau NaN."""

    def test_ev_large_values(self, large_payoff_matrix):
        probs = np.array([0.5, 0.5])
        ev = compute_ev(large_payoff_matrix, probs)
        assert np.all(np.isfinite(ev)), "EV harus finite untuk nilai besar"

    def test_evpi_large_values(self, large_payoff_matrix):
        probs = np.array([0.5, 0.5])
        evpi = compute_evpi(large_payoff_matrix, probs)
        assert math.isfinite(evpi), "EVPI harus finite untuk nilai besar"
        assert evpi >= 0

    def test_ol_large_values_nonnegative(self, large_payoff_matrix):
        ol = compute_opportunity_loss(large_payoff_matrix)
        assert np.all(ol >= 0)
        assert np.all(np.isfinite(ol))


# ===========================================================================
# Uncertainty Criteria — Edge Cases
# ===========================================================================

class TestUncertaintyEdgeCases:
    """Edge cases untuk kriteria ketidakpastian."""

    def test_maximax_equal_payoffs(self, equal_payoff_matrix):
        # compute_maximax returns (max_value, best_indices)
        max_val, best_indices = compute_maximax(equal_payoff_matrix)
        assert len(best_indices) == 3

    def test_maximin_equal_payoffs(self, equal_payoff_matrix):
        # compute_maximin returns (min_value, best_indices)
        min_val, best_indices = compute_maximin(equal_payoff_matrix)
        assert len(best_indices) == 3

    def test_laplace_equal_payoffs(self, equal_payoff_matrix):
        # compute_laplace returns (laplace_ev_array, best_indices)
        laplace_ev, best_indices = compute_laplace(equal_payoff_matrix)
        assert np.allclose(laplace_ev, 5.0)
        assert len(best_indices) == 3

    def test_minimax_regret_equal_payoffs(self, equal_payoff_matrix):
        # compute_minimax_regret returns (max_regret_value, best_indices, regret_matrix)
        max_regret, best_indices, regret_matrix = compute_minimax_regret(equal_payoff_matrix)
        assert np.allclose(max_regret, 0.0)

    def test_hurwicz_alpha_zero(self):
        """Alpha=0 → pure pessimist (maximin) — skipped: compute_hurwicz not in module."""
        pytest.skip("compute_hurwicz not implemented in uncertainty module")

    def test_hurwicz_alpha_one(self):
        """Alpha=1 → pure optimist (maximax) — skipped: compute_hurwicz not in module."""
        pytest.skip("compute_hurwicz not implemented in uncertainty module")

    def test_negative_payoffs_maximax(self, negative_payoff_matrix):
        # compute_maximax returns (max_value, best_indices)
        max_val, best_indices = compute_maximax(negative_payoff_matrix)
        # Maximax dari [-100,-50], [-200,-10], [-150,-80]
        # Max per row: -50, -10, -80 → best = alt 1 (-10)
        assert 1 in best_indices

    def test_negative_payoffs_maximin(self, negative_payoff_matrix):
        # compute_maximin returns (min_value, best_indices)
        min_val, best_indices = compute_maximin(negative_payoff_matrix)
        # Min per row: -100, -200, -150 → best = alt 0 (-100)
        assert 0 in best_indices


# ===========================================================================
# Probability Validator — Boundary Cases
# ===========================================================================

class TestProbabilityValidator:
    """Boundary cases untuk validasi probabilitas."""

    def test_exact_sum_one(self):
        valid, msg = validate_probabilities([0.3, 0.3, 0.4])
        assert valid, msg

    def test_sum_within_tolerance(self):
        # 0.3333 * 3 = 0.9999 — dalam toleransi ±0.001
        valid, msg = validate_probabilities([0.3333, 0.3333, 0.3334])
        assert valid, msg

    def test_sum_outside_tolerance(self):
        valid, msg = validate_probabilities([0.3, 0.3, 0.3])
        assert not valid
        assert "1.0" in msg

    def test_single_probability_one(self):
        valid, msg = validate_probabilities([1.0])
        assert valid, msg

    def test_zero_probability_allowed(self):
        valid, msg = validate_probabilities([0.0, 0.5, 0.5])
        assert valid, msg

    def test_negative_probability_rejected(self):
        valid, msg = validate_probabilities([-0.1, 0.6, 0.5])
        assert not valid

    def test_probability_above_one_rejected(self):
        valid, msg = validate_probabilities([1.1, 0.0])
        assert not valid

    def test_empty_list_rejected(self):
        valid, msg = validate_probabilities([])
        assert not valid


# ===========================================================================
# Monte Carlo — Safe Expression Evaluator
# ===========================================================================

class TestSafeEvalExpr:
    """Unit tests untuk safe_eval_expr — menggantikan eval()."""

    def test_simple_addition(self):
        ns = {"x": np.array([1.0, 2.0, 3.0]), "y": np.array([4.0, 5.0, 6.0])}
        result = safe_eval_expr("x + y", ns)
        assert np.allclose(result, [5.0, 7.0, 9.0])

    def test_simple_subtraction(self):
        ns = {"revenue": np.array([100.0, 200.0]), "cost": np.array([60.0, 80.0])}
        result = safe_eval_expr("revenue - cost", ns)
        assert np.allclose(result, [40.0, 120.0])

    def test_multiplication(self):
        ns = {"price": np.array([10.0, 20.0]), "qty": np.array([5.0, 3.0])}
        result = safe_eval_expr("price * qty", ns)
        assert np.allclose(result, [50.0, 60.0])

    def test_power_operator(self):
        ns = {"x": np.array([2.0, 3.0])}
        result = safe_eval_expr("x ** 2", ns)
        assert np.allclose(result, [4.0, 9.0])

    def test_sqrt_function(self):
        ns = {"x": np.array([4.0, 9.0, 16.0])}
        result = safe_eval_expr("sqrt(x)", ns)
        assert np.allclose(result, [2.0, 3.0, 4.0])

    def test_np_sqrt(self):
        ns = {"x": np.array([4.0, 9.0])}
        result = safe_eval_expr("np.sqrt(x)", ns)
        assert np.allclose(result, [2.0, 3.0])

    def test_complex_expression(self):
        ns = {"a": np.array([3.0]), "b": np.array([4.0])}
        result = safe_eval_expr("sqrt(a**2 + b**2)", ns)
        assert np.allclose(result, [5.0])

    def test_constant_pi(self):
        ns = {"r": np.array([1.0, 2.0])}
        result = safe_eval_expr("pi * r ** 2", ns)
        assert np.allclose(result, [math.pi, 4 * math.pi])

    def test_scalar_result(self):
        ns = {"x": 5.0}
        result = safe_eval_expr("x * 2", ns)
        assert math.isclose(float(result), 10.0)

    def test_syntax_error_raises(self):
        with pytest.raises(SyntaxError):
            safe_eval_expr("x +* y", {"x": 1.0, "y": 2.0})

    def test_undefined_variable_raises(self):
        with pytest.raises(NameError):
            safe_eval_expr("undefined_var + 1", {"x": 1.0})

    def test_import_blocked(self):
        """Ekspresi tidak boleh mengakses __import__ atau os."""
        with pytest.raises((ValueError, NameError)):
            safe_eval_expr("__import__('os').system('echo hacked')", {})

    def test_exec_blocked(self):
        """exec() tidak boleh tersedia dalam ekspresi."""
        with pytest.raises((ValueError, NameError)):
            safe_eval_expr("exec('import os')", {})

    def test_open_blocked(self):
        """open() tidak boleh tersedia dalam ekspresi."""
        with pytest.raises((ValueError, NameError)):
            safe_eval_expr("open('/etc/passwd').read()", {})

    def test_division_by_zero(self):
        """Pembagian dengan nol harus menghasilkan inf atau raise, bukan crash."""
        ns = {"x": np.array([1.0, 2.0]), "y": np.array([0.0, 1.0])}
        # numpy division by zero menghasilkan inf/nan, bukan exception
        result = safe_eval_expr("x / y", ns)
        assert np.isinf(result[0]) or np.isnan(result[0])


# ===========================================================================
# Monte Carlo — run_monte_carlo Integration
# ===========================================================================

class TestRunMonteCarlo:
    """Integration tests untuk run_monte_carlo dengan safe evaluator."""

    def test_basic_simulation(self):
        variables = [
            {"name": "x", "dist_type": "Normal", "params": {"mean": 0.0, "std": 1.0}},
        ]
        result = run_monte_carlo(variables, "x", n=1000)
        assert result["n_iterations"] == 1000
        assert len(result["output"]) == 1000
        assert result["var_names"] == ["x"]

    def test_two_variable_simulation(self):
        variables = [
            {"name": "revenue", "dist_type": "Normal", "params": {"mean": 100.0, "std": 10.0}},
            {"name": "cost",    "dist_type": "Uniform", "params": {"min": 50.0, "max": 80.0}},
        ]
        result = run_monte_carlo(variables, "revenue - cost", n=500)
        assert result["n_iterations"] == 500
        assert len(result["output"]) == 500
        # Profit harus positif sebagian besar waktu (revenue mean 100, cost max 80)
        assert float(np.mean(result["output"])) > 0

    def test_triangular_distribution(self):
        variables = [
            {"name": "x", "dist_type": "Triangular", "params": {"min": 0.0, "mode": 5.0, "max": 10.0}},
        ]
        result = run_monte_carlo(variables, "x", n=1000)
        output = result["output"]
        assert np.all(output >= 0.0)
        assert np.all(output <= 10.0)

    def test_sensitivity_spearman_range(self):
        variables = [
            {"name": "a", "dist_type": "Normal", "params": {"mean": 0.0, "std": 1.0}},
            {"name": "b", "dist_type": "Normal", "params": {"mean": 0.0, "std": 1.0}},
        ]
        result = run_monte_carlo(variables, "a + b", n=2000)
        corrs = result["spearman_corrs"]
        assert np.all(np.abs(corrs) <= 1.0), "Korelasi Spearman harus dalam [-1, 1]"

    def test_sqrt_expression(self):
        """Ekspresi dengan fungsi sqrt harus berjalan dengan safe evaluator."""
        variables = [
            {"name": "a", "dist_type": "Uniform", "params": {"min": 1.0, "max": 10.0}},
            {"name": "b", "dist_type": "Uniform", "params": {"min": 1.0, "max": 10.0}},
        ]
        result = run_monte_carlo(variables, "sqrt(a**2 + b**2)", n=500)
        assert np.all(np.isfinite(result["output"]))
        assert np.all(result["output"] > 0)


# ===========================================================================
# Monte Carlo — compute_sim_stats
# ===========================================================================

class TestComputeSimStats:
    """Unit tests untuk compute_sim_stats."""

    def test_known_distribution(self):
        np.random.seed(42)
        output = np.random.normal(loc=100.0, scale=10.0, size=100_000)
        stats = compute_sim_stats(output)
        assert math.isclose(stats["mean"], 100.0, abs_tol=0.5)
        assert math.isclose(stats["std"], 10.0, abs_tol=0.5)
        assert stats["p5"] < stats["mean"] < stats["p95"]
        assert stats["min"] <= stats["p5"]
        assert stats["p95"] <= stats["max"]

    def test_single_value(self):
        output = np.array([42.0])
        stats = compute_sim_stats(output)
        assert stats["mean"] == 42.0
        assert stats["min"] == 42.0
        assert stats["max"] == 42.0

    def test_all_same_values(self):
        output = np.full(100, 7.5)
        stats = compute_sim_stats(output)
        assert stats["mean"] == 7.5
        assert stats["std"] == 0.0
        assert stats["p5"] == 7.5
        assert stats["p95"] == 7.5


# ===========================================================================
# Validate Sim Variable — Edge Cases
# ===========================================================================

class TestValidateSimVariable:
    """Edge cases untuk validate_sim_variable."""

    def test_valid_normal(self):
        ok, msg = validate_sim_variable("x", "Normal", {"mean": 0.0, "std": 1.0})
        assert ok, msg

    def test_normal_std_zero_rejected(self):
        ok, msg = validate_sim_variable("x", "Normal", {"mean": 0.0, "std": 0.0})
        assert not ok

    def test_normal_std_negative_rejected(self):
        ok, msg = validate_sim_variable("x", "Normal", {"mean": 0.0, "std": -1.0})
        assert not ok

    def test_uniform_min_equals_max_rejected(self):
        ok, msg = validate_sim_variable("x", "Uniform", {"min": 5.0, "max": 5.0})
        assert not ok

    def test_uniform_min_greater_than_max_rejected(self):
        ok, msg = validate_sim_variable("x", "Uniform", {"min": 10.0, "max": 5.0})
        assert not ok

    def test_triangular_mode_outside_range_rejected(self):
        ok, msg = validate_sim_variable("x", "Triangular", {"min": 0.0, "mode": 15.0, "max": 10.0})
        assert not ok

    def test_triangular_valid(self):
        ok, msg = validate_sim_variable("x", "Triangular", {"min": 0.0, "mode": 5.0, "max": 10.0})
        assert ok, msg

    def test_empty_name_rejected(self):
        ok, msg = validate_sim_variable("", "Normal", {"mean": 0.0, "std": 1.0})
        assert not ok

    def test_invalid_identifier_rejected(self):
        ok, msg = validate_sim_variable("1x", "Normal", {"mean": 0.0, "std": 1.0})
        assert not ok

    def test_valid_identifier_with_underscore(self):
        ok, msg = validate_sim_variable("my_var_1", "Normal", {"mean": 0.0, "std": 1.0})
        assert ok, msg


# ===========================================================================
# Validate Sim Expression — Edge Cases
# ===========================================================================

class TestValidateSimExpression:
    """Edge cases untuk validate_sim_expression."""

    def test_valid_simple_expression(self):
        ok, msg = validate_sim_expression("x + y", ["x", "y"])
        assert ok, msg

    def test_empty_expression_rejected(self):
        ok, msg = validate_sim_expression("", ["x"])
        assert not ok

    def test_whitespace_only_rejected(self):
        ok, msg = validate_sim_expression("   ", ["x"])
        assert not ok

    def test_undefined_variable_rejected(self):
        ok, msg = validate_sim_expression("x + z", ["x", "y"])
        assert not ok
        assert "z" in msg or "tidak terdefinisi" in msg

    def test_syntax_error_rejected(self):
        ok, msg = validate_sim_expression("x +* y", ["x", "y"])
        assert not ok

    def test_valid_with_function(self):
        ok, msg = validate_sim_expression("sqrt(x)", ["x"])
        assert ok, msg

    def test_valid_complex(self):
        ok, msg = validate_sim_expression("revenue - cost * 0.1", ["revenue", "cost"])
        assert ok, msg
