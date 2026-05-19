"""
tests/test_ev_eol.py
--------------------
Property-based tests untuk modules/ev_eol.py menggunakan Hypothesis.

Properties yang diuji:
- Property 12: EV computation equals dot product          (Validates: Requirements 4.2)
- Property 13: OL matrix is non-negative with column zeros (Validates: Requirements 4.4)
- Property 14: EOL computation equals dot product of OL   (Validates: Requirements 4.5)
- Property 15: Optimal alternative set includes all ties  (Validates: Requirements 4.8)
- Property 16: EVPI is always non-negative                (Validates: Requirements 4.10)
"""

import numpy as np
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from modules.ev_eol import (
    compute_ev,
    compute_eol,
    compute_evpi,
    compute_opportunity_loss,
    get_optimal_indices,
)

# ---------------------------------------------------------------------------
# Strategi / Generator
# ---------------------------------------------------------------------------

# Dimensi matriks payoff: m alternatif (2–8), n kondisi alam (2–8)
m_strategy = st.integers(min_value=2, max_value=8)
n_strategy = st.integers(min_value=2, max_value=8)

# Nilai payoff: float terbatas, tidak NaN/Inf
payoff_values = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
)


def payoff_matrix_strategy(m: int, n: int):
    """Buat strategi matriks payoff shape (m, n)."""
    return arrays(
        dtype=np.float64,
        shape=(m, n),
        elements=payoff_values,
    )


def probability_vector_strategy(n: int):
    """
    Buat strategi vektor probabilitas shape (n,) yang valid:
    - Setiap elemen dalam [0, 1]
    - Jumlah total = 1.0 (dinormalisasi)
    """
    raw = arrays(
        dtype=np.float64,
        shape=(n,),
        elements=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    )
    # Normalisasi agar jumlah = 1; skip jika semua nol
    return raw.map(lambda p: p / p.sum() if p.sum() > 0 else np.ones(n) / n)


# ---------------------------------------------------------------------------
# Property 12: EV computation equals dot product
# Validates: Requirements 4.2
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(m_strategy.flatmap(lambda m: n_strategy.flatmap(
    lambda n: st.tuples(payoff_matrix_strategy(m, n), probability_vector_strategy(n))
)))
def test_property_12_ev_equals_dot_product(args):
    """
    **Validates: Requirements 4.2**

    Property 12: Untuk sembarang matriks payoff P shape (m, n) dan vektor
    probabilitas p shape (n,) yang berjumlah 1, compute_ev(P, p) harus
    sama dengan P @ p secara element-wise untuk semua m alternatif.
    """
    payoff, probs = args
    assume(np.isfinite(probs).all() and probs.sum() > 0)

    result = compute_ev(payoff, probs)
    expected = payoff @ probs

    assert result.shape == (payoff.shape[0],), (
        f"Shape EV harus (m,) = ({payoff.shape[0]},), dapat {result.shape}"
    )
    np.testing.assert_allclose(
        result, expected, rtol=1e-10, atol=1e-10,
        err_msg="compute_ev harus sama dengan payoff @ probs"
    )


# ---------------------------------------------------------------------------
# Property 13: OL matrix is non-negative with column zeros
# Validates: Requirements 4.4
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(m_strategy.flatmap(lambda m: n_strategy.flatmap(
    lambda n: payoff_matrix_strategy(m, n)
)))
def test_property_13_ol_matrix_non_negative_with_column_zeros(payoff):
    """
    **Validates: Requirements 4.4**

    Property 13: Untuk sembarang matriks payoff P, matriks OL yang dihitung
    oleh compute_opportunity_loss(P) harus memenuhi:
    (a) OL[i,j] >= 0 untuk semua i, j
    (b) Setiap kolom j mengandung minimal satu nol (alternatif terbaik
        memiliki OL = 0 untuk kondisi alam tersebut).
    """
    ol = compute_opportunity_loss(payoff)

    assert ol.shape == payoff.shape, (
        f"Shape OL harus sama dengan payoff: {payoff.shape}, dapat {ol.shape}"
    )

    # (a) Semua nilai OL >= 0
    assert np.all(ol >= -1e-10), (
        f"Semua nilai OL harus >= 0, ditemukan nilai negatif: {ol.min()}"
    )

    # (b) Setiap kolom mengandung minimal satu nol
    for j in range(ol.shape[1]):
        col_min = ol[:, j].min()
        assert col_min <= 1e-10, (
            f"Kolom {j} harus mengandung minimal satu nol (OL = 0 untuk alternatif terbaik), "
            f"nilai minimum kolom = {col_min}"
        )


# ---------------------------------------------------------------------------
# Property 14: EOL computation equals dot product of OL and probabilities
# Validates: Requirements 4.5
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(m_strategy.flatmap(lambda m: n_strategy.flatmap(
    lambda n: st.tuples(payoff_matrix_strategy(m, n), probability_vector_strategy(n))
)))
def test_property_14_eol_equals_dot_product(args):
    """
    **Validates: Requirements 4.5**

    Property 14: Untuk sembarang matriks OL shape (m, n) dan vektor
    probabilitas p shape (n,), compute_eol(OL, p) harus sama dengan
    OL @ p secara element-wise.
    """
    payoff, probs = args
    assume(np.isfinite(probs).all() and probs.sum() > 0)

    ol_matrix = compute_opportunity_loss(payoff)
    result = compute_eol(ol_matrix, probs)
    expected = ol_matrix @ probs

    assert result.shape == (payoff.shape[0],), (
        f"Shape EOL harus (m,) = ({payoff.shape[0]},), dapat {result.shape}"
    )
    np.testing.assert_allclose(
        result, expected, rtol=1e-10, atol=1e-10,
        err_msg="compute_eol harus sama dengan ol_matrix @ probs"
    )


# ---------------------------------------------------------------------------
# Property 15: Optimal alternative set includes all ties
# Validates: Requirements 4.8
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    arrays(
        dtype=np.float64,
        shape=st.integers(min_value=2, max_value=20),
        elements=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
    )
)
def test_property_15_optimal_indices_includes_all_ties(values):
    """
    **Validates: Requirements 4.8**

    Property 15: Untuk sembarang vektor numerik v:
    - get_optimal_indices(v, 'max') harus mengembalikan SEMUA indeks i
      di mana v[i] == max(v)
    - get_optimal_indices(v, 'min') harus mengembalikan SEMUA indeks i
      di mana v[i] == min(v)
    """
    assume(np.isfinite(values).all() and len(values) >= 2)

    # Test mode 'max'
    max_indices = get_optimal_indices(values, mode="max")
    max_val = values.max()

    assert len(max_indices) >= 1, "Harus ada minimal satu indeks optimal"

    # Semua indeks yang dikembalikan harus memiliki nilai == max
    for idx in max_indices:
        assert values[idx] == max_val, (
            f"Indeks {idx} dikembalikan tapi values[{idx}]={values[idx]} != max={max_val}"
        )

    # Semua indeks dengan nilai == max harus dikembalikan (tidak ada yang terlewat)
    expected_max_indices = set(int(i) for i in np.where(values == max_val)[0])
    assert set(max_indices) == expected_max_indices, (
        f"get_optimal_indices('max') harus mengembalikan semua tied indices: "
        f"expected {expected_max_indices}, got {set(max_indices)}"
    )

    # Test mode 'min'
    min_indices = get_optimal_indices(values, mode="min")
    min_val = values.min()

    assert len(min_indices) >= 1, "Harus ada minimal satu indeks optimal"

    for idx in min_indices:
        assert values[idx] == min_val, (
            f"Indeks {idx} dikembalikan tapi values[{idx}]={values[idx]} != min={min_val}"
        )

    expected_min_indices = set(int(i) for i in np.where(values == min_val)[0])
    assert set(min_indices) == expected_min_indices, (
        f"get_optimal_indices('min') harus mengembalikan semua tied indices: "
        f"expected {expected_min_indices}, got {set(min_indices)}"
    )


# ---------------------------------------------------------------------------
# Property 16: EVPI is always non-negative
# Validates: Requirements 4.10
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(m_strategy.flatmap(lambda m: n_strategy.flatmap(
    lambda n: st.tuples(payoff_matrix_strategy(m, n), probability_vector_strategy(n))
)))
def test_property_16_evpi_always_non_negative(args):
    """
    **Validates: Requirements 4.10**

    Property 16: Untuk sembarang matriks payoff P yang valid dan vektor
    probabilitas p yang valid, compute_evpi(P, p) harus >= 0.

    Informasi sempurna tidak pernah memperburuk keputusan — EVPI selalu
    bernilai non-negatif.
    """
    payoff, probs = args
    assume(np.isfinite(probs).all() and probs.sum() > 0)
    assume(np.isfinite(payoff).all())

    evpi = compute_evpi(payoff, probs)

    assert isinstance(evpi, float), f"EVPI harus bertipe float, dapat {type(evpi)}"

    # Toleransi relatif untuk floating-point rounding pada nilai payoff besar.
    # EVPI secara matematis selalu >= 0, tapi IEEE 754 dapat menghasilkan
    # nilai negatif kecil (~-1e-10) saat semua payoff identik dan besar.
    # Toleransi dihitung relatif terhadap skala nilai payoff.
    payoff_scale = max(abs(payoff).max(), 1.0)
    tol = payoff_scale * 1e-9
    assert evpi >= -tol, (
        f"EVPI harus >= 0 (informasi sempurna tidak memperburuk keputusan), "
        f"dapat EVPI = {evpi} (toleransi = {-tol})"
    )


# ---------------------------------------------------------------------------
# Unit tests tambahan untuk verifikasi contoh konkret
# ---------------------------------------------------------------------------

class TestComputeEvConcrete:
    """Unit tests dengan contoh konkret untuk compute_ev."""

    def test_simple_2x2(self):
        """Contoh sederhana 2 alternatif × 2 kondisi alam."""
        payoff = np.array([[10.0, 20.0],
                           [15.0, 12.0]])
        probs = np.array([0.4, 0.6])
        result = compute_ev(payoff, probs)
        # EV_1 = 0.4*10 + 0.6*20 = 4 + 12 = 16
        # EV_2 = 0.4*15 + 0.6*12 = 6 + 7.2 = 13.2
        np.testing.assert_allclose(result, [16.0, 13.2], rtol=1e-10)

    def test_equal_probabilities(self):
        """Dengan probabilitas sama, EV = rata-rata baris."""
        payoff = np.array([[10.0, 20.0, 30.0],
                           [5.0,  15.0, 25.0]])
        probs = np.array([1/3, 1/3, 1/3])
        result = compute_ev(payoff, probs)
        np.testing.assert_allclose(result, [20.0, 15.0], rtol=1e-10)


class TestComputeOpportunityLossConcrete:
    """Unit tests dengan contoh konkret untuk compute_opportunity_loss."""

    def test_simple_2x2(self):
        """Contoh sederhana 2 alternatif × 2 kondisi alam."""
        payoff = np.array([[10.0, 20.0],
                           [15.0, 12.0]])
        ol = compute_opportunity_loss(payoff)
        # col_max = [15, 20]
        # OL = [[15-10, 20-20], [15-15, 20-12]] = [[5, 0], [0, 8]]
        expected = np.array([[5.0, 0.0],
                              [0.0, 8.0]])
        np.testing.assert_allclose(ol, expected, rtol=1e-10)

    def test_all_zeros_when_single_alternative(self):
        """Dengan satu alternatif, semua OL = 0."""
        payoff = np.array([[5.0, 10.0, 3.0]])
        ol = compute_opportunity_loss(payoff)
        np.testing.assert_allclose(ol, np.zeros((1, 3)), atol=1e-10)


class TestComputeEvpiConcrete:
    """Unit tests dengan contoh konkret untuk compute_evpi."""

    def test_evpi_zero_when_dominant_alternative(self):
        """
        Jika satu alternatif selalu lebih baik di semua kondisi,
        EVPI = 0 (tidak ada nilai dari informasi tambahan).
        """
        # Alternatif 1 selalu lebih baik
        payoff = np.array([[20.0, 30.0],
                           [10.0, 15.0]])
        probs = np.array([0.5, 0.5])
        evpi = compute_evpi(payoff, probs)
        assert evpi >= 0.0
        # EVwPI = 0.5*20 + 0.5*30 = 25, EV* = max(25, 12.5) = 25 → EVPI = 0
        assert abs(evpi) < 1e-10

    def test_evpi_positive_when_no_dominant(self):
        """Ketika tidak ada alternatif yang dominan, EVPI > 0."""
        payoff = np.array([[30.0, 5.0],
                           [10.0, 25.0]])
        probs = np.array([0.5, 0.5])
        evpi = compute_evpi(payoff, probs)
        # EVwPI = 0.5*30 + 0.5*25 = 27.5
        # EV_1 = 0.5*30 + 0.5*5 = 17.5, EV_2 = 0.5*10 + 0.5*25 = 17.5
        # EV* = 17.5, EVPI = 27.5 - 17.5 = 10.0
        assert abs(evpi - 10.0) < 1e-10


class TestGetOptimalIndicesConcrete:
    """Unit tests dengan contoh konkret untuk get_optimal_indices."""

    def test_single_max(self):
        values = np.array([1.0, 5.0, 3.0])
        assert get_optimal_indices(values, "max") == [1]

    def test_tied_max(self):
        values = np.array([5.0, 3.0, 5.0])
        assert set(get_optimal_indices(values, "max")) == {0, 2}

    def test_single_min(self):
        values = np.array([4.0, 1.0, 3.0])
        assert get_optimal_indices(values, "min") == [1]

    def test_tied_min(self):
        values = np.array([1.0, 3.0, 1.0])
        assert set(get_optimal_indices(values, "min")) == {0, 2}

    def test_all_equal(self):
        values = np.array([7.0, 7.0, 7.0])
        assert set(get_optimal_indices(values, "max")) == {0, 1, 2}
        assert set(get_optimal_indices(values, "min")) == {0, 1, 2}
