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
    "background": "#F8F9FA",  # abu-abu muda
    "white":      "#FFFFFF",
}


def inject_custom_css() -> None:
    """
    Inject Google Fonts (Inter) dan CSS custom ke halaman Streamlit
    via st.markdown() dengan unsafe_allow_html=True.

    Menerapkan:
    - Font Inter (sans-serif) ke seluruh elemen halaman
    - Warna latar belakang akademis
    - Tipografi heading yang bersih dan konsisten
    - Styling sidebar, tombol, dan komponen Streamlit lainnya
    """
    css = f"""
    <style>
    /* ------------------------------------------------------------------ */
    /* Google Fonts — Inter                                                 */
    /* ------------------------------------------------------------------ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

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
        font-weight: 700;
        border-bottom: 3px solid {COLORS["accent"]};
        padding-bottom: 0.4rem;
        margin-bottom: 1rem;
    }}

    h2 {{
        font-size: 1.5rem;
        font-weight: 600;
    }}

    h3 {{
        font-size: 1.2rem;
        font-weight: 500;
    }}

    /* ------------------------------------------------------------------ */
    /* Sidebar                                                              */
    /* ------------------------------------------------------------------ */
    section[data-testid="stSidebar"] {{
        background-color: {COLORS["primary"]};
    }}

    section[data-testid="stSidebar"] * {{
        font-family: 'Inter', sans-serif !important;
        color: {COLORS["white"]} !important;
    }}

    section[data-testid="stSidebar"] .stRadio label {{
        font-size: 0.95rem;
        padding: 0.3rem 0;
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: {COLORS["white"]} !important;
        border-bottom-color: {COLORS["accent"]} !important;
    }}

    /* ------------------------------------------------------------------ */
    /* Tombol utama                                                         */
    /* ------------------------------------------------------------------ */
    .stButton > button {{
        font-family: 'Inter', sans-serif !important;
        background-color: {COLORS["accent"]};
        color: {COLORS["white"]};
        border: none;
        border-radius: 6px;
        font-weight: 500;
        padding: 0.45rem 1.2rem;
        transition: background-color 0.2s ease;
    }}

    .stButton > button:hover {{
        background-color: {COLORS["primary"]};
        color: {COLORS["white"]};
    }}

    /* ------------------------------------------------------------------ */
    /* Metric cards                                                         */
    /* ------------------------------------------------------------------ */
    [data-testid="stMetric"] {{
        background-color: {COLORS["white"]};
        border-left: 4px solid {COLORS["accent"]};
        border-radius: 6px;
        padding: 0.75rem 1rem;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
    }}

    [data-testid="stMetricLabel"] {{
        font-family: 'Inter', sans-serif !important;
        font-size: 0.85rem;
        color: {COLORS["primary"]} !important;
        font-weight: 500;
    }}

    [data-testid="stMetricValue"] {{
        font-family: 'Inter', sans-serif !important;
        font-weight: 700;
        color: {COLORS["primary"]} !important;
    }}

    /* ------------------------------------------------------------------ */
    /* Dataframe / tabel                                                    */
    /* ------------------------------------------------------------------ */
    .stDataFrame {{
        border-radius: 6px;
        overflow: hidden;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
    }}

    /* ------------------------------------------------------------------ */
    /* Info / warning / success callout boxes                              */
    /* ------------------------------------------------------------------ */
    .stAlert {{
        font-family: 'Inter', sans-serif !important;
        border-radius: 6px;
    }}

    /* ------------------------------------------------------------------ */
    /* Expander                                                             */
    /* ------------------------------------------------------------------ */
    .streamlit-expanderHeader {{
        font-family: 'Inter', sans-serif !important;
        font-weight: 500;
        color: {COLORS["primary"]};
    }}

    /* ------------------------------------------------------------------ */
    /* Input widgets                                                        */
    /* ------------------------------------------------------------------ */
    .stTextInput input,
    .stNumberInput input,
    .stSelectbox select,
    .stTextArea textarea {{
        font-family: 'Inter', sans-serif !important;
        border-radius: 4px;
    }}

    /* ------------------------------------------------------------------ */
    /* Divider                                                              */
    /* ------------------------------------------------------------------ */
    hr {{
        border-color: {COLORS["accent"]}33;
        margin: 1.5rem 0;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
