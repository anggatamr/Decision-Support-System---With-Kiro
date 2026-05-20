"""Configuration file for DSS Dashboard

Centralized settings for all modules, styling, and behavior.
"""

# ──────────────────────────────────────────────────────────────────────────────
# MONTE CARLO SETTINGS
# ──────────────────────────────────────────────────────────────────────────────

MC_SIMULATIONS_DEFAULT = 10000
"""Default number of Monte Carlo simulations (can be overridden in UI)"""

MC_SIMULATIONS_MIN = 100
MC_SIMULATIONS_MAX = 100000


# ──────────────────────────────────────────────────────────────────────────────
# DISTRIBUTION SETTINGS
# ──────────────────────────────────────────────────────────────────────────────

SUPPORTED_DISTRIBUTIONS = [
    'normal',
    'binomial',
    'poisson',
    'beta',
    'gamma',
    'exponential',
]
"""List of supported probability distributions"""

DISTRIBUTION_DESCRIPTIONS = {
    'normal': 'Bell curve (continuous). Use for: heights, test scores, returns',
    'binomial': 'Count of successes (discrete). Use for: defects in batch, coin flips',
    'poisson': 'Count of rare events (discrete). Use for: complaints/week, crashes/month',
    'beta': 'Flexible bounded distribution (continuous). Use for: percentages, probabilities',
    'gamma': 'Right-skewed (continuous). Use for: wait times, lifetime durations',
    'exponential': 'Exponential decay (continuous). Use for: queue wait times',
}


# ──────────────────────────────────────────────────────────────────────────────
# UNCERTAINTY CRITERIA SETTINGS
# ──────────────────────────────────────────────────────────────────────────────

UNCERTAINTY_CRITERIA = ['maximax', 'maximin', 'minimax_regret', 'laplace']
"""Decision criteria for decisions under uncertainty (no probabilities)"""

CRITERIA_DESCRIPTIONS = {
    'maximax': '🚀 Optimistic — Choose best of best outcomes',
    'maximin': '🛡️  Pessimistic — Choose best of worst outcomes',
    'minimax_regret': '📉 Minimize regret — Avoid biggest mistakes',
    'laplace': '⚖️  Neutral — Assume all states equally likely',
}


# ──────────────────────────────────────────────────────────────────────────────
# COLOR SCHEME (Neobrutalism)
# ──────────────────────────────────────────────────────────────────────────────

COLORS = {
    'primary': '#00FF00',          # Lime Green
    'accent': '#FF1493',           # Hot Pink (for CTA, highlights)
    'accent2': '#00FFFF',          # Cyan (for hero sections)
    'warning': '#FFFF00',          # Bright Yellow (warnings, alerts)
    'success': '#00FF00',          # Lime Green (success states)
    'info': '#00FFFF',             # Cyan (info messages)
    'error': '#FF0000',            # Red (errors)
    'border': '#000000',           # Black (borders)
    'primary_text': '#000000',     # Black text
    'body_text': '#333333',        # Dark gray text
    'mid_gray': '#666666',         # Medium gray
    'light_gray': '#EEEEEE',       # Light gray (backgrounds)
    'white': '#FFFFFF',            # White
}

COLOR_DESCRIPTIONS = {
    'primary': 'Lime Green — Main accent, success, important data',
    'accent': 'Hot Pink — Call-to-action, highlights, warnings',
    'accent2': 'Cyan — Hero sections, primary headings',
    'warning': 'Bright Yellow — Warnings, caution states',
}


# ──────────────────────────────────────────────────────────────────────────────
# STREAMLIT PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────

PAGE_CONFIG = {
    'page_title': 'Dashboard DSS — Decision Support System',
    'page_icon': '📊',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
}


# ──────────────────────────────────────────────────────────────────────────────
# MODULE METADATA
# ──────────────────────────────────────────────────────────────────────────────

MODULES_INFO = {
    'data_driven': {
        'name': '📊 Data-Driven DSS',
        'description': 'Upload & explore datasets',
        'icon': '📊',
        'order': 1,
    },
    'payoff_table': {
        'name': '📋 Payoff Table',
        'description': 'Define decision matrix',
        'icon': '📋',
        'order': 2,
    },
    'ev_eol': {
        'name': '🎲 EV & EOL',
        'description': 'Expected Value analysis',
        'icon': '🎲',
        'order': 3,
    },
    'uncertainty': {
        'name': '❓ Uncertainty',
        'description': 'Uncertainty criteria (Maximax, Maximin, etc.)',
        'icon': '❓',
        'order': 4,
    },
    'distribution': {
        'name': '📈 Distribution',
        'description': 'Fit & visualize probability distributions',
        'icon': '📈',
        'order': 5,
    },
    'utility': {
        'name': '⚖️ Utility',
        'description': 'Risk preference modeling',
        'icon': '⚖️',
        'order': 6,
    },
    'monte_carlo': {
        'name': '🎰 Monte Carlo',
        'description': 'Stochastic simulations',
        'icon': '🎰',
        'order': 7,
    },
    'recommendation': {
        'name': '🏆 Recommendation',
        'description': 'Consensus across methods',
        'icon': '🏆',
        'order': 8,
    },
}


# ──────────────────────────────────────────────────────────────────────────────
# INPUT VALIDATION THRESHOLDS
# ──────────────────────────────────────────────────────────────────────────────

VALIDATION = {
    'max_alternatives': 20,
    'max_states': 20,
    'min_alternatives': 2,
    'min_states': 2,
    'probability_tolerance': 0.01,  # Probabilities sum to 1 ± this tolerance
    'min_payoff': -1_000_000,
    'max_payoff': 1_000_000,
    'max_csv_rows': 100_000,
}


# ──────────────────────────────────────────────────────────────────────────────
# VISUALIZATION SETTINGS
# ──────────────────────────────────────────────────────────────────────────────

PLOTLY_TEMPLATE = 'plotly_white'
"""Plotly theme for all charts"""

CHART_HEIGHT = 450
"""Default height for charts (pixels)"""

CHART_FONT_SIZE = 12
"""Default font size for chart text"""


# ──────────────────────────────────────────────────────────────────────────────
# LATEX & FORMULA SETTINGS
# ──────────────────────────────────────────────────────────────────────────────

SHOW_FORMULAS = True
"""Display LaTeX formulas for mathematical rigor"""

FORMULA_SIZE = 'normal'
"""Font size for LaTeX: 'small', 'normal', 'large'"""


# ──────────────────────────────────────────────────────────────────────────────
# TESTING & LOGGING
# ──────────────────────────────────────────────────────────────────────────────

LOGGING_ENABLED = False
"""Enable debug logging (set True for troubleshooting)"""

LOG_LEVEL = 'INFO'  # 'DEBUG', 'INFO', 'WARNING', 'ERROR'
"""Logging verbosity level"""

TEST_MODE = False
"""If True, use reduced datasets for testing"""


# ──────────────────────────────────────────────────────────────────────────────
# PRESENTATION MODE
# ──────────────────────────────────────────────────────────────────────────────

PRESENTATION_MODE = False
"""If True, emphasize UI/UX over warnings; hide technical errors"""

PRESENTATION_DEFAULTS = {
    'show_formulas': True,
    'detailed_explanations': True,
    'show_uncertainty_warning': True,
    'demo_mode_available': True,
}


# ──────────────────────────────────────────────────────────────────────────────
# EXAMPLE FILES
# ──────────────────────────────────────────────────────────────────────────────

EXAMPLE_FILES = {
    'dataset': 'example_dataset.csv',
    'payoff': 'example_payoff.csv',
}


# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE DEFAULTS
# ──────────────────────────────────────────────────────────────────────────────

SESSION_STATE_DEFAULTS = {
    'df': None,
    'df_filename': None,
    'payoff_matrix': None,
    'alt_names': [],
    'state_names': [],
    'probabilities': None,
    'ev_results': None,
    'eol_results': None,
    'uncertainty_results': None,
    'dist_type': None,
    'dist_params': None,
    'utility_params': None,
    'utility_func_type': None,
    'mc_results': None,
    'mc_input_matrix': None,
    'active_module': None,
    'completed_modules': set(),
}


# ──────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTION TYPES
# ──────────────────────────────────────────────────────────────────────────────

UTILITY_FUNCTIONS = {
    'risk_averse': 'U(x) = ln(x)',
    'risk_neutral': 'U(x) = x',
    'risk_seeking': 'U(x) = x^2',
}

UTILITY_DESCRIPTIONS = {
    'risk_averse': '🛡️  Diminishing returns — Each extra dollar brings less happiness',
    'risk_neutral': '⚖️  Linear — Each dollar is equally valuable',
    'risk_seeking': '🚀 Increasing returns — Each extra dollar brings more excitement',
}


if __name__ == '__main__':
    print("Configuration loaded.")
    print(f"Supported distributions: {', '.join(SUPPORTED_DISTRIBUTIONS)}")
    print(f"Primary color: {COLORS['primary']}")
    print(f"Modules: {len(MODULES_INFO)}")
