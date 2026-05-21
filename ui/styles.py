"""
ui/styles.py — Neobrutalism Gen-Z Edition (Clean Rewrite)
=========================================================
Single source of truth for all visual styling.
All color values are properly interpolated via f-strings.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Color palette — Neobrutalism high-contrast
# ---------------------------------------------------------------------------
COLORS: dict[str, str] = {
    "primary":       "#000000",
    "accent":        "#c1ff72",   # Lime Green
    "accent2":       "#ff66c4",   # Hot Pink
    "success":       "#c1ff72",
    "warning":       "#ffde59",   # Yellow
    "danger":        "#ff5757",   # Red
    "info":          "#5ce1e6",   # Cyan
    "background":    "#f4f4f0",   # Light Gray/Beige
    "surface":       "#ffffff",
    "card_bg":       "#ffffff",
    "light_gray":    "#e0e0e0",
    "mid_gray":      "#000000",
    "dark_text":     "#000000",
    "body_text":     "#000000",
    "white":         "#ffffff",
    "border":        "#000000",
    "border_strong": "#000000",
    "sidebar_bg":    "#ffde59",   # Yellow sidebar
    "sidebar_end":   "#ffde59",
    "highlight_ev":  "#c1ff72",
    "highlight_ok":  "#5ce1e6",
}


def inject_custom_css() -> None:
    """Inject Neobrutalism CSS. All COLORS refs are resolved at call time."""
    css = f"""
    <style>
    /* ============================================================ */
    /* FONT                                                          */
    /* ============================================================ */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

    /* ============================================================ */
    /* GLOBAL RESET                                                  */
    /* ============================================================ */
    html, body, [class*="css"], .stApp {{
        font-family: 'Space Grotesk', sans-serif !important;
        color: #000 !important;
    }}

    p, li, span, label, div {{
        font-family: 'Space Grotesk', sans-serif !important;
    }}

    /* ============================================================ */
    /* APP BACKGROUND                                                */
    /* ============================================================ */
    .stApp {{
        background: {COLORS["background"]} !important;
    }}

    /* ============================================================ */
    /* MAIN CONTENT CONTAINER                                        */
    /* ============================================================ */
    .main .block-container {{
        padding: 2rem 2.5rem 3rem !important;
        max-width: 1200px !important;
        background-color: #ffffff !important;
        border: 4px solid #000 !important;
        box-shadow: 8px 8px 0px #000 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 2rem !important;
        border-radius: 0px !important;
    }}

    /* ============================================================ */
    /* HEADINGS                                                      */
    /* ============================================================ */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Space Grotesk', sans-serif !important;
        color: #000 !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: -1px !important;
    }}

    h1 {{
        font-size: 2.2rem !important;
        border-bottom: 4px solid #000 !important;
        background: {COLORS["accent"]} !important;
        display: inline-block !important;
        padding: 0.5rem 1rem !important;
        box-shadow: 4px 4px 0px #000 !important;
        margin-bottom: 1.5rem !important;
    }}

    /* ============================================================ */
    /* MARKDOWN TEXT                                                  */
    /* ============================================================ */
    .stMarkdown p,
    [data-testid="stMarkdownContainer"] p {{
        color: #000 !important;
        font-weight: 500 !important;
    }}

    .stMarkdown strong,
    [data-testid="stMarkdownContainer"] strong {{
        color: #000 !important;
        font-weight: 700 !important;
    }}

    .stMarkdown li,
    [data-testid="stMarkdownContainer"] li {{
        color: #000 !important;
    }}

    /* Markdown tables */
    .stMarkdown table {{
        border-collapse: collapse !important;
        width: 100% !important;
        border: 3px solid #000 !important;
    }}
    .stMarkdown thead tr {{
        background: {COLORS["accent"]} !important;
    }}
    .stMarkdown thead th {{
        color: #000 !important;
        font-weight: 700 !important;
        padding: 0.6rem 1rem !important;
        border: 2px solid #000 !important;
    }}
    .stMarkdown tbody td {{
        padding: 0.5rem 1rem !important;
        border: 1px solid #000 !important;
        color: #000 !important;
    }}
    .stMarkdown tbody tr:nth-child(even) {{
        background: {COLORS["background"]} !important;
    }}

    /* ============================================================ */
    /* SIDEBAR                                                       */
    /* ============================================================ */
    section[data-testid="stSidebar"] {{
        background-color: {COLORS["sidebar_bg"]} !important;
        border-right: 4px solid #000 !important;
    }}

    section[data-testid="stSidebar"] *,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span:not([data-baseweb]),
    section[data-testid="stSidebar"] small {{
        color: #000 !important;
        font-weight: 700 !important;
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {{
        color: #000 !important;
    }}

    section[data-testid="stSidebar"] hr {{
        border-color: rgba(0,0,0,0.3) !important;
    }}

    /* Sidebar buttons */
    section[data-testid="stSidebar"] button {{
        background-color: #fff !important;
        color: #000 !important;
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        font-weight: 700 !important;
        box-shadow: 4px 4px 0px #000 !important;
        margin-bottom: 10px !important;
        transition: all 0.1s ease !important;
    }}
    section[data-testid="stSidebar"] button:hover {{
        background-color: {COLORS["accent2"]} !important;
        transform: translate(2px, 2px) !important;
        box-shadow: 2px 2px 0px #000 !important;
    }}
    section[data-testid="stSidebar"] button[kind="primary"] {{
        background-color: {COLORS["info"]} !important;
    }}

    /* Sidebar inputs */
    section[data-testid="stSidebar"] input {{
        background-color: #fff !important;
        color: #000 !important;
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        box-shadow: 2px 2px 0px #000 !important;
    }}
    section[data-testid="stSidebar"] [data-baseweb="select"] > div:first-child {{
        background-color: #fff !important;
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        box-shadow: 2px 2px 0px #000 !important;
    }}
    section[data-testid="stSidebar"] [data-baseweb="select"] span {{
        color: #000 !important;
    }}

    /* Sidebar alerts */
    section[data-testid="stSidebar"] .stAlert p,
    section[data-testid="stSidebar"] .stAlert div {{
        color: #000 !important;
    }}

    /* ============================================================ */
    /* MAIN PANEL BUTTONS                                            */
    /* ============================================================ */
    .stButton > button {{
        background-color: {COLORS["info"]} !important;
        color: #000 !important;
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        font-weight: 700 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        text-transform: uppercase !important;
        box-shadow: 5px 5px 0px #000 !important;
        transition: all 0.1s ease !important;
    }}
    .stButton > button:hover {{
        background-color: {COLORS["accent2"]} !important;
        transform: translate(2px, 2px) !important;
        box-shadow: 3px 3px 0px #000 !important;
        color: #000 !important;
    }}
    .stButton > button:active {{
        transform: translate(4px, 4px) !important;
        box-shadow: 1px 1px 0px #000 !important;
    }}

    /* Download button */
    .stDownloadButton > button {{
        background-color: {COLORS["accent"]} !important;
        color: #000 !important;
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        font-weight: 700 !important;
        box-shadow: 5px 5px 0px #000 !important;
        transition: all 0.1s ease !important;
    }}
    .stDownloadButton > button:hover {{
        background-color: {COLORS["accent2"]} !important;
        transform: translate(2px, 2px) !important;
        box-shadow: 3px 3px 0px #000 !important;
    }}

    /* ============================================================ */
    /* METRIC CARDS                                                  */
    /* ============================================================ */
    [data-testid="stMetric"] {{
        background-color: {COLORS["warning"]} !important;
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        padding: 1rem 1.2rem !important;
        box-shadow: 5px 5px 0px #000 !important;
        transition: all 0.1s ease !important;
    }}
    [data-testid="stMetric"]:hover {{
        transform: translate(2px, 2px) !important;
        box-shadow: 3px 3px 0px #000 !important;
    }}
    [data-testid="stMetricLabel"] p {{
        color: #000 !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        font-size: 0.8rem !important;
    }}
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] > div {{
        color: #000 !important;
        font-weight: 800 !important;
    }}
    [data-testid="stMetricDelta"] {{
        color: #000 !important;
    }}

    /* ============================================================ */
    /* CALLOUT BOXES — success / info / warning / error              */
    /* ============================================================ */
    .stAlert {{
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        box-shadow: 5px 5px 0px #000 !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }}
    .stAlert p, .stAlert div {{
        color: #000 !important;
    }}
    [data-testid="stAlert"][data-alert-level="success"] {{
        background-color: {COLORS["success"]} !important;
    }}
    [data-testid="stAlert"][data-alert-level="info"] {{
        background-color: {COLORS["info"]} !important;
    }}
    [data-testid="stAlert"][data-alert-level="warning"] {{
        background-color: {COLORS["warning"]} !important;
    }}
    [data-testid="stAlert"][data-alert-level="error"] {{
        background-color: {COLORS["danger"]} !important;
    }}

    /* ============================================================ */
    /* EXPANDER                                                      */
    /* ============================================================ */
    [data-testid="stExpander"] {{
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        box-shadow: 5px 5px 0px #000 !important;
        overflow: hidden !important;
        margin-bottom: 0.75rem !important;
    }}
    [data-testid="stExpander"] summary,
    .streamlit-expanderHeader {{
        background-color: {COLORS["accent"]} !important;
        border-bottom: 3px solid #000 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        padding: 0.7rem 1rem !important;
    }}
    [data-testid="stExpander"] summary p,
    .streamlit-expanderHeader p {{
        color: #000 !important;
        font-weight: 700 !important;
    }}
    .streamlit-expanderContent {{
        border-top: 2px solid #000 !important;
        padding: 1rem 1.2rem !important;
        background-color: #ffffff !important;
    }}

    /* ============================================================ */
    /* INPUT WIDGETS (main panel)                                     */
    /* ============================================================ */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {{
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        color: #000 !important;
        background-color: #fff !important;
        box-shadow: 3px 3px 0px #000 !important;
        font-weight: 600 !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }}
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {{
        border-color: {COLORS["accent2"]} !important;
        box-shadow: 3px 3px 0px {COLORS["accent2"]} !important;
        outline: none !important;
    }}

    /* Labels */
    .stTextInput label p, .stNumberInput label p, .stSelectbox label p,
    .stTextArea label p, .stRadio label p, .stCheckbox label p {{
        color: #000 !important;
        font-weight: 700 !important;
    }}

    /* Selectbox (main panel) */
    .stSelectbox > div > div,
    [data-baseweb="select"] > div {{
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        color: #000 !important;
        background-color: #fff !important;
        box-shadow: 3px 3px 0px #000 !important;
        font-weight: 600 !important;
    }}
    [data-baseweb="select"] span {{
        color: #000 !important;
    }}

    /* Dropdown popover */
    [data-baseweb="popover"] li {{
        font-family: 'Space Grotesk', sans-serif !important;
        color: #000 !important;
    }}
    [data-baseweb="popover"] li:hover {{
        background-color: {COLORS["accent"]} !important;
    }}

    /* Radio & Checkbox */
    .stRadio [data-testid="stMarkdownContainer"] p,
    .stCheckbox [data-testid="stMarkdownContainer"] p {{
        color: #000 !important;
    }}

    /* ============================================================ */
    /* TABS                                                          */
    /* ============================================================ */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0px !important;
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        padding: 0 !important;
        background-color: #fff !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 0px !important;
        font-weight: 700 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        color: #000 !important;
        text-transform: uppercase !important;
        padding: 0.5rem 1.2rem !important;
        border-right: 2px solid #000 !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLORS["accent"]} !important;
        color: #000 !important;
        font-weight: 800 !important;
    }}

    /* ============================================================ */
    /* DATAFRAME                                                     */
    /* ============================================================ */
    .stDataFrame {{
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        box-shadow: 6px 6px 0px #000 !important;
        overflow: hidden !important;
    }}

    /* ============================================================ */
    /* PLOTLY CHARTS                                                 */
    /* ============================================================ */
    .stPlotlyChart {{
        border: 4px solid #000 !important;
        border-radius: 0px !important;
        box-shadow: 8px 8px 0px #000 !important;
        overflow: hidden !important;
    }}

    /* ============================================================ */
    /* LATEX                                                          */
    /* ============================================================ */
    .katex, .katex-display {{
        color: #000 !important;
        font-size: 1.05em !important;
    }}
    .katex-display {{
        background: {COLORS["background"]} !important;
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        padding: 0.8rem 1rem !important;
        margin: 0.6rem 0 !important;
        box-shadow: 3px 3px 0px #000 !important;
    }}

    /* ============================================================ */
    /* DSS CARD COMPONENTS                                           */
    /* ============================================================ */
    .dss-card {{
        background-color: #fff !important;
        border-radius: 0px !important;
        padding: 1.3rem 1.4rem !important;
        box-shadow: 5px 5px 0px #000 !important;
        border: 3px solid #000 !important;
        margin-bottom: 1rem !important;
        transition: all 0.1s ease !important;
    }}
    .dss-card:hover {{
        transform: translate(2px, 2px) !important;
        box-shadow: 3px 3px 0px #000 !important;
    }}
    .dss-card p, .dss-card span {{
        color: #000 !important;
    }}

    .dss-card-accent  {{ border-left: 6px solid {COLORS["accent"]} !important; }}
    .dss-card-success  {{ border-left: 6px solid {COLORS["success"]} !important; }}
    .dss-card-warning  {{ border-left: 6px solid {COLORS["warning"]} !important; }}
    .dss-card-info     {{ border-left: 6px solid {COLORS["info"]} !important; }}

    /* ============================================================ */
    /* DSS BADGES                                                    */
    /* ============================================================ */
    .dss-badge {{
        display: inline-block !important;
        padding: 0.2rem 0.7rem !important;
        border: 2px solid #000 !important;
        border-radius: 0px !important;
        box-shadow: 2px 2px 0px #000 !important;
        font-weight: 700 !important;
        color: #000 !important;
        text-transform: uppercase !important;
        font-size: 0.78rem !important;
    }}
    .dss-badge-success {{ background-color: {COLORS["success"]} !important; }}
    .dss-badge-info    {{ background-color: {COLORS["info"]} !important; }}
    .dss-badge-warning {{ background-color: {COLORS["warning"]} !important; }}
    .dss-badge-gray    {{ background-color: #e0e0e0 !important; }}

    /* ============================================================ */
    /* DIVIDER                                                       */
    /* ============================================================ */
    hr {{
        border: none !important;
        border-top: 4px solid #000 !important;
        margin: 2rem 0 !important;
    }}

    /* ============================================================ */
    /* FILE UPLOADER                                                 */
    /* ============================================================ */
    [data-testid="stFileUploaderDropzone"] {{
        background-color: {COLORS["accent"]} !important;
        border: 3px dashed #000 !important;
        border-radius: 0px !important;
        box-shadow: 5px 5px 0px #000 !important;
    }}
    [data-testid="stFileUploaderDropzone"] p,
    [data-testid="stFileUploaderDropzone"] span {{
        color: #000 !important;
    }}

    /* ============================================================ */
    /* CAPTION / SMALL TEXT                                           */
    /* ============================================================ */
    .stCaption,
    [data-testid="stCaptionContainer"] p,
    small {{
        color: #555 !important;
        font-size: 0.82rem !important;
    }}

    /* ============================================================ */
    /* CODE BLOCKS                                                   */
    /* ============================================================ */
    code, pre {{
        font-family: 'Space Mono', monospace !important;
        background-color: {COLORS["background"]} !important;
        color: #000 !important;
        border: 2px solid #000 !important;
        border-radius: 0px !important;
    }}
    pre code {{
        background: transparent !important;
        border: none !important;
    }}
    .stCodeBlock {{
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #000 !important;
        overflow: hidden !important;
    }}

    /* ============================================================ */
    /* PROGRESS BAR & SPINNER                                        */
    /* ============================================================ */
    .stProgress > div > div > div > div {{
        background: {COLORS["accent"]} !important;
    }}
    .stSpinner > div {{
        border-top-color: {COLORS["accent2"]} !important;
    }}

    /* ============================================================ */
    /* TOOLTIP                                                       */
    /* ============================================================ */
    [data-testid="stTooltipHoverTarget"] {{
        color: #555 !important;
    }}

    /* ============================================================ */
    /* SCROLLBAR                                                     */
    /* ============================================================ */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: {COLORS["background"]};
    }}
    ::-webkit-scrollbar-thumb {{
        background: #000;
        border: 1px solid {COLORS["background"]};
    }}

    /* ============================================================ */
    /* MOBILE RESPONSIVE                                             */
    /* ============================================================ */
    @media (max-width: 768px) {{
        /* Reduce main container padding on mobile */
        .main .block-container {{
            padding: 1rem 1rem 2rem !important;
            margin-top: 0.5rem !important;
            border: 2px solid #000 !important;
            box-shadow: 4px 4px 0px #000 !important;
        }}

        /* Smaller headings on mobile */
        h1 {{
            font-size: 1.5rem !important;
            padding: 0.4rem 0.7rem !important;
        }}
        h2 {{ font-size: 1.3rem !important; }}
        h3 {{ font-size: 1.1rem !important; }}

        /* Hero section on mobile */
        div[style*="padding: 2.5rem"] {{
            padding: 1.2rem 1rem !important;
        }}

        /* Metric cards — reduce shadow on mobile */
        [data-testid="stMetric"] {{
            box-shadow: 3px 3px 0px #000 !important;
            padding: 0.7rem 0.9rem !important;
        }}

        /* Buttons — full width on mobile */
        .stButton > button {{
            width: 100% !important;
            box-shadow: 3px 3px 0px #000 !important;
        }}

        /* Charts — reduce border on mobile */
        .stPlotlyChart {{
            border: 2px solid #000 !important;
            box-shadow: 4px 4px 0px #000 !important;
        }}

        /* Expanders — reduce shadow */
        [data-testid="stExpander"] {{
            box-shadow: 3px 3px 0px #000 !important;
        }}

        /* Alerts — reduce shadow */
        .stAlert {{
            box-shadow: 3px 3px 0px #000 !important;
        }}

        /* Sidebar — full width overlay on mobile */
        section[data-testid="stSidebar"] {{
            border-right: 2px solid #000 !important;
        }}

        /* Tables — horizontal scroll on mobile */
        .stDataFrame {{
            overflow-x: auto !important;
            box-shadow: 3px 3px 0px #000 !important;
        }}

        /* Reduce font size for captions */
        .stCaption,
        [data-testid="stCaptionContainer"] p,
        small {{
            font-size: 0.75rem !important;
        }}
    }}

    @media (max-width: 480px) {{
        /* Extra small screens */
        .main .block-container {{
            padding: 0.75rem 0.75rem 1.5rem !important;
        }}

        h1 {{
            font-size: 1.2rem !important;
            letter-spacing: -0.5px !important;
        }}

        [data-testid="stMetricValue"],
        [data-testid="stMetricValue"] > div {{
            font-size: 1.2rem !important;
        }}
    }}

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
