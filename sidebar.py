"""
ui/sidebar.py — Sidebar navigation for DSS Dashboard.

Renders the left-panel navigation menu with:
- Overall progress bar (X/8 modules complete)
- Colored status badges per module (🟢 / ⚪)
- Active module highlight
- Module dependency hints

CHANGELOG (Optimized):
- Progress bar now uses inline HTML for more control
- Branding text uses explicit white so it's always readable
- Help tooltips improved
"""

from __future__ import annotations

import streamlit as st
from ui.styles import COLORS

# ---------------------------------------------------------------------------
# Navigation registry
# ---------------------------------------------------------------------------

MODULES: list[tuple[str, str]] = [
    ("data_driven",    "📊 Data-Driven DSS"),
    ("payoff_table",   "📋 Certainty — Payoff Table"),
    ("ev_eol",         "🎲 Risk — EV & EOL"),
    ("uncertainty",    "❓ Uncertainty — Kriteria"),
    ("distribution",   "📈 Probabilistic — Distribusi"),
    ("utility",        "⚖️ Utility — Fungsi Utilitas"),
    ("monte_carlo",    "🎰 Simulation — Monte Carlo"),
    ("recommendation", "🏆 Recommendation Engine"),
]

# Modules that require payoff_table to be completed first
_REQUIRES_PAYOFF = {"ev_eol", "uncertainty", "utility"}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_sidebar() -> str | None:
    """
    Render sidebar navigation and return the key of the selected module.
    """
    if "completed_modules" not in st.session_state:
        st.session_state["completed_modules"] = set()
    if "active_module" not in st.session_state:
        st.session_state["active_module"] = None

    completed: set[str] = st.session_state["completed_modules"]
    total = len(MODULES)
    n_done = len(completed)
    progress_pct = int(n_done / total * 100)

    with st.sidebar:
        # ------------------------------------------------------------------
        # App branding
        # ------------------------------------------------------------------
        st.markdown(
            """
            <div style="text-align: center; padding: 1rem 0 0.6rem 0;">
                <div style="
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    width: 52px;
                    height: 52px;
                    background: rgba(36,113,163,0.35);
                    border-radius: 14px;
                    margin-bottom: 0.6rem;
                    font-size: 1.6rem;
                ">📊</div>
                <p style="
                    font-size: 1.1rem;
                    font-weight: 800;
                    margin: 0;
                    color: #FFFFFF;
                    letter-spacing: -0.3px;
                    font-family: 'DM Sans', sans-serif;
                ">Dashboard DSS</p>
                <p style="
                    font-size: 0.7rem;
                    color: rgba(255,255,255,0.55);
                    margin: 0.15rem 0 0 0;
                    font-family: 'DM Sans', sans-serif;
                    letter-spacing: 0.3px;
                ">Decision Support System</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<hr style='border-color: rgba(255,255,255,0.12); margin: 0.4rem 0 0.8rem 0;'>",
            unsafe_allow_html=True,
        )

        # ------------------------------------------------------------------
        # Progress bar — pure HTML for reliable contrast
        # ------------------------------------------------------------------
        st.markdown(
            f"""
            <div style="padding: 0 0.2rem; margin-bottom: 0.8rem;">
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 0.5rem;
                ">
                    <p style="
                        font-size: 0.7rem;
                        color: rgba(255,255,255,0.65);
                        font-weight: 700;
                        text-transform: uppercase;
                        letter-spacing: 0.6px;
                        margin: 0;
                        font-family: 'DM Sans', sans-serif;
                    ">Progress</p>
                    <p style="
                        font-size: 0.75rem;
                        color: rgba(255,255,255,0.8);
                        font-weight: 600;
                        margin: 0;
                        font-family: 'DM Sans', sans-serif;
                    ">{n_done}/{total}</p>
                </div>
                <div style="
                    background: rgba(255,255,255,0.12);
                    border-radius: 8px;
                    height: 8px;
                    overflow: hidden;
                ">
                    <div style="
                        background: linear-gradient(90deg, #2E86C1 0%, #1ABC9C 100%);
                        width: {progress_pct}%;
                        height: 100%;
                        border-radius: 8px;
                        transition: width 0.5s ease;
                        min-width: {'8px' if n_done > 0 else '0'};
                    "></div>
                </div>
                <p style="
                    font-size: 0.68rem;
                    color: rgba(255,255,255,0.45);
                    margin: 0.3rem 0 0 0;
                    text-align: right;
                    font-family: 'DM Sans', sans-serif;
                ">{progress_pct}% selesai</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<hr style='border-color: rgba(255,255,255,0.12); margin: 0.4rem 0 0.6rem 0;'>",
            unsafe_allow_html=True,
        )

        # ------------------------------------------------------------------
        # Navigation label
        # ------------------------------------------------------------------
        st.markdown(
            """
            <p style="
                font-size: 0.7rem;
                color: rgba(255,255,255,0.55);
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.6px;
                margin: 0 0 0.5rem 0;
                font-family: 'DM Sans', sans-serif;
            ">Navigasi Modul</p>
            """,
            unsafe_allow_html=True,
        )

        # ------------------------------------------------------------------
        # Navigation buttons
        # ------------------------------------------------------------------
        for key, label in MODULES:
            is_active = st.session_state["active_module"] == key
            is_done = key in completed
            needs_payoff = key in _REQUIRES_PAYOFF
            payoff_missing = needs_payoff and "payoff_table" not in completed

            status_dot = "🟢" if is_done else "⚪"
            display_label = f"{status_dot} {label}"
            button_type = "primary" if is_active else "secondary"

            if st.button(
                display_label,
                key=f"nav_{key}",
                use_container_width=True,
                type=button_type,
                help=(
                    "⚠️ Selesaikan Payoff Table terlebih dahulu"
                    if payoff_missing else
                    f"Buka modul {label}"
                ),
            ):
                st.session_state["active_module"] = key

        # ------------------------------------------------------------------
        # Home button
        # ------------------------------------------------------------------
        st.markdown(
            "<hr style='border-color: rgba(255,255,255,0.12); margin: 0.6rem 0;'>",
            unsafe_allow_html=True,
        )

        if st.button(
            "🏠 Beranda",
            key="nav_home",
            use_container_width=True,
            type="secondary",
            help="Kembali ke halaman sambutan",
        ):
            st.session_state["active_module"] = None

        # ------------------------------------------------------------------
        # Footer
        # ------------------------------------------------------------------
        st.markdown(
            """
            <div style="text-align: center; padding: 0.8rem 0 0.3rem 0;">
                <p style="
                    font-size: 0.68rem;
                    color: rgba(255,255,255,0.35);
                    margin: 0;
                    line-height: 1.7;
                    font-family: 'DM Sans', sans-serif;
                ">8 modul · 279 tests<br>Python + Streamlit<br>
                <span style="color: rgba(255,255,255,0.2);">Built with Kiro</span>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return st.session_state["active_module"]
