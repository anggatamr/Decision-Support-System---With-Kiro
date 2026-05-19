"""
tests/test_payoff_table.py
--------------------------
Property-based tests dan unit tests untuk modules/payoff_table.py
menggunakan Hypothesis.

Properties yang diuji:
- Property 10: Column-wise maximum identification is correct
              (Validates: Requirements 3.5)

Unit tests tambahan:
- build_payoff_matrix: konversi, validasi dimensi, error handling
- get_column_max_indices: contoh konkret termasuk ties dan edge cases
"""

import numpy as np
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from modules.payoff_table import build_payoff_matrix, get_column_max_indices


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
    """Buat strategi matriks payoff shape (m, n) dengan nilai float64 terbatas."""
    return arrays(
        dtype=np.float64,
        shape=(m, n),
        elements=payoff_values,
    )


# ---------------------------------------------------------------------------
# Property 10: Column-wise maximum identification is correct
# Validates: Requirements 3.5
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    m_strategy.flatmap(lambda m: n_strategy.flatmap(
        lambda n: payoff_matrix_strategy(m, n)
    ))
)
def test_property_10_column_max_indices_correct(payoff):
    """
    **Validates: Requirements 3.5**

    Property 10: Untuk sembarang matriks payoff yang valid (numpy array),
    get_column_max_indices harus mengidentifikasi tepat indeks baris dengan
    nilai tertinggi di setiap kolom. Ties harus mengembalikan semua indeks
    yang terikat.

    Properti yang diverifikasi:
    1. Panjang hasil == jumlah kolom (n)
    2. Setiap indeks yang dikembalikan valid (dalam rentang [0, m-1])
    3. Nilai pada setiap indeks yang dikembalikan == nilai maksimum kolom
    4. Semua indeks dengan nilai == maksimum kolom dikembalikan (tidak ada
       yang terlewat — ties lengkap)
    5. Setiap sub-list tidak kosong (setiap kolom pasti punya maksimum)
    """
    assume(np.isfinite(payoff).all())

    result = get_column_max_indices(payoff)
    m, n = payoff.shape

    # 1. Panjang hasil harus == jumlah kolom
    assert len(result) == n, (
        f"Panjang hasil harus {n} (jumlah kolom), dapat {len(result)}"
    )

    for j in range(n):
        col = payoff[:, j]
        col_max = col.max()
        returned_indices = result[j]

        # 5. Sub-list tidak boleh kosong
        assert len(returned_indices) >= 1, (
            f"Kolom {j} harus memiliki minimal satu indeks maksimum, "
            f"tetapi sub-list kosong"
        )

        for idx in returned_indices:
            # 2. Setiap indeks valid
            assert 0 <= idx < m, (
                f"Indeks {idx} pada kolom {j} di luar rentang [0, {m-1}]"
            )
            # 3. Nilai pada indeks == nilai maksimum kolom
            assert payoff[idx, j] == col_max, (
                f"payoff[{idx}, {j}] = {payoff[idx, j]} != col_max = {col_max} "
                f"untuk kolom {j}"
            )

        # 4. Semua indeks dengan nilai == maksimum harus dikembalikan (ties lengkap)
        expected_indices = set(int(i) for i in np.where(col == col_max)[0])
        actual_indices = set(returned_indices)
        assert actual_indices == expected_indices, (
            f"Kolom {j}: indeks yang dikembalikan {actual_indices} tidak sama "
            f"dengan semua indeks maksimum yang diharapkan {expected_indices}. "
            f"Nilai kolom: {col.tolist()}, col_max = {col_max}"
        )


# ---------------------------------------------------------------------------
# Unit tests untuk build_payoff_matrix
# ---------------------------------------------------------------------------

class TestBuildPayoffMatrix:
    """Unit tests dengan contoh konkret untuk build_payoff_matrix."""

    def test_basic_conversion_from_strings(self):
        """Konversi list of lists berisi string ke numpy array float64."""
        raw = [["10", "20"], ["15", "12"]]
        alt_names = ["A1", "A2"]
        state_names = ["S1", "S2"]
        result = build_payoff_matrix(raw, alt_names, state_names)

        assert result.dtype == np.float64
        assert result.shape == (2, 2)
        np.testing.assert_array_equal(result, [[10.0, 20.0], [15.0, 12.0]])

    def test_conversion_from_floats(self):
        """Konversi list of lists berisi float langsung."""
        raw = [[1.5, 2.5, 3.5], [4.0, 5.0, 6.0]]
        alt_names = ["A1", "A2"]
        state_names = ["S1", "S2", "S3"]
        result = build_payoff_matrix(raw, alt_names, state_names)

        assert result.dtype == np.float64
        assert result.shape == (2, 3)
        np.testing.assert_allclose(result, [[1.5, 2.5, 3.5], [4.0, 5.0, 6.0]])

    def test_conversion_from_mixed_types(self):
        """Konversi list of lists berisi campuran int, float, dan string."""
        raw = [[1, "2.5", 3.0], ["4", 5, "6.7"]]
        alt_names = ["A1", "A2"]
        state_names = ["S1", "S2", "S3"]
        result = build_payoff_matrix(raw, alt_names, state_names)

        assert result.dtype == np.float64
        np.testing.assert_allclose(result, [[1.0, 2.5, 3.0], [4.0, 5.0, 6.7]])

    def test_negative_values(self):
        """Nilai negatif harus dikonversi dengan benar."""
        raw = [["-10", "-20.5"], ["0", "15"]]
        alt_names = ["A1", "A2"]
        state_names = ["S1", "S2"]
        result = build_payoff_matrix(raw, alt_names, state_names)

        np.testing.assert_allclose(result, [[-10.0, -20.5], [0.0, 15.0]])

    def test_shape_matches_alt_and_state_names(self):
        """Shape hasil harus (len(alt_names), len(state_names))."""
        raw = [[str(i * 3 + j) for j in range(4)] for i in range(3)]
        alt_names = ["A1", "A2", "A3"]
        state_names = ["S1", "S2", "S3", "S4"]
        result = build_payoff_matrix(raw, alt_names, state_names)

        assert result.shape == (3, 4)

    def test_raises_on_non_numeric_cell(self):
        """ValueError harus dilempar jika ada sel non-numerik."""
        raw = [["10", "abc"], ["15", "12"]]
        alt_names = ["A1", "A2"]
        state_names = ["S1", "S2"]

        with pytest.raises(ValueError, match=r"tidak dapat dikonversi ke float"):
            build_payoff_matrix(raw, alt_names, state_names)

    def test_raises_on_wrong_row_count(self):
        """ValueError jika jumlah baris raw_values != len(alt_names)."""
        raw = [["10", "20"]]  # hanya 1 baris, tapi 2 alternatif
        alt_names = ["A1", "A2"]
        state_names = ["S1", "S2"]

        with pytest.raises(ValueError, match=r"Jumlah baris"):
            build_payoff_matrix(raw, alt_names, state_names)

    def test_raises_on_wrong_column_count(self):
        """ValueError jika jumlah kolom baris != len(state_names)."""
        raw = [["10", "20", "30"], ["15", "12"]]  # baris ke-1 punya 3 kolom, baris ke-2 punya 2
        alt_names = ["A1", "A2"]
        state_names = ["S1", "S2", "S3"]

        with pytest.raises(ValueError, match=r"kolom"):
            build_payoff_matrix(raw, alt_names, state_names)

    def test_single_cell_matrix(self):
        """Matriks 1×1 (satu alternatif, satu kondisi alam)."""
        raw = [["42.0"]]
        alt_names = ["A1"]
        state_names = ["S1"]
        result = build_payoff_matrix(raw, alt_names, state_names)

        assert result.shape == (1, 1)
        assert result[0, 0] == 42.0


# ---------------------------------------------------------------------------
# Unit tests untuk get_column_max_indices
# ---------------------------------------------------------------------------

class TestGetColumnMaxIndices:
    """Unit tests dengan contoh konkret untuk get_column_max_indices."""

    def test_no_ties_simple(self):
        """Contoh sederhana tanpa ties."""
        payoff = np.array([[10.0, 5.0],
                           [3.0,  8.0],
                           [7.0,  2.0]])
        result = get_column_max_indices(payoff)
        # Kolom 0: max = 10 → baris 0
        # Kolom 1: max = 8  → baris 1
        assert result == [[0], [1]]

    def test_tie_in_first_column(self):
        """Tie di kolom pertama antara baris 0 dan 2."""
        payoff = np.array([[10.0, 5.0],
                           [3.0,  8.0],
                           [10.0, 2.0]])
        result = get_column_max_indices(payoff)
        # Kolom 0: max = 10 → baris 0 dan 2 (tie)
        # Kolom 1: max = 8  → baris 1
        assert set(result[0]) == {0, 2}
        assert result[1] == [1]

    def test_all_equal_values(self):
        """Semua nilai sama — semua baris harus dikembalikan untuk setiap kolom."""
        payoff = np.array([[5.0, 5.0],
                           [5.0, 5.0],
                           [5.0, 5.0]])
        result = get_column_max_indices(payoff)
        assert len(result) == 2
        assert set(result[0]) == {0, 1, 2}
        assert set(result[1]) == {0, 1, 2}

    def test_single_row(self):
        """Matriks dengan satu baris — selalu baris 0 untuk semua kolom."""
        payoff = np.array([[3.0, 7.0, 1.0]])
        result = get_column_max_indices(payoff)
        assert result == [[0], [0], [0]]

    def test_single_column(self):
        """Matriks dengan satu kolom."""
        payoff = np.array([[3.0], [9.0], [6.0]])
        result = get_column_max_indices(payoff)
        assert result == [[1]]

    def test_negative_values(self):
        """Nilai negatif — maksimum adalah nilai paling kecil absolutnya."""
        payoff = np.array([[-1.0, -5.0],
                           [-3.0, -2.0]])
        result = get_column_max_indices(payoff)
        # Kolom 0: max = -1 → baris 0
        # Kolom 1: max = -2 → baris 1
        assert result == [[0], [1]]

    def test_mixed_positive_negative(self):
        """Campuran nilai positif dan negatif."""
        payoff = np.array([[-10.0, 20.0],
                           [5.0,  -3.0],
                           [5.0,   15.0]])
        result = get_column_max_indices(payoff)
        # Kolom 0: max = 5 → baris 1 dan 2 (tie)
        # Kolom 1: max = 20 → baris 0
        assert set(result[0]) == {1, 2}
        assert result[1] == [0]

    def test_empty_matrix_returns_empty(self):
        """Matriks kosong (shape 0×n atau m×0) harus mengembalikan list kosong."""
        payoff_empty_rows = np.empty((0, 3), dtype=np.float64)
        assert get_column_max_indices(payoff_empty_rows) == []

        payoff_empty_cols = np.empty((3, 0), dtype=np.float64)
        assert get_column_max_indices(payoff_empty_cols) == []

    def test_returns_list_of_lists(self):
        """Tipe kembalian harus list[list[int]]."""
        payoff = np.array([[1.0, 2.0], [3.0, 4.0]])
        result = get_column_max_indices(payoff)

        assert isinstance(result, list)
        for sub in result:
            assert isinstance(sub, list)
            for idx in sub:
                assert isinstance(idx, int)

    def test_3x3_example_from_docstring(self):
        """Contoh dari docstring: matriks 3×2 dengan tie di kolom 0."""
        # Kolom 0: baris 0 dan 2 tie (nilai 10), kolom 1: baris 1 (nilai 8)
        payoff = np.array([[10.0, 5.0],
                           [3.0,  8.0],
                           [10.0, 2.0]])
        result = get_column_max_indices(payoff)
        assert set(result[0]) == {0, 2}
        assert result[1] == [1]
