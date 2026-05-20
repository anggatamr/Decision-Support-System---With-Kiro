# 🚀 Quick Start Guide — Set Up & Run DSS Dashboard

**Get the dashboard running in 3 minutes**

---

## Prerequisites

- 🐍 **Python 3.9+** ([Download](https://www.python.org/downloads/))
- 📁 **Git** (to clone repo) — optional, can download ZIP
- 💻 **Any operating system** (Windows, Mac, Linux)

---

## 1️⃣ Installation

### Option A: Using Git (Recommended)

```bash
# Clone the repository
git clone https://github.com/anggatamr/Decision-Support-System---With-Kiro.git
cd Decision-Support-System---With-Kiro

# Install dependencies
pip install -r requirements.txt
```

### Option B: Download ZIP

1. Go to: https://github.com/anggatamr/Decision-Support-System---With-Kiro
2. Click **Code** → **Download ZIP**
3. Unzip the folder
4. Open terminal/command prompt in the folder
5. Run: `pip install -r requirements.txt`

---

## 2️⃣ Launch the Dashboard

```bash
streamlit run app.py
```

✅ **Success!** The dashboard opens in your browser at `http://localhost:8501`

---

## 3️⃣ Explore the Dashboard

### Welcome Page
- **4 Info Cards** — Shows module count, test count, technologies
- **Module Map** — Visual overview of all 8 modules
- **Quick Start** — Recommended usage flow
- **Two CTA buttons:**
  - 🚀 "Start — Create Payoff Table"
  - 📊 "Explore Data First"

### Sidebar Navigation
- Select any module to jump directly to it
- 🟢 Green dot = module completed
- ⚪ White = not yet visited

---

## 📊 Demo Workflow (5 minutes)

### Step 1: Data Exploration (1 min)

1. Click **📊 Data-Driven DSS**
2. Upload `example_dataset.csv`
3. See:
   - Descriptive statistics (mean, std, min, max)
   - Distribution histograms
   - Correlation heatmap

### Step 2: Build Decision Matrix (1 min)

1. Click **📋 Payoff Table**
2. Load `example_payoff.csv` OR manually enter:
   - **Alternatives:** Strategy A, Strategy B, Strategy C
   - **States:** Market Boom, Stable, Recession
   - **Payoffs:** Example matrix values

### Step 3: Analyze Under Risk (1 min)

1. Click **🎲 EV & EOL**
2. Enter probabilities: e.g., [0.4, 0.35, 0.25]
3. See:
   - Expected Value for each alternative
   - Expected Opportunity Loss
   - EVPI (value of perfect information)

### Step 4: Analyze Under Uncertainty (1 min)

1. Click **❓ Uncertainty**
2. See:
   - Maximax winner (optimistic)
   - Maximin winner (pessimistic)
   - Laplace winner (neutral)
   - Minimax Regret winner

### Step 5: Get Final Recommendation (1 min)

1. Click **🏆 Recommendation Engine**
2. See consensus vote from all methods
3. Insights on agreement/disagreement

---

## 📁 Project Structure

```
Decision-Support-System---With-Kiro/
├── app.py                      # Main entry point
├── requirements.txt            # Python dependencies
├── README.md                   # Project overview
├── QUICK_START.md              # This file
├── PRESENTATION_GUIDE.md       # Presentation tips
├── GLOSSARY.md                 # Technical terms
├── config.py                   # Configuration settings
├── example_dataset.csv         # Sample data for Data-Driven DSS
├── example_payoff.csv          # Sample payoff matrix
│
├── modules/                    # Decision analysis modules
│   ├── data_driven.py         # 📊 Data exploration
│   ├── payoff_table.py        # 📋 Decision matrix builder
│   ├── ev_eol.py              # 🎲 Expected Value analysis
│   ├── uncertainty.py         # ❓ Uncertainty criteria
│   ├── distribution.py        # 📈 Distribution fitting
│   ├── utility.py             # ⚖️  Utility functions
│   ├── monte_carlo.py         # 🎰 Stochastic simulation
│   └── recommendation_engine.py # 🏆 Consensus aggregation
│
├── ui/                         # User interface components
│   ├── styles.py              # CSS/color definitions
│   ├── sidebar.py             # Navigation sidebar
│   └── components.py          # Reusable UI widgets
│
├── utils/                      # Helper functions
│   ├── calculations.py        # Mathematical functions
│   └── validators.py          # Input validation
│
└── tests/                      # Unit & property-based tests
    ├── test_calculations.py   # Math function tests
    ├── test_distributions.py  # Distribution tests
    └── test_integration.py    # End-to-end tests
```

---

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Number of Monte Carlo simulations
MC_SIMULATIONS = 10000

# UI Color scheme
COLORS = {
    'primary': '#00FF00',      # Lime Green
    'accent': '#FF1493',       # Hot Pink
    'accent2': '#00FFFF',      # Cyan
    'warning': '#FFFF00',      # Bright Yellow
}

# Distribution types supported
DISTRIBUTIONS = ['normal', 'binomial', 'poisson', 'beta', 'gamma', 'exponential']
```

---

## 🔧 Troubleshooting

### Problem: `ModuleNotFoundError: No module named 'streamlit'`

**Solution:**
```bash
pip install streamlit pandas numpy scipy plotly
```

---

### Problem: Port 8501 already in use

**Solution:**
```bash
streamlit run app.py --server.port 8502
```

---

### Problem: CSV file upload fails

**Solution:**
1. Ensure CSV has headers in first row
2. Use `example_dataset.csv` as a template
3. No special characters in column names
4. Save as **UTF-8 encoding** (not Excel's default)

---

### Problem: Dashboard runs slowly

**Solution:**
1. Reduce Monte Carlo simulations: Edit `config.py` set `MC_SIMULATIONS = 1000`
2. Close other applications
3. For large datasets (>100k rows), use data sampling first

---

### Problem: "Module X not found" error

**Solution:**
1. Verify all files exist in `/modules/` folder
2. Check file names match exactly (case-sensitive)
3. Run from root directory: `cd Decision-Support-System---With-Kiro`
4. Restart Streamlit: `Ctrl+C` then `streamlit run app.py`

---

## 📚 Example CSV Formats

### Data-Driven DSS: `example_dataset.csv`

```csv
Metric,Q1,Q2,Q3,Q4
Revenue,100000,120000,150000,180000
Expense,60000,65000,70000,80000
Profit,40000,55000,80000,100000
```

### Payoff Table: `example_payoff.csv`

```csv
Alternative,Market Boom,Stable,Recession
Strategy A,500000,250000,-100000
Strategy B,300000,300000,100000
Strategy C,200000,200000,200000
```

---

## 🧪 Run Tests

```bash
# Install pytest if not already installed
pip install pytest

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_calculations.py -v

# Run with coverage report
pytest tests/ --cov=modules --cov=utils
```

Expected: **All tests pass** ✅

---

## 📖 Learn More

- **Presentation Guide:** `PRESENTATION_GUIDE.md` — Talking points for your presentation
- **Glossary:** `GLOSSARY.md` — Definitions of technical terms
- **User Guide:** `dss_guide.md` — Detailed walkthrough of each module
- **GitHub:** https://github.com/anggatamr/Decision-Support-System---With-Kiro

---

## 💡 Tips for Presentation

1. **Pre-load data** — Have `example_dataset.csv` and `example_payoff.csv` ready
2. **Test before presenting** — Run the dashboard 10 minutes before your talk
3. **Network independence** — This runs offline; presentation works even with no internet
4. **Zoom-friendly** — Increase browser zoom (Ctrl+Plus on Windows, Cmd+Plus on Mac) for better visibility
5. **Backup plan** — Have screenshots ready in case of technical issues

---

**Ready to present? Good luck! 🚀**
