"""
ui/styles.py — Clean, high-contrast theme for DSS Dashboard.
White main panel, dark navy sidebar, crisp typography.
"""

import streamlit as st

COLORS: dict[str, str] = {
    "primary":       "#1B3A6B",   # navy biru tua
    "accent":        "#2563EB",   # biru cerah
    "accent2":       "#0EA5E9",   # biru langit
    "success":       "#16A34A",   # hijau
    "warning":       "#D97706",   # amber
    "danger":        "#DC2626",   # merah
    "info":          "#0284C7",   # biru info
    "background":    "#F1F5F9",   # abu-abu sangat muda
    "surface":       "#FFFFFF",   # putih bersih
    "card_bg":       "#FFFFFF",
    "light_gray":    "#E2E8F0",
    "mid_gray":      "#64748B",
    "dark_text":     "#0F172A",   # hampir hitam
    "body_text":     "#1E293B",
    "white":         "#FFFFFF",
    "border":        "#CBD5E1",
    "border_strong": "#94A3B8",
    "sidebar_bg":    "#1B3A6B",
    "sidebar_end":   "#0F2347",
    "highlight_ev":  "#EFF6FF",
    "highlight_ok":  "#F0FDF4",
}


def inject_custom_css() -> None:
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── GLOBAL ─────────────────────────────────────────────── */
    html, body, [class*="css"], .stApp, .stMarkdown,
    p, span, label, div, li, td, th {{
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
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Inter', sans-serif !important;
        color: {COLORS["primary"]} !important;
    }}
    h1 {{
        font-size: 2rem !important;
        font-weight: 800 !important;
        border-bottom: 3px solid {COLORS["accent"]} !important;
        padding-bottom: 0.5rem !important;
        margin-bottom: 1.2rem !important;
    }}
    h2 {{ font-size: 1.45rem !important; font-weight: 700 !important; }}
    h3 {{ font-size: 1.15rem !important; font-weight: 600 !important; }}

    /* ── BODY TEXT ───────────────────────────────────────────── */
    .stMarkdown p,
    [data-testid="stMarkdownContainer"] p,
    .stMarkdown li,
    [data-testid="stMarkdownContainer"] li {{
        color: {COLORS["body_text"]} !important;
        font-size: 0.95rem !important;
        line-height: 1.7 !important;
    }}
    .stMarkdown strong,
    [data-testid="stMarkdownContainer"] strong {{
        color: {COLORS["primary"]} !important;
        font-weight: 700 !important;
    }}

    /* ── SIDEBAR ─────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg,
            {COLORS["sidebar_bg"]} 0%,
            {COLORS["sidebar_end"]} 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.08) !important;
    }}

    /* Force ALL sidebar text white */
    section[data-testid="stSidebar"] *,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] small,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        color: rgba(255,255,255,0.90) !important;
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: #FFFFFF !important;
        border-bottom-color: rgba(255,255,255,0.15) !important;
    }}

    /* Sidebar nav buttons — FULL TEXT VISIBLE */
    section[data-testid="stSidebar"] .stButton > button {{
        background: rgba(255,255,255,0.07) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.87rem !important;
        padding: 0.55rem 0.9rem !important;
        text-align: left !important;
        width: 100% !important;
        margin-bottom: 3px !important;
        transition: all 0.18s ease !important;
        white-space: normal !important;
        word-break: break-word !important;
        min-height: 42px !important;
        line-height: 1.4 !important;
    }}

    section[data-testid="stSidebar"] .stButton > button:hover {{
        background: rgba(37,99,235,0.45) !important;
        border-color: {COLORS["accent2"]} !important;
        color: #FFFFFF !important;
        transform: translateX(3px) !important;
    }}

    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, {COLORS["accent"]} 0%, #1d4ed8 100%) !important;
        border-color: {COLORS["accent"]} !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        box-shadow: 0 3px 10px rgba(37,99,235,0.4) !important;
    }}

    /* Sidebar inputs */
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] .stNumberInput input,
    section[data-testid="stSidebar"] .stTextInput input,
    section[data-testid="stSidebar"] .stTextArea textarea {{
        background: rgba(255,255,255,0.10) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.22) !important;
        border-radius: 7px !important;
        caret-color: #FFFFFF !important;
    }}
    section[data-testid="stSidebar"] input::placeholder {{
        color: rgba(255,255,255,0.40) !important;
    }}
    section[data-testid="stSidebar"] input:focus {{
        background: rgba(255,255,255,0.16) !important;
        border-color: {COLORS["accent2"]} !important;
        box-shadow: 0 0 0 2px rgba(14,165,233,0.3) !important;
    }}

    /* Sidebar selectbox */
    section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background: rgba(255,255,255,0.10) !important;
        border: 1px solid rgba(255,255,255,0.22) !important;
        border-radius: 7px !important;
    }}
    section[data-testid="stSidebar"] [data-baseweb="select"] span,
    section[data-testid="stSidebar"] [data-baseweb="select"] div {{
        color: #FFFFFF !important;
    }}

    /* Sidebar radio */
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stRadio span,
    section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {{
        color: rgba(255,255,255,0.88) !important;
    }}

    /* Sidebar file uploader */
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {{
        background: rgba(255,255,255,0.07) !important;
        border: 1.5px dashed rgba(255,255,255,0.25) !important;
        border-radius: 8px !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] p,
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] span {{
        color: rgba(255,255,255,0.75) !important;
    }}

    /* Sidebar caption */
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
    section[data-testid="stSidebar"] small {{
        color: rgba(255,255,255,0.50) !important;
    }}

    /* Sidebar alerts */
    section[data-testid="stSidebar"] .stAlert p,
    section[data-testid="stSidebar"] .stAlert div {{
        color: {COLORS["dark_text"]} !important;
    }}

    section[data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.12) !important;
    }}

    /* ── MAIN PANEL BUTTONS ──────────────────────────────────── */
    .stButton > button {{
        font-family: 'Inter', sans-serif !important;
        background: {COLORS["accent"]} !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.4rem !important;
        transition: all 0.18s ease !important;
        box-shadow: 0 2px 6px rgba(37,99,235,0.25) !important;
    }}
    .stButton > button:hover {{
        background: #1d4ed8 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(37,99,235,0.35) !important;
        transform: translateY(-1px) !important;
    }}

    /* ── METRIC CARDS ────────────────────────────────────────── */
    [data-testid="stMetric"] {{
        background: #FFFFFF !important;
        border-left: 4px solid {COLORS["accent"]} !important;
        border-radius: 10px !important;
        padding: 1rem 1.2rem !important;
        box-shadow: 0 1px 8px rgba(0,0,0,0.07) !important;
        border: 1px solid {COLORS["border"]} !important;
        border-left: 4px solid {COLORS["accent"]} !important;
    }}
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] label,
    [data-testid="stMetricLabel"] {{
        color: {COLORS["mid_gray"]} !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }}
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] > div {{
        color: {COLORS["primary"]} !important;
        font-weight: 800 !important;
        font-size: 1.7rem !important;
    }}

    /* ── DATAFRAME ───────────────────────────────────────────── */
    .stDataFrame {{
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 1px 8px rgba(0,0,0,0.07) !important;
        border: 1px solid {COLORS["border"]} !important;
    }}

    /* ── CALLOUT BOXES ───────────────────────────────────────── */
    .stAlert {{
        border-radius: 10px !important;
        border-left-width: 4px !important;
    }}
    .stAlert p,
    .stAlert div,
    .stAlert [data-testid="stMarkdownContainer"] p {{
        color: {COLORS["dark_text"]} !important;
    }}

    /* ── EXPANDER ────────────────────────────────────────────── */
    [data-testid="stExpander"] {{
        border: 1px solid {COLORS["border"]} !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        margin-bottom: 0.6rem !important;
    }}
    .streamlit-expanderHeader,
    [data-testid="stExpander"] summary {{
        font-weight: 600 !important;
        color: {COLORS["primary"]} !important;
        background: {COLORS["light_gray"]} !important;
        padding: 0.65rem 1rem !important;
    }}
    .streamlit-expanderHeader p,
    [data-testid="stExpander"] summary p {{
        color: {COLORS["primary"]} !important;
        font-weight: 600 !important;
    }}
    .streamlit-expanderContent {{
        background: #FFFFFF !important;
        padding: 1rem 1.2rem !important;
        border-top: 1px solid {COLORS["border"]} !important;
    }}

    /* ── INPUT WIDGETS (main panel) ──────────────────────────── */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {{
        border-radius: 7px !important;
        border: 1.5px solid {COLORS["border"]} !important;
        color: {COLORS["dark_text"]} !important;
        background: #FFFFFF !important;
        font-size: 0.93rem !important;
    }}
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {{
        border-color: {COLORS["accent"]} !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
    }}
    .stTextInput label, .stNumberInput label,
    .stSelectbox label, .stTextArea label,
    .stRadio label, .stCheckbox label {{
        color: {COLORS["body_text"]} !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }}

    /* ── SELECTBOX (main panel) ──────────────────────────────── */
    .stSelectbox > div > div,
    [data-baseweb="select"] > div {{
        border-radius: 7px !important;
        border: 1.5px solid {COLORS["border"]} !important;
        background: #FFFFFF !important;
    }}
    [data-baseweb="select"] span {{
        color: {COLORS["dark_text"]} !important;
    }}

    /* ── TABS ────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {{
        background: {COLORS["light_gray"]} !important;
        border-radius: 10px !important;
        padding: 4px !important;
        gap: 3px !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 7px !important;
        color: {COLORS["mid_gray"]} !important;
        font-weight: 500 !important;
        padding: 0.4rem 1rem !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: #FFFFFF !important;
        color: {COLORS["primary"]} !important;
        font-weight: 700 !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important;
    }}

    /* ── DOWNLOAD BUTTON ─────────────────────────────────────── */
    .stDownloadButton > button {{
        background: {COLORS["success"]} !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }}
    .stDownloadButton > button:hover {{
        background: #15803d !important;
        transform: translateY(-1px) !important;
    }}

    /* ── CAPTION ─────────────────────────────────────────────── */
    [data-testid="stCaptionContainer"] p,
    .stCaption, small {{
        color: {COLORS["mid_gray"]} !important;
        font-size: 0.82rem !important;
    }}

    /* ── LATEX ───────────────────────────────────────────────── */
    .katex, .katex-display {{
        color: {COLORS["dark_text"]} !important;
    }}
    .katex-display {{
        background: #F8FAFC !important;
        border: 1px solid {COLORS["border"]} !important;
        border-radius: 8px !important;
        padding: 0.8rem 1rem !important;
        margin: 0.5rem 0 !important;
    }}

    /* ── PROGRESS BAR ────────────────────────────────────────── */
    .stProgress > div > div > div,
    .stProgress > div > div > div > div {{
        background: {COLORS["accent"]} !important;
        border-radius: 4px !important;
    }}

    /* ── DIVIDER ─────────────────────────────────────────────── */
    hr {{
        border: none !important;
        border-top: 1.5px solid {COLORS["border"]} !important;
        margin: 1.5rem 0 !important;
    }}

    /* ── FILE UPLOADER (main panel) ──────────────────────────── */
    [data-testid="stFileUploaderDropzone"] {{
        background: #F8FAFC !important;
        border: 2px dashed {COLORS["border_strong"]} !important;
        border-radius: 10px !important;
    }}
    [data-testid="stFileUploaderDropzone"]:hover {{
        border-color: {COLORS["accent"]} !important;
        background: {COLORS["highlight_ev"]} !important;
    }}
    [data-testid="stFileUploaderDropzone"] p,
    [data-testid="stFileUploaderDropzone"] span {{
        color: {COLORS["body_text"]} !important;
    }}

    /* ── PLOTLY CHART ────────────────────────────────────────── */
    .stPlotlyChart {{
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 1px 8px rgba(0,0,0,0.07) !important;
        border: 1px solid {COLORS["border"]} !important;
    }}

    /* ── DSS CARD ────────────────────────────────────────────── */
    .dss-card {{
        background: #FFFFFF !important;
        border-radius: 12px !important;
        padding: 1.3rem 1.4rem !important;
        box-shadow: 0 1px 8px rgba(0,0,0,0.07) !important;
        border: 1px solid {COLORS["border"]} !important;
        margin-bottom: 0.9rem !important;
        transition: box-shadow 0.2s, transform 0.2s !important;
    }}
    .dss-card:hover {{
        box-shadow: 0 6px 20px rgba(0,0,0,0.11) !important;
        transform: translateY(-2px) !important;
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
        background: #DCFCE7 !important; color: #15803D !important;
        border: 1px solid #86EFAC !important;
    }}
    .dss-badge-info {{
        background: #DBEAFE !important; color: #1D4ED8 !important;
        border: 1px solid #93C5FD !important;
    }}
    .dss-badge-warning {{
        background: #FEF3C7 !important; color: #B45309 !important;
        border: 1px solid #FCD34D !important;
    }}
    .dss-badge-gray {{
        background: {COLORS["light_gray"]} !important; color: {COLORS["mid_gray"]} !important;
        border: 1px solid {COLORS["border"]} !important;
    }}

    /* ── MARKDOWN TABLE ──────────────────────────────────────── */
    .stMarkdown table {{
        border-collapse: collapse !important;
        width: 100% !important;
        border-radius: 8px !important;
        overflow: hidden !important;
        border: 1px solid {COLORS["border"]} !important;
    }}
    .stMarkdown thead tr {{
        background: {COLORS["primary"]} !important;
    }}
    .stMarkdown thead th {{
        color: #FFFFFF !important;
        font-weight: 600 !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.88rem !important;
    }}
    .stMarkdown tbody tr:nth-child(even) {{
        background: #F8FAFC !important;
    }}
    .stMarkdown tbody tr:hover {{
        background: {COLORS["highlight_ev"]} !important;
    }}
    .stMarkdown tbody td {{
        color: {COLORS["body_text"]} !important;
        padding: 0.5rem 1rem !important;
        border-bottom: 1px solid {COLORS["border"]} !important;
    }}

    /* ── SCROLLBAR ───────────────────────────────────────────── */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: {COLORS["background"]}; }}
    ::-webkit-scrollbar-thumb {{
        background: {COLORS["border_strong"]};
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{ background: {COLORS["accent"]}; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
