"""
ui/components.py
Reusable UI components for DSS Dashboard.

Provides:
- dashboard_card()       — styled metric/info card
- module_status_badge()  — colored status badge
- section_header()       — consistent section header with icon
- download_csv_button()  — download button for DataFrame results
- next_module_hint()     — navigation hint to next logical module
- prerequisite_warning() — prerequisite modules warning

CHANGELOG (Optimized):
- dashboard_card: fixed all text contrast, dark subtitles, icon spacing
- next_module_hint: refined color and contrast
- prerequisite_warning: improved readability
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
    color    : One of "accent", "success", "warning", "danger", "primary", "info"
    icon     : Optional emoji/icon prefix for the title
    """
    border_color_map = {
        "accent":  COLORS["accent"],
        "success": COLORS["success"],
        "warning": COLORS["warning"],
        "danger":  COLORS["danger"],
        "primary": COLORS["primary"],
        "info":    COLORS["info"],
    }
    value_color_map = {
        "accent":  COLORS["accent"],
        "success": COLORS["success"],
        "warning": COLORS["warning"],
        "danger":  COLORS["danger"],
        "primary": COLORS["primary"],
        "info":    COLORS["info"],
    }

    border_color = border_color_map.get(color, COLORS["accent"])
    value_color = value_color_map.get(color, COLORS["primary"])
    icon_prefix = f"{icon} " if icon else ""

    st.markdown(
        f"""
        <div style="
            background: #FFFFFF;
            border-left: 5px solid {border_color};
            border-radius: 14px;
            padding: 1.3rem 1.4rem;
            box-shadow: 0 2px 14px rgba(15,52,96,0.09);
            border: 1px solid {COLORS['border']};
            border-left: 5px solid {border_color};
            margin-bottom: 0.5rem;
            transition: box-shadow 0.25s ease;
        ">
            <p style="
                color: {COLORS['mid_gray']};
                font-size: 0.76rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.8px;
                margin: 0 0 0.4rem 0;
                font-family: 'DM Sans', sans-serif;
            ">{icon_prefix}{title}</p>
            <p style="
                color: {value_color};
                font-size: 1.75rem;
                font-weight: 800;
                margin: 0;
                line-height: 1.15;
                font-family: 'DM Sans', sans-serif;
                letter-spacing: -0.5px;
            ">{value}</p>
            {f'<p style="color: {COLORS["body_text"]}; font-size: 0.8rem; margin: 0.3rem 0 0 0; font-family: DM Sans, sans-serif; opacity: 0.8;">{subtitle}</p>' if subtitle else ''}
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
        "completed":   ("🟢 Selesai",  "dss-badge dss-badge-success"),
        "in_progress": ("🟡 Berjalan", "dss-badge dss-badge-warning"),
        "not_started": ("⚪ Belum",     "dss-badge dss-badge-gray"),
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
    ("data_driven",    "📊 Data-Driven DSS",            "Unggah dataset untuk analisis eksplorasi"),
    ("payoff_table",   "📋 Certainty — Payoff Table",   "Definisikan alternatif dan nilai payoff"),
    ("ev_eol",         "🎲 Risk — EV & EOL",            "Hitung Expected Value dan EOL"),
    ("uncertainty",    "❓ Uncertainty — Kriteria",      "Bandingkan empat kriteria ketidakpastian"),
    ("distribution",   "📈 Probabilistic — Distribusi", "Estimasi distribusi probabilitas"),
    ("utility",        "⚖️ Utility — Fungsi Utilitas",  "Petakan preferensi risiko"),
    ("monte_carlo",    "🎰 Simulation — Monte Carlo",   "Jalankan simulasi stokastik"),
    ("recommendation", "🏆 Recommendation Engine",      "Lihat rekomendasi konsensus"),
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
            "🎉 **Semua modul telah dijelajahi!** "
            "Lihat **🏆 Recommendation Engine** untuk rekomendasi konsensus.",
            icon="✅",
        )
        return

    next_key, next_label, next_desc = _MODULE_SEQUENCE[idx + 1]

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #EBF5FB 0%, #F8FBFE 100%);
            border-left: 5px solid {COLORS['info']};
            border-radius: 12px;
            padding: 1.1rem 1.3rem;
            border: 1px solid {COLORS['border']};
            border-left: 5px solid {COLORS['info']};
            margin-top: 0.5rem;
        ">
            <p style="
                color: {COLORS['mid_gray']};
                font-size: 0.74rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.7px;
                margin: 0 0 0.35rem 0;
                font-family: 'DM Sans', sans-serif;
            ">➡️ Langkah Berikutnya</p>
            <p style="
                color: {COLORS['primary']};
                font-size: 1rem;
                font-weight: 700;
                margin: 0 0 0.2rem 0;
                font-family: 'DM Sans', sans-serif;
            ">{next_label}</p>
            <p style="
                color: {COLORS['body_text']};
                font-size: 0.85rem;
                margin: 0;
                font-family: 'DM Sans', sans-serif;
            ">{next_desc}</p>
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
    items_html = "".join(
        f'<li style="color: {COLORS["body_text"]}; margin: 0.2rem 0;">{m}</li>'
        for m in missing_modules
    )
    st.markdown(
        f"""
        <div style="
            background: #FEF9E7;
            border-left: 5px solid {COLORS['warning']};
            border-radius: 12px;
            padding: 1.1rem 1.3rem;
            border: 1px solid #F9E79F;
            border-left: 5px solid {COLORS['warning']};
            margin-bottom: 1rem;
        ">
            <p style="
                color: {COLORS['warning']};
                font-weight: 700;
                margin: 0 0 0.5rem 0;
                font-family: 'DM Sans', sans-serif;
            ">⚠️ Prasyarat Belum Terpenuhi</p>
            <p style="
                color: {COLORS['body_text']};
                font-size: 0.9rem;
                margin: 0 0 0.4rem 0;
                font-family: 'DM Sans', sans-serif;
            ">Modul berikut perlu diselesaikan terlebih dahulu:</p>
            <ul style="margin: 0; padding-left: 1.2rem;">
                {items_html}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
