"""
tests/test_utility.py
---------------------
Property-based tests untuk modules/utility.py menggunakan Hypothesis.

Properties yang diuji:
- Property 26: Risk preference classification is deterministic  (Validates: Requirements 7.6)
- Property 27: Expected utility computation equals weighted sum (Validates: Requirements 7.9)
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from modules.utility import (
    UTILITY_FUNCTIONS,
    classify_risk_preference,
    compute_expected_utility,
    compute_r_squared,
    fit_utility_curve,
)

# ---------------------------------------------------------------------------
# Strategi / Generator
# ---------------------------------------------------------------------------

# Semua kunci fungsi utilitas yang valid
VALID_FUNC_TYPES = list(UTILITY_FUNCTIONS.keys())

func_type_strategy = st.sampled_from(VALID_FUNC_TYPES)

# Dimensi matriks payoff: m alternatif (2–6), n kondisi alam (2–6)
m_strategy = st.integers(min_value=2, max_value=6)
n_strategy = st.integers(min_value=2, max_value=6)

# Nilai payoff: float terbatas, positif agar fungsi logaritmik tidak error
payoff_positive_values = st.floats(
    min_value=0.1,
    max_value=100.0,
    allow_nan=False,
    allow_infinity=False,
)


def payoff_matrix_strategy(m: int, n: int):
    """Buat strategi matriks payoff shape (m, n) dengan nilai positif."""
    return arrays(
        dtype=np.float64,
        shape=(m, n),
        elements=payoff_positive_values,
    )


def probability_vector_strategy(n: int):
    """
    Buat strategi vektor probabilitas shape (n,) yang valid:
    - Setiap elemen dalam (0, 1]
    - Jumlah total = 1.0 (dinormalisasi)
    """
    raw = arrays(
        dtype=np.float64,
        shape=(n,),
        elements=st.floats(
            min_value=0.01,
            max_value=1.0,
            allow_nan=False,
            allow_infinity=False,
        ),
    )
    return raw.map(lambda p: p / p.sum())


# ---------------------------------------------------------------------------
# Property 26: Risk preference classification is deterministic
# Validates: Requirements 7.6
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(func_type_strategy)
def test_property_26_risk_preference_is_deterministic(func_type):
    """
    **Validates: Requirements 7.6**

    Property 26: Untuk sembarang func_type yang valid, classify_risk_preference()
    harus selalu mengembalikan hasil yang sama pada setiap pemanggilan
    (deterministik — tidak ada randomness atau side effects).

    Selain itu, hasil harus selalu berupa salah satu dari tiga kategori yang
    valid: "Risk Averse", "Risk Neutral", atau "Risk Seeking".
    """
    valid_categories = {"Risk Averse", "Risk Neutral", "Risk Seeking"}

    # Panggil dua kali — harus menghasilkan hasil yang identik
    result_1 = classify_risk_preference(func_type)
    result_2 = classify_risk_preference(func_type)

    assert result_1 == result_2, (
        f"classify_risk_preference('{func_type}') tidak deterministik: "
        f"pemanggilan pertama = '{result_1}', pemanggilan kedua = '{result_2}'"
    )

    assert result_1 in valid_categories, (
        f"classify_risk_preference('{func_type}') mengembalikan '{result_1}' "
        f"yang bukan kategori valid. Kategori valid: {valid_categories}"
    )


@settings(max_examples=100)
@given(func_type_strategy)
def test_property_26_risk_preference_mapping_correct(func_type):
    """
    **Validates: Requirements 7.6**

    Property 26 (lanjutan): Verifikasi bahwa mapping deterministik sesuai
    dengan spesifikasi desain:
    - Eksponensial → Risk Averse
    - Logaritmik   → Risk Averse
    - Linear       → Risk Neutral
    - Kuadratik    → Risk Seeking
    """
    expected_mapping = {
        "Eksponensial": "Risk Averse",
        "Logaritmik":   "Risk Averse",
        "Linear":       "Risk Neutral",
        "Kuadratik":    "Risk Seeking",
    }

    result = classify_risk_preference(func_type)
    expected = expected_mapping[func_type]

    assert result == expected, (
        f"classify_risk_preference('{func_type}') harus mengembalikan "
        f"'{expected}', tapi mendapat '{result}'"
    )


# ---------------------------------------------------------------------------
# Property 27: Expected utility computation equals weighted sum
# Validates: Requirements 7.9
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    m_strategy.flatmap(lambda m: n_strategy.flatmap(
        lambda n: st.tuples(
            payoff_matrix_strategy(m, n),
            probability_vector_strategy(n),
        )
    )),
    func_type_strategy,
)
def test_property_27_expected_utility_equals_weighted_sum(args, func_type):
    """
    **Validates: Requirements 7.9**

    Property 27: Untuk sembarang matriks payoff P shape (m, n), vektor
    probabilitas p shape (n,), dan fungsi utilitas U dengan parameter params,
    compute_expected_utility(P, p, U, params) harus sama dengan U(P, *params) @ p
    secara element-wise — yaitu jumlah tertimbang dari utilitas.

    EU_i = sum_j( p_j * U(v_ij) ) = U_matrix @ probs
    """
    payoff, probs = args
    assume(np.isfinite(payoff).all())
    assume(np.isfinite(probs).all() and probs.sum() > 0)

    utility_func = UTILITY_FUNCTIONS[func_type]

    # Tentukan parameter default yang aman per tipe fungsi
    # agar U_matrix dapat dihitung tanpa error numerik
    if func_type == "Eksponensial":
        # R > 0; gunakan R = 50 agar exp(-x/R) tidak overflow untuk x ∈ [0.1, 100]
        params = (50.0,)
    elif func_type == "Logaritmik":
        # a > 0, b > 0 agar log(x + b) terdefinisi untuk x > 0
        params = (1.0, 1.0)
    elif func_type == "Linear":
        params = (1.0, 0.0)
    else:  # Kuadratik
        params = (0.01, 1.0, 0.0)

    # Hitung U_matrix secara manual
    U_matrix = utility_func(payoff, *params)  # shape (m, n)
    assume(np.isfinite(U_matrix).all())

    expected = U_matrix @ probs  # shape (m,)

    result = compute_expected_utility(payoff, probs, utility_func, params)

    assert result.shape == (payoff.shape[0],), (
        f"Shape EU harus (m,) = ({payoff.shape[0]},), dapat {result.shape}"
    )

    np.testing.assert_allclose(
        result, expected, rtol=1e-10, atol=1e-10,
        err_msg=(
            f"compute_expected_utility harus sama dengan U_matrix @ probs "
            f"untuk func_type='{func_type}'"
        ),
    )


@settings(max_examples=100)
@given(
    m_strategy.flatmap(lambda m: n_strategy.flatmap(
        lambda n: st.tuples(
            payoff_matrix_strategy(m, n),
            probability_vector_strategy(n),
        )
    )),
)
def test_property_27_expected_utility_shape(args):
    """
    **Validates: Requirements 7.9**

    Property 27 (lanjutan): Output compute_expected_utility harus selalu
    memiliki shape (m,) — satu nilai EU per alternatif.
    """
    payoff, probs = args
    assume(np.isfinite(payoff).all())
    assume(np.isfinite(probs).all() and probs.sum() > 0)

    utility_func = UTILITY_FUNCTIONS["Linear"]
    params = (1.0, 0.0)

    result = compute_expected_utility(payoff, probs, utility_func, params)

    assert result.shape == (payoff.shape[0],), (
        f"Shape EU harus (m,) = ({payoff.shape[0]},), dapat {result.shape}"
    )
    assert np.isfinite(result).all(), (
        "Semua nilai EU harus finite (tidak NaN atau Inf)"
    )


# ---------------------------------------------------------------------------
# Unit tests tambahan — verifikasi contoh konkret
# ---------------------------------------------------------------------------

class TestClassifyRiskPreferenceConcrete:
    """Unit tests dengan contoh konkret untuk classify_risk_preference."""

    def test_eksponensial_is_risk_averse(self):
        assert classify_risk_preference("Eksponensial") == "Risk Averse"

    def test_logaritmik_is_risk_averse(self):
        assert classify_risk_preference("Logaritmik") == "Risk Averse"

    def test_linear_is_risk_neutral(self):
        assert classify_risk_preference("Linear") == "Risk Neutral"

    def test_kuadratik_is_risk_seeking(self):
        assert classify_risk_preference("Kuadratik") == "Risk Seeking"

    def test_invalid_func_type_raises_value_error(self):
        with pytest.raises(ValueError, match="tidak dikenal"):
            classify_risk_preference("TidakAda")

    def test_all_valid_types_return_string(self):
        for func_type in VALID_FUNC_TYPES:
            result = classify_risk_preference(func_type)
            assert isinstance(result, str)
            assert len(result) > 0


class TestComputeExpectedUtilityConcrete:
    """Unit tests dengan contoh konkret untuk compute_expected_utility."""

    def test_linear_utility_equals_ev(self):
        """
        Dengan fungsi utilitas linear U(x) = x (a=1, b=0),
        EU harus sama dengan EV biasa.
        """
        payoff = np.array([[10.0, 20.0],
                           [15.0, 12.0]])
        probs = np.array([0.4, 0.6])
        utility_func = UTILITY_FUNCTIONS["Linear"]
        params = (1.0, 0.0)

        eu = compute_expected_utility(payoff, probs, utility_func, params)
        # EU_1 = 0.4*10 + 0.6*20 = 16.0
        # EU_2 = 0.4*15 + 0.6*12 = 13.2
        np.testing.assert_allclose(eu, [16.0, 13.2], rtol=1e-10)

    def test_output_shape(self):
        """Output harus memiliki shape (m,)."""
        payoff = np.array([[1.0, 2.0, 3.0],
                           [4.0, 5.0, 6.0],
                           [7.0, 8.0, 9.0]])
        probs = np.array([1/3, 1/3, 1/3])
        utility_func = UTILITY_FUNCTIONS["Linear"]
        params = (1.0, 0.0)

        eu = compute_expected_utility(payoff, probs, utility_func, params)
        assert eu.shape == (3,)

    def test_equal_probs_equals_row_mean_utility(self):
        """
        Dengan probabilitas sama, EU_i = mean(U(v_ij)) untuk setiap baris i.
        """
        payoff = np.array([[1.0, 4.0, 9.0]])
        probs = np.array([1/3, 1/3, 1/3])
        # Gunakan fungsi kuadrat sederhana: U(x) = x (linear a=1, b=0)
        utility_func = UTILITY_FUNCTIONS["Linear"]
        params = (1.0, 0.0)

        eu = compute_expected_utility(payoff, probs, utility_func, params)
        expected_mean = np.mean([1.0, 4.0, 9.0])
        np.testing.assert_allclose(eu[0], expected_mean, rtol=1e-10)


class TestFitUtilityCurveConcrete:
    """Unit tests dengan contoh konkret untuk fit_utility_curve."""

    def test_linear_fit_recovers_params(self):
        """Fitting fungsi linear pada data linear harus merecovery parameter."""
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
        # y = 2*x + 1
        y = 2.0 * x + 1.0
        popt, pcov = fit_utility_curve("Linear", x, y)
        np.testing.assert_allclose(popt, [2.0, 1.0], rtol=1e-5)

    def test_invalid_func_type_raises_value_error(self):
        """func_type yang tidak valid harus raise ValueError."""
        x = np.array([1.0, 2.0, 3.0])
        y = np.array([0.5, 0.7, 0.9])
        with pytest.raises(ValueError, match="tidak dikenal"):
            fit_utility_curve("TidakAda", x, y)

    def test_returns_tuple_of_arrays(self):
        """fit_utility_curve harus mengembalikan tuple (popt, pcov)."""
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
        popt, pcov = fit_utility_curve("Linear", x, y)
        assert isinstance(popt, np.ndarray)
        assert isinstance(pcov, np.ndarray)


class TestComputeRSquaredConcrete:
    """Unit tests dengan contoh konkret untuk compute_r_squared."""

    def test_perfect_fit_returns_one(self):
        """Prediksi sempurna harus menghasilkan R² = 1.0."""
        y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        r2 = compute_r_squared(y, y)
        assert abs(r2 - 1.0) < 1e-10

    def test_constant_y_true_returns_one(self):
        """Jika y_true konstan (SS_tot = 0) dan prediksi sempurna, harus mengembalikan 1.0."""
        y_true = np.array([3.0, 3.0, 3.0])
        y_pred = np.array([3.0, 3.0, 3.0])
        r2 = compute_r_squared(y_true, y_pred)
        assert r2 == 1.0

    def test_r_squared_range(self):
        """R² untuk fit yang baik harus berada dalam rentang yang masuk akal."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.1, 1.9, 3.1, 3.9, 5.1])
        r2 = compute_r_squared(y_true, y_pred)
        assert r2 <= 1.0
        assert r2 > 0.9  # fit yang baik
