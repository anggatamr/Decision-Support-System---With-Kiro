# 🚀 DSS Dashboard: The Gen Z Decision Support System

Welcome to the **Decision Support System (DSS) Dashboard**! This project is a Streamlit-based web application designed to help you make complex decisions under certainty, risk, and uncertainty, all wrapped up in a sleek, high-contrast **Neobrutalism** aesthetic.

Made with ⚡ by **Kiro** and **Antigravity**.

## 🎨 What's New? (Neobrutalist UI Overhaul)
We completely transformed the dashboard to vibe with modern design trends:
- **Bold Aesthetics:** Space Grotesk typography, harsh black borders (`4px solid #000`), and thick drop-shadows.
- **High-Contrast Colors:** Lime Green, Hot Pink, Cyan, and Bright Yellow against a clean background for maximum readability.
- **Better UX:** Moved all input widgets from the cluttered sidebar directly into the main interface to make it accessible and intuitive.

## 🛠️ Features (The 8 Modules)
1. **Data-Driven DSS 📊:** Upload your CSV data and let the app automatically generate insights, distributions, and correlations.
2. **Payoff Table 📋:** The foundation for decision making. Map out your Alternatives against different Conditions/States of nature.
3. **EV & EOL (Risk) 🎲:** Calculate Expected Value and Expected Opportunity Loss when probabilities are known.
4. **Uncertainty ❓:** Make decisions when you have zero clue what will happen using Maximax, Maximin, and Laplace criteria.
5. **Distribution 📈:** Estimate probability distributions (Normal, Binomial, Poisson, etc.) from your data and visualize their PDF/PMF.
6. **Utility ⚖️:** Define your Risk Preference (Risk Averse, Neutral, Seeking) by fitting a curve to your Utility Function data points.
7. **Monte Carlo 🎰:** Run thousands of random simulations based on your data to predict future outcomes.
8. **Recommendation Engine 🏆:** A one-stop consensus engine that aggregates results from all methods to give you the ultimate best choice.

## 📂 Example Files
To help you get started immediately, we've included some plug-and-play example files:
- `example_dataset.csv`: A sample Gen Z startup metrics dataset for the **Data-Driven DSS**.
- `example_payoff.csv`: A ready-to-use matrix showing payoff values for different career choices under various market conditions.
- Check out `dss_guide.md` for a quick, stress-free tutorial on how to use everything!

## 🚀 How to Run Locally
Make sure you have Python installed, then run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Stay based and make good decisions. 📈✨
