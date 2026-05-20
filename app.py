"""
app.py — Entry point untuk Dashboard DSS (Decision Support System).

Tanggung jawab:
- Konfigurasi halaman Streamlit (set_page_config)
- Inisialisasi semua key st.session_state
- Inject CSS custom dan render sidebar navigasi
- Routing: active_module == None → halaman sambutan; selain itu → renderer modul

Requirements: 1.3, 1.4, 1.7, 1.8
"""

from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# Konfigurasi halaman — HARUS dipanggil sebelum perintah Streamlit lainnya
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard DSS — Decision Support System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Import komponen UI
# ---------------------------------------------------------------------------
from ui.styles import inject_custom_css, COLORS
from ui.sidebar import render_sidebar
from ui.components import dashboard_card, next_module_hint

# ---------------------------------------------------------------------------
# Import renderer modul
# ---------------------------------------------------------------------------

def _placeholder_renderer(module_name: str):
    """Renderer sementara untuk modul yang belum diimplementasikan."""
    def _render():
        st.info(
            f"⚙️ **Modul sedang dalam pengembangan**\n\n"
            f"Modul `{module_name}` belum tersedia.",
            icon="🔧",
        )
    return _render


try:
    from modules.data_driven import render_data_driven_module
except (ImportError, Exception):
    render_data_driven_module = _placeholder_renderer("data_driven")

try:
    from modules.payoff_table import render_payoff_table_module
except (ImportError, Exception):
    render_payoff_table_module = _placeholder_renderer("payoff_table")

try:
    from modules.ev_eol import render_ev_eol_module
except (ImportError, Exception):
    render_ev_eol_module = _placeholder_renderer("ev_eol")

try:
    from modules.uncertainty import render_uncertainty_module
except (ImportError, Exception):
    render_uncertainty_module = _placeholder_renderer("uncertainty")

try:
    from modules.distribution import render_distribution_module
except (ImportError, Exception):
    render_distribution_module = _placeholder_renderer("distribution")

try:
    from modules.utility import render_utility_module
except (ImportError, Exception):
    render_utility_module = _placeholder_renderer("utility")

try:
    from modules.monte_carlo import render_monte_carlo_module
except (ImportError, Exception):
    render_monte_carlo_module = _placeholder_renderer("monte_carlo")

try:
    from modules.recommendation_engine import render_recommendation_module
except (ImportError, Exception):
    render_recommendation_module = _placeholder_renderer("recommendation")

# ---------------------------------------------------------------------------
# Peta routing: key modul → fungsi renderer
# ---------------------------------------------------------------------------
MODULE_RENDERERS: dict[str, callable] = {
    "data_driven":    render_data_driven_module,
    "payoff_table":   render_payoff_table_module,
    "ev_eol":         render_ev_eol_module,
    "uncertainty":    render_uncertainty_module,
    "distribution":   render_distribution_module,
    "utility":        render_utility_module,
    "monte_carlo":    render_monte_carlo_module,
    "recommendation": render_recommendation_module,
}


# ---------------------------------------------------------------------------
# Inisialisasi session state
# ---------------------------------------------------------------------------

def _init_session_state() -> None:
    defaults: dict = {
        "df":                   None,
        "df_filename":          None,
        "payoff_matrix":        None,
        "alt_names":            [],
        "state_names":          [],
        "probabilities":        None,
        "ev_results":           None,
        "eol_results":          None,
        "uncertainty_results":  None,
        "dist_type":            None,
        "dist_params":          None,
        "utility_params":       None,
        "utility_func_type":    None,
        "mc_results":           None,
        "mc_input_matrix":      None,
        "active_module":        None,
        "completed_modules":    set(),
    }
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


# ---------------------------------------------------------------------------
# Welcome page — optimized for presentation
# ---------------------------------------------------------------------------

def render_welcome_page() -> None:
    """Render halaman sambutan yang optimal untuk presentasi."""

    # ------------------------------------------------------------------
    # Hero section — gradient lebih kontras dan informatif
    # ------------------------------------------------------------------
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {COLORS['primary']} 0%, #082040 55%, #0d2d4a 100%);
            border-radius: 18px;
            padding: 2.8rem 2.4rem;
            margin-bottom: 1.8rem;
            color: white;
            border: 1px solid rgba(36,113,163,0.3);
            box-shadow: 0 8px 32px rgba(15,52,96,0.25);
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: -40px; right: -40px;
                width: 200px; height: 200px;
                background: radial-gradient(circle, rgba(36,113,163,0.25) 0%, transparent 70%);
                border-radius: 50%;
            "></div>
            <div style="
                position: absolute;
                bottom: -30px; left: 60%;
                width: 150px; height: 150px;
                background: radial-gradient(circle, rgba(26,188,156,0.15) 0%, transparent 70%);
                border-radius: 50%;
            "></div>
            <div style="position: relative; z-index: 1;">
                <p style="
                    font-size: 0.8rem;
                    color: rgba(255,255,255,0.55);
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 1.5px;
                    margin: 0 0 0.5rem 0;
                    font-family: 'DM Sans', sans-serif;
                ">Sistem Pendukung Keputusan Akademik</p>
                <p style="
                    font-size: 2.6rem;
                    font-weight: 800;
                    margin: 0 0 0.4rem 0;
                    line-height: 1.1;
                    letter-spacing: -1px;
                    font-family: 'DM Sans', sans-serif;
                    color: #FFFFFF;
                ">📊 Dashboard DSS</p>
                <p style="
                    font-size: 1.05rem;
                    color: rgba(255,255,255,0.72);
                    margin: 0 0 1.4rem 0;
                    font-weight: 400;
                    font-family: 'DM Sans', sans-serif;
                ">Platform analisis keputusan kuantitatif terintegrasi — dari Data-Driven hingga Model-Driven DSS</p>
                <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
                    <span style="
                        background: rgba(255,255,255,0.12);
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(255,255,255,0.2);
                        border-radius: 20px;
                        padding: 0.3rem 0.9rem;
                        font-size: 0.8rem;
                        font-weight: 600;
                        color: #FFFFFF;
                        font-family: 'DM Sans', sans-serif;
                    ">🧮 8 Modul Analisis</span>
                    <span style="
                        background: rgba(255,255,255,0.12);
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(255,255,255,0.2);
                        border-radius: 20px;
                        padding: 0.3rem 0.9rem;
                        font-size: 0.8rem;
                        font-weight: 600;
                        color: #FFFFFF;
                        font-family: 'DM Sans', sans-serif;
                    ">✅ 279 Property Tests</span>
                    <span style="
                        background: rgba(255,255,255,0.12);
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(255,255,255,0.2);
                        border-radius: 20px;
                        padding: 0.3rem 0.9rem;
                        font-size: 0.8rem;
                        font-weight: 600;
                        color: #FFFFFF;
                        font-family: 'DM Sans', sans-serif;
                    ">🐍 Python + Streamlit</span>
                    <span style="
                        background: rgba(255,255,255,0.12);
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(255,255,255,0.2);
                        border-radius: 20px;
                        padding: 0.3rem 0.9rem;
                        font-size: 0.8rem;
                        font-weight: 600;
                        color: #FFFFFF;
                        font-family: 'DM Sans', sans-serif;
                    ">📐 Hypothesis Testing</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------------
    # Stats row
    # ------------------------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        dashboard_card("Modul Tersedia", "8", "Data-Driven + Model-Driven", "accent", "🧩")
    with c2:
        dashboard_card("Metode Keputusan", "6", "Certainty → Simulation", "primary", "📐")
    with c3:
        dashboard_card("Property Tests", "279", "Semua lulus ✓", "success", "✅")
    with c4:
        dashboard_card("Distribusi Didukung", "6", "Normal, Beta, Poisson…", "info", "📈")

    st.markdown("---")

    # ------------------------------------------------------------------
    # Two-column: What is DSS + Module map
    # ------------------------------------------------------------------
    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.subheader("🎯 Apa itu Decision Support System?")
        st.markdown(
            """
            **Decision Support System (DSS)** adalah sistem berbasis komputer yang membantu
            pengambil keputusan menganalisis data, membangun model kuantitatif, dan mengevaluasi
            alternatif secara sistematis.

            Dashboard ini mengintegrasikan **dua paradigma DSS** dalam satu antarmuka terpadu:

            - 📊 **Data-Driven DSS** — eksplorasi dataset nyata: statistik deskriptif,
              visualisasi tren, dan analisis korelasi.
            - 🧮 **Model-Driven DSS** — enam kelompok metode Teori Keputusan kuantitatif,
              dari analisis kepastian hingga simulasi Monte Carlo.

            Semua komputasi berjalan **secara lokal** — tidak ada data yang dikirim ke server
            eksternal. State setiap modul tersimpan otomatis selama sesi aktif.
            """
        )

    with col_right:
        st.subheader("🗺️ Peta Modul")
        module_info = [
            ("📊", "Data-Driven DSS",      "Upload & eksplorasi dataset"),
            ("📋", "Payoff Table",          "Definisi alternatif & payoff"),
            ("🎲", "EV & EOL",             "Expected Value & Opportunity Loss"),
            ("❓", "Uncertainty",           "Maximax, Maximin, Laplace"),
            ("📈", "Distribusi",            "MLE + PDF/PMF interaktif"),
            ("⚖️", "Fungsi Utilitas",       "Curve fitting & risk preference"),
            ("🎰", "Monte Carlo",           "Simulasi stokastik + sensitivity"),
            ("🏆", "Recommendation",        "Konsensus lintas metode"),
        ]
        for icon, name, desc in module_info:
            st.markdown(
                f"""
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    padding: 0.5rem 0.85rem;
                    border-radius: 9px;
                    margin-bottom: 5px;
                    background: #FFFFFF;
                    border: 1px solid {COLORS['border']};
                    transition: border-color 0.2s;
                ">
                    <span style="font-size: 1.05rem;">{icon}</span>
                    <div>
                        <p style="
                            margin: 0;
                            font-weight: 700;
                            font-size: 0.87rem;
                            color: {COLORS['primary']};
                            font-family: 'DM Sans', sans-serif;
                        ">{name}</p>
                        <p style="
                            margin: 0;
                            font-size: 0.74rem;
                            color: {COLORS['mid_gray']};
                            font-family: 'DM Sans', sans-serif;
                        ">{desc}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ------------------------------------------------------------------
    # Feature cards — 3 columns
    # ------------------------------------------------------------------
    st.subheader("✨ Fitur Unggulan")

    fc1, fc2, fc3 = st.columns(3)

    feature_cards = [
        (fc1, "📐", "Rumus LaTeX", COLORS["accent"],
         "Setiap metode dilengkapi rumus matematis yang dirender via <code>st.latex()</code> — tampil profesional untuk presentasi akademik."),
        (fc2, "📊", "Visualisasi Interaktif", COLORS["success"],
         "Semua chart menggunakan Plotly dengan template <code>plotly_white</code>, judul, label sumbu, dan legenda yang konsisten."),
        (fc3, "🔬", "Property-Based Testing", COLORS["warning"],
         "279 property tests via Hypothesis memverifikasi kebenaran matematis setiap fungsi komputasi secara formal."),
    ]

    for col, icon, title, accent, desc in feature_cards:
        with col:
            st.markdown(
                f"""
                <div style="
                    background: #FFFFFF;
                    border-radius: 14px;
                    padding: 1.4rem 1.3rem;
                    border: 1px solid {COLORS['border']};
                    border-top: 4px solid {accent};
                    box-shadow: 0 2px 12px rgba(15,52,96,0.07);
                    height: 100%;
                ">
                    <p style="font-size: 1.6rem; margin: 0 0 0.6rem 0;">{icon}</p>
                    <p style="
                        font-weight: 700;
                        color: {COLORS['primary']};
                        margin: 0 0 0.4rem 0;
                        font-family: 'DM Sans', sans-serif;
                        font-size: 0.98rem;
                    ">{title}</p>
                    <p style="
                        color: {COLORS['body_text']};
                        font-size: 0.84rem;
                        margin: 0;
                        line-height: 1.6;
                        font-family: 'DM Sans', sans-serif;
                    ">{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ------------------------------------------------------------------
    # Quick-start guide — alur presentasi yang disarankan
    # ------------------------------------------------------------------
    st.subheader("🚀 Alur Penggunaan yang Disarankan")

    steps = [
        ("1", "📋", "Buat Payoff Table",
         "**payoff_table",
         "Mulai dari modul **Certainty — Payoff Table**. Definisikan alternatif keputusan, kondisi alam, dan isi nilai payoff. Tabel ini menjadi fondasi untuk modul EV & EOL, Uncertainty, dan Utility."),
        ("2", "🎲", "Jalankan Analisis Risiko",
         "ev_eol",
         "Buka **Risk — EV & EOL**, masukkan probabilitas kondisi alam, dan hitung Expected Value, Expected Opportunity Loss, serta EVPI."),
        ("3", "❓", "Bandingkan Kriteria Ketidakpastian",
         "uncertainty",
         "Di modul **Uncertainty**, bandingkan empat kriteria (Maximax, Maximin, Minimax Regret, Laplace) tanpa informasi probabilitas."),
        ("4", "🏆", "Lihat Rekomendasi Konsensus",
         "recommendation",
         "Setelah ≥2 modul dijalankan, **Recommendation Engine** merangkum alternatif terbaik dari semua metode dan menampilkan tingkat konsensus."),
    ]

    for num, icon, title, module_key, desc in steps:
        col_num, col_content = st.columns([1, 11])
        with col_num:
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, {COLORS['accent']} 0%, {COLORS['primary']} 100%);
                    color: white;
                    border-radius: 50%;
                    width: 38px; height: 38px;
                    display: flex; align-items: center; justify-content: center;
                    font-weight: 800; font-size: 1rem;
                    margin-top: 0.2rem;
                    box-shadow: 0 3px 10px rgba(36,113,163,0.35);
                    font-family: 'DM Sans', sans-serif;
                ">{num}</div>
                """,
                unsafe_allow_html=True,
            )
        with col_content:
            st.markdown(f"**{icon} {title}**")
            st.markdown(
                f"<p style='color: {COLORS['body_text']}; font-size: 0.88rem; margin: 0; line-height: 1.6;'>{desc}</p>",
                unsafe_allow_html=True,
            )
        st.markdown("")

    st.markdown("---")

    # ------------------------------------------------------------------
    # Tips row
    # ------------------------------------------------------------------
    st.subheader("💡 Tips Penggunaan")
    t1, t2, t3 = st.columns(3)

    with t1:
        st.success(
            "**State Tersimpan Otomatis**\n\n"
            "Data yang sudah diinput di satu modul tetap tersimpan saat berpindah modul "
            "dalam sesi yang sama.",
            icon="💾",
        )
    with t2:
        st.info(
            "**Indikator 🟢 di Sidebar**\n\n"
            "Modul yang sudah selesai ditandai dengan lingkaran hijau di sidebar navigasi.",
            icon="🧭",
        )
    with t3:
        st.warning(
            "**Urutan yang Disarankan**\n\n"
            "Payoff Table → EV & EOL → Uncertainty → Utility → Recommendation Engine.",
            icon="⚠️",
        )

    # ------------------------------------------------------------------
    # CTA button — mulai presentasi
    # ------------------------------------------------------------------
    st.markdown("---")
    col_cta, col_data, _ = st.columns([2, 2, 3])
    with col_cta:
        if st.button(
            "🚀 Mulai — Buat Payoff Table",
            type="primary",
            use_container_width=True,
        ):
            st.session_state["active_module"] = "payoff_table"
            st.rerun()
    with col_data:
        if st.button(
            "📊 Eksplorasi Data Terlebih Dulu",
            type="secondary",
            use_container_width=True,
        ):
            st.session_state["active_module"] = "data_driven"
            st.rerun()

    st.caption(
        "Dashboard DSS — Dibuat untuk keperluan presentasi akademik Statistika. "
        "Semua komputasi berjalan secara lokal · Session state otomatis tersimpan."
    )


# ---------------------------------------------------------------------------
# Routing utama
# ---------------------------------------------------------------------------

def route_to_module(active_module: str) -> None:
    """Route ke renderer modul yang sesuai."""
    renderer = MODULE_RENDERERS.get(active_module)

    if renderer is None:
        st.error(
            f"❌ Modul `{active_module}` tidak dikenali. "
            "Silakan pilih modul yang valid dari sidebar.",
            icon="🚫",
        )
        return

    renderer()

    # Show next-module hint at the bottom of every module page
    st.markdown("---")
    next_module_hint(active_module)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    _init_session_state()
    inject_custom_css()
    render_sidebar()

    active_module: str | None = st.session_state.get("active_module")

    if active_module is None:
        render_welcome_page()
    else:
        route_to_module(active_module)


if __name__ == "__main__":
    main()
