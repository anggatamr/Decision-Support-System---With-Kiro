# 🚀 DSS Dashboard: The Gen Z Decision Support System

Welcome to the **Decision Support System (DSS) Dashboard**! A Streamlit-based web application for making complex decisions under certainty, risk, and uncertainty — wrapped in a sleek, high-contrast **Neobrutalism** aesthetic.

Made with ⚡ by **Kiro** and **Angga Tamara**.

---

## ✨ Latest Updates

### v2.0 — UI/UX & Security Improvements
- **Font consistency** — Space Grotesk applied uniformly across all components
- **Safe expression evaluator** — Monte Carlo `eval()` replaced with AST-based parser; blocks `__import__`, `exec`, `open`, and all non-math constructs
- **Mobile responsive CSS** — `@media` breakpoints for 768px and 480px screens
- **73 edge case unit tests** — equal payoffs, single alt/state, negative payoffs, large values, probability boundary, security tests
- **Bug fixes:**
  - Distribution stats: fixed `_parse_args_stats() got multiple values for 'moments'`
  - Monte Carlo CDF: fixed invalid 8-digit hex `fillcolor` for Plotly
  - Sidebar: fixed escaped quote rendering (`keyboard_double` text artifact)

---

## 🎨 Design System (Neobrutalism)
- **Typography:** Space Grotesk — consistent across all UI elements
- **Colors:** Lime Green `#c1ff72`, Hot Pink `#ff66c4`, Cyan `#5ce1e6`, Yellow `#ffde59`
- **Style:** 4px solid black borders, thick drop-shadows, zero border-radius
- **Sidebar:** Yellow background with white nav buttons and progress indicator

---

## 🛠️ The 8 Modules

| # | Module | Description |
|---|--------|-------------|
| 1 | 📊 Data-Driven DSS | Upload CSV/Excel, explore stats, trends, correlations |
| 2 | 📋 Payoff Table | Define alternatives, states of nature, and payoff values |
| 3 | 🎲 EV & EOL | Expected Value, Expected Opportunity Loss, EVPI |
| 4 | ❓ Uncertainty | Maximax, Maximin, Minimax Regret, Laplace criteria |
| 5 | 📈 Distribusi | MLE parameter estimation, PDF/PMF charts, bootstrap CI |
| 6 | ⚖️ Fungsi Utilitas | Risk preference curve fitting (averse/neutral/seeking) |
| 7 | 🎰 Monte Carlo | Stochastic simulation + Spearman sensitivity tornado chart |
| 8 | 🏆 Rekomendasi | Consensus engine aggregating all methods |

---

## 🔬 Testing

```
279 property-based tests (Hypothesis) — all passing
 73 edge case unit tests (pytest)      — all passing
```

Run tests:
```bash
pytest tests/ -v
```

---

## 📂 Example Files

- `example_dataset.csv` — sample startup metrics for Data-Driven DSS
- `example_payoff.csv` — ready-to-use payoff matrix for career decisions
- `dss_guide.md` — quick tutorial on using all 8 modules

---

## 🚀 How to Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Stay based and make good decisions. 📈✨
