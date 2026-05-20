"""
modules/payoff_table.py
-----------------------
Modul Payoff Table — Kelompok 1 (Certainty) dari Model-Driven DSS.

Struktur file:
  - Computation Layer (pure functions, tidak mengimpor streamlit)
      build_payoff_matrix      — konversi raw input ke numpy array float64
      get_column_max_indices   — indeks nilai maksimum per kolom (handle ties)
  - UI Layer
      render_payoff_table_module() — render seluruh modul Payoff Table Generator
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Computation Layer — pure functions (no Streamlit imports)
# ---------------------------------------------------------------------------


def build_payoff_matrix(
    raw_values: list[list],
    alt_names: list[str],
    state_names: list[str],
) -> np.ndarray:
    """
    Konversi raw_values (list of lists berisi string atau float) ke numpy array
    dengan dtype float64.

    Parameters
    ----------
    raw_values : list[list]
        Matriks nilai payoff mentah berukuran (m, n), di mana setiap elemen
        dapat berupa str, int, atau float yang merepresentasikan angka.
    alt_names : list[str]
        Nama-nama alternatif keputusan (m entri). Digunakan untuk validasi
        dimensi baris.
    state_names : list[str]
        Nama-nama kondisi alam / state of nature (n entri). Digunakan untuk
        validasi dimensi kolom.

    Returns
    -------
    np.ndarray
        Array float64 dengan shape (len(alt_names), len(state_names)).

    Raises
    ------
    ValueError
        Jika konversi ke float gagal untuk sel mana pun, atau jika dimensi
        raw_values tidak sesuai dengan len(alt_names) × len(state_names).
    """
    m = len(alt_names)
    n = len(state_names)

    if len(raw_values) != m:
        raise ValueError(
            f"Jumlah baris raw_values ({len(raw_values)}) tidak sesuai "
            f"dengan jumlah alternatif ({m})."
        )

    result = np.empty((m, n), dtype=np.float64)

    for i, row in enumerate(raw_values):
        if len(row) != n:
            raise ValueError(
                f"Baris {i} memiliki {len(row)} kolom, "
                f"tetapi diharapkan {n} kolom (jumlah kondisi alam)."
            )
        for j, cell in enumerate(row):
            try:
                result[i, j] = float(cell)
            except (ValueError, TypeError) as exc:
                raise ValueError(
                    f"Nilai pada sel ({i}, {j}) tidak dapat dikonversi ke float: "
                    f"'{cell}'"
                ) from exc

    return result


def get_column_max_indices(payoff: np.ndarray) -> list[list[int]]:
    """
    Untuk setiap kolom j pada payoff matrix, kembalikan daftar indeks baris
    yang memiliki nilai maksimum di kolom tersebut (termasuk semua ties).

    Parameters
    ----------
    payoff : np.ndarray
        Array float64 dengan shape (m, n) — m alternatif, n kondisi alam.

    Returns
    -------
    list[list[int]]
        List dengan panjang n (jumlah kolom). Setiap elemen adalah list indeks
        baris (int) yang memiliki nilai maksimum di kolom tersebut.

        Contoh: untuk matriks 3×2 di mana kolom 0 memiliki tie antara baris 0
        dan 2, dan kolom 1 maksimumnya di baris 1:
            [[0, 2], [1]]

    Notes
    -----
    - Jika payoff kosong (shape (0, n) atau (m, 0)), kembalikan list kosong.
    - Ties ditangani dengan mengembalikan semua indeks yang memiliki nilai
      sama dengan nilai maksimum kolom tersebut.
    """
    if payoff.ndim != 2 or payoff.size == 0:
        return []

    n_cols = payoff.shape[1]
    result: list[list[int]] = []

    for j in range(n_cols):
        col = payoff[:, j]
        col_max = col.max()
        # np.where mengembalikan tuple; ambil array pertama dan konversi ke list[int]
        indices = [int(i) for i in np.where(col == col_max)[0]]
        result.append(indices)

    return result


# ---------------------------------------------------------------------------
# UI Layer — render_payoff_table_module()
# ---------------------------------------------------------------------------

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.validators import validate_payoff_matrix
from utils.formatters import fmt_monetary, fmt_stat


def render_payoff_table_module() -> None:
    """
    Render modul Payoff Table Generator (Kelompok 1 — Certainty).

    Alur:
    1. Sidebar: input jumlah alternatif & kondisi alam, nama-nama, tombol konfirmasi
    2. Main panel: grid input nilai payoff (setelah konfirmasi)
    3. Main panel: tampilkan payoff table + highlight maks per kolom
    4. Main panel: heatmap Plotly
    5. Main panel: rumus LaTeX + deskripsi metodologi
    6. Simpan ke session_state dan tandai modul selesai
    """

    # ------------------------------------------------------------------
    # Inisialisasi session_state keys yang dibutuhkan modul ini
    # ------------------------------------------------------------------
    if "payoff_matrix" not in st.session_state:
        st.session_state["payoff_matrix"] = None
    if "alt_names" not in st.session_state:
        st.session_state["alt_names"] = []
    if "state_names" not in st.session_state:
        st.session_state["state_names"] = []
    if "completed_modules" not in st.session_state:
        st.session_state["completed_modules"] = set()
    if "_pt_confirmed" not in st.session_state:
        st.session_state["_pt_confirmed"] = False
    if "_pt_n_alt" not in st.session_state:
        st.session_state["_pt_n_alt"] = 3
    if "_pt_n_states" not in st.session_state:
        st.session_state["_pt_n_states"] = 3

    # ------------------------------------------------------------------
    # Sidebar — dimensi tabel
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("⚙️ Dimensi Payoff Table")

    n_alt = st.number_input(
        "Jumlah Alternatif",
        min_value=2,
        max_value=10,
        value=st.session_state["_pt_n_alt"],
        step=1,
        key="_sidebar_n_alt",
        help="Masukkan jumlah alternatif keputusan (2–10)",
    )
    n_states = st.number_input(
        "Jumlah Kondisi Alam",
        min_value=2,
        max_value=10,
        value=st.session_state["_pt_n_states"],
        step=1,
        key="_sidebar_n_states",
        help="Masukkan jumlah kondisi alam / state of nature (2–10)",
    )

    # Jika dimensi berubah, reset konfirmasi
    if n_alt != st.session_state["_pt_n_alt"] or n_states != st.session_state["_pt_n_states"]:
        st.session_state["_pt_confirmed"] = False
        st.session_state["_pt_n_alt"] = int(n_alt)
        st.session_state["_pt_n_states"] = int(n_states)

    # ------------------------------------------------------------------
    # Sidebar — nama alternatif
    # ------------------------------------------------------------------
    st.markdown("**Nama Alternatif:**")
    alt_names_input: list[str] = []
    for i in range(int(n_alt)):
        default_alt = (
            st.session_state["alt_names"][i]
            if i < len(st.session_state["alt_names"])
            else f"Alternatif {i + 1}"
        )
        name = st.text_input(
            f"Alternatif {i + 1}",
            value=default_alt,
            max_chars=50,
            key=f"_pt_alt_{i}",
        )
        alt_names_input.append(name.strip() if name.strip() else f"Alternatif {i + 1}")

    # ------------------------------------------------------------------
    # Sidebar — nama kondisi alam
    # ------------------------------------------------------------------
    st.markdown("**Nama Kondisi Alam:**")
    state_names_input: list[str] = []
    for j in range(int(n_states)):
        default_state = (
            st.session_state["state_names"][j]
            if j < len(st.session_state["state_names"])
            else f"Kondisi {j + 1}"
        )
        name = st.text_input(
            f"Kondisi {j + 1}",
            value=default_state,
            max_chars=50,
            key=f"_pt_state_{j}",
        )
        state_names_input.append(name.strip() if name.strip() else f"Kondisi {j + 1}")

    # ------------------------------------------------------------------
    # Sidebar — tombol konfirmasi dimensi
    # ------------------------------------------------------------------
    if st.button("✅ Konfirmasi Dimensi", key="_pt_confirm_btn", use_container_width=True):
        st.session_state["_pt_confirmed"] = True
        st.session_state["_pt_n_alt"] = int(n_alt)
        st.session_state["_pt_n_states"] = int(n_states)
        # Reset payoff matrix saat dimensi dikonfirmasi ulang
        st.session_state["payoff_matrix"] = None
        st.session_state["alt_names"] = alt_names_input
        st.session_state["state_names"] = state_names_input

    # ------------------------------------------------------------------
    # Main Panel — header
    # ------------------------------------------------------------------
    st.title("📋 Certainty — Payoff Table Generator")
    st.markdown(
        "Buat dan visualisasikan **Payoff Table** secara interaktif untuk analisis "
        "keputusan di bawah kondisi kepastian."
    )

    if not st.session_state["_pt_confirmed"]:
        st.info(
            "👈 Atur jumlah alternatif, jumlah kondisi alam, dan nama-namanya di sidebar, "
            "lalu tekan **Konfirmasi Dimensi** untuk melanjutkan."
        )
        return

    # Ambil nama yang sudah dikonfirmasi
    confirmed_alt_names: list[str] = st.session_state["alt_names"]
    confirmed_state_names: list[str] = st.session_state["state_names"]
    m = len(confirmed_alt_names)
    n = len(confirmed_state_names)

    st.success(
        f"Dimensi dikonfirmasi: **{m} alternatif** × **{n} kondisi alam**. "
        "Isi nilai payoff pada grid di bawah ini."
    )

    # ------------------------------------------------------------------
    # Main Panel — grid input nilai payoff
    # ------------------------------------------------------------------
    st.subheader("📝 Input Nilai Payoff")
    st.markdown(
        "Masukkan nilai payoff untuk setiap kombinasi alternatif dan kondisi alam. "
        "Nilai harus berupa angka numerik."
    )

    # Buat header kolom
    col_headers = st.columns([2] + [1] * n)
    col_headers[0].markdown("**Alternatif \\ Kondisi**")
    for j, sname in enumerate(confirmed_state_names):
        col_headers[j + 1].markdown(f"**{sname}**")

    # Inisialisasi raw_values dari session_state jika ada
    raw_values: list[list[float]] = []
    for i, aname in enumerate(confirmed_alt_names):
        row_cols = st.columns([2] + [1] * n)
        row_cols[0].markdown(f"**{aname}**")
        row: list[float] = []
        for j in range(n):
            # Coba ambil nilai sebelumnya dari payoff_matrix
            default_val = 0.0
            if (
                st.session_state["payoff_matrix"] is not None
                and i < st.session_state["payoff_matrix"].shape[0]
                and j < st.session_state["payoff_matrix"].shape[1]
            ):
                default_val = float(st.session_state["payoff_matrix"][i, j])

            cell_val = row_cols[j + 1].number_input(
                label=f"p_{i+1}{j+1}",
                value=default_val,
                step=0.01,
                format="%.2f",
                key=f"_pt_cell_{i}_{j}",
                label_visibility="collapsed",
            )
            row.append(cell_val)
        raw_values.append(row)

    # ------------------------------------------------------------------
    # Tombol Buat Payoff Table
    # ------------------------------------------------------------------
    if st.button("🔨 Buat Payoff Table", key="_pt_build_btn", type="primary"):
        # Validasi via validator
        raw_str = [[str(v) for v in row] for row in raw_values]
        is_valid, invalid_cells = validate_payoff_matrix(raw_str)

        if not is_valid:
            cell_list = ", ".join(
                f"({confirmed_alt_names[r]}, {confirmed_state_names[c]})"
                for r, c in invalid_cells
            )
            st.error(
                f"❌ Terdapat sel yang tidak valid: {cell_list}. "
                "Pastikan semua sel berisi nilai numerik yang valid."
            )
        else:
            # Bangun numpy array
            matrix = build_payoff_matrix(raw_values, confirmed_alt_names, confirmed_state_names)
            st.session_state["payoff_matrix"] = matrix
            st.session_state["alt_names"] = confirmed_alt_names
            st.session_state["state_names"] = confirmed_state_names
            st.session_state["completed_modules"].add("payoff_table")
            st.success("✅ Payoff Table berhasil dibuat!")

    # ------------------------------------------------------------------
    # Tampilkan hasil jika payoff_matrix sudah ada
    # ------------------------------------------------------------------
    if st.session_state["payoff_matrix"] is None:
        return

    payoff = st.session_state["payoff_matrix"]
    alt_names = st.session_state["alt_names"]
    state_names = st.session_state["state_names"]

    # ------------------------------------------------------------------
    # Payoff Table dengan highlight nilai maksimum per kolom
    # ------------------------------------------------------------------
    st.subheader("📊 Payoff Table")

    df_payoff = pd.DataFrame(payoff, index=alt_names, columns=state_names)

    def highlight_col_max(df: pd.DataFrame) -> pd.DataFrame:
        """Kembalikan DataFrame style string dengan highlight hijau pada nilai maks per kolom."""
        styles = pd.DataFrame("", index=df.index, columns=df.columns)
        for col in df.columns:
            col_max = df[col].max()
            styles.loc[df[col] == col_max, col] = (
                "background-color: #d4edda; color: #155724; font-weight: bold;"
            )
        return styles

    styled_df = df_payoff.style.apply(highlight_col_max, axis=None).format("{:.2f}")
    st.dataframe(styled_df, use_container_width=True)

    st.caption(
        "🟢 Sel yang disorot hijau menunjukkan nilai payoff **maksimum** pada setiap kondisi alam (kolom)."
    )

    # ------------------------------------------------------------------
    # Heatmap Plotly
    # ------------------------------------------------------------------
    st.subheader("🌡️ Heatmap Payoff Table")

    fig_heatmap = px.imshow(
        df_payoff,
        labels={"x": "Kondisi Alam", "y": "Alternatif", "color": "Nilai Payoff"},
        title="Heatmap Distribusi Nilai Payoff",
        color_continuous_scale="Blues",
        text_auto=".2f",
        template="plotly_white",
        aspect="auto",
    )
    fig_heatmap.update_layout(
        title_font_size=16,
        xaxis_title="Kondisi Alam",
        yaxis_title="Alternatif Keputusan",
        coloraxis_colorbar_title="Payoff",
        margin={"t": 60, "b": 40, "l": 40, "r": 40},
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # ------------------------------------------------------------------
    # Rumus LaTeX dan deskripsi metodologi
    # ------------------------------------------------------------------
    st.subheader("📐 Notasi Matematis")

    st.latex(r"P = [p_{ij}]")
    st.markdown(
        r"""
Di mana:
- $P$ adalah **matriks payoff** berukuran $m \times n$
- $p_{ij}$ adalah nilai payoff untuk **alternatif ke-$i$** pada **kondisi alam ke-$j$**
- $i = 1, 2, \ldots, m$ adalah indeks alternatif keputusan
- $j = 1, 2, \ldots, n$ adalah indeks kondisi alam (*state of nature*)
"""
    )

    st.subheader("📖 Metodologi Payoff Table")

    with st.expander("Lihat deskripsi metodologi lengkap", expanded=False):
        st.markdown(
            """
### Definisi Konsep

**Payoff Table** (Tabel Hasil) adalah representasi matriks dari nilai hasil yang diperoleh
pengambil keputusan untuk setiap kombinasi antara **alternatif keputusan** yang dipilih
dan **kondisi alam** (*state of nature*) yang terjadi.

### Asumsi Kondisi Kepastian

Dalam analisis di bawah kondisi **kepastian** (*certainty*):
- Pengambil keputusan **mengetahui dengan pasti** kondisi alam mana yang akan terjadi.
- Oleh karena itu, keputusan optimal adalah memilih alternatif dengan nilai payoff
  **tertinggi** pada kondisi alam yang diketahui tersebut.
- Tidak ada probabilitas yang diperlukan — setiap kolom kondisi alam berdiri sendiri.

### Panduan Interpretasi Nilai Optimal per Kolom

- Setiap **kolom** merepresentasikan satu kondisi alam yang mungkin terjadi.
- Nilai **maksimum** pada setiap kolom (disorot hijau) menunjukkan alternatif terbaik
  **jika** kondisi alam tersebut yang terjadi.
- Untuk analisis lebih lanjut di bawah kondisi **risiko** atau **ketidakpastian**,
  gunakan modul **EV & EOL** atau **Kriteria Keputusan** di menu navigasi.

### Langkah Penggunaan

1. Tentukan jumlah alternatif dan kondisi alam di sidebar.
2. Beri nama setiap alternatif dan kondisi alam.
3. Isi nilai payoff pada grid input.
4. Klik **Buat Payoff Table** untuk menghasilkan tabel dan visualisasi.
5. Payoff Table yang telah dibuat akan tersedia untuk modul-modul analisis lanjutan.
"""
        )

    # ------------------------------------------------------------------
    # Ringkasan statistik payoff
    # ------------------------------------------------------------------
    st.subheader("📈 Ringkasan Statistik Payoff")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nilai Minimum", fmt_monetary(payoff.min()))
    col2.metric("Nilai Maksimum", fmt_monetary(payoff.max()))
    col3.metric("Rata-rata", fmt_monetary(payoff.mean()))
    col4.metric("Standar Deviasi", fmt_stat(payoff.std()))

    st.info(
        "✅ **Payoff Table telah tersimpan.** Data ini akan digunakan secara otomatis "
        "oleh modul **EV & EOL**, **Kriteria Keputusan**, dan **Fungsi Utilitas**."
    )

    # ------------------------------------------------------------------
    # Download payoff table
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📥 Unduh Payoff Table")
    csv_bytes = df_payoff.to_csv().encode("utf-8")
    st.download_button(
        label="📥 Unduh Payoff Table (CSV)",
        data=csv_bytes,
        file_name="payoff_table.csv",
        mime="text/csv",
    )
