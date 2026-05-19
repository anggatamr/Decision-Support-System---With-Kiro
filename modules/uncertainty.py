"""
modules/uncertainty.py
----------------------
Computation layer untuk Modul 4: Kriteria Keputusan di Bawah Ketidakpastian.

Empat kriteria yang diimplementasikan:
- Maximax   : optimistis — pilih alternatif dengan payoff maksimum tertinggi
- Maximin   : pesimistis — pilih alternatif dengan payoff minimum tertinggi
- Minimax Regret : Savage — minimasi penyesalan (regret) maksimum
- Laplace   : netral — asumsikan semua kondisi alam sama-sama mungkin

Semua fungsi di lapisan ini adalah pure functions — tidak mengimpor Streamlit
dan dapat diuji secara independen.

Fungsi compute_opportunity_loss dan get_optimal_indices di-reuse dari
modules.ev_eol untuk menghindari duplikasi logika.

UI layer (render_uncertainty_module) akan diimplementasikan pada task 8.6.
"""

import numpy as np

from modules.ev_eol import compute_opportunity_loss, get_optimal_indices


def compute_maximax(payoff: np.ndarray) -> tuple[float, list[int]]:
    """
    Hitung kriteria Maximax.

    Strategi optimistis: untuk setiap alternatif ambil nilai maksimum
    di semua kondisi alam, lalu pilih alternatif dengan nilai maksimum
    tertinggi.

    Rumus: Maximax = max_i ( max_j v_ij )

    Parameters
    ----------
    payoff : np.ndarray
        Matriks payoff dengan shape (m, n).

    Returns
    -------
    tuple[float, list[int]]
        - val  : nilai Maximax (float) — nilai terbesar dalam seluruh matriks
        - idx  : daftar indeks alternatif yang mencapai nilai tersebut
                 (menangani ties)
    """
    row_max = payoff.max(axis=1)          # max per alternatif, shape (m,)
    val = float(row_max.max())
    idx = get_optimal_indices(row_max, "max")
    return val, idx


def compute_maximin(payoff: np.ndarray) -> tuple[float, list[int]]:
    """
    Hitung kriteria Maximin.

    Strategi pesimistis: untuk setiap alternatif ambil nilai minimum
    di semua kondisi alam, lalu pilih alternatif dengan nilai minimum
    tertinggi.

    Rumus: Maximin = max_i ( min_j v_ij )

    Parameters
    ----------
    payoff : np.ndarray
        Matriks payoff dengan shape (m, n).

    Returns
    -------
    tuple[float, list[int]]
        - val  : nilai Maximin (float) — maksimum dari row-minimum
        - idx  : daftar indeks alternatif yang mencapai nilai tersebut
                 (menangani ties)
    """
    row_min = payoff.min(axis=1)          # min per alternatif, shape (m,)
    val = float(row_min.max())
    idx = get_optimal_indices(row_min, "max")
    return val, idx


def compute_minimax_regret(payoff: np.ndarray) -> tuple[float, list[int], np.ndarray]:
    """
    Hitung kriteria Minimax Regret (Savage).

    Langkah:
    1. Hitung matriks regret R_ij = max_k(v_kj) - v_ij  (reuse dari ev_eol)
    2. Untuk setiap alternatif, ambil regret maksimum di semua kondisi alam
    3. Pilih alternatif dengan regret maksimum terendah

    Rumus: Minimax Regret = min_i ( max_j R_ij )

    Parameters
    ----------
    payoff : np.ndarray
        Matriks payoff dengan shape (m, n).

    Returns
    -------
    tuple[float, list[int], np.ndarray]
        - val    : nilai Minimax Regret (float)
        - idx    : daftar indeks alternatif yang mencapai nilai tersebut
                   (menangani ties)
        - regret : matriks regret dengan shape (m, n), semua nilai >= 0
    """
    regret = compute_opportunity_loss(payoff)   # reuse dari ev_eol, shape (m, n)
    row_max_regret = regret.max(axis=1)         # max regret per alternatif, shape (m,)
    val = float(row_max_regret.min())
    idx = get_optimal_indices(row_max_regret, "min")
    return val, idx, regret


def compute_laplace(payoff: np.ndarray) -> tuple[np.ndarray, list[int]]:
    """
    Hitung kriteria Laplace (Principle of Insufficient Reason).

    Asumsikan semua kondisi alam memiliki probabilitas yang sama (1/n),
    sehingga skor Laplace setiap alternatif adalah rata-rata payoff-nya.

    Rumus: v̄_i = (1/n) * sum_j v_ij

    Parameters
    ----------
    payoff : np.ndarray
        Matriks payoff dengan shape (m, n).

    Returns
    -------
    tuple[np.ndarray, list[int]]
        - scores : vektor skor Laplace dengan shape (m,) — rata-rata baris
        - idx    : daftar indeks alternatif dengan skor tertinggi
                   (menangani ties)
    """
    scores = payoff.mean(axis=1)              # rata-rata baris, shape (m,)
    idx = get_optimal_indices(scores, "max")
    return scores, idx


# ---------------------------------------------------------------------------
# UI Layer — render_uncertainty_module()
# Task 8.6 — Requirements: 5.1–5.12
# ---------------------------------------------------------------------------


def render_uncertainty_module() -> None:
    """
    Render modul Kriteria Keputusan di Bawah Ketidakpastian secara lengkap.

    Alur:
    1. Cek prasyarat: payoff_matrix harus sudah ada di session_state
    2. Hitung keempat kriteria menggunakan fungsi komputasi
    3. Tampilkan tabel ringkasan berdampingan dengan highlight optimal
    4. Render grouped bar chart Plotly perbandingan keempat kriteria
    5. Render rumus LaTeX untuk setiap kriteria dengan fallback teks plain
    6. Render deskripsi metodologi (asumsi filosofis setiap kriteria)
    7. Simpan hasil ke session_state dan tandai modul selesai

    Requirements: 5.1–5.12
    """

    # UI-layer imports — kept inside function so the module can be imported
    # without streamlit installed (e.g. during unit/property-based tests).
    import streamlit as st
    import pandas as pd
    import plotly.graph_objects as go
    from ui.styles import COLORS
    from utils.formatters import fmt_stat

    # ------------------------------------------------------------------
    # Judul modul
    # ------------------------------------------------------------------
    st.title("❓ Uncertainty — Kriteria Keputusan")
    st.markdown(
        "Bandingkan **empat kriteria keputusan** di bawah kondisi ketidakpastian — "
        "tanpa informasi probabilitas kondisi alam. Setiap kriteria mencerminkan "
        "sikap filosofis yang berbeda terhadap ketidakpastian."
    )

    # ------------------------------------------------------------------
    # Cek prasyarat: payoff_matrix harus sudah ada (Req 5.7)
    # ------------------------------------------------------------------
    payoff_matrix: np.ndarray | None = st.session_state.get("payoff_matrix")
    if payoff_matrix is None:
        st.warning(
            "⚠️ **Payoff Table belum didefinisikan.**\n\n"
            "Silakan buka modul **📋 Certainty — Payoff Table** terlebih dahulu "
            "untuk membuat matriks payoff sebelum menjalankan analisis kriteria "
            "ketidakpastian."
        )
        st.button("Hitung Keempat Kriteria", disabled=True)
        return

    alt_names: list[str] = st.session_state.get("alt_names", [])
    state_names: list[str] = st.session_state.get("state_names", [])
    m = len(alt_names)   # jumlah alternatif
    n = len(state_names) # jumlah kondisi alam

    # Validasi dimensi minimal (Req 5.7)
    if m < 2 or n < 2:
        st.warning(
            "⚠️ **Payoff Table tidak lengkap.**\n\n"
            "Dibutuhkan minimal **2 alternatif** dan **2 kondisi alam** untuk "
            "menjalankan analisis kriteria ketidakpastian."
        )
        st.button("Hitung Keempat Kriteria", disabled=True)
        return

    # ------------------------------------------------------------------
    # Komputasi keempat kriteria
    # ------------------------------------------------------------------
    maximax_val, maximax_idx = compute_maximax(payoff_matrix)
    maximin_val, maximin_idx = compute_maximin(payoff_matrix)
    minimax_regret_val, minimax_regret_idx, regret_matrix = compute_minimax_regret(payoff_matrix)
    laplace_scores, laplace_idx = compute_laplace(payoff_matrix)

    # ------------------------------------------------------------------
    # Simpan ke session_state (Req 5.10)
    # ------------------------------------------------------------------
    st.session_state["uncertainty_results"] = {
        "maximax_val": maximax_val,
        "maximax_idx": maximax_idx,
        "maximin_val": maximin_val,
        "maximin_idx": maximin_idx,
        "minimax_regret_val": minimax_regret_val,
        "minimax_regret_idx": minimax_regret_idx,
        "laplace_scores": laplace_scores,
        "laplace_idx": laplace_idx,
        "regret_matrix": regret_matrix,
    }
    if "completed_modules" not in st.session_state:
        st.session_state["completed_modules"] = set()
    st.session_state["completed_modules"].add("uncertainty")

    # ------------------------------------------------------------------
    # Helper: nama alternatif optimal (handle ties)
    # ------------------------------------------------------------------
    def _fmt_optimal(idx_list: list[int]) -> str:
        names = [alt_names[i] for i in idx_list]
        if len(names) == 1:
            return names[0]
        return ", ".join(names) + " *(seri)*"

    # ------------------------------------------------------------------
    # Tabel ringkasan keempat kriteria berdampingan (Req 5.10)
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📊 Ringkasan Keempat Kriteria Ketidakpastian")

    # Buat DataFrame ringkasan
    summary_data = {
        "Kriteria": ["Maximax", "Maximin", "Minimax Regret", "Laplace"],
        "Nilai Optimal": [
            maximax_val,
            maximin_val,
            minimax_regret_val,
            float(laplace_scores[laplace_idx[0]]),
        ],
        "Alternatif Optimal": [
            _fmt_optimal(maximax_idx),
            _fmt_optimal(maximin_idx),
            _fmt_optimal(minimax_regret_idx),
            _fmt_optimal(laplace_idx),
        ],
        "Pendekatan": ["Optimistis", "Pesimistis", "Penyesalan Minimum", "Netral"],
    }
    summary_df = pd.DataFrame(summary_data)

    st.dataframe(
        summary_df.style.format({"Nilai Optimal": "{:.4f}"}),
        use_container_width=True,
        hide_index=True,
    )

    # ------------------------------------------------------------------
    # Tabel detail per kriteria berdampingan (Req 5.10 — highlight optimal)
    # ------------------------------------------------------------------
    st.markdown("#### Detail Nilai per Alternatif")

    col1, col2 = st.columns(2)

    # --- Maximax ---
    with col1:
        st.markdown("**Maximax** *(Optimistis)*")
        row_max_vals = payoff_matrix.max(axis=1)
        maximax_df = pd.DataFrame({
            "Alternatif": alt_names,
            "Maks Payoff": row_max_vals,
        })

        def _hl_maximax(row):
            idx = maximax_df.index[maximax_df["Alternatif"] == row["Alternatif"]].tolist()
            if idx and idx[0] in maximax_idx:
                return [
                    f"background-color: {COLORS['success']}22; font-weight: bold; color: {COLORS['success']}"
                ] * len(row)
            return [""] * len(row)

        st.dataframe(
            maximax_df.style.apply(_hl_maximax, axis=1).format({"Maks Payoff": "{:.4f}"}),
            use_container_width=True,
            hide_index=True,
        )
        best_names = [alt_names[i] for i in maximax_idx]
        st.success(
            f"✅ **Optimal:** {', '.join(best_names)} — nilai = {fmt_stat(maximax_val)}"
        )

    # --- Maximin ---
    with col2:
        st.markdown("**Maximin** *(Pesimistis)*")
        row_min_vals = payoff_matrix.min(axis=1)
        maximin_df = pd.DataFrame({
            "Alternatif": alt_names,
            "Min Payoff": row_min_vals,
        })

        def _hl_maximin(row):
            idx = maximin_df.index[maximin_df["Alternatif"] == row["Alternatif"]].tolist()
            if idx and idx[0] in maximin_idx:
                return [
                    f"background-color: {COLORS['success']}22; font-weight: bold; color: {COLORS['success']}"
                ] * len(row)
            return [""] * len(row)

        st.dataframe(
            maximin_df.style.apply(_hl_maximin, axis=1).format({"Min Payoff": "{:.4f}"}),
            use_container_width=True,
            hide_index=True,
        )
        best_names = [alt_names[i] for i in maximin_idx]
        st.success(
            f"✅ **Optimal:** {', '.join(best_names)} — nilai = {fmt_stat(maximin_val)}"
        )

    col3, col4 = st.columns(2)

    # --- Minimax Regret ---
    with col3:
        st.markdown("**Minimax Regret** *(Penyesalan Minimum)*")
        row_max_regret = regret_matrix.max(axis=1)
        minimax_df = pd.DataFrame({
            "Alternatif": alt_names,
            "Maks Regret": row_max_regret,
        })

        def _hl_minimax(row):
            idx = minimax_df.index[minimax_df["Alternatif"] == row["Alternatif"]].tolist()
            if idx and idx[0] in minimax_regret_idx:
                return [
                    f"background-color: {COLORS['success']}22; font-weight: bold; color: {COLORS['success']}"
                ] * len(row)
            return [""] * len(row)

        st.dataframe(
            minimax_df.style.apply(_hl_minimax, axis=1).format({"Maks Regret": "{:.4f}"}),
            use_container_width=True,
            hide_index=True,
        )
        best_names = [alt_names[i] for i in minimax_regret_idx]
        st.success(
            f"✅ **Optimal:** {', '.join(best_names)} — nilai = {fmt_stat(minimax_regret_val)}"
        )

    # --- Laplace ---
    with col4:
        st.markdown("**Laplace** *(Netral)*")
        laplace_df = pd.DataFrame({
            "Alternatif": alt_names,
            "Rata-rata Payoff": laplace_scores,
        })

        def _hl_laplace(row):
            idx = laplace_df.index[laplace_df["Alternatif"] == row["Alternatif"]].tolist()
            if idx and idx[0] in laplace_idx:
                return [
                    f"background-color: {COLORS['success']}22; font-weight: bold; color: {COLORS['success']}"
                ] * len(row)
            return [""] * len(row)

        st.dataframe(
            laplace_df.style.apply(_hl_laplace, axis=1).format({"Rata-rata Payoff": "{:.4f}"}),
            use_container_width=True,
            hide_index=True,
        )
        best_names = [alt_names[i] for i in laplace_idx]
        st.success(
            f"✅ **Optimal:** {', '.join(best_names)} — nilai = {fmt_stat(float(laplace_scores[laplace_idx[0]]))}"
        )

    # ------------------------------------------------------------------
    # Tabel Regret Matrix — expandable
    # ------------------------------------------------------------------
    with st.expander("📋 Tabel Regret (Minimax Regret)", expanded=False):
        regret_df = pd.DataFrame(
            regret_matrix,
            index=alt_names,
            columns=state_names,
        )
        st.dataframe(regret_df.style.format("{:.4f}"), use_container_width=True)
        st.caption(
            "R_ij = max_k(v_kj) − v_ij — nilai nol menunjukkan alternatif terbaik "
            "untuk kondisi alam tersebut."
        )

    # ------------------------------------------------------------------
    # Grouped bar chart Plotly perbandingan keempat kriteria (Req 5.11)
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📈 Perbandingan Keempat Kriteria per Alternatif")

    # Warna berbeda untuk setiap kriteria
    CRITERION_COLORS = [
        COLORS["accent"],    # Maximax — biru
        "#E74C3C",           # Maximin — merah
        COLORS["warning"],   # Minimax Regret — kuning
        COLORS["success"],   # Laplace — hijau
    ]

    fig = go.Figure()

    # Maximax — row max per alternatif
    fig.add_trace(go.Bar(
        name="Maximax (Maks Payoff)",
        x=alt_names,
        y=payoff_matrix.max(axis=1).tolist(),
        marker_color=CRITERION_COLORS[0],
        text=[f"{v:.4f}" for v in payoff_matrix.max(axis=1)],
        textposition="outside",
    ))

    # Maximin — row min per alternatif
    fig.add_trace(go.Bar(
        name="Maximin (Min Payoff)",
        x=alt_names,
        y=payoff_matrix.min(axis=1).tolist(),
        marker_color=CRITERION_COLORS[1],
        text=[f"{v:.4f}" for v in payoff_matrix.min(axis=1)],
        textposition="outside",
    ))

    # Minimax Regret — max regret per alternatif
    fig.add_trace(go.Bar(
        name="Minimax Regret (Maks Regret)",
        x=alt_names,
        y=regret_matrix.max(axis=1).tolist(),
        marker_color=CRITERION_COLORS[2],
        text=[f"{v:.4f}" for v in regret_matrix.max(axis=1)],
        textposition="outside",
    ))

    # Laplace — rata-rata payoff per alternatif
    fig.add_trace(go.Bar(
        name="Laplace (Rata-rata Payoff)",
        x=alt_names,
        y=laplace_scores.tolist(),
        marker_color=CRITERION_COLORS[3],
        text=[f"{v:.4f}" for v in laplace_scores],
        textposition="outside",
    ))

    fig.update_layout(
        title="Perbandingan Nilai Keempat Kriteria Ketidakpastian per Alternatif",
        xaxis_title="Alternatif Keputusan",
        yaxis_title="Nilai Kriteria",
        barmode="group",
        template="plotly_white",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        title_font_size=16,
    )

    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------------------
    # Rumus LaTeX untuk setiap kriteria (Req 5.2, 5.4, 5.6, 5.9)
    # dengan fallback teks plain jika rendering gagal
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📐 Rumus Matematis")

    with st.expander("Lihat Rumus Keempat Kriteria", expanded=True):
        col_f1, col_f2 = st.columns(2)

        with col_f1:
            # Maximax (Req 5.2)
            st.markdown("**Maximax**")
            try:
                st.latex(r"\text{Maximax} = \max_i \left( \max_j \, v_{ij} \right)")
            except Exception:
                st.code("Maximax = max_i ( max_j v_ij )")
            st.caption(
                "Pilih alternatif dengan nilai payoff maksimum tertinggi di antara "
                "semua kondisi alam."
            )

            st.markdown("---")

            # Maximin (Req 5.4)
            st.markdown("**Maximin**")
            try:
                st.latex(r"\text{Maximin} = \max_i \left( \min_j \, v_{ij} \right)")
            except Exception:
                st.code("Maximin = max_i ( min_j v_ij )")
            st.caption(
                "Pilih alternatif dengan nilai payoff minimum tertinggi — "
                "strategi terbaik dalam skenario terburuk."
            )

        with col_f2:
            # Minimax Regret (Req 5.6)
            st.markdown("**Minimax Regret**")
            try:
                st.latex(r"R_{ij} = \max_k(v_{kj}) - v_{ij}")
                st.latex(r"\text{Minimax Regret} = \min_i \left( \max_j \, R_{ij} \right)")
            except Exception:
                st.code("R_ij = max_k(v_kj) - v_ij")
                st.code("Minimax Regret = min_i ( max_j R_ij )")
            st.caption(
                "Hitung matriks regret, lalu pilih alternatif dengan regret "
                "maksimum terendah."
            )

            st.markdown("---")

            # Laplace (Req 5.9)
            st.markdown("**Laplace**")
            try:
                st.latex(r"\bar{v}_i = \frac{1}{n} \sum_{j=1}^{n} v_{ij}")
            except Exception:
                st.code("v_bar_i = (1/n) * sum_j v_ij")
            st.caption(
                "Asumsikan semua kondisi alam sama-sama mungkin (probabilitas 1/n), "
                "lalu pilih alternatif dengan rata-rata payoff tertinggi."
            )

    # ------------------------------------------------------------------
    # Download hasil kriteria ketidakpastian
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📥 Unduh Hasil")
    import pandas as _pd_dl
    dl_df = _pd_dl.DataFrame({
        "Alternatif": alt_names,
        "Maximax (Maks Payoff)": payoff_matrix.max(axis=1).tolist(),
        "Maximin (Min Payoff)": payoff_matrix.min(axis=1).tolist(),
        "Minimax Regret (Maks Regret)": regret_matrix.max(axis=1).tolist(),
        "Laplace (Rata-rata)": laplace_scores.tolist(),
    })
    csv_bytes = dl_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Unduh Hasil Kriteria Ketidakpastian (CSV)",
        data=csv_bytes,
        file_name="uncertainty_results.csv",
        mime="text/csv",
    )

    # ------------------------------------------------------------------
    # Deskripsi metodologi (Req 5.12)
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📚 Metodologi Kriteria Ketidakpastian")

    with st.expander("Baca Deskripsi Metodologi", expanded=False):
        st.markdown(
            """
            ### Analisis Keputusan di Bawah Kondisi Ketidakpastian

            **Kondisi Ketidakpastian** terjadi ketika pengambil keputusan tidak memiliki
            informasi tentang probabilitas masing-masing kondisi alam yang mungkin terjadi.
            Berbeda dengan kondisi risiko, di sini kita tidak dapat menghitung nilai harapan
            (expected value). Sebagai gantinya, empat kriteria berikut menawarkan pendekatan
            berbeda berdasarkan sikap filosofis pengambil keputusan.

            ---

            ### 1. Maximax — Kriteria Optimistis

            **Asumsi filosofis:** Pengambil keputusan bersikap *sangat optimistis* — ia
            percaya bahwa kondisi alam terbaik akan selalu terjadi.

            **Langkah perhitungan:**
            1. Untuk setiap alternatif $i$, identifikasi nilai payoff maksimum:
               $M_i = \\max_j v_{ij}$
            2. Pilih alternatif dengan $M_i$ tertinggi: $\\text{Maximax} = \\max_i M_i$

            **Interpretasi:** Cocok untuk pengambil keputusan yang berani mengambil risiko
            demi potensi keuntungan tertinggi. Tidak mempertimbangkan kemungkinan skenario
            buruk.

            ---

            ### 2. Maximin — Kriteria Pesimistis (Wald)

            **Asumsi filosofis:** Pengambil keputusan bersikap *sangat pesimistis* — ia
            selalu mengantisipasi kondisi alam terburuk.

            **Langkah perhitungan:**
            1. Untuk setiap alternatif $i$, identifikasi nilai payoff minimum:
               $m_i = \\min_j v_{ij}$
            2. Pilih alternatif dengan $m_i$ tertinggi: $\\text{Maximin} = \\max_i m_i$

            **Interpretasi:** Strategi *"terbaik dalam skenario terburuk"*. Cocok untuk
            pengambil keputusan yang menghindari risiko dan mengutamakan keamanan.

            ---

            ### 3. Minimax Regret — Kriteria Penyesalan (Savage)

            **Asumsi filosofis:** Pengambil keputusan ingin *meminimalkan penyesalan* —
            yaitu selisih antara hasil yang diperoleh dan hasil terbaik yang mungkin
            diperoleh jika kondisi alam diketahui sebelumnya.

            **Langkah perhitungan:**
            1. Hitung matriks regret: $R_{ij} = \\max_k(v_{kj}) - v_{ij}$
            2. Untuk setiap alternatif $i$, ambil regret maksimum: $r_i = \\max_j R_{ij}$
            3. Pilih alternatif dengan $r_i$ terendah: $\\text{Minimax Regret} = \\min_i r_i$

            **Interpretasi:** Menyeimbangkan antara optimisme dan pesimisme. Pengambil
            keputusan tidak ingin "menyesal" terlalu besar atas pilihan yang dibuat.

            ---

            ### 4. Laplace — Kriteria Netral (Prinsip Ketidakcukupan Alasan)

            **Asumsi filosofis:** Karena tidak ada informasi tentang probabilitas kondisi
            alam, semua kondisi alam dianggap *sama-sama mungkin* (probabilitas 1/n).

            **Langkah perhitungan:**
            1. Untuk setiap alternatif $i$, hitung rata-rata payoff:
               $\\bar{v}_i = \\frac{1}{n} \\sum_{j=1}^{n} v_{ij}$
            2. Pilih alternatif dengan $\\bar{v}_i$ tertinggi

            **Interpretasi:** Pendekatan paling "adil" secara statistik ketika tidak ada
            alasan untuk memprioritaskan satu kondisi alam di atas yang lain. Setara
            dengan menghitung EV dengan probabilitas seragam.

            ---

            ### Perbandingan dan Rekomendasi Penggunaan

            | Kriteria | Sikap Risiko | Cocok Untuk |
            |---|---|---|
            | Maximax | Sangat optimistis | Pengambil risiko, potensi keuntungan besar |
            | Maximin | Sangat pesimistis | Penghindar risiko, keamanan utama |
            | Minimax Regret | Moderat | Meminimalkan penyesalan pasca-keputusan |
            | Laplace | Netral | Tidak ada preferensi, semua kondisi setara |

            **Catatan:** Tidak ada kriteria yang "terbaik" secara universal. Pilihan
            kriteria bergantung pada konteks keputusan, toleransi risiko, dan preferensi
            subjektif pengambil keputusan.
            """
        )
