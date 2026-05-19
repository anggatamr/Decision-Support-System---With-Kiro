"""
tests/test_data_driven.py
--------------------------
Property-based tests untuk computation layer modules/data_driven.py.

Properties yang diuji:
  Property 4 — File parsing round-trip preserves DataFrame shape (Req 2.2)
  Property 5 — Dataset info extraction is accurate (Req 2.3)
  Property 6 — Descriptive statistics match pandas (Req 2.4)
  Property 7 — Default column selection is first numeric column (Req 2.6)
  Property 8 — Correlation matrix matches pandas (Req 2.10)

Framework: Hypothesis dengan @settings(max_examples=100)
"""

from __future__ import annotations

import io

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings, assume, HealthCheck
from hypothesis import strategies as st
from hypothesis.extra.pandas import column, data_frames, range_indexes

from modules.data_driven import (
    compute_correlation_matrix,
    get_dataset_info,
    get_default_numeric_column,
    get_descriptive_stats,
    get_numeric_columns,
    parse_uploaded_file,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_csv_file(df: pd.DataFrame) -> io.BytesIO:
    """Serialisasi DataFrame ke CSV bytes dan kembalikan sebagai file-like object."""
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    buf.name = "test.csv"  # parse_uploaded_file membutuhkan atribut .name
    return buf


# ---------------------------------------------------------------------------
# Strategi Hypothesis
# ---------------------------------------------------------------------------

# Strategi untuk menghasilkan DataFrame dengan ≥1 baris dan ≥1 kolom numerik
_numeric_df_strategy = data_frames(
    columns=[
        column("col_a", dtype=float, elements=st.floats(
            min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False
        )),
        column("col_b", dtype=float, elements=st.floats(
            min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False
        )),
    ],
    index=range_indexes(min_size=1, max_size=50),
)

# Strategi untuk DataFrame dengan ≥2 kolom numerik (untuk korelasi)
_multi_numeric_df_strategy = data_frames(
    columns=[
        column("num_x", dtype=float, elements=st.floats(
            min_value=-1e4, max_value=1e4, allow_nan=False, allow_infinity=False
        )),
        column("num_y", dtype=float, elements=st.floats(
            min_value=-1e4, max_value=1e4, allow_nan=False, allow_infinity=False
        )),
        column("num_z", dtype=float, elements=st.floats(
            min_value=-1e4, max_value=1e4, allow_nan=False, allow_infinity=False
        )),
    ],
    index=range_indexes(min_size=2, max_size=50),
)

# Strategi untuk DataFrame dengan campuran kolom numerik dan non-numerik
_mixed_df_strategy = data_frames(
    columns=[
        column("num_col", dtype=float, elements=st.floats(
            min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False
        )),
        column("str_col", elements=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
            min_size=1, max_size=10
        )),
    ],
    index=range_indexes(min_size=1, max_size=30),
)


# ---------------------------------------------------------------------------
# Property 4: File parsing round-trip preserves DataFrame shape
# Validates: Requirements 2.2
# ---------------------------------------------------------------------------

class TestProperty4ParseRoundTrip:
    """
    **Validates: Requirements 2.2**

    For any valid DataFrame with at least 1 row and 1 column, serializing it
    to CSV bytes and parsing it back via parse_uploaded_file() should produce
    a DataFrame with the same number of rows and columns.
    """

    @given(_numeric_df_strategy)
    @settings(max_examples=100)
    def test_csv_roundtrip_preserves_shape(self, df: pd.DataFrame):
        """Round-trip CSV: jumlah baris dan kolom harus sama."""
        assume(len(df) >= 1)

        csv_file = _make_csv_file(df)
        result = parse_uploaded_file(csv_file)

        assert result.shape[0] == df.shape[0], (
            f"Jumlah baris berubah: expected {df.shape[0]}, got {result.shape[0]}"
        )
        assert result.shape[1] == df.shape[1], (
            f"Jumlah kolom berubah: expected {df.shape[1]}, got {result.shape[1]}"
        )

    @given(_mixed_df_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_csv_roundtrip_preserves_column_names(self, df: pd.DataFrame):
        """Round-trip CSV: nama kolom harus dipertahankan."""
        assume(len(df) >= 1)

        csv_file = _make_csv_file(df)
        result = parse_uploaded_file(csv_file)

        assert list(result.columns) == list(df.columns), (
            f"Nama kolom berubah: expected {list(df.columns)}, got {list(result.columns)}"
        )

    def test_parse_raises_for_unsupported_format(self):
        """ValueError harus dilempar untuk format yang tidak didukung."""
        buf = io.BytesIO(b"data")
        buf.name = "file.txt"
        with pytest.raises(ValueError, match="Format tidak didukung"):
            parse_uploaded_file(buf)

    def test_parse_raises_for_empty_csv(self):
        """ValueError harus dilempar untuk CSV yang hanya berisi header."""
        buf = io.BytesIO(b"col_a,col_b\n")
        buf.name = "empty.csv"
        with pytest.raises(ValueError, match="tidak memiliki baris data"):
            parse_uploaded_file(buf)


# ---------------------------------------------------------------------------
# Property 5: Dataset info extraction is accurate
# Validates: Requirements 2.3
# ---------------------------------------------------------------------------

class TestProperty5DatasetInfo:
    """
    **Validates: Requirements 2.3**

    For any pandas DataFrame, the info extraction function should return
    row count equal to len(df), column count equal to len(df.columns),
    and dtype mapping equal to df.dtypes.to_dict() (as strings).
    """

    @given(_numeric_df_strategy)
    @settings(max_examples=100)
    def test_n_rows_equals_len_df(self, df: pd.DataFrame):
        """n_rows harus sama dengan len(df)."""
        info = get_dataset_info(df)
        assert info["n_rows"] == len(df)

    @given(_numeric_df_strategy)
    @settings(max_examples=100)
    def test_n_cols_equals_len_columns(self, df: pd.DataFrame):
        """n_cols harus sama dengan len(df.columns)."""
        info = get_dataset_info(df)
        assert info["n_cols"] == len(df.columns)

    @given(_mixed_df_strategy)
    @settings(max_examples=100)
    def test_columns_list_matches(self, df: pd.DataFrame):
        """Daftar kolom harus sama dengan list(df.columns)."""
        info = get_dataset_info(df)
        assert info["columns"] == list(df.columns)

    @given(_mixed_df_strategy)
    @settings(max_examples=100)
    def test_dtypes_mapping_matches(self, df: pd.DataFrame):
        """Mapping dtype harus sama dengan df.dtypes (sebagai string)."""
        info = get_dataset_info(df)
        expected_dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
        assert info["dtypes"] == expected_dtypes

    @given(_numeric_df_strategy)
    @settings(max_examples=100)
    def test_info_keys_present(self, df: pd.DataFrame):
        """Dict hasil harus memiliki keempat kunci yang diperlukan."""
        info = get_dataset_info(df)
        assert set(info.keys()) == {"n_rows", "n_cols", "columns", "dtypes"}


# ---------------------------------------------------------------------------
# Property 6: Descriptive statistics match pandas
# Validates: Requirements 2.4
# ---------------------------------------------------------------------------

class TestProperty6DescriptiveStats:
    """
    **Validates: Requirements 2.4**

    For any DataFrame with at least one numeric column, the computed
    descriptive statistics should equal the output of df.describe()
    for all numeric columns.
    """

    @given(_numeric_df_strategy)
    @settings(max_examples=100)
    def test_describe_matches_pandas(self, df: pd.DataFrame):
        """Output get_descriptive_stats harus identik dengan df.describe()."""
        result = get_descriptive_stats(df)
        expected = df.describe()

        pd.testing.assert_frame_equal(result, expected)

    @given(_mixed_df_strategy)
    @settings(max_examples=100)
    def test_describe_only_numeric_columns(self, df: pd.DataFrame):
        """Statistik deskriptif hanya mencakup kolom numerik (default pandas)."""
        result = get_descriptive_stats(df)
        expected = df.describe()

        # Kolom dalam hasil harus sama dengan kolom numerik saja
        assert list(result.columns) == list(expected.columns)

    @given(_numeric_df_strategy)
    @settings(max_examples=100)
    def test_describe_contains_standard_stats(self, df: pd.DataFrame):
        """Hasil harus mengandung statistik standar: count, mean, std, min, max."""
        result = get_descriptive_stats(df)
        for stat in ["count", "mean", "std", "min", "max"]:
            assert stat in result.index, f"Statistik '{stat}' tidak ditemukan dalam hasil"


# ---------------------------------------------------------------------------
# Property 7: Default column selection is first numeric column
# Validates: Requirements 2.6
# ---------------------------------------------------------------------------

class TestProperty7DefaultNumericColumn:
    """
    **Validates: Requirements 2.6**

    For any DataFrame with at least one numeric column,
    get_default_numeric_column(df) should return the name of the first
    column whose dtype is numeric.
    """

    @given(_numeric_df_strategy)
    @settings(max_examples=100)
    def test_returns_first_numeric_column(self, df: pd.DataFrame):
        """Harus mengembalikan kolom numerik pertama."""
        numeric_cols = list(df.select_dtypes(include="number").columns)
        assume(len(numeric_cols) >= 1)

        result = get_default_numeric_column(df)
        assert result == numeric_cols[0], (
            f"Expected '{numeric_cols[0]}', got '{result}'"
        )

    @given(_mixed_df_strategy)
    @settings(max_examples=100)
    def test_returns_numeric_column_not_string(self, df: pd.DataFrame):
        """Kolom yang dikembalikan harus bertipe numerik."""
        numeric_cols = list(df.select_dtypes(include="number").columns)
        assume(len(numeric_cols) >= 1)

        result = get_default_numeric_column(df)
        assert result in numeric_cols, (
            f"'{result}' bukan kolom numerik. Kolom numerik: {numeric_cols}"
        )

    def test_raises_when_no_numeric_columns(self):
        """ValueError harus dilempar jika tidak ada kolom numerik."""
        df = pd.DataFrame({"nama": ["Alice", "Bob"], "kota": ["Jakarta", "Bandung"]})
        with pytest.raises(ValueError, match="Tidak ada kolom numerik"):
            get_default_numeric_column(df)

    @given(_numeric_df_strategy)
    @settings(max_examples=100)
    def test_result_is_string(self, df: pd.DataFrame):
        """Nilai kembalian harus berupa string (nama kolom)."""
        result = get_default_numeric_column(df)
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Property 8: Correlation matrix matches pandas
# Validates: Requirements 2.10
# ---------------------------------------------------------------------------

class TestProperty8CorrelationMatrix:
    """
    **Validates: Requirements 2.10**

    For any DataFrame with at least 2 numeric columns, the computed
    correlation matrix should equal df.select_dtypes(include='number').corr().
    """

    @given(_multi_numeric_df_strategy)
    @settings(max_examples=100)
    def test_correlation_matches_pandas(self, df: pd.DataFrame):
        """Matriks korelasi harus identik dengan pandas .corr()."""
        result = compute_correlation_matrix(df)
        expected = df.select_dtypes(include="number").corr()

        pd.testing.assert_frame_equal(result, expected)

    @given(_multi_numeric_df_strategy)
    @settings(max_examples=100)
    def test_correlation_matrix_is_square(self, df: pd.DataFrame):
        """Matriks korelasi harus berbentuk persegi (n × n)."""
        result = compute_correlation_matrix(df)
        assert result.shape[0] == result.shape[1], (
            f"Matriks korelasi tidak persegi: {result.shape}"
        )

    @given(_multi_numeric_df_strategy)
    @settings(max_examples=100)
    def test_correlation_diagonal_is_one(self, df: pd.DataFrame):
        """Diagonal matriks korelasi harus bernilai 1.0 (korelasi diri sendiri)."""
        result = compute_correlation_matrix(df)
        numeric_cols = list(df.select_dtypes(include="number").columns)

        for col in numeric_cols:
            diag_val = result.loc[col, col]
            assert abs(diag_val - 1.0) < 1e-9 or pd.isna(diag_val), (
                f"Diagonal untuk kolom '{col}' bukan 1.0: {diag_val}"
            )

    @given(_multi_numeric_df_strategy)
    @settings(max_examples=100)
    def test_correlation_values_in_range(self, df: pd.DataFrame):
        """Semua nilai korelasi harus berada dalam rentang [-1, 1] atau NaN."""
        result = compute_correlation_matrix(df)
        values = result.values.flatten()

        for val in values:
            if not np.isnan(val):
                assert -1.0 - 1e-9 <= val <= 1.0 + 1e-9, (
                    f"Nilai korelasi di luar rentang [-1, 1]: {val}"
                )

    def test_correlation_with_no_numeric_columns(self):
        """DataFrame tanpa kolom numerik harus menghasilkan DataFrame kosong."""
        df = pd.DataFrame({"nama": ["Alice", "Bob"], "kota": ["Jakarta", "Bandung"]})
        result = compute_correlation_matrix(df)
        assert result.empty

    @given(_multi_numeric_df_strategy)
    @settings(max_examples=100)
    def test_correlation_column_names_match_numeric_columns(self, df: pd.DataFrame):
        """Nama kolom dan indeks matriks korelasi harus sama dengan kolom numerik."""
        result = compute_correlation_matrix(df)
        numeric_cols = list(df.select_dtypes(include="number").columns)

        assert list(result.columns) == numeric_cols
        assert list(result.index) == numeric_cols
