"""
modules/utility.py
==================
Module 6: Utility Function & Risk Preference

Computation layer (pure functions — no Streamlit imports):
  - UTILITY_FUNCTIONS: dict of four utility function forms
  - fit_utility_curve: scipy.optimize.curve_fit wrapper
  - classify_risk_preference: deterministic mapping to risk category
  - compute_expected_utility: EU_i = U_matrix @ probs
  - compute_r_squared: goodness-of-fit metric

UI layer:
  - render_utility_module(): Streamlit UI (implemented in task 11.4)

Requirements: 7.3, 7.4, 7.6, 7.9
"""

from __future__ import annotations

import numpy as np
import scipy.optimize

# ---------------------------------------------------------------------------
# Utility function definitions (named functions — required for scipy.optimize.curve_fit)
# ---------------------------------------------------------------------------

def _util_exponential(x, R):
    """Exponential utility: U(x) = 1 - exp(-x / R)"""
    return 1 - np.exp(-x / R)


def _util_logarithmic(x, a, b):
    """Logarithmic utility: U(x) = a * log(x + b)"""
    return a * np.log(x + b)


def _util_linear(x, a, b):
    """Linear utility: U(x) = a * x + b"""
    return a * x + b


def _util_quadratic(x, a, b, c):
    """Quadratic utility: U(x) = a * x² + b * x + c"""
    return a * x**2 + b * x + c


UTILITY_FUNCTIONS: dict = {
    "Eksponensial": _util_exponential,
    "Logaritmik":   _util_logarithmic,
    "Linear":       _util_linear,
    "Kuadratik":    _util_quadratic,
}


# ---------------------------------------------------------------------------
# Computation layer
# ---------------------------------------------------------------------------

def fit_utility_curve(
    func_type: str,
    x_data: np.ndarray,
    y_data: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Fit a utility curve to (x_data, y_data) using scipy.optimize.curve_fit.

    Parameters
    ----------
    func_type : str
        One of the keys in UTILITY_FUNCTIONS.
    x_data : np.ndarray
        Monetary values (independent variable).
    y_data : np.ndarray
        Utility values (dependent variable).

    Returns
    -------
    popt : np.ndarray
        Optimal parameter values.
    pcov : np.ndarray
        Estimated covariance of popt.

    Raises
    ------
    ValueError
        If func_type is not recognised or curve fitting fails to converge.
    """
    if func_type not in UTILITY_FUNCTIONS:
        raise ValueError(
            f"Tipe fungsi tidak dikenal: '{func_type}'. "
            f"Pilih salah satu dari: {list(UTILITY_FUNCTIONS.keys())}"
        )

    func = UTILITY_FUNCTIONS[func_type]
    try:
        popt, pcov = scipy.optimize.curve_fit(func, x_data, y_data, maxfev=5000)
        return popt, pcov
    except RuntimeError:
        raise ValueError(
            "Curve fitting gagal — coba tambahkan lebih banyak titik data "
            "atau pilih bentuk fungsi yang berbeda"
        )


def classify_risk_preference(func_type: str) -> str:
    """
    Return the risk preference category for a given utility function type.

    Mapping (deterministic):
      - Eksponensial → Risk Averse
      - Logaritmik   → Risk Averse
      - Linear       → Risk Neutral
      - Kuadratik    → Risk Seeking

    Parameters
    ----------
    func_type : str
        One of the keys in UTILITY_FUNCTIONS.

    Returns
    -------
    str
        "Risk Averse", "Risk Neutral", or "Risk Seeking".

    Raises
    ------
    ValueError
        If func_type is not recognised.
    """
    mapping: dict[str, str] = {
        "Eksponensial": "Risk Averse",
        "Logaritmik":   "Risk Averse",
        "Linear":       "Risk Neutral",
        "Kuadratik":    "Risk Seeking",
    }
    if func_type not in mapping:
        raise ValueError(
            f"Tipe fungsi tidak dikenal: '{func_type}'. "
            f"Pilih salah satu dari: {list(mapping.keys())}"
        )
    return mapping[func_type]


def compute_expected_utility(
    payoff: np.ndarray,
    probs: np.ndarray,
    utility_func,
    params,
) -> np.ndarray:
    """
    Compute Expected Utility for each alternative.

    EU_i = sum_j( p_j * U(v_ij) ) = U_matrix @ probs

    Parameters
    ----------
    payoff : np.ndarray
        Payoff matrix of shape (m, n).
    probs : np.ndarray
        Probability vector of shape (n,), must sum to ~1.
    utility_func : callable
        A function from UTILITY_FUNCTIONS (or any compatible callable).
    params : sequence
        Fitted parameters to unpack into utility_func.

    Returns
    -------
    np.ndarray
        Expected utility vector of shape (m,).
    """
    U_matrix = utility_func(payoff, *params)  # shape (m, n)
    return U_matrix @ probs                   # shape (m,)


def compute_r_squared(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Compute the coefficient of determination (R²) as a goodness-of-fit metric.

    R² = 1 - SS_res / SS_tot
       where SS_res = sum((y_true - y_pred)²)
             SS_tot = sum((y_true - mean(y_true))²)

    Parameters
    ----------
    y_true : np.ndarray
        Observed values.
    y_pred : np.ndarray
        Predicted values from the fitted curve.

    Returns
    -------
    float
        R² value. Returns 1.0 if SS_tot is zero (constant y_true with perfect prediction).
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))

    if ss_tot == 0.0:
        return 1.0
    return 1.0 - ss_res / ss_tot


# ---------------------------------------------------------------------------
# UI layer — render_utility_module()
# Task 11.4 — Requirements: 7.1–7.11
# ---------------------------------------------------------------------------

def render_utility_module() -> None:
    """
    Render modul Utility Function & Risk Preference secara lengkap.

    Alur:
    1. Sidebar — input jumlah titik data (3–20) dan pasangan (nilai moneter, utilitas)
    2. Sidebar — selector bentuk fungsi utilitas
    3. Sidebar — tombol "Fit Curve"
    4. Pada fit: panggil fit_utility_curve(), tampilkan error jika ValueError
    5. Main panel — Plotly kurva utilitas + titik data input
    6. Main panel — Plotly tiga kurva perbandingan (Risk Averse, Neutral, Seeking)
    7. Tampilkan klasifikasi Risk Preference otomatis
    8. Jika payoff_matrix dan probabilities tersedia: hitung dan tampilkan EU
    9. st.latex() untuk rumus fungsi utilitas yang dipilih
    10. Set session_state["utility_params"] dan tambahkan ke completed_modules

    Requirements: 7.1–7.11
    """
    # -----------------------------------------------------------------------
    # Lazy imports — kept inside function so the module can be imported
    # without streamlit/plotly installed (e.g. during unit/property-based tests)
    # -----------------------------------------------------------------------
    import streamlit as st
    import pandas as pd
    import plotly.graph_objects as go
    from ui.styles import COLORS
    from utils.formatters import fmt_stat

    # -----------------------------------------------------------------------
    # Judul modul
    # -----------------------------------------------------------------------
    st.title("⚖️ Utility — Fungsi Utilitas & Preferensi Risiko")
    st.markdown(
        "Petakan **fungsi utilitas** dari pasangan nilai moneter–utilitas yang Anda masukkan, "
        "identifikasi **preferensi risiko** pengambil keputusan, dan hitung "
        "**Expected Utility (EU)** jika Payoff Table dan probabilitas tersedia."
    )

    # -----------------------------------------------------------------------
    # Sidebar — jumlah titik data (Req 7.1)
    # -----------------------------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚖️ Fungsi Utilitas")
    st.sidebar.markdown("**Langkah 1: Titik Data**")

    n_points: int = st.sidebar.number_input(
        label="Jumlah titik data (3–20)",
        min_value=3,
        max_value=20,
        value=int(st.session_state.get("utility_n_points", 5)),
        step=1,
        key="utility_n_points_input",
    )
    st.session_state["utility_n_points"] = n_points

    # -----------------------------------------------------------------------
    # Sidebar — input pasangan (nilai moneter, utilitas) (Req 7.1)
    # -----------------------------------------------------------------------
    st.sidebar.markdown("**Pasangan Nilai Moneter — Utilitas:**")

    monetary_vals: list[float] = []
    utility_vals: list[float] = []

    # Ambil nilai sebelumnya jika ada
    prev_monetary = st.session_state.get("utility_monetary_vals", [])
    prev_utility  = st.session_state.get("utility_utility_vals", [])

    for i in range(n_points):
        col_m, col_u = st.sidebar.columns(2)
        default_m = float(prev_monetary[i]) if i < len(prev_monetary) else float(i * 100)
        default_u = float(prev_utility[i])  if i < len(prev_utility)  else round(i / max(n_points - 1, 1), 2)

        with col_m:
            m_val = st.number_input(
                label=f"x{i+1}",
                value=default_m,
                step=10.0,
                format="%.2f",
                key=f"utility_m_{i}",
            )
        with col_u:
            u_val = st.number_input(
                label=f"U{i+1}",
                min_value=0.0,
                max_value=1.0,
                value=min(max(default_u, 0.0), 1.0),
                step=0.05,
                format="%.3f",
                key=f"utility_u_{i}",
            )
        monetary_vals.append(m_val)
        utility_vals.append(u_val)

    # Simpan nilai input ke session_state
    st.session_state["utility_monetary_vals"] = monetary_vals
    st.session_state["utility_utility_vals"]  = utility_vals

    # -----------------------------------------------------------------------
    # Sidebar — selector bentuk fungsi utilitas (Req 7.2)
    # -----------------------------------------------------------------------
    st.sidebar.markdown("**Langkah 2: Bentuk Fungsi**")
    func_options = list(UTILITY_FUNCTIONS.keys())  # ["Eksponensial", "Logaritmik", "Linear", "Kuadratik"]
    prev_func = st.session_state.get("utility_func_type", "Eksponensial")
    default_func_idx = func_options.index(prev_func) if prev_func in func_options else 0

    func_type: str = st.sidebar.selectbox(
        label="Bentuk fungsi utilitas",
        options=func_options,
        index=default_func_idx,
        key="utility_func_type_select",
    )
    st.session_state["utility_func_type"] = func_type

    # -----------------------------------------------------------------------
    # Sidebar — tombol "Fit Curve" (Req 7.3)
    # -----------------------------------------------------------------------
    st.sidebar.markdown("**Langkah 3: Fit Kurva**")
    fit_clicked = st.sidebar.button("🔧 Fit Curve", key="utility_fit_btn", use_container_width=True)

    # -----------------------------------------------------------------------
    # State untuk menyimpan hasil fitting
    # -----------------------------------------------------------------------
    if "utility_fit_result" not in st.session_state:
        st.session_state["utility_fit_result"] = None  # None | dict

    # -----------------------------------------------------------------------
    # Proses fitting saat tombol diklik (Req 7.3, 7.4)
    # -----------------------------------------------------------------------
    if fit_clicked:
        x_data = np.array(monetary_vals, dtype=float)
        y_data = np.array(utility_vals, dtype=float)

        # Validasi utilitas dalam [0, 1]
        if np.any(y_data < 0.0) or np.any(y_data > 1.0):
            st.sidebar.error("❌ Nilai utilitas harus berada dalam rentang [0, 1].")
            st.session_state["utility_fit_result"] = None
        else:
            try:
                with st.spinner("⏳ Fitting kurva..."):
                    popt, pcov = fit_utility_curve(func_type, x_data, y_data)
                func = UTILITY_FUNCTIONS[func_type]
                y_pred = func(x_data, *popt)
                r2 = compute_r_squared(y_data, y_pred)
                risk_pref = classify_risk_preference(func_type)

                st.session_state["utility_fit_result"] = {
                    "func_type":    func_type,
                    "popt":         popt,
                    "pcov":         pcov,
                    "r_squared":    r2,
                    "risk_pref":    risk_pref,
                    "x_data":       x_data,
                    "y_data":       y_data,
                }
                st.sidebar.success(f"✅ Fitting berhasil! R² = {r2:.4f}")

            except ValueError as exc:
                # Req 7.4 — tampilkan error jika gagal konvergen
                st.sidebar.error(f"❌ {exc}")
                st.session_state["utility_fit_result"] = None

    # -----------------------------------------------------------------------
    # Ambil hasil fitting dari session_state
    # -----------------------------------------------------------------------
    fit_result: dict | None = st.session_state.get("utility_fit_result")

    # -----------------------------------------------------------------------
    # Jika belum ada hasil fitting, tampilkan panduan
    # -----------------------------------------------------------------------
    if fit_result is None:
        st.info(
            "💡 **Cara penggunaan:**\n"
            "1. Masukkan jumlah titik data (3–20) di sidebar\n"
            "2. Isi pasangan nilai moneter (x) dan utilitas U(x) ∈ [0, 1]\n"
            "3. Pilih bentuk fungsi utilitas\n"
            "4. Klik tombol **🔧 Fit Curve** untuk mengestimasi kurva"
        )
        # Tetap render bagian metodologi di bawah
    else:
        # -------------------------------------------------------------------
        # Ekstrak hasil fitting
        # -------------------------------------------------------------------
        fitted_func_type: str   = fit_result["func_type"]
        popt: np.ndarray        = fit_result["popt"]
        r2: float               = fit_result["r_squared"]
        risk_pref: str          = fit_result["risk_pref"]
        x_data: np.ndarray      = fit_result["x_data"]
        y_data: np.ndarray      = fit_result["y_data"]
        func                    = UTILITY_FUNCTIONS[fitted_func_type]

        # -------------------------------------------------------------------
        # Klasifikasi Risk Preference (Req 7.6)
        # -------------------------------------------------------------------
        st.markdown("---")
        st.subheader("🎯 Klasifikasi Preferensi Risiko")

        risk_color_map = {
            "Risk Averse":   COLORS["success"],
            "Risk Neutral":  COLORS["accent"],
            "Risk Seeking":  COLORS["warning"],
        }
        risk_emoji_map = {
            "Risk Averse":  "🛡️",
            "Risk Neutral": "⚖️",
            "Risk Seeking": "🎲",
        }
        badge_color = risk_color_map.get(risk_pref, COLORS["primary"])
        badge_emoji = risk_emoji_map.get(risk_pref, "")

        col_badge, col_r2 = st.columns([2, 1])
        with col_badge:
            st.markdown(
                f"""
                <div style="
                    display: inline-block;
                    background-color: {badge_color}22;
                    border: 2px solid {badge_color};
                    border-radius: 8px;
                    padding: 0.6rem 1.2rem;
                    font-size: 1.1rem;
                    font-weight: 600;
                    color: {badge_color};
                ">
                    {badge_emoji} {risk_pref}
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption(
                "Klasifikasi otomatis berdasarkan bentuk fungsi utilitas yang dipilih."
            )
        with col_r2:
            st.metric(
                label="Goodness of Fit (R²)",
                value=fmt_stat(r2),
                help="R² mendekati 1.0 menunjukkan fitting yang sangat baik.",
            )

        # -------------------------------------------------------------------
        # Plotly — kurva utilitas + titik data input (Req 7.5)
        # -------------------------------------------------------------------
        st.markdown("---")
        st.subheader("📈 Kurva Fungsi Utilitas")

        x_min = float(x_data.min())
        x_max = float(x_data.max())
        x_range = np.linspace(x_min, x_max, 300)

        try:
            y_curve = func(x_range, *popt)
        except Exception:
            y_curve = np.full_like(x_range, np.nan)

        fig_curve = go.Figure()

        # Kurva fitted
        fig_curve.add_trace(go.Scatter(
            x=x_range.tolist(),
            y=y_curve.tolist(),
            mode="lines",
            name=f"Kurva {fitted_func_type}",
            line=dict(color=COLORS["accent"], width=2.5),
        ))

        # Titik data input
        fig_curve.add_trace(go.Scatter(
            x=x_data.tolist(),
            y=y_data.tolist(),
            mode="markers",
            name="Titik Data Input",
            marker=dict(
                color=COLORS["primary"],
                size=10,
                symbol="circle",
                line=dict(color=COLORS["white"], width=1.5),
            ),
        ))

        fig_curve.update_layout(
            title=f"Fungsi Utilitas — {fitted_func_type} (R² = {r2:.4f})",
            xaxis_title="Nilai Moneter (x)",
            yaxis_title="Utilitas U(x)",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            title_font_size=15,
            yaxis=dict(range=[-0.05, 1.1]),
        )

        st.plotly_chart(fig_curve, use_container_width=True)

        # -------------------------------------------------------------------
        # Plotly — tiga kurva perbandingan (Req 7.8)
        # -------------------------------------------------------------------
        st.markdown("---")
        st.subheader("📊 Perbandingan Tiga Tipe Preferensi Risiko")

        # Gunakan rentang x yang dinormalisasi [0, 1] untuk perbandingan
        x_comp = np.linspace(0.01, 1.0, 300)

        # Risk Averse — logaritmik: a*log(x+b) dinormalisasi
        y_averse  = np.log(x_comp + 1) / np.log(2)          # log(x+1)/log(2), range [0,1]
        # Risk Neutral — linear
        y_neutral = x_comp
        # Risk Seeking — kuadratik konveks
        y_seeking = x_comp ** 2

        fig_comp = go.Figure()

        fig_comp.add_trace(go.Scatter(
            x=x_comp.tolist(),
            y=y_averse.tolist(),
            mode="lines",
            name="Risk Averse (Konkaf)",
            line=dict(color=COLORS["success"], width=2.5, dash="solid"),
        ))
        fig_comp.add_trace(go.Scatter(
            x=x_comp.tolist(),
            y=y_neutral.tolist(),
            mode="lines",
            name="Risk Neutral (Linear)",
            line=dict(color=COLORS["accent"], width=2.5, dash="dash"),
        ))
        fig_comp.add_trace(go.Scatter(
            x=x_comp.tolist(),
            y=y_seeking.tolist(),
            mode="lines",
            name="Risk Seeking (Konveks)",
            line=dict(color=COLORS["warning"], width=2.5, dash="dot"),
        ))

        # Tandai posisi preferensi risiko saat ini
        fig_comp.update_layout(
            title="Perbandingan Bentuk Kurva Utilitas: Risk Averse vs Neutral vs Seeking",
            xaxis_title="Nilai Moneter (dinormalisasi)",
            yaxis_title="Utilitas U(x)",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            title_font_size=15,
        )

        st.plotly_chart(fig_comp, use_container_width=True)

        st.caption(
            f"Pengambil keputusan ini diklasifikasikan sebagai **{risk_pref}** "
            f"berdasarkan fungsi {fitted_func_type} yang dipilih."
        )

        # -------------------------------------------------------------------
        # Expected Utility — jika payoff_matrix dan probabilities tersedia (Req 7.9)
        # -------------------------------------------------------------------
        payoff_matrix: np.ndarray | None = st.session_state.get("payoff_matrix")
        probabilities: np.ndarray | None = st.session_state.get("probabilities")

        if payoff_matrix is not None and probabilities is not None:
            st.markdown("---")
            st.subheader("🧮 Expected Utility (EU) per Alternatif")

            alt_names: list[str] = st.session_state.get("alt_names", [
                f"Alternatif {i+1}" for i in range(payoff_matrix.shape[0])
            ])

            try:
                eu_values = compute_expected_utility(payoff_matrix, probabilities, func, popt)

                eu_df = pd.DataFrame({
                    "Alternatif": alt_names,
                    "Expected Utility (EU)": eu_values,
                })

                best_eu_idx = int(np.argmax(eu_values))

                def _highlight_eu(row):
                    idx = eu_df.index[eu_df["Alternatif"] == row["Alternatif"]].tolist()
                    if idx and idx[0] == best_eu_idx:
                        return [
                            f"background-color: {COLORS['success']}22; "
                            f"font-weight: bold; color: {COLORS['success']}"
                        ] * len(row)
                    return [""] * len(row)

                eu_styled = eu_df.style.apply(_highlight_eu, axis=1).format(
                    {"Expected Utility (EU)": "{:.4f}"}
                )
                st.dataframe(eu_styled, use_container_width=True, hide_index=True)

                best_alt = alt_names[best_eu_idx]
                st.success(
                    f"✅ **Rekomendasi berdasarkan EU tertinggi:** {best_alt} "
                    f"— EU = {eu_values[best_eu_idx]:.4f}"
                )

                # Bar chart EU
                fig_eu = go.Figure(go.Bar(
                    name="Expected Utility (EU)",
                    x=alt_names,
                    y=eu_values.tolist(),
                    marker_color=[
                        COLORS["success"] if i == best_eu_idx else COLORS["accent"]
                        for i in range(len(alt_names))
                    ],
                    text=[f"{v:.4f}" for v in eu_values],
                    textposition="outside",
                ))
                fig_eu.update_layout(
                    title="Expected Utility per Alternatif Keputusan",
                    xaxis_title="Alternatif Keputusan",
                    yaxis_title="Expected Utility (EU)",
                    template="plotly_white",
                    showlegend=False,
                    title_font_size=15,
                )
                st.plotly_chart(fig_eu, use_container_width=True)

            except Exception as exc:
                st.error(
                    f"❌ Gagal menghitung Expected Utility: {exc}\n\n"
                    "Pastikan fungsi utilitas kompatibel dengan rentang nilai payoff."
                )
        else:
            # Req 7.10 — tampilkan info prasyarat
            missing = []
            if payoff_matrix is None:
                missing.append("**Payoff Table** (modul Certainty — Payoff Table)")
            if probabilities is None:
                missing.append("**Probabilitas kondisi alam** (modul Risk — EV & EOL)")
            st.info(
                "ℹ️ **Expected Utility belum dapat dihitung.**\n\n"
                "Prasyarat yang belum terpenuhi:\n"
                + "\n".join(f"- {m}" for m in missing)
            )

        # -------------------------------------------------------------------
        # Rumus LaTeX fungsi utilitas (Req 7.7)
        # -------------------------------------------------------------------
        st.markdown("---")
        st.subheader("📐 Rumus Fungsi Utilitas")

        latex_map = {
            "Eksponensial": (
                r"U(x) = 1 - e^{-x/R}",
                f"di mana R = {popt[0]:.4f} (koefisien toleransi risiko)",
            ),
            "Logaritmik": (
                r"U(x) = a \cdot \ln(x + b)",
                f"di mana a = {popt[0]:.4f}, b = {popt[1]:.4f}",
            ),
            "Linear": (
                r"U(x) = a \cdot x + b",
                f"di mana a = {popt[0]:.6f}, b = {popt[1]:.4f}",
            ),
            "Kuadratik": (
                r"U(x) = a \cdot x^2 + b \cdot x + c",
                f"di mana a = {popt[0]:.6f}, b = {popt[1]:.6f}, c = {popt[2]:.4f}",
            ),
        }

        latex_formula, param_desc = latex_map.get(
            fitted_func_type,
            (r"U(x) = f(x)", "Parameter tidak tersedia"),
        )

        st.latex(latex_formula)
        st.caption(f"**Parameter hasil fitting:** {param_desc}")
        st.caption(f"**Goodness of fit:** R² = {r2:.4f}")

        # -------------------------------------------------------------------
        # Simpan ke session_state (Req 7.9 — utility_params)
        # -------------------------------------------------------------------
        coefficients_dict: dict = {}
        if fitted_func_type == "Eksponensial":
            coefficients_dict = {"R": float(popt[0])}
        elif fitted_func_type == "Logaritmik":
            coefficients_dict = {"a": float(popt[0]), "b": float(popt[1])}
        elif fitted_func_type == "Linear":
            coefficients_dict = {"a": float(popt[0]), "b": float(popt[1])}
        elif fitted_func_type == "Kuadratik":
            coefficients_dict = {"a": float(popt[0]), "b": float(popt[1]), "c": float(popt[2])}

        st.session_state["utility_params"] = {
            "func_type":       fitted_func_type,
            "coefficients":    coefficients_dict,
            "risk_preference": risk_pref,
            "r_squared":       r2,
        }

        if "completed_modules" not in st.session_state:
            st.session_state["completed_modules"] = set()
        st.session_state["completed_modules"].add("utility")

    # -----------------------------------------------------------------------
    # Deskripsi metodologi (Req 7.11) — selalu ditampilkan
    # -----------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📚 Metodologi Teori Utilitas")

    with st.expander("Baca Deskripsi Metodologi", expanded=False):
        st.markdown(
            """
            ### Teori Utilitas dalam Pengambilan Keputusan

            **Teori Utilitas** (von Neumann–Morgenstern) menyatakan bahwa pengambil keputusan
            yang rasional memaksimalkan *nilai harapan utilitas* — bukan nilai harapan moneter
            semata. Fungsi utilitas memetakan nilai moneter ke skala preferensi subjektif [0, 1].

            ---

            ### Preferensi Risiko

            | Tipe | Bentuk Kurva | Fungsi | Karakteristik |
            |------|-------------|--------|---------------|
            | **Risk Averse** | Konkaf (cembung ke atas) | Logaritmik / Eksponensial | Menghindari risiko; lebih suka kepastian |
            | **Risk Neutral** | Linear | Linear | Netral terhadap risiko; keputusan = EV |
            | **Risk Seeking** | Konveks (cembung ke bawah) | Kuadratik | Menyukai risiko; bersedia berjudi |

            ---

            ### Curve Fitting

            Parameter fungsi utilitas diestimasi menggunakan **`scipy.optimize.curve_fit`**
            (metode Levenberg–Marquardt) yang meminimalkan jumlah kuadrat residual antara
            titik data input dan kurva yang dipilih.

            **Goodness of fit** diukur dengan koefisien determinasi:
            """
        )
        try:
            st.latex(
                r"R^2 = 1 - \frac{SS_{res}}{SS_{tot}} = 1 - \frac{\sum(U_i - \hat{U}_i)^2}{\sum(U_i - \bar{U})^2}"
            )
        except Exception:
            st.code("R^2 = 1 - SS_res/SS_tot = 1 - sum(U_i - U_hat_i)^2 / sum(U_i - U_bar)^2")
        st.markdown(
            """
            Nilai R² mendekati 1.0 menunjukkan fitting yang sangat baik.

            ---

            ### Expected Utility (EU)

            Jika Payoff Table dan probabilitas kondisi alam tersedia, EU dihitung sebagai:
            """
        )
        try:
            st.latex(r"EU_i = \sum_{j=1}^{n} p_j \cdot U(v_{ij})")
        except Exception:
            st.code("EU_i = sum_j p_j * U(v_ij)")
        st.markdown(
            r"""
            di mana $p_j$ = probabilitas kondisi alam $j$, $v_{ij}$ = nilai payoff
            alternatif $i$ pada kondisi $j$, dan $U(\cdot)$ = fungsi utilitas yang diestimasi.

            **Interpretasi:** Alternatif dengan EU tertinggi adalah pilihan optimal bagi
            pengambil keputusan dengan preferensi risiko yang diwakili oleh fungsi utilitas tersebut.

            ---

            ### Panduan Interpretasi

            - **R² < 0.8**: Pertimbangkan untuk menambah titik data atau memilih bentuk fungsi lain
            - **R² 0.8–0.95**: Fitting cukup baik untuk analisis keputusan
            - **R² > 0.95**: Fitting sangat baik; kurva merepresentasikan preferensi dengan akurat
            - **Risk Averse**: Cocok untuk pengambil keputusan konservatif (asuransi, investasi aman)
            - **Risk Neutral**: Cocok untuk analisis EV standar
            - **Risk Seeking**: Cocok untuk pengambil keputusan agresif (spekulasi, venture capital)
            """
        )
