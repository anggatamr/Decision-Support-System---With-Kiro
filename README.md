# Dashboard DSS — Decision Support System

> A modular, academically-oriented Decision Support System built with Python and Streamlit. Designed for Statistics students to present quantitative decision analysis methods in a clean, interactive interface — complete with LaTeX-rendered formulas, Plotly visualizations, and a property-based test suite.

---

## Overview

This application integrates two DSS paradigms into a single unified interface:

- **Data-Driven DSS** — upload real datasets, explore descriptive statistics, visualize trends, and inspect correlation matrices.
- **Model-Driven DSS** — six groups of quantitative Decision Theory methods, from certainty analysis through Monte Carlo simulation.

All computation is session-local. No database, no external API calls, no persistent storage — everything lives in `st.session_state` for the duration of a session.

---

## Modules

| # | Module | Method Group | Key Output |
|---|--------|-------------|------------|
| 1 | 📊 Data-Driven DSS | Descriptive Statistics | Dataset preview, trend charts, correlation heatmap |
| 2 | 📋 Certainty — Payoff Table | Decision under Certainty | Payoff matrix with column-max highlights |
| 3 | 🎲 Risk — EV & EOL | Decision under Risk | Expected Value, Expected Opportunity Loss, EVPI |
| 4 | ❓ Uncertainty — Criteria | Decision under Uncertainty | Maximax, Maximin, Minimax Regret, Laplace |
| 5 | 📈 Probabilistic — Distribution | Probability Estimation | MLE parameter estimation, PDF/PMF, 95% CI via bootstrap |
| 6 | ⚖️ Utility — Utility Function | Utility Theory | Curve fitting, Risk Preference classification, Expected Utility |
| 7 | 🎰 Simulation — Monte Carlo | Stochastic Simulation | Output distribution, CDF, Spearman sensitivity tornado chart |
| 8 | 🏆 Recommendation Engine | Consensus Analysis | Cross-method consensus, exportable report |

---

## Architecture

```
dss-dashboard-streamlit/
├── app.py                          # Entry point — routing, session state, welcome page
├── requirements.txt
├── modules/
│   ├── data_driven.py              # Module 1: file upload + descriptive stats
│   ├── payoff_table.py             # Module 2: payoff table generator
│   ├── ev_eol.py                   # Module 3: EV, EOL, EVPI
│   ├── uncertainty.py              # Module 4: Maximax, Maximin, Minimax Regret, Laplace
│   ├── distribution.py             # Module 5: probability distribution estimation
│   ├── utility.py                  # Module 6: utility function + risk preference
│   ├── monte_carlo.py              # Module 7: Monte Carlo simulation + sensitivity
│   └── recommendation_engine.py   # Module 8: consensus recommendation engine
├── ui/
│   ├── styles.py                   # inject_custom_css(), COLORS palette
│   └── sidebar.py                  # render_sidebar() → active module key
├── utils/
│   ├── validators.py               # Input validation (file, matrix, probabilities, distributions)
│   ├── formatters.py               # Number formatters (monetary, probability, stat)
│   └── recommendation.py          # collect_results(), find_consensus(), generate_report_text()
└── tests/
    ├── test_data_driven.py         # Properties 4–8
    ├── test_ev_eol.py              # Properties 12–16
    ├── test_uncertainty.py         # Properties 17–20
    ├── test_distribution.py        # Properties 21–24
    ├── test_utility.py             # Properties 26–27
    ├── test_monte_carlo.py         # Properties 29–31
    ├── test_recommendation.py      # Property 32
    ├── test_validators.py          # Properties 9, 11, 25, 28
    ├── test_formatters.py          # Property 33
    └── test_payoff_table.py        # Property 10
```

Each module follows a strict two-layer separation:

- **Computation Layer** — pure Python functions with no Streamlit dependency. Accepts NumPy arrays / pandas DataFrames, returns numerical results. Fully testable in isolation.
- **UI Layer** — `render_*()` functions that call the Streamlit API, read/write `st.session_state`, and render Plotly charts and LaTeX formulas.

---

## Correctness & Testing

The test suite uses **[Hypothesis](https://hypothesis.readthedocs.io/)** for property-based testing — each property encodes a formal correctness guarantee derived from the mathematical specification.

```
279 passed in ~2m 33s
```

Selected properties:

| Property | Guarantee |
|----------|-----------|
| **P4** | CSV round-trip preserves DataFrame shape |
| **P12** | `compute_ev(P, p)` equals `P @ p` element-wise |
| **P13** | Opportunity loss matrix is non-negative with column zeros |
| **P16** | EVPI is always ≥ 0 |
| **P17** | Maximax equals the global maximum of the payoff matrix |
| **P21** | MLE for Normal equals `(np.mean(x), np.std(x, ddof=0))` |
| **P29** | Monte Carlo output length equals iteration count |
| **P32** | Consensus finds all tied best alternatives |

Run the full suite:

```bash
pytest tests/ -v
```

With coverage:

```bash
pytest tests/ -v --cov=modules --cov=utils --cov-report=term-missing
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/anggatamr/Decision-Support-System---With-Kiro.git
cd Decision-Support-System---With-Kiro

# Create and activate a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## Usage Guide

1. **Start with Data-Driven DSS** *(optional)* — upload a CSV or XLSX file to explore your dataset. The loaded data becomes available to the Distribution module for MLE estimation.

2. **Build a Payoff Table** — define your decision alternatives and states of nature. This table is shared across modules 3, 4, and 6.

3. **Run Risk Analysis (EV & EOL)** — enter state probabilities to compute Expected Value, Expected Opportunity Loss, and EVPI.

4. **Run Uncertainty Analysis** — compare Maximax, Maximin, Minimax Regret, and Laplace criteria without probability information.

5. **Estimate a Probability Distribution** — fit Normal, Binomial, Poisson, Exponential, Uniform, or Beta distributions to your data or manual parameters.

6. **Fit a Utility Function** — input monetary–utility pairs, fit a curve, and classify the decision-maker's risk preference (Risk Averse / Neutral / Seeking).

7. **Run Monte Carlo Simulation** — define stochastic input variables, write an output expression, and simulate up to 10M iterations with Spearman sensitivity analysis.

8. **Review the Recommendation** — after running ≥2 modules, the Recommendation Engine aggregates results across all methods and reports the consensus alternative with a percentage agreement score.

> **State persistence:** data entered in any module is preserved when navigating to another module within the same session. The sidebar shows a ✅ indicator next to completed modules.

---

## Key Algorithms

### Expected Value & EOL

```
EV_i  = Σ_j  p_j · v_ij          (payoff @ probs)
OL_ij = max_k(v_kj) − v_ij
EOL_i = Σ_j  p_j · OL_ij         (ol_matrix @ probs)
EVPI  = EVwPI − EV*  ≥ 0
```

### Uncertainty Criteria

```
Maximax        = max_i ( max_j v_ij )
Maximin        = max_i ( min_j v_ij )
Minimax Regret = min_i ( max_j R_ij ),  R_ij = max_k(v_kj) − v_ij
Laplace        = max_i ( (1/n) Σ_j v_ij )
```

### Monte Carlo

```
μ̂ = (1/N) Σ_{i=1}^{N} f(X_i)
```

Expression evaluation uses a restricted namespace (`__builtins__: {}`) to prevent arbitrary code execution while allowing mathematical expressions with `np`.

---

## Tech Stack

| Library | Role |
|---------|------|
| [Streamlit](https://streamlit.io/) | Web framework & UI |
| [Pandas](https://pandas.pydata.org/) | Data manipulation |
| [NumPy](https://numpy.org/) | Numerical computation |
| [SciPy](https://scipy.org/) | Statistical distributions, curve fitting, Spearman correlation |
| [Plotly](https://plotly.com/python/) | Interactive charts |
| [openpyxl](https://openpyxl.readthedocs.io/) | XLSX file parsing |
| [Hypothesis](https://hypothesis.readthedocs.io/) | Property-based testing |
| [pytest](https://pytest.org/) | Test runner |

---

## License

This project is released for academic and educational use.

---

*Built with [Kiro](https://kiro.dev) — spec-driven development from requirements through implementation.*
