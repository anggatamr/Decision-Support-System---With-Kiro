"""
app.py — Entry point Dashboard DSS.
Clean, high-contrast welcome page. No KeyError on COLORS.
"""

from __future__ import annotations
import streamlit as st

st.set_page_config(
    page_title="Dashboard DSS — Decision Support System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.styles import inject_custom_css, COLORS
from ui.sidebar import render_sidebar
from ui.components import dashboard_card, next_module_hint


# ── Module imports ────────────────────────────────────────────────────────

def _placeholder(name: str):
    def _r():
        st.info(f"⚙️ Modul `{name}` belum tersedia.", icon="🔧")
    return _r

try:
    from modules.data_driven import render_data_driven_module
except Exception:
    render_data_driven_module = _placeholder("data_driven")

try:
    from modules.payoff_table import render_payoff_table_module
except Exception:
    render_payoff_table_module = _placeholder("payoff_table")

try:
    from modules.ev_eol import render_ev_eol_module
except Exception:
    render_ev_eol_module = _placeholder("ev_eol")

try:
    from modules.uncertainty import render_uncertainty_module
except Exception:
    render_uncertainty_module = _placeholder("uncertainty")

try:
    from modules.distribution import render_distribution_module
except Exception:
    render_distribution_module = _placeholder("distribution")

try:
    from modules.utility import render_utility_module
except Exception:
    render_utility_module = _placeholder("utility")

try:
    from modules.monte_carlo import render_monte_carlo_module
except Exception:
    render_monte_carlo_module = _placeholder("monte_carlo")

try:
    from modules.recommendation_engine import render_recommendation_module
except Exception:
    render_recommendation_module = _placeholder("recommendation")

MODULE_RENDERERS = {
    "data_driven":    render_data_driven_module,
    "payoff_table":   render_payoff_table_module,
    "ev_eol":         render_ev_eol_module,
    "uncertainty":    render_uncertainty_module,
    "distribution":   render_distribution_module,
    "utility":        render_utility_module,
    "monte_carlo":    render_monte_carlo_module,
    "recommendation": render_recommendation_module,
}


# ── Session state ─────────────────────────────────────────────────────────

def _init_session_state() -> None:
    defaults = {
        "df": None, "df_filename": None,
        "payoff_matrix": None, "alt_names": [], "state_names": [],
        "probabilities": None, "ev_results": None, "eol_results": None,
        "uncertainty_results": None, "dist_type": None, "dist_params": None,
        "utility_params": None, "utility_func_type": None,
        "mc_results": None, "mc_input_matrix": None,
        "active_module": None, "completed_modules": set(),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Welcome page ──────────────────────────────────────────────────────────

def render_welcome_page() -> None:

    # Hero — dark navy, bright white text
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {COLORS['primary']} 0%, #0F2347 100%);
            border-radius: 16px;
            padding: 2.8rem 2.4rem;
            margin-bottom: 1.8rem;
            border: 1px solid rgba(37,99,235,0.25);
            box-shadow: 0 8px 32px rgba(15,52,96,0.2);
        ">
            <p style="font-size:0.75rem; color:rgba(255,255,255,0.5);
                      font-weight:700; text-transform:uppercase; letter-spacing:1.5px;
                      margin:0 0 0.5rem; font-family:'Inter',sans-serif;">
                Sistem Pendukung Keputusan Akademik
            </p>
            <p style="font-size:2.5rem; font-weight:800; color:#FFFFFF;
                      margin:0 0 0.5rem; line-height:1.1; letter-spacing:-1px;
                      font-family:'Inter',sans-serif;">
                📊 Dashboard DSS
            </p>
            <p style="font-size:1rem; color:rgba(255,255,255,0.75);
                      margin:0 0 1.5rem; font-family:'Inter',sans-serif;">
                Platform analisis keputusan kuantitatif — Data-Driven &amp; Model-Driven DSS
            </p>
            <div style="display:flex; gap:0.6rem; flex-wrap:wrap;">
                {"".join([
                    f'<span style="background:rgba(255,255,255,0.12);border:1px solid rgba(255,255,255,0.2);'
                    f'border-radius:20px;padding:0.28rem 0.85rem;font-size:0.78rem;font-weight:600;'
                    f'color:#FFFFFF;font-family:Inter,sans-serif;">{t}</span>'
                    for t in ["🧮 8 Modul", "✅ 279 Tests", "🐍 Python + Streamlit", "📐 LaTeX Formulas"]
                ])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Stats row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        dashboard_card("Modul Tersedia", "8", "Data-Driven + Model-Driven", "accent", "🧩")
    with c2:
        dashboard_card("Metode Keputusan", "6", "Certainty → Simulation", "primary", "📐")
    with c3:
        dashboard_card("Property Tests", "279", "Semua lulus ✓", "success", "✅")
    with c4:
        dashboard_card("Distribusi", "6", "Normal, Beta, Poisson…", "info", "📈")

    st.markdown("---")

    # Two-column: description + module map
    col_l, col_r = st.columns([3, 2], gap="large")

    with col_l:
        st.subheader("🎯 Apa itu Decision Support System?")
        st.markdown(
            """
            **Decision Support System (DSS)** adalah sistem berbasis komputer yang membantu
            pengambil keputusan menganalisis data, membangun model kuantitatif, dan mengevaluasi
            alternatif secara sistematis.

            Dashboard ini mengintegrasikan **dua paradigma DSS**:

            - 📊 **Data-Driven DSS** — eksplorasi dataset: statistik deskriptif, tren, korelasi.
            - 🧮 **Model-Driven DSS** — enam kelompok metode Teori Keputusan kuantitatif.

            Semua komputasi berjalan **secara lokal** — tidak ada data yang dikirim ke server.
            """
        )

    with col_r:
        st.subheader("🗺️ Peta Modul")
        items = [
            ("📊", "Data-Driven DSS",    "Upload & eksplorasi dataset"),
            ("📋", "Payoff Table",        "Definisi alternatif & payoff"),
            ("🎲", "EV & EOL",           "Expected Value & Opportunity Loss"),
            ("❓", "Uncertainty",         "Maximax, Maximin, Laplace"),
            ("📈", "Distribusi",          "MLE + PDF/PMF interaktif"),
            ("⚖️", "Fungsi Utilitas",     "Curve fitting & risk preference"),
            ("🎰", "Monte Carlo",         "Simulasi stokastik + sensitivity"),
            ("🏆", "Rekomendasi",         "Konsensus lintas metode"),
        ]
        for icon, name, desc in items:
            st.markdown(
                f"""
                <div style="display:flex;align-items:center;gap:0.7rem;
                            padding:0.45rem 0.8rem;border-radius:8px;margin-bottom:4px;
                            background:#FFFFFF;border:1px solid {COLORS['border']};">
                    <span style="font-size:1rem;">{icon}</span>
                    <div>
                        <p style="margin:0;font-weight:700;font-size:0.86rem;
                                  color:{COLORS['primary']};font-family:'Inter',sans-serif;">{name}</p>
                        <p style="margin:0;font-size:0.73rem;color:{COLORS['mid_gray']};
                                  font-family:'Inter',sans-serif;">{desc}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Feature cards
    st.subheader("✨ Fitur Unggulan")
    fc1, fc2, fc3 = st.columns(3)
    features = [
        (fc1, "📐", "Rumus LaTeX",           COLORS["accent"],
         "Setiap metode dilengkapi rumus matematis via <code>st.latex()</code> — tampil profesional."),
        (fc2, "📊", "Visualisasi Interaktif", COLORS["success"],
         "Semua chart Plotly dengan <code>plotly_white</code>, judul, label sumbu, dan legenda."),
        (fc3, "🔬", "Property-Based Testing", COLORS["warning"],
         "279 property tests via Hypothesis memverifikasi kebenaran matematis setiap fungsi."),
    ]
    for col, icon, title, accent, desc in features:
        with col:
            st.markdown(
                f"""
                <div style="background:#FFFFFF;border-radius:12px;padding:1.3rem;
                            border:1px solid {COLORS['border']};border-top:4px solid {accent};
                            box-shadow:0 1px 8px rgba(0,0,0,0.06);height:100%;">
                    <p style="font-size:1.5rem;margin:0 0 0.5rem;">{icon}</p>
                    <p style="font-weight:700;color:{COLORS['primary']};margin:0 0 0.35rem;
                              font-family:'Inter',sans-serif;font-size:0.95rem;">{title}</p>
                    <p style="color:{COLORS['body_text']};font-size:0.83rem;margin:0;
                              line-height:1.6;font-family:'Inter',sans-serif;">{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Quick-start steps
    st.subheader("🚀 Alur Penggunaan")
    steps = [
        ("1", "📋", "Buat Payoff Table",
         "Mulai dari <b>Payoff Table</b>. Definisikan alternatif, kondisi alam, dan nilai payoff. Tabel ini digunakan oleh modul EV & EOL, Uncertainty, dan Utility."),
        ("2", "🎲", "Analisis Risiko (EV & EOL)",
         "Masukkan probabilitas kondisi alam, hitung <b>Expected Value</b>, <b>EOL</b>, dan <b>EVPI</b>."),
        ("3", "❓", "Kriteria Ketidakpastian",
         "Bandingkan <b>Maximax, Maximin, Minimax Regret, Laplace</b> tanpa informasi probabilitas."),
        ("4", "🏆", "Rekomendasi Konsensus",
         "Setelah ≥2 modul dijalankan, <b>Recommendation Engine</b> merangkum alternatif terbaik dari semua metode."),
    ]
    for num, icon, title, desc in steps:
        cn, cc = st.columns([1, 11])
        with cn:
            st.markdown(
                f"""<div style="background:{COLORS['accent']};color:#FFFFFF;border-radius:50%;
                    width:36px;height:36px;display:flex;align-items:center;justify-content:center;
                    font-weight:800;font-size:0.95rem;margin-top:0.15rem;
                    box-shadow:0 2px 8px rgba(37,99,235,0.3);font-family:'Inter',sans-serif;">
                    {num}</div>""",
                unsafe_allow_html=True,
            )
        with cc:
            st.markdown(f"**{icon} {title}**")
            st.markdown(
                f"<p style='color:{COLORS['body_text']};font-size:0.88rem;margin:0;line-height:1.6;"
                f"font-family:\"Inter\",sans-serif;'>{desc}</p>",
                unsafe_allow_html=True,
            )
        st.markdown("")

    st.markdown("---")

    # Tips
    t1, t2, t3 = st.columns(3)
    with t1:
        st.success("**State Tersimpan Otomatis**\n\nData yang diinput tetap tersimpan saat berpindah modul.", icon="💾")
    with t2:
        st.info("**Indikator 🟢 di Sidebar**\n\nModul selesai ditandai lingkaran hijau di sidebar.", icon="🧭")
    with t3:
        st.warning("**Urutan Disarankan**\n\nPayoff Table → EV & EOL → Uncertainty → Rekomendasi.", icon="⚠️")

    st.markdown("---")

    # CTA buttons
    col_a, col_b, _ = st.columns([2, 2, 3])
    with col_a:
        if st.button("🚀 Mulai — Buat Payoff Table", type="primary", use_container_width=True):
            st.session_state["active_module"] = "payoff_table"
            st.rerun()
    with col_b:
        if st.button("📊 Eksplorasi Data Dulu", type="secondary", use_container_width=True):
            st.session_state["active_module"] = "data_driven"
            st.rerun()

    st.caption("Dashboard DSS — Presentasi akademik Statistika · Semua komputasi lokal.")


# ── Routing ───────────────────────────────────────────────────────────────

def route_to_module(active_module: str) -> None:
    renderer = MODULE_RENDERERS.get(active_module)
    if renderer is None:
        st.error(f"❌ Modul `{active_module}` tidak dikenali.", icon="🚫")
        return
    renderer()
    st.markdown("---")
    next_module_hint(active_module)


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    _init_session_state()
    inject_custom_css()
    render_sidebar()

    active = st.session_state.get("active_module")
    if active is None:
        render_welcome_page()
    else:
        route_to_module(active)


if __name__ == "__main__":
    main()
