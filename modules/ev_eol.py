"""
modules/ev_eol.py
-----------------
Computation layer untuk Modul 3: EV (Expected Value), EOL (Expected Opportunity Loss),
dan EVPI (Expected Value of Perfect Information).

Semua fungsi di lapisan ini adalah pure functions — tidak mengimpor Streamlit
dan dapat diuji secara independen.

UI layer (render_ev_eol_module) akan diimplementasikan pada task 6.7.
"""

import numpy as np


def compute_ev(payoff: np.ndarray, probs: np.ndarray) -> np.ndarray:
    """
    Hitung Expected Value untuk setiap alternatif.

    EV_i = sum_j(p_j * v_ij) = payoff @ probs

    Parameters
    ----------
    payoff : np.ndarray
        Matriks payoff dengan shape (m, n), di mana m = jumlah alternatif
        dan n = jumlah kondisi alam.
    probs : np.ndarray
        Vektor probabilitas dengan shape (n,), jumlah harus ≈ 1.0.

    Returns
    -------
    np.ndarray
        Vektor EV dengan shape (m,), satu nilai per alternatif.
    """
    return payoff @ probs


def compute_opportunity_loss(payoff: np.ndarray) -> np.ndarray:
    """
    Hitung matriks Opportunity Loss (OL) dari matriks payoff.

    OL_ij = max_k(v_kj) - v_ij

    Setiap sel OL merepresentasikan "penyesalan" jika alternatif i dipilih
    saat kondisi alam j terjadi. Nilai selalu >= 0.

    Parameters
    ----------
    payoff : np.ndarray
        Matriks payoff dengan shape (m, n).

    Returns
    -------
    np.ndarray
        Matriks OL dengan shape (m, n), semua nilai >= 0.
        Setiap kolom j mengandung minimal satu nol (alternatif terbaik
        untuk kondisi j memiliki OL = 0).
    """
    col_max = payoff.max(axis=0)  # shape (n,)
    return col_max - payoff       # shape (m, n), broadcasting


def compute_eol(ol_matrix: np.ndarray, probs: np.ndarray) -> np.ndarray:
    """
    Hitung Expected Opportunity Loss untuk setiap alternatif.

    EOL_i = sum_j(p_j * OL_ij) = ol_matrix @ probs

    Parameters
    ----------
    ol_matrix : np.ndarray
        Matriks opportunity loss dengan shape (m, n).
    probs : np.ndarray
        Vektor probabilitas dengan shape (n,), jumlah harus ≈ 1.0.

    Returns
    -------
    np.ndarray
        Vektor EOL dengan shape (m,), satu nilai per alternatif.
    """
    return ol_matrix @ probs


def compute_evpi(payoff: np.ndarray, probs: np.ndarray) -> float:
    """
    Hitung Expected Value of Perfect Information (EVPI).

    EVPI = EVwPI - EV*

    di mana:
    - EVwPI = sum_j(p_j * max_i(v_ij))  — EV dengan informasi sempurna
    - EV*   = max_i(EV_i)               — EV terbaik tanpa informasi sempurna

    EVPI selalu >= 0 karena informasi sempurna tidak pernah memperburuk keputusan.

    Parameters
    ----------
    payoff : np.ndarray
        Matriks payoff dengan shape (m, n).
    probs : np.ndarray
        Vektor probabilitas dengan shape (n,), jumlah harus ≈ 1.0.

    Returns
    -------
    float
        Nilai EVPI, selalu >= 0.
    """
    ev_with_pi = probs @ payoff.max(axis=0)   # EVwPI: dot product probs dan col-max
    ev_star = compute_ev(payoff, probs).max()  # EV terbaik
    return float(ev_with_pi - ev_star)


def get_optimal_indices(values: np.ndarray, mode: str = "max") -> list[int]:
    """
    Kembalikan semua indeks yang tied untuk nilai maksimum atau minimum.

    Menangani ties dengan mengembalikan SEMUA indeks yang memiliki nilai
    optimal, bukan hanya indeks pertama.

    Parameters
    ----------
    values : np.ndarray
        Vektor nilai 1-D.
    mode : str
        "max" untuk mencari indeks dengan nilai tertinggi,
        "min" untuk mencari indeks dengan nilai terendah.

    Returns
    -------
    list[int]
        Daftar semua indeks yang tied untuk nilai optimal.
    """
    target = values.max() if mode == "max" else values.min()
    return [int(i) for i in np.where(values == target)[0]]


# ---------------------------------------------------------------------------
# UI Layer — render_ev_eol_module()
# Task 6.7 — Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11
# ---------------------------------------------------------------------------


def render_ev_eol_module() -> None:
    """
    Render modul EV & EOL secara lengkap.

    Alur:
    1. Cek prasyarat: payoff_matrix harus sudah ada di session_state
    2. Sidebar — input probabilitas kondisi alam (satu per state)
    3. Validasi probabilitas via validate_probabilities()
    4. Hitung EV, OL, EOL, EVPI menggunakan fungsi komputasi
    5. Tampilkan tabel EV dan EOL berdampingan dengan highlight optimal
    6. Render bar chart Plotly perbandingan EV dan EOL
    7. Render rumus LaTeX EV, EOL, EVPI dan deskripsi metodologi
    8. Simpan hasil ke session_state dan tandai modul selesai

    Requirements: 4.1–4.11
    """
    # UI-layer imports — kept inside function so the module can be imported
    # without streamlit installed (e.g. during unit/property-based testing).
    import streamlit as st
    import pandas as pd
    import plotly.graph_objects as go
    from utils.validators import validate_probabilities
    from utils.formatters import fmt_monetary, fmt_stat
    from ui.styles import COLORS

    # ------------------------------------------------------------------
    # Judul modul
    # ------------------------------------------------------------------
    st.title("🎲 Risk — Expected Value & Expected Opportunity Loss")
    st.markdown(
        "Hitung **Expected Value (EV)**, **Expected Opportunity Loss (EOL)**, "
        "dan **EVPI** untuk setiap alternatif keputusan berdasarkan probabilitas "
        "kondisi alam yang Anda masukkan."
    )

    # ------------------------------------------------------------------
    # Cek prasyarat: payoff_matrix harus sudah ada (Req 4.2)
    # ------------------------------------------------------------------
    payoff_matrix: np.ndarray | None = st.session_state.get("payoff_matrix")
    if payoff_matrix is None:
        st.warning(
            "⚠️ **Payoff Table belum didefinisikan.**\n\n"
            "Silakan buka modul **📋 Certainty — Payoff Table** terlebih dahulu "
            "untuk membuat matriks payoff sebelum menjalankan analisis EV & EOL."
        )
        return

    alt_names: list[str] = st.session_state.get("alt_names", [])
    state_names: list[str] = st.session_state.get("state_names", [])
    m = len(alt_names)   # jumlah alternatif
    n = len(state_names) # jumlah kondisi alam

    # ------------------------------------------------------------------
    # Sidebar — input probabilitas kondisi alam (Req 4.1)
    # ------------------------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎲 Probabilitas Kondisi Alam")
    st.sidebar.markdown(
        "Masukkan probabilitas untuk setiap kondisi alam. "
        "Total harus sama dengan **1.0** (toleransi ±0.001)."
    )

    prob_inputs: list[float] = []
    for j, state in enumerate(state_names):
        # Ambil nilai sebelumnya dari session_state jika ada
        prev_probs = st.session_state.get("probabilities")
        default_val = float(prev_probs[j]) if prev_probs is not None and len(prev_probs) == n else round(1.0 / n, 4)

        p = st.sidebar.number_input(
            label=f"P({state})",
            min_value=0.0,
            max_value=1.0,
            value=default_val,
            step=0.01,
            format="%.4f",
            key=f"ev_eol_prob_{j}",
        )
        prob_inputs.append(p)

    # Tampilkan total probabilitas di sidebar
    total_prob = sum(prob_inputs)
    if abs(total_prob - 1.0) <= 0.001:
        st.sidebar.success(f"✅ Total probabilitas: **{total_prob:.4f}**")
    else:
        st.sidebar.error(f"❌ Total probabilitas: **{total_prob:.4f}** (harus = 1.0)")

    # ------------------------------------------------------------------
    # Validasi probabilitas (Req 4.1)
    # ------------------------------------------------------------------
    is_valid, error_msg = validate_probabilities(prob_inputs)
    if not is_valid:
        st.error(f"❌ **Probabilitas tidak valid:** {error_msg}")
        st.info(
            "💡 Pastikan setiap nilai probabilitas berada dalam rentang [0, 1] "
            "dan jumlah total probabilitas sama dengan 1.0 (toleransi ±0.001)."
        )
        return

    # Konversi ke numpy array
    probs = np.array(prob_inputs, dtype=np.float64)

    # ------------------------------------------------------------------
    # Komputasi EV, OL, EOL, EVPI
    # ------------------------------------------------------------------
    ev_values = compute_ev(payoff_matrix, probs)                    # shape (m,)
    ol_matrix = compute_opportunity_loss(payoff_matrix)             # shape (m, n)
    eol_values = compute_eol(ol_matrix, probs)                      # shape (m,)
    evpi_value = compute_evpi(payoff_matrix, probs)                 # float

    best_ev_idx = get_optimal_indices(ev_values, "max")             # list[int]
    best_eol_idx = get_optimal_indices(eol_values, "min")           # list[int]

    # ------------------------------------------------------------------
    # Simpan ke session_state
    # ------------------------------------------------------------------
    st.session_state["probabilities"] = probs
    st.session_state["ev_results"] = {
        "ev": ev_values,
        "eol": eol_values,
        "ol_matrix": ol_matrix,
        "evpi": evpi_value,
        "best_ev_idx": best_ev_idx,
        "best_eol_idx": best_eol_idx,
    }
    st.session_state["eol_results"] = {
        "eol": eol_values,
        "best_eol_idx": best_eol_idx,
    }
    if "completed_modules" not in st.session_state:
        st.session_state["completed_modules"] = set()
    st.session_state["completed_modules"].add("ev_eol")

    # ------------------------------------------------------------------
    # Tabel EV dan EOL berdampingan (Req 4.7, 4.8)
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📊 Hasil Perhitungan EV dan EOL")

    col_ev, col_eol = st.columns(2)

    # --- Tabel EV ---
    with col_ev:
        st.markdown("#### Expected Value (EV)")

        ev_df = pd.DataFrame({
            "Alternatif": alt_names,
            "EV": ev_values,
        })

        # Highlight baris optimal (max EV) — handle ties
        def _highlight_ev_row(row):
            idx = ev_df.index[ev_df["Alternatif"] == row["Alternatif"]].tolist()
            if idx and idx[0] in best_ev_idx:
                return [f"background-color: {COLORS['success']}22; font-weight: bold; color: {COLORS['success']}"] * len(row)
            return [""] * len(row)

        ev_styled = ev_df.style.apply(_highlight_ev_row, axis=1).format({"EV": "{:.4f}"})
        st.dataframe(ev_styled, use_container_width=True, hide_index=True)

        # Tampilkan alternatif optimal
        best_ev_names = [alt_names[i] for i in best_ev_idx]
        if len(best_ev_names) == 1:
            st.success(f"✅ **Alternatif optimal (EV tertinggi):** {best_ev_names[0]} — EV = {fmt_monetary(ev_values[best_ev_idx[0]])}")
        else:
            st.success(f"✅ **Alternatif optimal (EV tertinggi — seri):** {', '.join(best_ev_names)} — EV = {fmt_monetary(ev_values[best_ev_idx[0]])}")

    # --- Tabel EOL ---
    with col_eol:
        st.markdown("#### Expected Opportunity Loss (EOL)")

        eol_df = pd.DataFrame({
            "Alternatif": alt_names,
            "EOL": eol_values,
        })

        def _highlight_eol_row(row):
            idx = eol_df.index[eol_df["Alternatif"] == row["Alternatif"]].tolist()
            if idx and idx[0] in best_eol_idx:
                return [f"background-color: {COLORS['success']}22; font-weight: bold; color: {COLORS['success']}"] * len(row)
            return [""] * len(row)

        eol_styled = eol_df.style.apply(_highlight_eol_row, axis=1).format({"EOL": "{:.4f}"})
        st.dataframe(eol_styled, use_container_width=True, hide_index=True)

        # Tampilkan alternatif optimal
        best_eol_names = [alt_names[i] for i in best_eol_idx]
        if len(best_eol_names) == 1:
            st.success(f"✅ **Alternatif optimal (EOL terendah):** {best_eol_names[0]} — EOL = {fmt_monetary(eol_values[best_eol_idx[0]])}")
        else:
            st.success(f"✅ **Alternatif optimal (EOL terendah — seri):** {', '.join(best_eol_names)} — EOL = {fmt_monetary(eol_values[best_eol_idx[0]])}")

    # ------------------------------------------------------------------
    # Tabel Opportunity Loss (OL) — expandable
    # ------------------------------------------------------------------
    with st.expander("📋 Tabel Opportunity Loss (OL)", expanded=False):
        ol_df = pd.DataFrame(
            ol_matrix,
            index=alt_names,
            columns=state_names,
        )
        st.dataframe(ol_df.style.format("{:.4f}"), use_container_width=True)
        st.caption(
            "OL_ij = max_k(v_kj) − v_ij — nilai nol menunjukkan alternatif terbaik "
            "untuk kondisi alam tersebut."
        )

    # ------------------------------------------------------------------
    # Bar chart Plotly perbandingan EV dan EOL (Req 4.9)
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📈 Perbandingan EV dan EOL Antar Alternatif")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Expected Value (EV)",
        x=alt_names,
        y=ev_values.tolist(),
        marker_color=COLORS["accent"],
        text=[f"{v:.4f}" for v in ev_values],
        textposition="outside",
    ))

    fig.add_trace(go.Bar(
        name="Expected Opportunity Loss (EOL)",
        x=alt_names,
        y=eol_values.tolist(),
        marker_color=COLORS["warning"],
        text=[f"{v:.4f}" for v in eol_values],
        textposition="outside",
    ))

    fig.update_layout(
        title="Perbandingan EV dan EOL per Alternatif Keputusan",
        xaxis_title="Alternatif Keputusan",
        yaxis_title="Nilai",
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
    # EVPI — nilai dan interpretasi (Req 4.10)
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("💡 EVPI — Expected Value of Perfect Information")

    col_evpi, col_interp = st.columns([1, 2])

    with col_evpi:
        st.metric(
            label="Nilai EVPI",
            value=fmt_monetary(evpi_value),
            help="EVPI = EVwPI − EV* ≥ 0",
        )

    with col_interp:
        ev_star = float(ev_values.max())
        ev_wpi = evpi_value + ev_star
        st.markdown(
            f"""
            **Interpretasi EVPI:**
            - **EVwPI** (EV dengan informasi sempurna) = **{fmt_monetary(ev_wpi)}**
            - **EV\\*** (EV terbaik tanpa informasi sempurna) = **{fmt_monetary(ev_star)}**
            - **EVPI** = EVwPI − EV\\* = **{fmt_monetary(evpi_value)}**

            EVPI merepresentasikan **nilai maksimum** yang layak dibayarkan untuk
            mendapatkan informasi sempurna tentang kondisi alam yang akan terjadi.
            Jika biaya informasi lebih rendah dari EVPI, maka informasi tersebut
            layak untuk diperoleh.
            """
        )

    if evpi_value == 0.0:
        st.info(
            "ℹ️ EVPI = 0 berarti informasi sempurna tidak memberikan nilai tambah — "
            "alternatif terbaik sudah optimal di semua kondisi alam."
        )

    # ------------------------------------------------------------------
    # Rumus LaTeX (Req 4.3, 4.6, 4.10)
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📐 Rumus Matematis")

    with st.expander("Lihat Rumus EV, EOL, dan EVPI", expanded=True):
        col_f1, col_f2 = st.columns(2)

        with col_f1:
            st.markdown("**Expected Value (EV)**")
            st.latex(r"EV_i = \sum_{j=1}^{n} p_j \cdot v_{ij}")
            st.caption(
                "di mana $p_j$ = probabilitas kondisi alam $j$, "
                "$v_{ij}$ = nilai payoff alternatif $i$ pada kondisi $j$."
            )

            st.markdown("**Opportunity Loss (OL)**")
            st.latex(r"OL_{ij} = \max_k(v_{kj}) - v_{ij}")
            st.caption(
                "Nilai penyesalan jika alternatif $i$ dipilih saat kondisi $j$ terjadi. "
                "Selalu ≥ 0."
            )

        with col_f2:
            st.markdown("**Expected Opportunity Loss (EOL)**")
            st.latex(r"EOL_i = \sum_{j=1}^{n} p_j \cdot OL_{ij}")
            st.caption(
                "Nilai harapan kerugian peluang untuk alternatif $i$. "
                "Alternatif optimal memiliki EOL terendah."
            )

            st.markdown("**Expected Value of Perfect Information (EVPI)**")
            st.latex(r"EVPI = EVwPI - EV^*")
            st.latex(r"EVwPI = \sum_{j=1}^{n} p_j \cdot \max_i(v_{ij})")
            st.caption(
                "$EV^*$ = nilai EV tertinggi tanpa informasi sempurna. "
                "EVPI selalu ≥ 0."
            )

    # ------------------------------------------------------------------
    # Deskripsi metodologi (Req 4.11)
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📚 Metodologi EV & EOL")

    with st.expander("Baca Deskripsi Metodologi", expanded=False):
        st.markdown(
            """
            ### Analisis Keputusan di Bawah Kondisi Risiko

            **Kondisi Risiko** terjadi ketika pengambil keputusan mengetahui probabilitas
            masing-masing kondisi alam yang mungkin terjadi. Berbeda dengan kondisi
            ketidakpastian (di mana probabilitas tidak diketahui), analisis di bawah
            risiko memanfaatkan informasi probabilitas untuk menghitung nilai harapan.

            ---

            ### Expected Value (EV)

            **Definisi:** EV adalah rata-rata tertimbang dari semua nilai payoff suatu
            alternatif, dengan bobot berupa probabilitas kondisi alam.

            **Asumsi:** Pengambil keputusan bersikap *risk neutral* — keputusan didasarkan
            semata-mata pada nilai harapan moneter tanpa mempertimbangkan preferensi risiko.

            **Langkah perhitungan:**
            1. Tentukan probabilitas $p_j$ untuk setiap kondisi alam $j$
            2. Untuk setiap alternatif $i$, hitung $EV_i = \\sum_j p_j \\cdot v_{ij}$
            3. Pilih alternatif dengan **EV tertinggi** sebagai keputusan optimal

            **Interpretasi:** Alternatif dengan EV tertinggi memberikan hasil rata-rata
            terbaik jika keputusan yang sama diulang berkali-kali dalam jangka panjang.

            ---

            ### Expected Opportunity Loss (EOL)

            **Definisi:** EOL mengukur rata-rata "penyesalan" yang diharapkan jika suatu
            alternatif dipilih. Penyesalan (opportunity loss) terjadi karena tidak memilih
            alternatif terbaik untuk kondisi alam yang terjadi.

            **Langkah perhitungan:**
            1. Hitung matriks Opportunity Loss: $OL_{ij} = \\max_k(v_{kj}) - v_{ij}$
            2. Untuk setiap alternatif $i$, hitung $EOL_i = \\sum_j p_j \\cdot OL_{ij}$
            3. Pilih alternatif dengan **EOL terendah** sebagai keputusan optimal

            **Hubungan EV dan EOL:** Alternatif dengan EV tertinggi selalu memiliki EOL
            terendah — keduanya menghasilkan rekomendasi yang konsisten.

            ---

            ### EVPI — Expected Value of Perfect Information

            **Definisi:** EVPI adalah nilai maksimum yang layak dibayarkan untuk mendapatkan
            informasi sempurna tentang kondisi alam yang akan terjadi.

            **Interpretasi praktis:**
            - Jika biaya riset/informasi < EVPI → informasi layak diperoleh
            - Jika biaya riset/informasi ≥ EVPI → tidak perlu mencari informasi tambahan
            - EVPI = 0 → alternatif terbaik sudah dominan di semua kondisi alam

            **Catatan:** EVPI selalu ≥ 0 karena informasi sempurna tidak pernah
            memperburuk kualitas keputusan.
            """
        )
