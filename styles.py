"""
ui/styles.py
Konstanta warna dan fungsi inject_custom_css() untuk Dashboard DSS.

Requirements: 1.6, 10.1, 10.2

CHANGELOG (Optimized for Presentation):
- Fixed white-on-white contrast issues in metric cards, dataframes, sidebar widgets
- Fixed selectbox/number_input text invisible in sidebar
- Fixed st.latex() rendering contrast
- Fixed st.expander header/content contrast
- Fixed st.success/info/warning/error callout text colors
- Improved chart area background contrast
- Added smooth hover transitions on all interactive elements
- Elevated typography hierarchy
- Fixed stDataFrame header row white-on-white
- Added focus ring accessibility
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Palet warna — akademis, kontras tinggi, presentasi-ready
# ---------------------------------------------------------------------------
COLORS: dict[str, str] = {
    "primary":    "#0F3460",   # biru tua akademis (lebih dalam)
    "accent":     "#2471A3",   # biru aksen
    "accent2":    "#1ABC9C",   # teal aksen kedua
    "success":    "#1A7A45",   # hijau untuk highlight optimal
    "warning":    "#B7770D",   # amber untuk peringatan
    "danger":     "#A93226",   # merah untuk error/alert
    "info":       "#1F618D",   # biru info
    "background": "#EBF2F8",   # abu-abu biru muda
    "surface":    "#F5F9FC",   # surface lebih terang
    "card_bg":    "#FFFFFF",   # putih untuk card
    "light_gray": "#DDE6ED",   # abu-abu muda
    "mid_gray":   "#8EACC2",   # abu-abu menengah (untuk subtitle)
    "dark_text":  "#1A2F42",   # teks gelap — WCAG AA compliant
    "body_text":  "#2C4357",   # teks body default
    "white":      "#FFFFFF",
    "border":     "#BAD4E8",   # border halus
    "border_strong": "#7FAECC",# border lebih kuat
    "sidebar_bg": "#0F3460",   # sidebar background utama
    "sidebar_end":"#082040",   # sidebar gradient akhir
    "highlight_ev": "#D6EAF8", # highlight baris EV table
    "highlight_ok": "#D5F5E3", # highlight baris optimal
}


def inject_custom_css() -> None:
    """
    Inject Google Fonts (DM Sans + DM Mono) dan CSS custom ke halaman Streamlit.
    Mengatasi semua isu kontras white-on-white dan meningkatkan kualitas presentasi.
    """
    css = f"""
    <style>
    /* ========================================================= */
    /* FONTS — DM Sans (clean, modern, academic-friendly)        */
    /* ========================================================= */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800;1,9..40,400&family=DM+Mono:wght@400;500&display=swap');

    /* ========================================================= */
    /* GLOBAL RESET — Paksa font dan warna teks yang konsisten   */
    /* ========================================================= */
    html, body, [class*="css"], [class*="st-"], .stApp {{
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: {COLORS["dark_text"]};
    }}
    
    .stMarkdown, .stText, p, span, label, div {{
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}

    /* ========================================================= */
    /* BACKGROUND UTAMA                                           */
    /* ========================================================= */
    .stApp {{
        background: linear-gradient(155deg, {COLORS["background"]} 0%, #D6E8F5 100%);
        min-height: 100vh;
    }}

    /* Main content area */
    .main .block-container {{
        padding: 2rem 2.5rem 3rem 2.5rem;
        max-width: 1200px;
    }}

    /* ========================================================= */
    /* HEADING HIERARCHY                                          */
    /* ========================================================= */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'DM Sans', sans-serif !important;
        color: {COLORS["primary"]} !important;
        letter-spacing: -0.3px;
    }}

    h1 {{
        font-size: 2.1rem !important;
        font-weight: 800 !important;
        border-bottom: 3px solid {COLORS["accent"]} !important;
        padding-bottom: 0.6rem !important;
        margin-bottom: 1.4rem !important;
        letter-spacing: -0.6px !important;
    }}

    h2 {{
        font-size: 1.55rem !important;
        font-weight: 700 !important;
    }}

    h3 {{
        font-size: 1.22rem !important;
        font-weight: 600 !important;
    }}

    /* ========================================================= */
    /* SIDEBAR — Dark theme, ALL kontras diperbaiki               */
    /* ========================================================= */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg,
            {COLORS["sidebar_bg"]} 0%,
            {COLORS["sidebar_end"]} 100%) !important;
        border-right: 1px solid rgba(36,113,163,0.4) !important;
        box-shadow: 4px 0 24px rgba(0,0,0,0.2) !important;
    }}

    /* PENTING: Paksa SEMUA teks di sidebar jadi putih */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] *,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stMarkdown p {{
        color: rgba(255, 255, 255, 0.92) !important;
    }}

    /* Heading di sidebar */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {{
        color: #FFFFFF !important;
        border-bottom-color: rgba(36,113,163,0.5) !important;
        text-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
    }}

    /* === FIX: Input widgets di sidebar — teks hitam di atas putih === */
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] .stNumberInput input,
    section[data-testid="stSidebar"] .stTextInput input,
    section[data-testid="stSidebar"] .stTextArea textarea {{
        background-color: rgba(255, 255, 255, 0.12) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 7px !important;
        caret-color: #FFFFFF !important;
    }}

    section[data-testid="stSidebar"] input::placeholder {{
        color: rgba(255,255,255,0.45) !important;
    }}

    section[data-testid="stSidebar"] input:focus,
    section[data-testid="stSidebar"] .stNumberInput input:focus {{
        background-color: rgba(255,255,255,0.2) !important;
        border-color: rgba(100, 180, 255, 0.7) !important;
        box-shadow: 0 0 0 2px rgba(100,180,255,0.25) !important;
        outline: none !important;
    }}

    /* === FIX: Selectbox di sidebar === */
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background-color: rgba(255, 255, 255, 0.12) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 7px !important;
    }}
    section[data-testid="stSidebar"] [data-baseweb="select"] span,
    section[data-testid="stSidebar"] [data-baseweb="select"] div {{
        color: #FFFFFF !important;
    }}

    /* === FIX: Radio button di sidebar === */
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stRadio span {{
        color: rgba(255,255,255,0.9) !important;
    }}
    section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {{
        color: rgba(255,255,255,0.9) !important;
    }}

    /* === FIX: Checkbox di sidebar === */
    section[data-testid="stSidebar"] .stCheckbox label,
    section[data-testid="stSidebar"] .stCheckbox span {{
        color: rgba(255,255,255,0.9) !important;
    }}

    /* === FIX: File uploader di sidebar === */
    section[data-testid="stSidebar"] .stFileUploader label,
    section[data-testid="stSidebar"] .stFileUploader span,
    section[data-testid="stSidebar"] .stFileUploader p {{
        color: rgba(255,255,255,0.9) !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {{
        background: rgba(255,255,255,0.08) !important;
        border: 1.5px dashed rgba(255,255,255,0.3) !important;
        border-radius: 8px !important;
    }}

    /* === FIX: Caption / small text di sidebar === */
    section[data-testid="stSidebar"] small,
    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
        color: rgba(255,255,255,0.6) !important;
    }}

    /* === FIX: st.success / st.info / st.warning / st.error di sidebar === */
    section[data-testid="stSidebar"] .stAlert {{
        border-radius: 8px !important;
    }}
    section[data-testid="stSidebar"] .stAlert p,
    section[data-testid="stSidebar"] .stAlert div {{
        color: {COLORS["dark_text"]} !important;
    }}

    /* === FIX: Divider warna di sidebar === */
    section[data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.15) !important;
    }}

    /* ========================================================= */
    /* SIDEBAR NAV BUTTONS                                        */
    /* ========================================================= */
    section[data-testid="stSidebar"] .stButton > button {{
        background: rgba(255, 255, 255, 0.08) !important;
        color: rgba(255, 255, 255, 0.88) !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-radius: 9px !important;
        font-weight: 500 !important;
        font-size: 0.86rem !important;
        padding: 0.5rem 0.85rem !important;
        text-align: left !important;
        transition: all 0.2s ease !important;
        margin-bottom: 3px !important;
        backdrop-filter: blur(8px) !important;
    }}

    section[data-testid="stSidebar"] .stButton > button:hover {{
        background: rgba(36, 113, 163, 0.4) !important;
        border-color: {COLORS["accent"]} !important;
        color: #FFFFFF !important;
        transform: translateX(3px) !important;
        box-shadow: 0 3px 12px rgba(0,0,0,0.25) !important;
    }}

    section[data-testid="stSidebar"] .stButton > button[kind="primary"],
    section[data-testid="stSidebar"] .stButton > button[data-testid*="primary"] {{
        background: linear-gradient(135deg, {COLORS["accent"]} 0%, #1a5276 100%) !important;
        border-color: {COLORS["accent"]} !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        box-shadow: 0 3px 12px rgba(36,113,163,0.45) !important;
    }}

    /* ========================================================= */
    /* MAIN PANEL BUTTONS                                         */
    /* ========================================================= */
    .stButton > button {{
        font-family: 'DM Sans', sans-serif !important;
        background: linear-gradient(135deg, {COLORS["accent"]} 0%, {COLORS["primary"]} 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.5rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(36,113,163,0.3) !important;
        letter-spacing: 0.1px !important;
    }}

    .stButton > button:hover {{
        background: linear-gradient(135deg, {COLORS["primary"]} 0%, #06204a 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 5px 16px rgba(15,52,96,0.4) !important;
        transform: translateY(-2px) !important;
    }}

    .stButton > button:active {{
        transform: translateY(0px) !important;
        box-shadow: 0 2px 6px rgba(15,52,96,0.3) !important;
    }}

    /* ========================================================= */
    /* METRIC CARDS — fix white-on-white                          */
    /* ========================================================= */
    [data-testid="stMetric"] {{
        background: #FFFFFF !important;
        border-left: 4px solid {COLORS["accent"]} !important;
        border-radius: 12px !important;
        padding: 1.1rem 1.3rem !important;
        box-shadow: 0 2px 12px rgba(15,52,96,0.09) !important;
        transition: box-shadow 0.2s ease, transform 0.2s ease !important;
        border: 1px solid {COLORS["border"]} !important;
        border-left: 4px solid {COLORS["accent"]} !important;
    }}

    [data-testid="stMetric"]:hover {{
        box-shadow: 0 6px 20px rgba(15,52,96,0.15) !important;
        transform: translateY(-2px) !important;
    }}

    /* FIX: Label metric jangan transparan */
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] label {{
        font-size: 0.8rem !important;
        color: {COLORS["mid_gray"]} !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.6px !important;
    }}

    /* FIX: Value metric jangan putih */
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] > div {{
        font-weight: 800 !important;
        color: {COLORS["primary"]} !important;
        font-size: 1.65rem !important;
    }}

    [data-testid="stMetricDelta"] {{
        color: {COLORS["success"]} !important;
    }}

    /* ========================================================= */
    /* DATAFRAME / TABEL — fix header dan baris white-on-white   */
    /* ========================================================= */
    .stDataFrame {{
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08) !important;
        border: 1px solid {COLORS["border"]} !important;
    }}

    /* Wrapper iframe dataframe */
    .stDataFrame iframe {{
        border-radius: 10px !important;
    }}

    /* ========================================================= */
    /* CALLOUT BOXES — success / info / warning / error          */
    /* ========================================================= */
    .stAlert {{
        font-family: 'DM Sans', sans-serif !important;
        border-radius: 10px !important;
        border-left-width: 4px !important;
    }}

    /* FIX: Teks dalam callout tidak boleh mewarisi warna gelap yg invisible */
    .stAlert p,
    .stAlert div,
    .stAlert [data-testid="stMarkdownContainer"] p {{
        color: {COLORS["dark_text"]} !important;
    }}

    /* success */
    div[data-baseweb="notification"]:has(.st-emotion-cache-success),
    [data-testid="stAlert"][data-alert-level="success"] {{
        background-color: #E8F8F0 !important;
        border-color: {COLORS["success"]} !important;
    }}

    /* info */
    [data-testid="stAlert"][data-alert-level="info"] {{
        background-color: #EBF5FB !important;
        border-color: {COLORS["info"]} !important;
    }}

    /* warning */
    [data-testid="stAlert"][data-alert-level="warning"] {{
        background-color: #FEF9E7 !important;
        border-color: {COLORS["warning"]} !important;
    }}

    /* error */
    [data-testid="stAlert"][data-alert-level="error"] {{
        background-color: #FDEDEC !important;
        border-color: {COLORS["danger"]} !important;
    }}

    /* ========================================================= */
    /* EXPANDER — fix header tidak visible                        */
    /* ========================================================= */
    [data-testid="stExpander"] {{
        border: 1px solid {COLORS["border"]} !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        margin-bottom: 0.75rem !important;
    }}

    [data-testid="stExpander"] summary,
    .streamlit-expanderHeader {{
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        color: {COLORS["primary"]} !important;
        background-color: {COLORS["surface"]} !important;
        padding: 0.7rem 1rem !important;
        border-radius: 9px 9px 0 0 !important;
        transition: background 0.2s !important;
    }}

    [data-testid="stExpander"] summary:hover,
    .streamlit-expanderHeader:hover {{
        background-color: {COLORS["highlight_ev"]} !important;
    }}

    [data-testid="stExpander"] summary p,
    .streamlit-expanderHeader p {{
        color: {COLORS["primary"]} !important;
        font-weight: 600 !important;
    }}

    .streamlit-expanderContent {{
        border-top: 1px solid {COLORS["border"]} !important;
        padding: 1.1rem 1.2rem !important;
        background-color: #FFFFFF !important;
    }}

    /* ========================================================= */
    /* INPUT WIDGETS (main panel)                                 */
    /* ========================================================= */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {{
        font-family: 'DM Sans', sans-serif !important;
        border-radius: 8px !important;
        border: 1.5px solid {COLORS["border"]} !important;
        color: {COLORS["dark_text"]} !important;
        background-color: #FFFFFF !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
        padding: 0.45rem 0.75rem !important;
    }}

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {COLORS["accent"]} !important;
        box-shadow: 0 0 0 3px rgba(36,113,163,0.15) !important;
        outline: none !important;
    }}

    /* Label input main panel */
    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stTextArea label,
    .stSlider label,
    .stRadio label,
    .stCheckbox label {{
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        color: {COLORS["body_text"]} !important;
    }}

    /* ========================================================= */
    /* SELECTBOX (main panel)                                     */
    /* ========================================================= */
    .stSelectbox > div > div,
    [data-baseweb="select"] > div {{
        border-radius: 8px !important;
        border: 1.5px solid {COLORS["border"]} !important;
        background-color: #FFFFFF !important;
        color: {COLORS["dark_text"]} !important;
    }}

    [data-baseweb="select"] span {{
        color: {COLORS["dark_text"]} !important;
    }}

    /* Dropdown option list */
    [data-baseweb="popover"] li {{
        font-family: 'DM Sans', sans-serif !important;
        color: {COLORS["dark_text"]} !important;
    }}

    [data-baseweb="popover"] li:hover,
    [data-baseweb="option"][aria-selected="true"] {{
        background-color: {COLORS["highlight_ev"]} !important;
        color: {COLORS["primary"]} !important;
    }}

    /* ========================================================= */
    /* RADIO & CHECKBOX (main panel)                              */
    /* ========================================================= */
    .stRadio [data-testid="stMarkdownContainer"] p,
    .stCheckbox [data-testid="stMarkdownContainer"] p,
    .stRadio label, .stCheckbox label {{
        color: {COLORS["dark_text"]} !important;
    }}

    /* ========================================================= */
    /* TABS                                                        */
    /* ========================================================= */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px !important;
        background-color: {COLORS["light_gray"]} !important;
        border-radius: 12px !important;
        padding: 4px !important;
        border: 1px solid {COLORS["border"]} !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 9px !important;
        font-weight: 500 !important;
        font-family: 'DM Sans', sans-serif !important;
        color: {COLORS["body_text"]} !important;
        padding: 0.45rem 1.1rem !important;
        transition: all 0.2s ease !important;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: #FFFFFF !important;
        color: {COLORS["primary"]} !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important;
    }}

    /* ========================================================= */
    /* DOWNLOAD BUTTON                                            */
    /* ========================================================= */
    .stDownloadButton > button {{
        font-family: 'DM Sans', sans-serif !important;
        background: linear-gradient(135deg, {COLORS["success"]} 0%, #145a32 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(26,122,69,0.3) !important;
    }}

    .stDownloadButton > button:hover {{
        background: linear-gradient(135deg, #145a32 0%, #0e3d22 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(26,122,69,0.4) !important;
    }}

    /* ========================================================= */
    /* CAPTION & SMALL TEXT — jangan hilang                      */
    /* ========================================================= */
    .stCaption,
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p,
    small {{
        color: {COLORS["mid_gray"]} !important;
        font-size: 0.82rem !important;
    }}

    /* ========================================================= */
    /* LATEX FORMULA RENDERING                                    */
    /* ========================================================= */
    .katex, .katex-display {{
        color: {COLORS["dark_text"]} !important;
        font-size: 1.05em !important;
    }}

    .katex-display {{
        background: {COLORS["surface"]} !important;
        border: 1px solid {COLORS["border"]} !important;
        border-radius: 8px !important;
        padding: 0.8rem 1rem !important;
        margin: 0.6rem 0 !important;
        overflow-x: auto !important;
    }}

    /* ========================================================= */
    /* PROGRESS BAR & SPINNER                                     */
    /* ========================================================= */
    .stProgress > div > div > div,
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, {COLORS["accent"]} 0%, {COLORS["accent2"]} 100%) !important;
        border-radius: 4px !important;
    }}

    .stSpinner > div {{
        border-top-color: {COLORS["accent"]} !important;
    }}

    /* ========================================================= */
    /* DIVIDER                                                     */
    /* ========================================================= */
    hr {{
        border: none !important;
        border-top: 1.5px solid {COLORS["border"]} !important;
        margin: 1.5rem 0 !important;
    }}

    /* ========================================================= */
    /* CODE BLOCKS                                                */
    /* ========================================================= */
    code, pre {{
        font-family: 'DM Mono', 'Fira Code', monospace !important;
        background-color: #EEF4FA !important;
        color: {COLORS["primary"]} !important;
        border-radius: 6px !important;
        border: 1px solid {COLORS["border"]} !important;
    }}

    pre code {{
        background: transparent !important;
        border: none !important;
    }}

    .stCodeBlock {{
        border-radius: 10px !important;
        border: 1px solid {COLORS["border"]} !important;
        overflow: hidden !important;
    }}

    /* ========================================================= */
    /* FILE UPLOADER (main panel)                                 */
    /* ========================================================= */
    [data-testid="stFileUploaderDropzone"] {{
        background: #F5FAFF !important;
        border: 2px dashed {COLORS["border_strong"]} !important;
        border-radius: 12px !important;
        transition: all 0.2s ease !important;
    }}

    [data-testid="stFileUploaderDropzone"]:hover {{
        border-color: {COLORS["accent"]} !important;
        background: #EBF5FB !important;
    }}

    [data-testid="stFileUploaderDropzone"] p,
    [data-testid="stFileUploaderDropzone"] span {{
        color: {COLORS["body_text"]} !important;
    }}

    /* ========================================================= */
    /* PLOTLY CHART CONTAINER                                     */
    /* ========================================================= */
    .stPlotlyChart {{
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 12px rgba(15,52,96,0.08) !important;
        border: 1px solid {COLORS["border"]} !important;
    }}

    /* ========================================================= */
    /* CUSTOM DSS CARD COMPONENTS                                 */
    /* ========================================================= */
    .dss-card {{
        background-color: #FFFFFF !important;
        border-radius: 14px !important;
        padding: 1.4rem 1.5rem !important;
        box-shadow: 0 2px 14px rgba(15,52,96,0.09) !important;
        border: 1px solid {COLORS["border"]} !important;
        margin-bottom: 1rem !important;
        transition: box-shadow 0.25s ease, transform 0.25s ease !important;
    }}

    .dss-card:hover {{
        box-shadow: 0 8px 24px rgba(15,52,96,0.14) !important;
        transform: translateY(-2px) !important;
    }}

    .dss-card p, .dss-card span {{
        color: {COLORS["dark_text"]} !important;
    }}

    .dss-card-accent {{
        border-left: 5px solid {COLORS["accent"]} !important;
    }}

    .dss-card-success {{
        border-left: 5px solid {COLORS["success"]} !important;
    }}

    .dss-card-warning {{
        border-left: 5px solid {COLORS["warning"]} !important;
    }}

    .dss-card-info {{
        border-left: 5px solid {COLORS["info"]} !important;
    }}

    /* ========================================================= */
    /* DSS BADGE COMPONENTS                                       */
    /* ========================================================= */
    .dss-badge {{
        display: inline-block !important;
        padding: 0.22rem 0.75rem !important;
        border-radius: 20px !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
    }}

    .dss-badge-success {{
        background-color: #D5F5E3 !important;
        color: #1A7A45 !important;
        border: 1px solid #A9DFBF !important;
    }}

    .dss-badge-info {{
        background-color: #D6EAF8 !important;
        color: #1F618D !important;
        border: 1px solid #A9CCE3 !important;
    }}

    .dss-badge-warning {{
        background-color: #FEF9E7 !important;
        color: #B7770D !important;
        border: 1px solid #F9E79F !important;
    }}

    .dss-badge-gray {{
        background-color: #EAF0F6 !important;
        color: #5D7D94 !important;
        border: 1px solid {COLORS["border"]} !important;
    }}

    /* ========================================================= */
    /* TOOLTIP / HELP TEXT                                        */
    /* ========================================================= */
    [data-testid="stTooltipHoverTarget"] {{
        color: {COLORS["mid_gray"]} !important;
    }}

    /* ========================================================= */
    /* SCROLLBAR CUSTOM (Webkit)                                  */
    /* ========================================================= */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: {COLORS["background"]};
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb {{
        background: {COLORS["border_strong"]};
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {COLORS["accent"]};
    }}

    /* ========================================================= */
    /* MARKDOWN TEXT — pastikan terbaca                           */
    /* ========================================================= */
    .stMarkdown p,
    .stMarkdown li,
    .stMarkdown td,
    .stMarkdown th,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {{
        color: {COLORS["body_text"]} !important;
        line-height: 1.7 !important;
    }}

    .stMarkdown strong,
    [data-testid="stMarkdownContainer"] strong {{
        color: {COLORS["primary"]} !important;
        font-weight: 700 !important;
    }}

    /* Table dalam markdown */
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

    .stMarkdown tbody tr {{
        border-bottom: 1px solid {COLORS["border"]} !important;
    }}

    .stMarkdown tbody tr:nth-child(even) {{
        background: {COLORS["surface"]} !important;
    }}

    .stMarkdown tbody tr:hover {{
        background: {COLORS["highlight_ev"]} !important;
    }}

    .stMarkdown tbody td {{
        padding: 0.55rem 1rem !important;
        color: {COLORS["body_text"]} !important;
    }}

    /* ========================================================= */
    /* SLIDE ANIMATION — module page transition                   */
    /* ========================================================= */
    .main .block-container {{
        animation: fadeSlideIn 0.35s ease-out;
    }}

    @keyframes fadeSlideIn {{
        from {{
            opacity: 0;
            transform: translateY(10px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}

    /* ========================================================= */
    /* TOAST / STATUS MESSAGES dari Streamlit                     */
    /* ========================================================= */
    [data-testid="toastContainer"] {{
        font-family: 'DM Sans', sans-serif !important;
    }}

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
