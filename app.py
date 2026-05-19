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
    """
    Inisialisasi semua key st.session_state dengan nilai default.
    Hanya mengisi key yang belum ada agar state yang sudah tersimpan
    tidak tertimpa saat halaman di-rerun (Requirement 1.8).
    """
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
# Welcome page — enhanced with feature cards and quick-start
# ---------------------------------------------------------------------------

def render_welcome_page() -> None:
    """
    Render halaman sambutan dengan feature cards, quick-start guide,
    dan statistik aplikasi.
    """

    # ------------------------------------------------------------------
    # Hero section
    # ------------------------------------------------------------------
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {COLORS['primary']} 0%, #0d2d45 100%);
            border-radius: 16px;
            padding: 2.5rem 2rem;
            margin-bottom: 1.5rem;
            color: white;
        ">
            <p style="font-size: 2.4rem; font-weight: 800; margin: 0; line-height: 1.2;
                      letter-spacing: -1px;">
                📊 Dashboard DSS
            </p>
            <p style="font-size: 1.1rem; color: rgba(255,255,255,0.8);
                      margin: 0.5rem 0 1rem 0; font-weight: 400;">
                Decision Support System — Platform Analisis Keputusan Akademik
            </p>
            <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                <span style="background: rgba(255,255,255,0.15); border-radius: 20px;
                             padding: 0.3rem 0.9rem; font-size: 0.82rem; font-weight: 600;">
                    🧮 8 Modul Analisis
                </span>
                <span style="background: rgba(255,255,255,0.15); border-radius: 20px;
                             padding: 0.3rem 0.9rem; font-size: 0.82rem; font-weight: 600;">
                    ✅ 279 Property Tests
                </span>
                <span style="background: rgba(255,255,255,0.15); border-radius: 20px;
                             padding: 0.3rem 0.9rem; font-size: 0.82rem; font-weight: 600;">
                    🐍 Python + Streamlit
                </span>
                <span style="background: rgba(255,255,255,0.15); border-radius: 20px;
                             padding: 0.3rem 0.9rem; font-size: 0.82rem; font-weight: 600;">
                    📐 LaTeX Formulas
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------------
    # Quick stats row
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
            ("📊", "Data-Driven DSS",       "Upload & eksplorasi dataset"),
            ("📋", "Payoff Table",           "Definisi alternatif & payoff"),
            ("🎲", "EV & EOL",              "Expected Value & Opportunity Loss"),
            ("❓", "Uncertainty",            "Maximax, Maximin, Laplace"),
            ("📈", "Distribusi",             "MLE + PDF/PMF interaktif"),
            ("⚖️", "Fungsi Utilitas",        "Curve fitting & risk preference"),
            ("🎰", "Monte Carlo",            "Simulasi stokastik + sensitivity"),
            ("🏆", "Recommendation",         "Konsensus lintas metode"),
        ]
        for icon, name, desc in module_info:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; gap: 0.7rem;
                            padding: 0.45rem 0.7rem; border-radius: 8px;
                            margin-bottom: 4px; background: white;
                            border: 1px solid {COLORS['border']};">
                    <span style="font-size: 1.1rem;">{icon}</span>
                    <div>
                        <p style="margin: 0; font-weight: 600; font-size: 0.88rem;
                                  color: {COLORS['primary']};">{name}</p>
                        <p style="margin: 0; font-size: 0.75rem; color: #7f8c8d;">{desc}</p>
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

    with fc1:
        st.markdown(
            f"""
            <div class="dss-card dss-card-accent">
                <p style="font-size: 1.5rem; margin: 0 0 0.5rem 0;">📐</p>
                <p style="font-weight: 700; color: {COLORS['primary']};
                          margin: 0 0 0.3rem 0;">Rumus LaTeX</p>
                <p style="color: #5a7a8a; font-size: 0.85rem; margin: 0;">
                    Setiap metode dilengkapi rumus matematis yang dirender
                    via <code>st.latex()</code> — tampil profesional untuk presentasi akademik.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with fc2:
        st.markdown(
            f"""
            <div class="dss-card dss-card-success">
                <p style="font-size: 1.5rem; margin: 0 0 0.5rem 0;">📊</p>
                <p style="font-weight: 700; color: {COLORS['primary']};
                          margin: 0 0 0.3rem 0;">Visualisasi Interaktif</p>
                <p style="color: #5a7a8a; font-size: 0.85rem; margin: 0;">
                    Semua chart menggunakan Plotly dengan template <code>plotly_white</code>,
                    judul, label sumbu, dan legenda yang konsisten.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with fc3:
        st.markdown(
            f"""
            <div class="dss-card dss-card-warning">
                <p style="font-size: 1.5rem; margin: 0 0 0.5rem 0;">🔬</p>
                <p style="font-weight: 700; color: {COLORS['primary']};
                          margin: 0 0 0.3rem 0;">Property-Based Testing</p>
                <p style="color: #5a7a8a; font-size: 0.85rem; margin: 0;">
                    279 property tests via Hypothesis memverifikasi kebenaran
                    matematis setiap fungsi komputasi secara formal.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ------------------------------------------------------------------
    # Quick-start guide — numbered steps
    # ------------------------------------------------------------------
    st.subheader("🚀 Cara Memulai")

    steps = [
        ("1", "📋", "Buat Payoff Table",
         "Mulai dari modul **Certainty — Payoff Table**. Definisikan alternatif keputusan, "
         "kondisi alam, dan isi nilai payoff. Tabel ini menjadi fondasi untuk modul EV & EOL, "
         "Uncertainty, dan Utility."),
        ("2", "🎲", "Jalankan Analisis Risiko",
         "Buka **Risk — EV & EOL**, masukkan probabilitas kondisi alam, dan hitung "
         "Expected Value, Expected Opportunity Loss, serta EVPI."),
        ("3", "❓", "Bandingkan Kriteria Ketidakpastian",
         "Di modul **Uncertainty**, bandingkan empat kriteria (Maximax, Maximin, "
         "Minimax Regret, Laplace) tanpa memerlukan informasi probabilitas."),
        ("4", "🏆", "Lihat Rekomendasi Konsensus",
         "Setelah ≥2 modul dijalankan, **Recommendation Engine** merangkum alternatif "
         "terbaik dari semua metode dan menampilkan tingkat konsensus."),
    ]

    for num, icon, title, desc in steps:
        col_num, col_content = st.columns([1, 11])
        with col_num:
            st.markdown(
                f"""
                <div style="
                    background: {COLORS['accent']};
                    color: white;
                    border-radius: 50%;
                    width: 36px; height: 36px;
                    display: flex; align-items: center; justify-content: center;
                    font-weight: 800; font-size: 1rem;
                    margin-top: 0.2rem;
                ">{num}</div>
                """,
                unsafe_allow_html=True,
            )
        with col_content:
            st.markdown(f"**{icon} {title}**")
            st.markdown(f"<p style='color: #5a7a8a; font-size: 0.88rem; margin: 0;'>{desc}</p>",
                        unsafe_allow_html=True)
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
    # CTA button
    # ------------------------------------------------------------------
    st.markdown("---")
    col_cta, _ = st.columns([2, 3])
    with col_cta:
        if st.button(
            "🚀 Mulai — Buat Payoff Table",
            type="primary",
            use_container_width=True,
        ):
            st.session_state["active_module"] = "payoff_table"
            st.rerun()

    st.caption(
        "Dashboard DSS — Dibuat untuk keperluan presentasi akademik Statistika. "
        "Semua komputasi berjalan secara lokal."
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
