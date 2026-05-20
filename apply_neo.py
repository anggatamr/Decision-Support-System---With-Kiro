import os

neobrutalism_css = '''"""
ui/styles.py — Neobrutalism Gen-Z Edition
"""

import streamlit as st

COLORS: dict[str, str] = {
    "primary":       "#000000",
    "accent":        "#c1ff72",   # Lime Green
    "accent2":       "#ff66c4",   # Hot Pink
    "success":       "#c1ff72",
    "warning":       "#ffde59",   # Yellow
    "danger":        "#ff5757",   # Red
    "info":          "#5ce1e6",   # Cyan
    "background":    "#f4f4f0",   # Light Gray/Beige
    "surface":       "#ffffff",   # White
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
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stApp {{
        font-family: 'Space Grotesk', sans-serif !important;
        color: #000 !important;
    }}

    .stApp {{
        background: {{COLORS["background"]}} !important;
        background-image: radial-gradient(#000 1px, transparent 1px) !important;
        background-size: 20px 20px !important;
    }}

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
        background: {{COLORS["accent"]}} !important;
        display: inline-block !important;
        padding: 0.5rem 1rem !important;
        box-shadow: 4px 4px 0px #000 !important;
        margin-bottom: 1.5rem !important;
    }}

    p, li, span, label, div {{
        font-family: 'Space Grotesk', sans-serif !important;
    }}

    .stMarkdown p, [data-testid="stMarkdownContainer"] p {{
        color: #000 !important;
        font-weight: 500 !important;
    }}

    /* SIDEBAR */
    section[data-testid="stSidebar"] {{
        background-color: {{COLORS["sidebar_bg"]}} !important;
        border-right: 4px solid #000 !important;
    }}

    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span:not([data-baseweb]),
    section[data-testid="stSidebar"] small {{
        color: #000 !important;
        font-weight: 700 !important;
    }}

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
        background-color: {{COLORS["accent2"]}} !important;
        transform: translate(2px, 2px) !important;
        box-shadow: 2px 2px 0px #000 !important;
    }}

    section[data-testid="stSidebar"] button[kind="primary"] {{
        background-color: {{COLORS["info"]}} !important;
    }}

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
    section[data-testid="stSidebar"] [data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-baseweb="select"] span {{
        color: #000 !important;
    }}

    /* MAIN PANEL BUTTONS */
    .stButton > button {{
        background-color: {{COLORS["info"]}} !important;
        color: #000 !important;
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        box-shadow: 5px 5px 0px #000 !important;
        transition: all 0.1s ease !important;
    }}
    .stButton > button:hover {{
        background-color: {{COLORS["accent2"]}} !important;
        transform: translate(2px, 2px) !important;
        box-shadow: 3px 3px 0px #000 !important;
    }}

    /* METRIC CARDS */
    [data-testid="stMetric"] {{
        background-color: {{COLORS["warning"]}} !important;
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        padding: 1rem 1.2rem !important;
        box-shadow: 5px 5px 0px #000 !important;
    }}
    [data-testid="stMetricLabel"] p {{
        color: #000 !important;
        font-weight: 700 !important;
    }}
    [data-testid="stMetricValue"] {{
        color: #000 !important;
    }}

    /* CALLOUT BOXES */
    .stAlert {{
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        box-shadow: 5px 5px 0px #000 !important;
    }}
    [data-testid="stAlert"][data-alert-level="success"] {{ background-color: {{COLORS["success"]}} !important; }}
    [data-testid="stAlert"][data-alert-level="info"] {{ background-color: {{COLORS["info"]}} !important; }}
    [data-testid="stAlert"][data-alert-level="warning"] {{ background-color: {{COLORS["warning"]}} !important; }}
    [data-testid="stAlert"][data-alert-level="error"] {{ background-color: {{COLORS["danger"]}} !important; }}

    /* EXPANDER */
    [data-testid="stExpander"] {{
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        box-shadow: 5px 5px 0px #000 !important;
    }}
    .streamlit-expanderHeader {{
        background-color: {{COLORS["accent"]}} !important;
        border-bottom: 3px solid #000 !important;
    }}
    .streamlit-expanderHeader p {{
        color: #000 !important;
        font-weight: 700 !important;
    }}

    /* INPUT WIDGETS */
    .stTextInput input, .stNumberInput input, .stTextArea textarea,
    .stSelectbox > div > div, [data-baseweb="select"] > div {{
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        color: #000 !important;
        background-color: #fff !important;
        box-shadow: 3px 3px 0px #000 !important;
        font-weight: 600 !important;
    }}
    .stTextInput label p, .stNumberInput label p, .stSelectbox label p,
    .stTextArea label p, .stRadio label p, .stCheckbox label p {{
        color: #000 !important;
        font-weight: 700 !important;
    }}

    /* DATAFRAME */
    .stDataFrame {{
        border: 3px solid #000 !important;
        border-radius: 0px !important;
        box-shadow: 6px 6px 0px #000 !important;
    }}

    /* PLOTLY */
    .stPlotlyChart {{
        border: 4px solid #000 !important;
        border-radius: 0px !important;
        box-shadow: 8px 8px 0px #000 !important;
    }}

    /* DSS CARD */
    .dss-card {{
        background-color: #fff !important;
        border-radius: 0px !important;
        padding: 1.3rem 1.4rem !important;
        box-shadow: 5px 5px 0px #000 !important;
        border: 3px solid #000 !important;
        margin-bottom: 1rem !important;
    }}
    .dss-card p, .dss-card span {{
        color: #000 !important;
    }}

    /* DSS BADGE */
    .dss-badge {{
        display: inline-block !important;
        padding: 0.2rem 0.7rem !important;
        border: 2px solid #000 !important;
        border-radius: 0px !important;
        box-shadow: 2px 2px 0px #000 !important;
        font-weight: 700 !important;
        color: #000 !important;
        text-transform: uppercase !important;
    }}
    .dss-badge-success {{ background-color: {{COLORS["success"]}} !important; }}
    .dss-badge-info {{ background-color: {{COLORS["info"]}} !important; }}
    .dss-badge-warning {{ background-color: {{COLORS["warning"]}} !important; }}
    .dss-badge-gray {{ background-color: #e0e0e0 !important; }}

    hr {{
        border-top: 4px solid #000 !important;
        margin: 2rem 0 !important;
    }}
    
    [data-testid="stFileUploaderDropzone"] {{
        background-color: {{COLORS["accent"]}} !important;
        border: 3px dashed #000 !important;
        border-radius: 0px !important;
        box-shadow: 5px 5px 0px #000 !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
'''

with open('ui/styles.py', 'w', encoding='utf-8') as f:
    f.write(neobrutalism_css)

# Update app.py hero section inline styles
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

import re

# We will just replace the specific hero card style block
hero_old = """        <div style="
            background: linear-gradient(135deg, {COLORS['primary']} 0%, #0F2347 100%);
            border-radius: 16px;
            padding: 2.5rem 2.2rem;
            margin-bottom: 1.6rem;
            border: 1px solid rgba(37,99,235,0.20);
        ">"""

hero_new = """        <div style="
            background: {COLORS['accent2']};
            border: 4px solid #000;
            box-shadow: 8px 8px 0px #000;
            padding: 2.5rem 2.2rem;
            margin-bottom: 1.6rem;
        ">"""

app_content = app_content.replace(hero_old, hero_new)

# Also fix the subtitle colors inside the hero card
# Replace color: #FFFFFF; with color: #000; for the hero section paragraphs
# Just replace `#FFFFFF` with `#000000` or `#000` in the render_welcome_page area

app_content = app_content.replace('color: #FFFFFF;', 'color: #000;')
app_content = app_content.replace('color: #DDE6ED;', 'color: #000;')
app_content = app_content.replace('color: #8EACC2;', 'color: #000;')
# also if there's rgba
app_content = re.sub(r'color:\s*rgba\(255,\s*255,\s*255,\s*0\.85\);', 'color: #000;', app_content)
app_content = re.sub(r'color:\s*rgba\(255,\s*255,\s*255,\s*0\.9\);', 'color: #000;', app_content)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_content)

print("Applied Neobrutalism globally.")
