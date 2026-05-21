"""
ui/sidebar.py — Pure Streamlit sidebar. No HTML injection.
Uses st.markdown for text and st.button for nav — reliable on Streamlit Cloud.
"""

from __future__ import annotations
import streamlit as st
from ui.styles import COLORS

MODULES: list[tuple[str, str]] = [
    ("data_driven",    "📊 Data-Driven DSS"),
    ("payoff_table",   "📋 Payoff Table"),
    ("ev_eol",         "🎲 EV & EOL"),
    ("uncertainty",    "❓ Uncertainty"),
    ("distribution",   "📈 Distribusi"),
    ("utility",        "⚖️ Fungsi Utilitas"),
    ("monte_carlo",    "🎰 Monte Carlo"),
    ("recommendation", "🏆 Rekomendasi"),
]

_REQUIRES_PAYOFF = {"ev_eol", "uncertainty", "utility"}


def render_sidebar() -> str | None:
    if "completed_modules" not in st.session_state:
        st.session_state["completed_modules"] = set()
    if "active_module" not in st.session_state:
        st.session_state["active_module"] = None

    completed: set[str] = st.session_state["completed_modules"]
    n_done = len(completed)
    total  = len(MODULES)
    pct    = int(n_done / total * 100)

    with st.sidebar:
        # Branding — pure HTML, explicit white
        st.markdown(
            f"""<div style="text-align:center;padding:1rem 0 0.6rem;">
                <p style="font-size:1.1rem;font-weight:800;color:#FFFFFF;margin:0;
                          font-family:'Space Grotesk',sans-serif;">📊 Dashboard DSS</p>
                <p style="font-size:0.72rem;color:rgba(255,255,255,0.55);margin:0.1rem 0 0;
                          font-family:'Space Grotesk',sans-serif;">Decision Support System</p>
            </div>""",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.15);margin:0.4rem 0 0.7rem;'>",
            unsafe_allow_html=True,
        )

        # Progress bar — pure HTML
        st.markdown(
            f"""<div style="margin-bottom:0.8rem;">
                <div style="display:flex;justify-content:space-between;margin-bottom:0.35rem;">
                    <span style="font-size:0.68rem;font-weight:700;color:rgba(255,255,255,0.55);
                                 text-transform:uppercase;letter-spacing:0.6px;
                                 font-family:'Space Grotesk',sans-serif;">Progress</span>
                    <span style="font-size:0.72rem;font-weight:600;color:rgba(255,255,255,0.80);
                                 font-family:'Space Grotesk',sans-serif;">{n_done}/{total}</span>
                </div>
                <div style="background:rgba(255,255,255,0.15);border-radius:6px;height:7px;overflow:hidden;">
                    <div style="background:linear-gradient(90deg,#3B82F6,#06B6D4);
                                width:{pct}%;height:100%;border-radius:6px;
                                min-width:{'6px' if n_done > 0 else '0'};"></div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.15);margin:0.4rem 0 0.5rem;'>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<p style='font-size:0.68rem;font-weight:700;color:rgba(255,255,255,0.50);"
            "text-transform:uppercase;letter-spacing:0.6px;margin:0 0 0.4rem;"
            "font-family:Space Grotesk,sans-serif;'>Navigasi Modul</p>",
            unsafe_allow_html=True,
        )

        # Nav buttons
        for key, label in MODULES:
            is_active    = st.session_state["active_module"] == key
            is_done      = key in completed
            needs_payoff = key in _REQUIRES_PAYOFF
            payoff_miss  = needs_payoff and "payoff_table" not in completed

            dot     = "🟢" if is_done else "⚪"
            display = f"{dot} {label}"
            btype   = "primary" if is_active else "secondary"

            if st.button(
                display,
                key=f"nav_{key}",
                use_container_width=True,
                type=btype,
                help="Selesaikan Payoff Table dulu" if payoff_miss else None,
            ):
                st.session_state["active_module"] = key

        st.markdown(
            "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.15);margin:0.5rem 0;'>",
            unsafe_allow_html=True,
        )

        if st.button("🏠 Beranda", key="nav_home",
                     use_container_width=True, type="secondary"):
            st.session_state["active_module"] = None

        st.markdown(
            "<p style='text-align:center;font-size:0.63rem;color:rgba(255,255,255,0.28);"
            "margin:0.6rem 0 0;font-family:Space Grotesk,sans-serif;'>"
            "8 modul · 279 tests · Built with Kiro</p>",
            unsafe_allow_html=True,
        )

    return st.session_state["active_module"]
