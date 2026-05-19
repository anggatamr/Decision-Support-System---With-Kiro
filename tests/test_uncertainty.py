"""
tests/test_uncertainty.py
--------------------------
Property-based tests untuk modules/uncertainty.py menggunakan Hypothesis.

Properties yang diuji:
- Property 17: Maximax equals global maximum              (Validates: Requirements 5.1)
- Property 18: Maximin equals maximum of row minimums     (Validates: Requirements 5.3)
- Property 19: Minimax regret is non-negative with column zeros (Validates: Requirements 5.5)
- Property 20: Laplace scores equal row means             (Validates: Requirements 5.8)
"""

import numpy as np
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from modules.uncertainty import (
    compute_maximax,
    compute_maximin,
    compute_minimax_regret,
    compute_laplace,
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


# Strategi gabungan: hasilkan (m, n) lalu buat matriks payoff
payoff_strategy = m_strategy.flatmap(
    lambda m: n_strategy.flatmap(
        lambda n: payoff_matrix_strategy(m, n)
    )
)


# ---------------------------------------------------------------------------
# Property 17: Maximax equals global maximum
# Validates: Requirements 5.1
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(payoff_strategy)
def test_property_17_maximax_equals_global_maximum(payoff):
    """
    **Validates: Requirements 5.1**

    Property 17: Untuk sembarang matriks payoff P, compute_maximax(P)[0]
    harus sama dengan P.max() — nilai terbesar dalam seluruh matriks.

    Maximax = max_i ( max_j v_ij ) = max seluruh elemen matriks.
    """
    assume(np.isfinite(payoff).all())

    val, idx = compute_maximax(payoff)

    # Nilai Maximax harus sama dengan global maximum matriks
    expected_val = float(payoff.max())
    assert abs(val - expected_val) < 1e-10, (
        f"Maximax val={val} harus sama dengan global max={expected_val}"
    )

    # Indeks yang dikembalikan harus valid (dalam rentang [0, m))
    m = payoff.shape[0]
    for i in idx:
        assert 0 <= i < m, f"Indeks {i} di luar rentang [0, {m})"

    # Setiap indeks yang dikembalikan harus memiliki row_max == val
    for i in idx:
        row_max_i = float(payoff[i].max())
        assert abs(row_max_i - val) < 1e-10, (
            f"Alternatif {i} dikembalikan tapi row_max={row_max_i} != maximax={val}"
        )

    # Harus ada minimal satu indeks
    assert len(idx) >= 1, "Harus ada minimal satu alternatif optimal"


# ---------------------------------------------------------------------------
# Property 18: Maximin equals maximum of row minimums
# Validates: Requirements 5.3
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(payoff_strategy)
def test_property_18_maximin_equals_max_of_row_minimums(payoff):
    """
    **Validates: Requirements 5.3**

    Property 18: Untuk sembarang matriks payoff P, compute_maximin(P)[0]
    harus sama dengan P.min(axis=1).max().

    Maximin = max_i ( min_j v_ij ).
    """
    assume(np.isfinite(payoff).all())

    val, idx = compute_maximin(payoff)

    # Nilai Maximin harus sama dengan max dari row-minimum
    expected_val = float(payoff.min(axis=1).max())
    assert abs(val - expected_val) < 1e-10, (
        f"Maximin val={val} harus sama dengan P.min(axis=1).max()={expected_val}"
    )

    # Indeks yang dikembalikan harus valid
    m = payoff.shape[0]
    for i in idx:
        assert 0 <= i < m, f"Indeks {i} di luar rentang [0, {m})"

    # Setiap indeks yang dikembalikan harus memiliki row_min == val
    for i in idx:
        row_min_i = float(payoff[i].min())
        assert abs(row_min_i - val) < 1e-10, (
            f"Alternatif {i} dikembalikan tapi row_min={row_min_i} != maximin={val}"
        )

    # Harus ada minimal satu indeks
    assert len(idx) >= 1, "Harus ada minimal satu alternatif optimal"


# ---------------------------------------------------------------------------
# Property 19: Minimax regret is non-negative and regret matrix has column zeros
# Validates: Requirements 5.5
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(payoff_strategy)
def test_property_19_minimax_regret_non_negative_with_column_zeros(payoff):
    """
    **Validates: Requirements 5.5**

    Property 19: Untuk sembarang matriks payoff P:
    (a) Matriks regret R harus memiliki R[i,j] >= 0 untuk semua i, j
    (b) Setiap kolom j dari R harus mengandung minimal satu nol
    (c) Nilai Minimax Regret harus sama dengan R.max(axis=1).min()
    """
    assume(np.isfinite(payoff).all())

    val, idx, regret = compute_minimax_regret(payoff)

    # Shape matriks regret harus sama dengan payoff
    assert regret.shape == payoff.shape, (
        f"Shape regret {regret.shape} harus sama dengan payoff {payoff.shape}"
    )

    # (a) Semua nilai regret >= 0
    assert np.all(regret >= -1e-10), (
        f"Semua nilai regret harus >= 0, ditemukan nilai negatif: {regret.min()}"
    )

    # (b) Setiap kolom mengandung minimal satu nol
    for j in range(regret.shape[1]):
        col_min = regret[:, j].min()
        assert col_min <= 1e-10, (
            f"Kolom {j} harus mengandung minimal satu nol, "
            f"nilai minimum kolom = {col_min}"
        )

    # (c) Nilai Minimax Regret harus sama dengan R.max(axis=1).min()
    expected_val = float(regret.max(axis=1).min())
    assert abs(val - expected_val) < 1e-10, (
        f"Minimax Regret val={val} harus sama dengan "
        f"regret.max(axis=1).min()={expected_val}"
    )

    # Indeks yang dikembalikan harus valid
    m = payoff.shape[0]
    for i in idx:
        assert 0 <= i < m, f"Indeks {i} di luar rentang [0, {m})"

    # Harus ada minimal satu indeks
    assert len(idx) >= 1, "Harus ada minimal satu alternatif optimal"


# ---------------------------------------------------------------------------
# Property 20: Laplace scores equal row means
# Validates: Requirements 5.8
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(payoff_strategy)
def test_property_20_laplace_scores_equal_row_means(payoff):
    """
    **Validates: Requirements 5.8**

    Property 20: Untuk sembarang matriks payoff P, compute_laplace(P)[0][i]
    harus sama dengan P[i,:].mean() untuk semua i.

    Laplace mengasumsikan probabilitas sama untuk semua kondisi alam,
    sehingga skor = rata-rata baris.
    """
    assume(np.isfinite(payoff).all())

    scores, idx = compute_laplace(payoff)

    m = payoff.shape[0]

    # Shape scores harus (m,)
    assert scores.shape == (m,), (
        f"Shape scores harus ({m},), dapat {scores.shape}"
    )

    # Setiap skor harus sama dengan rata-rata baris yang bersangkutan
    for i in range(m):
        expected_score = float(payoff[i, :].mean())
        assert abs(float(scores[i]) - expected_score) < 1e-10, (
            f"scores[{i}]={scores[i]} harus sama dengan "
            f"P[{i},:].mean()={expected_score}"
        )

    # Indeks yang dikembalikan harus valid
    for i in idx:
        assert 0 <= i < m, f"Indeks {i} di luar rentang [0, {m})"

    # Harus ada minimal satu indeks
    assert len(idx) >= 1, "Harus ada minimal satu alternatif optimal"

    # Semua indeks yang dikembalikan harus memiliki skor == max skor
    max_score = float(scores.max())
    for i in idx:
        assert abs(float(scores[i]) - max_score) < 1e-10, (
            f"Alternatif {i} dikembalikan tapi scores[{i}]={scores[i]} "
            f"!= max_score={max_score}"
        )


# ---------------------------------------------------------------------------
# Unit tests tambahan untuk verifikasi contoh konkret
# ---------------------------------------------------------------------------

class TestComputeMaximaxConcrete:
    """Unit tests dengan contoh konkret untuk compute_maximax."""

    def test_simple_3x3(self):
        """Contoh 3 alternatif × 3 kondisi alam."""
        payoff = np.array([
            [10.0, 20.0, 30.0],   # row_max = 30
            [40.0,  5.0, 15.0],   # row_max = 40  ← Maximax
            [25.0, 25.0, 25.0],   # row_max = 25
        ])
        val, idx = compute_maximax(payoff)
        assert val == 40.0
        assert idx == [1]

    def test_tie_handling(self):
        """Dua alternatif dengan row_max yang sama."""
        payoff = np.array([
            [50.0, 10.0],   # row_max = 50
            [50.0, 20.0],   # row_max = 50
            [30.0, 30.0],   # row_max = 30
        ])
        val, idx = compute_maximax(payoff)
        assert val == 50.0
        assert set(idx) == {0, 1}

    def test_negative_payoffs(self):
        """Payoff negatif — Maximax adalah nilai negatif terkecil."""
        payoff = np.array([
            [-10.0, -20.0],   # row_max = -10  ← Maximax
            [-30.0, -15.0],   # row_max = -15
        ])
        val, idx = compute_maximax(payoff)
        assert val == -10.0
        assert idx == [0]


class TestComputeMaximinConcrete:
    """Unit tests dengan contoh konkret untuk compute_maximin."""

    def test_simple_3x3(self):
        """Contoh 3 alternatif × 3 kondisi alam."""
        payoff = np.array([
            [10.0, 20.0, 30.0],   # row_min = 10
            [40.0,  5.0, 15.0],   # row_min = 5
            [25.0, 18.0, 22.0],   # row_min = 18  ← Maximin
        ])
        val, idx = compute_maximin(payoff)
        assert val == 18.0
        assert idx == [2]

    def test_tie_handling(self):
        """Dua alternatif dengan row_min yang sama."""
        payoff = np.array([
            [15.0, 30.0],   # row_min = 15
            [15.0, 25.0],   # row_min = 15
            [10.0, 40.0],   # row_min = 10
        ])
        val, idx = compute_maximin(payoff)
        assert val == 15.0
        assert set(idx) == {0, 1}


class TestComputeMinimaxRegretConcrete:
    """Unit tests dengan contoh konkret untuk compute_minimax_regret."""

    def test_simple_2x2(self):
        """
        Contoh 2 alternatif × 2 kondisi alam.
        payoff = [[10, 20], [15, 12]]
        col_max = [15, 20]
        regret = [[5, 0], [0, 8]]
        row_max_regret = [5, 8]
        Minimax Regret = min(5, 8) = 5 → alternatif 0
        """
        payoff = np.array([[10.0, 20.0],
                           [15.0, 12.0]])
        val, idx, regret = compute_minimax_regret(payoff)
        assert val == 5.0
        assert idx == [0]
        expected_regret = np.array([[5.0, 0.0], [0.0, 8.0]])
        np.testing.assert_allclose(regret, expected_regret, atol=1e-10)

    def test_regret_column_zeros(self):
        """Setiap kolom regret harus mengandung minimal satu nol."""
        payoff = np.array([
            [30.0, 10.0, 20.0],
            [10.0, 30.0, 15.0],
            [20.0, 20.0, 25.0],
        ])
        _, _, regret = compute_minimax_regret(payoff)
        for j in range(regret.shape[1]):
            assert regret[:, j].min() == pytest.approx(0.0, abs=1e-10), (
                f"Kolom {j} harus mengandung nol"
            )


class TestComputeLaplaceConcrete:
    """Unit tests dengan contoh konkret untuk compute_laplace."""

    def test_simple_3x3(self):
        """Contoh 3 alternatif × 3 kondisi alam."""
        payoff = np.array([
            [10.0, 20.0, 30.0],   # mean = 20.0  ← Laplace
            [ 5.0, 15.0, 25.0],   # mean = 15.0
            [12.0, 18.0, 24.0],   # mean = 18.0
        ])
        scores, idx = compute_laplace(payoff)
        np.testing.assert_allclose(scores, [20.0, 15.0, 18.0], atol=1e-10)
        assert idx == [0]

    def test_equal_payoffs_all_tied(self):
        """Semua alternatif dengan payoff identik → semua tied."""
        payoff = np.array([
            [10.0, 10.0, 10.0],
            [10.0, 10.0, 10.0],
        ])
        scores, idx = compute_laplace(payoff)
        np.testing.assert_allclose(scores, [10.0, 10.0], atol=1e-10)
        assert set(idx) == {0, 1}

    def test_scores_equal_row_means(self):
        """Skor Laplace harus persis sama dengan rata-rata baris."""
        payoff = np.array([
            [1.0, 3.0, 5.0, 7.0],
            [2.0, 4.0, 6.0, 8.0],
        ])
        scores, _ = compute_laplace(payoff)
        np.testing.assert_allclose(scores[0], payoff[0].mean(), atol=1e-10)
        np.testing.assert_allclose(scores[1], payoff[1].mean(), atol=1e-10)
