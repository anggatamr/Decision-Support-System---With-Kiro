"""
ui/styles.py — Light sidebar theme. No dark-on-dark issues.
Streamlit Cloud compatible — minimal CSS overrides, maximum reliability.
"""

import streamlit as st

COLORS: dict[str, str] = {
    "primary":       "#1E3A5F",
    "accent":        "#2563EB",
    "accent2":       "#0EA5E9",
    "success":       "#16A34A",
    "warning":       "#D97706",
    "danger":        "#DC2626",
    "info":          "#0284C7",
    "background":    "#F8FAFC",
    "surface":       "#FFFFFF",
    "card_bg":       "#FFFFFF",
    "light_gray":    "#F1F5F9",
    "mid_gray":      "#64748B",
    "dark_text":     "#0F172A",
    "body_text":     "#1E293B",
    "white":         "#FFFFFF",
    "border":        "#E2E8F0",
    "border_strong": "#94A3B8",
    "sidebar_bg":    "#1E3A5F",
    "sidebar_end":   "#0F2347",
    "highlight_ev":  "#EFF6FF",
    "highlight_ok":  "#F0FDF4",
}


def inject_custom_css() -> None:
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── GLOBAL ─────────────────────────────────────────────── */
    html, body, [class*="css"], .stApp {{
        font-family: 'Inter', sans-serif !important;
    }}

    .stApp {{
        background-color: {COLORS["background"]} !important;
    }}

    .main .block-container {{
        padding: 2rem 2.5rem 3rem !important;
        max-width: 1280px !important;
    }}

    /* ── HEADINGS ────────────────────────────────────────────── */
    h1 {{
        font-size: 1.9rem !important;
        font-weight: 800 !important;
        color: {COLORS["primary"]} !important;
        border-bottom: 3px solid {COLORS["accent"]} !important;
        padding-bottom: 0.5rem !important;
        margin-bottom: 1.2rem !important;
    }}
    h2 {{
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        color: {COLORS["primary"]} !important;
    }}
    h3 {{
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: {COLORS["primary"]} !important;
    }}

    /* ── BODY TEXT ───────────────────────────────────────────── */
    p, li, span, label, div {{
        font-family: 'Inter', sans-serif !important;
    }}

    .stMarkdown p,
    [data-testid="stMarkdownContainer"] p {{
        color: {COLORS["body_text"]} !important;
        line-height: 1.7 !important;
    }}

    /* ── SIDEBAR — LIGHT THEME (avoids CSS override battles) ── */
    section[data-testid="stSidebar"] {{
        background-color: {COLORS["primary"]} !important;
    }}

    /* All text in sidebar = white */
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span:not([data-baseweb]),
    section[data-testid="stSidebar"] small {{
        color: rgba(255,255,255,0.88) !important;
    }}

    /* Sidebar buttons — FORCE white text, dark bg */
    section[data-testid="stSidebar"] button {{
        background-color: rgba(255,255,255,0.10) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.20) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        text-align: left !important;
        margin-bottom: 3px !important;
    }}

    section[data-testid="stSidebar"] button:hover {{
        background-color: rgba(37,99,235,0.50) !important;
        border-color: #60A5FA !important;
        color: #FFFFFF !important;
    }}

    section[data-testid="stSidebar"] button[kind="primary"] {{
        background-color: {COLORS["accent"]} !important;
        border-color: {COLORS["accent"]} !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }}

    /* Sidebar inputs */
    section[data-testid="stSidebar"] input {{
        background-color: rgba(255,255,255,0.12) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        border-radius: 6px !important;
        caret-color: white !important;
    }}

    section[data-testid="stSidebar"] input::placeholder {{
        color: rgba(255,255,255,0.40) !important;
    }}

    /* Sidebar selectbox */
    section[data-testid="stSidebar"] [data-baseweb="select"] > div:first-child {{
        background-color: rgba(255,255,255,0.12) !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        border-radius: 6px !important;
    }}

    section[data-testid="stSidebar"] [data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-baseweb="select"] span {{
        color: #FFFFFF !important;
    }}

    /* Sidebar radio */
    section[data-testid="stSidebar"] .stRadio label p,
    section[data-testid="stSidebar"] .stRadio span {{
        color: rgba(255,255,255,0.88) !important;
    }}

    /* Sidebar file uploader */
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {{
        background-color: rgba(255,255,255,0.08) !important;
        border: 1.5px dashed rgba(255,255,255,0.30) !important;
        border-radius: 8px !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] p,
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] span,
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small {{
        color: rgba(255,255,255,0.75) !important;
    }}

    /* Sidebar caption */
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
        color: rgba(255,255,255,0.50) !important;
    }}

    /* Sidebar hr */
    section[data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.15) !important;
    }}

    /* ── MAIN PANEL BUTTONS ──────────────────────────────────── */
    .stButton > button {{
        background-color: {COLORS["accent"]} !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: background-color 0.18s ease !important;
    }}

    .stButton > button:hover {{
        background-color: #1D4ED8 !important;
        color: #FFFFFF !important;
    }}

    /* ── METRIC CARDS ────────────────────────────────────────── */
    [data-testid="stMetric"] {{
        background-color: #FFFFFF !important;
        border-left: 4px solid {COLORS["accent"]} !important;
        border-radius: 10px !important;
        padding: 1rem 1.2rem !important;
        box-shadow: 0 1px 6px rgba(0,0,0,0.07) !important;
    }}

    [data-testid="stMetricLabel"] p {{
        color: {COLORS["mid_gray"]} !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }}

    [data-testid="stMetricValue"] {{
        color: {COLORS["primary"]} !important;
        font-weight: 800 !important;
        font-size: 1.65rem !important;
    }}

    /* ── CALLOUT BOXES ───────────────────────────────────────── */
    .stAlert {{
        border-radius: 10px !important;
    }}

    .stAlert p {{
        color: {COLORS["dark_text"]} !important;
    }}

    /* ── EXPANDER ────────────────────────────────────────────── */
    .streamlit-expanderHeader p {{
        color: {COLORS["primary"]} !important;
        font-weight: 600 !important;
    }}

    /* ── INPUT WIDGETS (main panel) ──────────────────────────── */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {{
        border-radius: 7px !important;
        border: 1.5px solid {COLORS["border"]} !important;
        color: {COLORS["dark_text"]} !important;
        background-color: #FFFFFF !important;
    }}

    .stTextInput label p,
    .stNumberInput label p,
    .stSelectbox label p,
    .stTextArea label p,
    .stRadio label p,
    .stCheckbox label p {{
        color: {COLORS["body_text"]} !important;
        font-weight: 600 !important;
    }}

    /* ── DOWNLOAD BUTTON ─────────────────────────────────────── */
    .stDownloadButton > button {{
        background-color: {COLORS["success"]} !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }}

    /* ── CAPTION ─────────────────────────────────────────────── */
    [data-testid="stCaptionContainer"] p {{
        color: {COLORS["mid_gray"]} !important;
    }}

    /* ── LATEX ───────────────────────────────────────────────── */
    .katex {{
        color: {COLORS["dark_text"]} !important;
    }}

    .katex-display {{
        background-color: #F8FAFC !important;
        border: 1px solid {COLORS["border"]} !important;
        border-radius: 8px !important;
        padding: 0.8rem 1rem !important;
        margin: 0.5rem 0 !important;
    }}

    /* ── DIVIDER ─────────────────────────────────────────────── */
    hr {{
        border: none !important;
        border-top: 1.5px solid {COLORS["border"]} !important;
        margin: 1.5rem 0 !important;
    }}

    /* ── PLOTLY CHART ────────────────────────────────────────── */
    .stPlotlyChart {{
        border-radius: 10px !important;
        border: 1px solid {COLORS["border"]} !important;
    }}

    /* ── DATAFRAME ───────────────────────────────────────────── */
    .stDataFrame {{
        border-radius: 10px !important;
        border: 1px solid {COLORS["border"]} !important;
    }}

    /* ── DSS CARD ────────────────────────────────────────────── */
    .dss-card {{
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        padding: 1.3rem 1.4rem !important;
        box-shadow: 0 1px 6px rgba(0,0,0,0.07) !important;
        border: 1px solid {COLORS["border"]} !important;
        margin-bottom: 0.9rem !important;
    }}

    .dss-card p, .dss-card span {{
        color: {COLORS["dark_text"]} !important;
    }}

    .dss-card-accent  {{ border-left: 4px solid {COLORS["accent"]}  !important; }}
    .dss-card-success {{ border-left: 4px solid {COLORS["success"]} !important; }}
    .dss-card-warning {{ border-left: 4px solid {COLORS["warning"]} !important; }}
    .dss-card-info    {{ border-left: 4px solid {COLORS["info"]}    !important; }}

    /* ── DSS BADGE ───────────────────────────────────────────── */
    .dss-badge {{
        display: inline-block !important;
        padding: 0.2rem 0.7rem !important;
        border-radius: 20px !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
    }}
    .dss-badge-success {{
        background-color: #DCFCE7 !important;
        color: #15803D !important;
    }}
    .dss-badge-info {{
        background-color: #DBEAFE !important;
        color: #1D4ED8 !important;
    }}
    .dss-badge-warning {{
        background-color: #FEF3C7 !important;
        color: #B45309 !important;
    }}
    .dss-badge-gray {{
        background-color: {COLORS["light_gray"]} !important;
        color: {COLORS["mid_gray"]} !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
