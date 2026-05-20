"""
ui/sidebar.py — Sidebar navigation for DSS Dashboard.
Clean dark sidebar with full-text nav buttons and progress bar.
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
    total = len(MODULES)
    pct = int(n_done / total * 100)

    with st.sidebar:
        # ── Branding ──────────────────────────────────────────
        st.markdown(
            """
            <div style="text-align:center; padding:1.2rem 0 0.8rem;">
                <div style="font-size:2rem; margin-bottom:0.4rem;">📊</div>
                <p style="font-size:1.05rem; font-weight:800; color:#FFFFFF;
                          margin:0; font-family:'Inter',sans-serif;">
                    Dashboard DSS
                </p>
                <p style="font-size:0.72rem; color:rgba(255,255,255,0.5);
                          margin:0.2rem 0 0; font-family:'Inter',sans-serif;">
                    Decision Support System
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.12);margin:0 0 0.8rem;'>",
            unsafe_allow_html=True,
        )

        # ── Progress bar ──────────────────────────────────────
        st.markdown(
            f"""
            <div style="padding:0 0.1rem; margin-bottom:0.9rem;">
                <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
                    <span style="font-size:0.68rem; font-weight:700; color:rgba(255,255,255,0.55);
                                 text-transform:uppercase; letter-spacing:0.7px;
                                 font-family:'Inter',sans-serif;">Progress</span>
                    <span style="font-size:0.72rem; font-weight:600; color:rgba(255,255,255,0.8);
                                 font-family:'Inter',sans-serif;">{n_done}/{total} modul</span>
                </div>
                <div style="background:rgba(255,255,255,0.12); border-radius:6px; height:7px; overflow:hidden;">
                    <div style="background:linear-gradient(90deg,#2563EB,#0EA5E9);
                                width:{pct}%; height:100%; border-radius:6px;
                                min-width:{'6px' if n_done>0 else '0'};"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.12);margin:0 0 0.6rem;'>",
            unsafe_allow_html=True,
        )

        # ── Nav label ─────────────────────────────────────────
        st.markdown(
            "<p style='font-size:0.68rem; font-weight:700; color:rgba(255,255,255,0.5);"
            "text-transform:uppercase; letter-spacing:0.7px; margin:0 0 0.5rem;"
            "font-family:\"Inter\",sans-serif;'>Navigasi Modul</p>",
            unsafe_allow_html=True,
        )

        # ── Nav buttons ───────────────────────────────────────
        for key, label in MODULES:
            is_active = st.session_state["active_module"] == key
            is_done   = key in completed
            needs_payoff = key in _REQUIRES_PAYOFF
            payoff_missing = needs_payoff and "payoff_table" not in completed

            dot = "🟢" if is_done else "⚪"
            display = f"{dot} {label}"
            btn_type = "primary" if is_active else "secondary"

            if st.button(
                display,
                key=f"nav_{key}",
                use_container_width=True,
                type=btn_type,
                help="Selesaikan Payoff Table dulu" if payoff_missing else None,
            ):
                st.session_state["active_module"] = key

        # ── Divider + Home ────────────────────────────────────
        st.markdown(
            "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.12);margin:0.6rem 0;'>",
            unsafe_allow_html=True,
        )

        if st.button("🏠 Beranda", key="nav_home",
                     use_container_width=True, type="secondary"):
            st.session_state["active_module"] = None

        # ── Footer ────────────────────────────────────────────
        st.markdown(
            "<p style='text-align:center; font-size:0.65rem; color:rgba(255,255,255,0.3);"
            "margin:0.8rem 0 0; font-family:\"Inter\",sans-serif;'>"
            "8 modul · 279 tests · Built with Kiro</p>",
            unsafe_allow_html=True,
        )

    return st.session_state["active_module"]
