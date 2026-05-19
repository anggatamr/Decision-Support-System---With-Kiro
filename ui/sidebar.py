"""
ui/sidebar.py — Sidebar navigation for DSS Dashboard.

Renders the left-panel navigation menu and returns the key of the
currently active module.  Displays a ✅ indicator next to any module
whose key is present in st.session_state["completed_modules"].
"""

from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# Navigation registry
# ---------------------------------------------------------------------------

MODULES: list[tuple[str, str]] = [
    ("data_driven",    "📊 Data-Driven DSS"),
    ("payoff_table",   "📋 Certainty — Payoff Table"),
    ("ev_eol",         "🎲 Risk — EV & EOL"),
    ("uncertainty",    "❓ Uncertainty — Kriteria Keputusan"),
    ("distribution",   "📈 Probabilistic — Distribusi"),
    ("utility",        "⚖️ Utility — Fungsi Utilitas"),
    ("monte_carlo",    "🎰 Simulation — Monte Carlo"),
    ("recommendation", "🏆 Recommendation Engine"),
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_sidebar() -> str | None:
    """Render sidebar navigation and return the key of the selected module.

    Returns
    -------
    str | None
        The key of the module the user clicked, or ``None`` if no module
        has been selected yet in this session.

    Side-effects
    ------------
    - Reads  ``st.session_state["completed_modules"]`` (set[str]) to decide
      which labels get the ✅ indicator.
    - Writes ``st.session_state["active_module"]`` when the user clicks a
      navigation button.
    """
    # Ensure required session-state keys exist (defensive initialisation —
    # app.py should also do this, but sidebar must be self-contained).
    if "completed_modules" not in st.session_state:
        st.session_state["completed_modules"] = set()
    if "active_module" not in st.session_state:
        st.session_state["active_module"] = None

    completed: set[str] = st.session_state["completed_modules"]

    with st.sidebar:
        st.markdown("## 🧭 Navigasi Modul")
        st.markdown("---")

        for key, label in MODULES:
            # Append completion indicator when the module has been completed.
            display_label = f"{label} ✅" if key in completed else label

            # Highlight the currently active module with a distinct style.
            is_active = st.session_state["active_module"] == key
            button_type = "primary" if is_active else "secondary"

            if st.button(
                display_label,
                key=f"nav_{key}",
                use_container_width=True,
                type=button_type,
            ):
                st.session_state["active_module"] = key

        st.markdown("---")
        st.caption("Dashboard DSS — Decision Support System")

    return st.session_state["active_module"]
