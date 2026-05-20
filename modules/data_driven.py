"""
modules/data_driven.py
----------------------
Modul Data-Driven DSS — eksplorasi dan analisis dataset yang diunggah pengguna.

Struktur file:
  - Computation Layer (pure functions, tidak mengimpor streamlit)
      parse_uploaded_file, get_dataset_info, get_descriptive_stats,
      get_numeric_columns, get_default_numeric_column, compute_correlation_matrix
  - UI Layer (render_data_driven_module) — diimplementasikan di task 4.7
"""

from __future__ import annotations

import io
from typing import Any

import pandas as pd


# ---------------------------------------------------------------------------
# Computation Layer — pure functions (no Streamlit imports)
# ---------------------------------------------------------------------------


def parse_uploaded_file(uploaded_file) -> pd.DataFrame:
    """
    Parse file CSV atau XLSX yang diunggah menjadi pandas DataFrame.

    Parameters
    ----------
    uploaded_file : file-like object
        Objek file dengan atribut `.name` (str) dan konten yang dapat dibaca.
        Kompatibel dengan Streamlit UploadedFile maupun objek BytesIO dengan
        atribut `name` yang ditambahkan secara manual (untuk testing).

    Returns
    -------
    pd.DataFrame
        DataFrame hasil parsing dengan ≥1 baris data.

    Raises
    ------
    ValueError
        - Jika ekstensi file bukan CSV, XLSX, atau XLS.
        - Jika file tidak memiliki baris data (DataFrame kosong setelah parsing).
    """
    filename: str = getattr(uploaded_file, "name", "") or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext == "csv":
        df = pd.read_csv(uploaded_file)
    elif ext in ("xlsx", "xls"):
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    else:
        raise ValueError(
            f"Format tidak didukung: '{ext}'. "
            "Harap unggah file berformat CSV atau XLSX."
        )

    if len(df) == 0:
        raise ValueError("File tidak memiliki baris data")

    return df


def get_dataset_info(df: pd.DataFrame) -> dict[str, Any]:
    """
    Kembalikan informasi ringkas tentang dataset.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    dict dengan kunci:
        "n_rows"  : int   — jumlah baris (len(df))
        "n_cols"  : int   — jumlah kolom (len(df.columns))
        "columns" : list[str] — nama-nama kolom
        "dtypes"  : dict[str, str] — mapping nama kolom → tipe data (sebagai string)
    """
    return {
        "n_rows": len(df),
        "n_cols": len(df.columns),
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }


def get_descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Hitung statistik deskriptif lengkap untuk semua kolom numerik.

    Wrapper tipis di atas `df.describe()` yang mencakup count, mean, std,
    min, Q1, median, Q3, dan max untuk setiap kolom numerik.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        Output dari `df.describe()`.
    """
    return df.describe()


def get_numeric_columns(df: pd.DataFrame) -> list[str]:
    """
    Kembalikan daftar nama kolom yang bertipe numerik.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    list[str]
        Nama kolom dengan dtype numerik (int, float, dll.).
        Kembalikan list kosong jika tidak ada kolom numerik.
    """
    return list(df.select_dtypes(include="number").columns)


def get_default_numeric_column(df: pd.DataFrame) -> str:
    """
    Kembalikan nama kolom numerik pertama sebagai pilihan default visualisasi.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    str
        Nama kolom numerik pertama.

    Raises
    ------
    ValueError
        Jika DataFrame tidak memiliki kolom numerik sama sekali.
    """
    numeric_cols = get_numeric_columns(df)
    if not numeric_cols:
        raise ValueError("Tidak ada kolom numerik yang terdeteksi")
    return numeric_cols[0]


def compute_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Hitung matriks korelasi Pearson antar semua kolom numerik.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        Matriks korelasi dari `df.select_dtypes(include='number').corr()`.
        Mengembalikan DataFrame kosong jika tidak ada kolom numerik.
    """
    return df.select_dtypes(include="number").corr()


# ---------------------------------------------------------------------------
# UI Layer — render_data_driven_module()
# Task 4.7 — Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10
# ---------------------------------------------------------------------------

import streamlit as st
import plotly.express as px

from utils.validators import validate_file


def render_data_driven_module() -> None:
    """
    Render modul Data-Driven DSS secara lengkap.

    Alur:
    1. Sidebar — file uploader (CSV/XLSX) + selector kolom
    2. Main panel — pratinjau data, info dataset, statistik deskriptif,
       chart tren, heatmap korelasi
    3. Simpan df ke session_state dan tandai modul sebagai selesai
    """

    # ------------------------------------------------------------------
    # Sidebar — file uploader
    # ------------------------------------------------------------------
    st.markdown("### 📂 Unggah Dataset")
    uploaded_file = st.file_uploader(
        "Pilih file CSV atau XLSX",
        type=["csv", "xlsx", "xls"],
        help="Ukuran maksimum: 50 MB",
        key="data_driven_uploader",
    )

    # ------------------------------------------------------------------
    # Main panel — judul
    # ------------------------------------------------------------------
    st.title("📊 Data-Driven DSS — Eksplorasi Dataset")
    st.markdown(
        "Unggah dataset Anda untuk melihat pratinjau data, statistik deskriptif, "
        "tren kolom numerik, dan matriks korelasi secara interaktif."
    )

    # Jika belum ada file yang diunggah, tampilkan petunjuk dan hentikan
    if uploaded_file is None:
        st.info("⬅️ Silakan unggah file CSV atau XLSX melalui panel sidebar untuk memulai analisis.")
        return

    # ------------------------------------------------------------------
    # Validasi file via validator
    # ------------------------------------------------------------------
    is_valid, error_msg = validate_file(uploaded_file)
    if not is_valid:
        st.error(f"❌ File tidak valid: {error_msg}")
        return

    # ------------------------------------------------------------------
    # Parse file (dengan spinner — Req 2.2)
    # ------------------------------------------------------------------
    with st.spinner("⏳ Memuat dataset, harap tunggu..."):
        try:
            df = parse_uploaded_file(uploaded_file)
        except ValueError as exc:
            st.error(f"❌ Gagal memuat file: {exc}")
            return
        except Exception as exc:  # noqa: BLE001
            st.error(f"❌ Terjadi kesalahan saat membaca file: {type(exc).__name__}: {exc}")
            return

    # ------------------------------------------------------------------
    # Simpan ke session_state
    # ------------------------------------------------------------------
    st.session_state["df"] = df
    st.session_state["df_filename"] = uploaded_file.name
    if "completed_modules" not in st.session_state:
        st.session_state["completed_modules"] = set()
    st.session_state["completed_modules"].add("data_driven")

    # ------------------------------------------------------------------
    # Informasi dataset — metric cards
    # ------------------------------------------------------------------
    info = get_dataset_info(df)

    st.markdown("---")
    st.subheader("ℹ️ Informasi Dataset")

    col1, col2, col3 = st.columns(3)
    col1.metric("Jumlah Baris", f"{info['n_rows']:,}")
    col2.metric("Jumlah Kolom", info["n_cols"])
    col3.metric("Nama File", uploaded_file.name)

    # Tabel tipe data kolom
    with st.expander("Tipe Data Setiap Kolom", expanded=False):
        dtype_df = pd.DataFrame(
            {"Kolom": list(info["dtypes"].keys()), "Tipe Data": list(info["dtypes"].values())}
        )
        st.dataframe(dtype_df, use_container_width=True, hide_index=True)

    # ------------------------------------------------------------------
    # Pratinjau 10 baris pertama
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("👁️ Pratinjau Data (10 Baris Pertama)")
    st.dataframe(df.head(10), use_container_width=True)

    # ------------------------------------------------------------------
    # Statistik deskriptif
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📐 Statistik Deskriptif")
    desc_stats = get_descriptive_stats(df)
    if desc_stats.empty:
        st.warning("⚠️ Tidak ada kolom numerik yang terdeteksi — statistik deskriptif tidak tersedia.")
    else:
        st.dataframe(desc_stats, use_container_width=True)

    # ------------------------------------------------------------------
    # Visualisasi tren data
    # ------------------------------------------------------------------
    numeric_cols = get_numeric_columns(df)

    st.markdown("---")
    st.subheader("📈 Visualisasi Tren Data")

    if not numeric_cols:
        # Req 2.9 — tidak ada kolom numerik
        st.warning("⚠️ Tidak ada kolom numerik yang terdeteksi. Visualisasi tren data tidak tersedia.")
    else:
        # Sidebar — selector kolom (Req 2.6)
        default_col = get_default_numeric_column(df)
        selected_col = st.selectbox(
            "Pilih kolom untuk divisualisasikan",
            options=numeric_cols,
            index=numeric_cols.index(default_col),
            key="data_driven_col_selector",
        )

        # Sidebar — pilihan jenis chart
        chart_type = st.radio(
            "Jenis chart",
            options=["Line Chart", "Bar Chart"],
            index=0,
            key="data_driven_chart_type",
        )

        # Buat chart (Req 2.5)
        chart_title = f"Tren '{selected_col}' berdasarkan Urutan Baris"
        x_label = "Indeks Baris"
        y_label = selected_col

        plot_df = df[[selected_col]].reset_index().rename(columns={"index": x_label})

        if chart_type == "Line Chart":
            fig = px.line(
                plot_df,
                x=x_label,
                y=selected_col,
                title=chart_title,
                labels={x_label: x_label, selected_col: y_label},
                template="plotly_white",
            )
        else:
            fig = px.bar(
                plot_df,
                x=x_label,
                y=selected_col,
                title=chart_title,
                labels={x_label: x_label, selected_col: y_label},
                template="plotly_white",
            )

        fig.update_layout(
            xaxis_title=x_label,
            yaxis_title=y_label,
            title_font_size=16,
        )
        st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------------------
    # Heatmap korelasi (Req 2.10) — hanya jika ≥2 kolom numerik
    # ------------------------------------------------------------------
    if len(numeric_cols) >= 2:
        st.markdown("---")
        st.subheader("🔥 Heatmap Korelasi Antar Kolom Numerik")

        corr_matrix = compute_correlation_matrix(df)

        fig_corr = px.imshow(
            corr_matrix,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            title="Matriks Korelasi Pearson",
            template="plotly_white",
            labels={"color": "Korelasi"},
        )
        fig_corr.update_layout(
            title_font_size=16,
            xaxis_title="Kolom",
            yaxis_title="Kolom",
        )
        st.plotly_chart(fig_corr, use_container_width=True)

        st.caption(
            "Nilai mendekati **+1** menunjukkan korelasi positif kuat, "
            "mendekati **-1** menunjukkan korelasi negatif kuat, "
            "dan mendekati **0** menunjukkan tidak ada korelasi linear."
        )
