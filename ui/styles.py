"""
ui/styles.py
Konstanta warna dan fungsi inject_custom_css() untuk Dashboard DSS.

Requirements: 1.6, 10.1, 10.2
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Palet warna akademis yang konsisten di seluruh aplikasi
# ---------------------------------------------------------------------------
COLORS: dict[str, str] = {
    "primary":    "#1B4F72",  # biru tua akademis
    "accent":     "#2E86C1",  # biru aksen
    "success":    "#1E8449",  # hijau untuk highlight optimal
    "warning":    "#D4AC0D",  # kuning untuk peringatan
    "danger":     "#C0392B",  # merah untuk error/alert
    "info":       "#3498DB",  # biru info
    "background": "#F0F4F8",  # abu-abu biru muda
    "card_bg":    "#FFFFFF",  # putih untuk card
    "light_gray": "#ECF0F1",  # abu-abu muda
    "dark_text":  "#2C3E50",  # teks gelap
    "white":      "#FFFFFF",
    "border":     "#D5E8F3",  # border halus
}


def inject_custom_css() -> None:
    """
    Inject Google Fonts (Inter) dan CSS custom ke halaman Streamlit
    via st.markdown() dengan unsafe_allow_html=True.
    """
    css = f"""
    <style>
    /* ------------------------------------------------------------------ */
    /* Google Fonts — Inter                                                 */
    /* ------------------------------------------------------------------ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ------------------------------------------------------------------ */
    /* Reset font ke Inter untuk seluruh halaman                           */
    /* ------------------------------------------------------------------ */
    html, body, [class*="css"], [class*="st-"], .stApp {{
        font-family: 'Inter', sans-serif !important;
    }}

    /* ------------------------------------------------------------------ */
    /* Latar belakang utama                                                 */
    /* ------------------------------------------------------------------ */
    .stApp {{
        background-color: {COLORS["background"]};
    }}

    /* ------------------------------------------------------------------ */
    /* Heading                                                              */
    /* ------------------------------------------------------------------ */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Inter', sans-serif !important;
        color: {COLORS["primary"]};
        font-weight: 600;
    }}

    h1 {{
        font-size: 2rem;
        font-weight: 800;
        border-bottom: 3px solid {COLORS["accent"]};
        padding-bottom: 0.5rem;
        margin-bottom: 1.2rem;
        letter-spacing: -0.5px;
    }}

    h2 {{
        font-size: 1.5rem;
        font-weight: 700;
    }}

    h3 {{
        font-size: 1.2rem;
        font-weight: 600;
    }}

    /* ------------------------------------------------------------------ */
    /* Sidebar — dark navy theme                                            */
    /* ------------------------------------------------------------------ */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS["primary"]} 0%, #0d2d45 100%);
        border-right: 1px solid {COLORS["accent"]}44;
    }}

    section[data-testid="stSidebar"] * {{
        font-family: 'Inter', sans-serif !important;
        color: {COLORS["white"]} !important;
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: {COLORS["white"]} !important;
        border-bottom-color: {COLORS["accent"]}88 !important;
    }}

    /* Sidebar progress bar */
    section[data-testid="stSidebar"] .stProgress > div > div {{
        background-color: {COLORS["accent"]};
    }}

    /* ------------------------------------------------------------------ */
    /* Tombol navigasi sidebar                                              */
    /* ------------------------------------------------------------------ */
    section[data-testid="stSidebar"] .stButton > button {{
        background-color: rgba(255,255,255,0.08);
        color: {COLORS["white"]} !important;
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.88rem;
        padding: 0.5rem 0.8rem;
        text-align: left;
        transition: all 0.2s ease;
        margin-bottom: 2px;
    }}

    section[data-testid="stSidebar"] .stButton > button:hover {{
        background-color: rgba(46,134,193,0.35);
        border-color: {COLORS["accent"]};
        transform: translateX(2px);
    }}

    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
        background-color: {COLORS["accent"]};
        border-color: {COLORS["accent"]};
        font-weight: 700;
        box-shadow: 0 2px 8px rgba(46,134,193,0.4);
    }}

    /* ------------------------------------------------------------------ */
    /* Tombol utama (main panel)                                            */
    /* ------------------------------------------------------------------ */
    .stButton > button {{
        font-family: 'Inter', sans-serif !important;
        background-color: {COLORS["accent"]};
        color: {COLORS["white"]};
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.4rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 6px rgba(46,134,193,0.25);
    }}

    .stButton > button:hover {{
        background-color: {COLORS["primary"]};
        color: {COLORS["white"]};
        box-shadow: 0 4px 12px rgba(27,79,114,0.35);
        transform: translateY(-1px);
    }}

    /* ------------------------------------------------------------------ */
    /* Metric cards — enhanced                                              */
    /* ------------------------------------------------------------------ */
    [data-testid="stMetric"] {{
        background-color: {COLORS["white"]};
        border-left: 4px solid {COLORS["accent"]};
        border-radius: 10px;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        transition: box-shadow 0.2s ease;
    }}

    [data-testid="stMetric"]:hover {{
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }}

    [data-testid="stMetricLabel"] {{
        font-family: 'Inter', sans-serif !important;
        font-size: 0.82rem;
        color: #5a7a8a !important;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    [data-testid="stMetricValue"] {{
        font-family: 'Inter', sans-serif !important;
        font-weight: 800;
        color: {COLORS["primary"]} !important;
        font-size: 1.6rem !important;
    }}

    /* ------------------------------------------------------------------ */
    /* Dataframe / tabel                                                    */
    /* ------------------------------------------------------------------ */
    .stDataFrame {{
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        border: 1px solid {COLORS["border"]};
    }}

    /* ------------------------------------------------------------------ */
    /* Info / warning / success callout boxes                              */
    /* ------------------------------------------------------------------ */
    .stAlert {{
        font-family: 'Inter', sans-serif !important;
        border-radius: 10px;
        border-left-width: 4px;
    }}

    /* ------------------------------------------------------------------ */
    /* Expander                                                             */
    /* ------------------------------------------------------------------ */
    .streamlit-expanderHeader {{
        font-family: 'Inter', sans-serif !important;
        font-weight: 600;
        color: {COLORS["primary"]};
        background-color: {COLORS["light_gray"]};
        border-radius: 8px;
        padding: 0.6rem 1rem;
    }}

    .streamlit-expanderContent {{
        border: 1px solid {COLORS["border"]};
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 1rem;
        background-color: {COLORS["white"]};
    }}

    /* ------------------------------------------------------------------ */
    /* Input widgets                                                        */
    /* ------------------------------------------------------------------ */
    .stTextInput input,
    .stNumberInput input,
    .stSelectbox select,
    .stTextArea textarea {{
        font-family: 'Inter', sans-serif !important;
        border-radius: 6px;
        border: 1px solid {COLORS["border"]};
        transition: border-color 0.2s ease;
    }}

    .stTextInput input:focus,
    .stNumberInput input:focus {{
        border-color: {COLORS["accent"]};
        box-shadow: 0 0 0 2px {COLORS["accent"]}22;
    }}

    /* ------------------------------------------------------------------ */
    /* Tabs                                                                 */
    /* ------------------------------------------------------------------ */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background-color: {COLORS["light_gray"]};
        border-radius: 10px;
        padding: 4px;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        font-weight: 500;
        font-family: 'Inter', sans-serif !important;
        color: {COLORS["dark_text"]};
        padding: 0.4rem 1rem;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {COLORS["white"]};
        color: {COLORS["primary"]};
        font-weight: 700;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
    }}

    /* ------------------------------------------------------------------ */
    /* Divider                                                              */
    /* ------------------------------------------------------------------ */
    hr {{
        border-color: {COLORS["border"]};
        margin: 1.5rem 0;
    }}

    /* ------------------------------------------------------------------ */
    /* Download button                                                      */
    /* ------------------------------------------------------------------ */
    .stDownloadButton > button {{
        font-family: 'Inter', sans-serif !important;
        background-color: {COLORS["success"]};
        color: {COLORS["white"]};
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }}

    .stDownloadButton > button:hover {{
        background-color: #145a32;
        transform: translateY(-1px);
    }}

    /* ------------------------------------------------------------------ */
    /* Spinner                                                              */
    /* ------------------------------------------------------------------ */
    .stSpinner > div {{
        border-top-color: {COLORS["accent"]} !important;
    }}

    /* ------------------------------------------------------------------ */
    /* Progress bar                                                         */
    /* ------------------------------------------------------------------ */
    .stProgress > div > div > div {{
        background-color: {COLORS["accent"]};
        border-radius: 4px;
    }}

    /* ------------------------------------------------------------------ */
    /* Custom card class (used via st.markdown unsafe_allow_html)          */
    /* ------------------------------------------------------------------ */
    .dss-card {{
        background-color: {COLORS["white"]};
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid {COLORS["border"]};
        margin-bottom: 1rem;
        transition: box-shadow 0.2s ease;
    }}

    .dss-card:hover {{
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }}

    .dss-card-accent {{
        border-left: 4px solid {COLORS["accent"]};
    }}

    .dss-card-success {{
        border-left: 4px solid {COLORS["success"]};
    }}

    .dss-card-warning {{
        border-left: 4px solid {COLORS["warning"]};
    }}

    .dss-badge {{
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }}

    .dss-badge-success {{
        background-color: #d4edda;
        color: {COLORS["success"]};
    }}

    .dss-badge-info {{
        background-color: #d1ecf1;
        color: #0c5460;
    }}

    .dss-badge-warning {{
        background-color: #fff3cd;
        color: #856404;
    }}

    .dss-badge-gray {{
        background-color: {COLORS["light_gray"]};
        color: #6c757d;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
