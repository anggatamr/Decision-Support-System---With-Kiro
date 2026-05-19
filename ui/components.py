"""
ui/components.py
Reusable UI components for DSS Dashboard.

Provides:
- dashboard_card()     — styled metric/info card
- module_status_badge() — colored status badge
- section_header()     — consistent section header with icon
- download_csv_button() — download button for DataFrame results
- next_module_hint()   — navigation hint to next logical module
"""

from __future__ import annotations

import io
import pandas as pd
import streamlit as st

from ui.styles import COLORS


# ---------------------------------------------------------------------------
# Dashboard card
# ---------------------------------------------------------------------------

def dashboard_card(
    title: str,
    value: str,
    subtitle: str = "",
    color: str = "accent",
    icon: str = "",
) -> None:
    """
    Render a styled metric card using HTML.

    Parameters
    ----------
    title    : Card label (small, uppercase)
    value    : Main metric value (large, bold)
    subtitle : Optional secondary line below value
    color    : One of "accent", "success", "warning", "danger", "primary"
    icon     : Optional emoji/icon prefix for the title
    """
    border_color = COLORS.get(color, COLORS["accent"])
    icon_prefix = f"{icon} " if icon else ""

    st.markdown(
        f"""
        <div class="dss-card" style="border-left: 4px solid {border_color};">
            <p style="
                color: #5a7a8a;
                font-size: 0.78rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.6px;
                margin: 0 0 0.3rem 0;
            ">{icon_prefix}{title}</p>
            <p style="
                color: {COLORS['primary']};
                font-size: 1.7rem;
                font-weight: 800;
                margin: 0;
                line-height: 1.2;
            ">{value}</p>
            {f'<p style="color: #7f8c8d; font-size: 0.82rem; margin: 0.3rem 0 0 0;">{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Module status badge
# ---------------------------------------------------------------------------

def module_status_badge(status: str) -> str:
    """
    Return an HTML badge string for a module status.

    Parameters
    ----------
    status : "completed" | "in_progress" | "not_started"

    Returns
    -------
    str — HTML span element
    """
    config = {
        "completed":   ("🟢 Selesai",    "dss-badge dss-badge-success"),
        "in_progress": ("🟡 Berjalan",   "dss-badge dss-badge-warning"),
        "not_started": ("⚪ Belum",       "dss-badge dss-badge-gray"),
    }
    label, css_class = config.get(status, config["not_started"])
    return f'<span class="{css_class}">{label}</span>'


# ---------------------------------------------------------------------------
# Section header
# ---------------------------------------------------------------------------

def section_header(title: str, subtitle: str = "", divider: bool = True) -> None:
    """
    Render a consistent section header with optional subtitle and divider.
    """
    if divider:
        st.markdown("---")
    st.subheader(title)
    if subtitle:
        st.caption(subtitle)


# ---------------------------------------------------------------------------
# Download CSV button
# ---------------------------------------------------------------------------

def download_csv_button(
    df: pd.DataFrame,
    filename: str,
    label: str = "📥 Unduh Hasil (CSV)",
) -> None:
    """
    Render a styled download button for a DataFrame as CSV.

    Parameters
    ----------
    df       : DataFrame to export
    filename : Output filename (e.g. "ev_results.csv")
    label    : Button label text
    """
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=label,
        data=csv_bytes,
        file_name=filename,
        mime="text/csv",
        use_container_width=False,
    )


# ---------------------------------------------------------------------------
# Download text button
# ---------------------------------------------------------------------------

def download_text_button(
    text: str,
    filename: str,
    label: str = "📥 Unduh Laporan (TXT)",
) -> None:
    """Render a download button for plain-text content."""
    st.download_button(
        label=label,
        data=text.encode("utf-8"),
        file_name=filename,
        mime="text/plain",
        use_container_width=False,
    )


# ---------------------------------------------------------------------------
# Next module hint
# ---------------------------------------------------------------------------

_MODULE_SEQUENCE: list[tuple[str, str, str]] = [
    ("data_driven",    "📊 Data-Driven DSS",              "Unggah dataset untuk analisis eksplorasi"),
    ("payoff_table",   "📋 Certainty — Payoff Table",     "Definisikan alternatif dan nilai payoff"),
    ("ev_eol",         "🎲 Risk — EV & EOL",              "Hitung Expected Value dan EOL"),
    ("uncertainty",    "❓ Uncertainty — Kriteria",        "Bandingkan empat kriteria ketidakpastian"),
    ("distribution",   "📈 Probabilistic — Distribusi",   "Estimasi distribusi probabilitas"),
    ("utility",        "⚖️ Utility — Fungsi Utilitas",    "Petakan preferensi risiko"),
    ("monte_carlo",    "🎰 Simulation — Monte Carlo",     "Jalankan simulasi stokastik"),
    ("recommendation", "🏆 Recommendation Engine",        "Lihat rekomendasi konsensus"),
]

_MODULE_KEYS = [m[0] for m in _MODULE_SEQUENCE]


def next_module_hint(current_key: str) -> None:
    """
    Show a subtle hint card pointing to the next logical module.

    Parameters
    ----------
    current_key : Key of the currently active module
    """
    try:
        idx = _MODULE_KEYS.index(current_key)
    except ValueError:
        return

    if idx >= len(_MODULE_SEQUENCE) - 1:
        # Last module — show completion message
        st.success(
            "🎉 **Semua modul tersedia telah Anda jelajahi!** "
            "Buka **🏆 Recommendation Engine** untuk melihat rekomendasi konsensus.",
            icon="✅",
        )
        return

    next_key, next_label, next_desc = _MODULE_SEQUENCE[idx + 1]

    st.markdown(
        f"""
        <div class="dss-card" style="
            border-left: 4px solid {COLORS['info']};
            background: linear-gradient(135deg, #f0f8ff 0%, #ffffff 100%);
        ">
            <p style="color: #5a7a8a; font-size: 0.78rem; font-weight: 600;
                      text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 0.4rem 0;">
                ➡️ Langkah Berikutnya
            </p>
            <p style="color: {COLORS['primary']}; font-size: 1rem; font-weight: 700; margin: 0 0 0.2rem 0;">
                {next_label}
            </p>
            <p style="color: #7f8c8d; font-size: 0.85rem; margin: 0;">
                {next_desc}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        f"Lanjut ke {next_label} →",
        key=f"next_module_hint_{current_key}",
        type="secondary",
    ):
        st.session_state["active_module"] = next_key
        st.rerun()


# ---------------------------------------------------------------------------
# Prerequisite warning card
# ---------------------------------------------------------------------------

def prerequisite_warning(missing_modules: list[str]) -> None:
    """
    Show a styled warning card listing missing prerequisite modules.

    Parameters
    ----------
    missing_modules : List of human-readable module names that are missing
    """
    items = "\n".join(f"- {m}" for m in missing_modules)
    st.markdown(
        f"""
        <div class="dss-card" style="border-left: 4px solid {COLORS['warning']};">
            <p style="color: {COLORS['warning']}; font-weight: 700; margin: 0 0 0.5rem 0;">
                ⚠️ Prasyarat Belum Terpenuhi
            </p>
            <p style="color: {COLORS['dark_text']}; font-size: 0.9rem; margin: 0;">
                Modul berikut perlu diselesaikan terlebih dahulu:
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for m in missing_modules:
        st.markdown(f"  - {m}")
