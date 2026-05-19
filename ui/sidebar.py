"""
ui/sidebar.py — Sidebar navigation for DSS Dashboard.

Renders the left-panel navigation menu with:
- Overall progress bar (X/8 modules complete)
- Colored status badges per module (🟢 / ⚪)
- Active module highlight
- Module dependency hints
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

    Features:
    - Progress bar showing overall completion
    - Colored status indicators (🟢 completed / ⚪ not started)
    - Active module highlighted with primary button style
    - Dependency hints for modules requiring payoff table
    """
    if "completed_modules" not in st.session_state:
        st.session_state["completed_modules"] = set()
    if "active_module" not in st.session_state:
        st.session_state["active_module"] = None

    completed: set[str] = st.session_state["completed_modules"]
    total = len(MODULES)
    n_done = len(completed)

    with st.sidebar:
        # ------------------------------------------------------------------
        # App branding
        # ------------------------------------------------------------------
        st.markdown(
            f"""
            <div style="text-align: center; padding: 0.8rem 0 0.4rem 0;">
                <p style="font-size: 1.5rem; margin: 0;">📊</p>
                <p style="font-size: 1rem; font-weight: 800; margin: 0;
                          color: white; letter-spacing: -0.3px;">Dashboard DSS</p>
                <p style="font-size: 0.72rem; color: rgba(255,255,255,0.6);
                          margin: 0.1rem 0 0 0;">Decision Support System</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # ------------------------------------------------------------------
        # Progress bar
        # ------------------------------------------------------------------
        progress_pct = n_done / total
        progress_label = f"{n_done}/{total} modul selesai"

        st.markdown(
            f"""
            <div style="margin-bottom: 0.3rem;">
                <p style="font-size: 0.72rem; color: rgba(255,255,255,0.7);
                          font-weight: 600; text-transform: uppercase;
                          letter-spacing: 0.5px; margin: 0 0 0.4rem 0;">
                    Progress
                </p>
                <div style="background: rgba(255,255,255,0.15); border-radius: 6px;
                            height: 6px; overflow: hidden;">
                    <div style="background: {COLORS['accent']}; width: {progress_pct*100:.0f}%;
                                height: 100%; border-radius: 6px;
                                transition: width 0.4s ease;"></div>
                </div>
                <p style="font-size: 0.72rem; color: rgba(255,255,255,0.6);
                          margin: 0.3rem 0 0 0; text-align: right;">{progress_label}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # ------------------------------------------------------------------
        # Navigation buttons
        # ------------------------------------------------------------------
        st.markdown(
            '<p style="font-size: 0.72rem; color: rgba(255,255,255,0.6); '
            'font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; '
            'margin: 0 0 0.5rem 0;">Navigasi Modul</p>',
            unsafe_allow_html=True,
        )

        for key, label in MODULES:
            is_active = st.session_state["active_module"] == key
            is_done = key in completed
            needs_payoff = key in _REQUIRES_PAYOFF
            payoff_missing = needs_payoff and "payoff_table" not in completed

            # Status indicator
            status_dot = "🟢" if is_done else "⚪"

            # Build display label
            display_label = f"{status_dot} {label}"

            # Dim label if prerequisite missing
            if payoff_missing and not is_active:
                display_label = f"⚪ {label}"

            button_type = "primary" if is_active else "secondary"

            if st.button(
                display_label,
                key=f"nav_{key}",
                use_container_width=True,
                type=button_type,
                help="Membutuhkan Payoff Table terlebih dahulu" if payoff_missing else None,
            ):
                st.session_state["active_module"] = key

        # ------------------------------------------------------------------
        # Footer
        # ------------------------------------------------------------------
        st.markdown("---")

        # Quick stats
        st.markdown(
            f"""
            <div style="text-align: center; padding: 0.3rem 0;">
                <p style="font-size: 0.7rem; color: rgba(255,255,255,0.45);
                          margin: 0; line-height: 1.6;">
                    8 modul · 279 tests · Python + Streamlit
                </p>
                <p style="font-size: 0.65rem; color: rgba(255,255,255,0.3);
                          margin: 0.3rem 0 0 0;">
                    Built with Kiro
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return st.session_state["active_module"]
