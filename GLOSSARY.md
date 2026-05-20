# 📚 DSS Dashboard — Technical Glossary

**For Judges, Peers, and Anyone Learning Decision Theory**

---

## Decision Theory Fundamentals

### **Alternative (Decision Option)**
One possible choice among many. Example: "Buy product X" or "Delay purchase."
- In the dashboard: rows of the payoff matrix
- Also called: "Decision option," "Strategy," "Course of action"

### **State of Nature (Condition, Scenario)**
A future condition outside the decision-maker's control. Example: "Market booms" vs. "Recession."
- In the dashboard: columns of the payoff matrix
- The decision-maker has no control; only assigns probabilities (if known)

### **Payoff (Outcome, Consequence)**
The numerical result (profit, loss, utility) of choosing Alternative i when State j occurs.
- Example: "If we choose Strategy A AND market booms, profit = $500k"
- In the dashboard: cell values in the payoff matrix

### **Payoff Matrix (Decision Matrix, Decision Table)**
A structured table showing:
- Rows = Alternatives
- Columns = States of Nature
- Cells = Payoffs

Example:
```
                Market Boom    Stable    Recession
Strategy A        $500k        $250k     -$100k
Strategy B        $300k        $300k     +$100k
Strategy C        $200k        $200k     +$200k
```

---

## Decision Environments

### **Certainty**
- **Definition:** The decision-maker knows exactly which state of nature will occur.
- **Example:** "I will invest $100 at 5% interest. Payoff = $105 guaranteed."
- **Method used:** Deterministic evaluation (just pick the best payoff)
- **Real-world:** Rare; most decisions involve some uncertainty

### **Risk**
- **Definition:** Multiple possible states; the probability of each state is KNOWN.
- **Example:** "If I flip a fair coin, Heads = win $100, Tails = lose $50."
- **Probabilities:** P(Heads) = 0.5, P(Tails) = 0.5
- **Method used:** Expected Value, Utility theory, Monte Carlo
- **Dashboard modules:** EV & EOL, Utility, Monte Carlo

### **Uncertainty**
- **Definition:** Multiple possible states; probabilities are UNKNOWN (or unknowable).
- **Example:** "A new competitor might enter the market. I have no idea how likely."
- **No probabilities:** Make decisions without probability data
- **Method used:** Maximax, Maximin, Laplace, Minimax Regret
- **Dashboard module:** Uncertainty
- **Real-world:** Common in startups, new markets, unprecedented events

---

## Expected Value (EV)

### **Definition**
The weighted average payoff if the decision is repeated infinitely many times (or population average).

### **Formula**
```
EV(Alternative i) = Σ [Payoff_ij × P(State j)]
```

### **Example**
```
Alternative:  Strategy A
Payoffs:      $500k (Boom), $250k (Stable), -$100k (Recession)
Probabilities: 0.4,         0.35,              0.25

EV(A) = $500k(0.4) + $250k(0.35) + (-$100k)(0.25)
      = $200k + $87.5k - $25k
      = $262.5k
```

### **Interpretation**
- "On average, Strategy A yields $262.5k per decision."
- "If we make this decision 100 times, total payoff ≈ $26.25M."

### **Limitation**
- Only useful if decision is repeated many times
- Example: One-time merger decision → EV less meaningful than daily inventory ordering

---

## Expected Opportunity Loss (EOL) / Regret

### **Definition**
The average amount of money you'd regret NOT having if you made the wrong choice.

### **Formula**
```
Regret_ij = Best_payoff_in_state_j - Payoff_ij
EOL(Alternative i) = Σ [Regret_ij × P(State j)]
```

### **Example**
```
For Market Boom state (P = 0.4):
Best payoff in Boom = $500k (Strategy A)

If choose Strategy B instead:
Regret = $500k - $300k = $200k
Weighted: $200k × 0.4 = $80k
```

### **Interpretation**
- "If I choose Strategy B, I'll regret missing out on $80k on average (in Boom states)."
- **EOL criterion:** Pick the alternative with MINIMUM EOL
- Related to: "Opportunity cost" in economics

---

## Expected Value of Perfect Information (EVPI)

### **Definition**
The maximum amount you should pay for perfect information (a crystal ball) about which state will occur.

### **Formula**
```
EVPI = EV with perfect information - Best EV without information

EV with perfect info = Σ [Best payoff in state j × P(State j)]
```

### **Example**
```
Without perfect info:
Best EV = $262.5k (Strategy A)

With perfect info (you know which state occurs):
If Boom (prob 0.4): Choose best in Boom = $500k
If Stable (prob 0.35): Choose best in Stable = $300k
If Recession (prob 0.25): Choose best in Recession = $200k

EV with perfect = $500k(0.4) + $300k(0.35) + $200k(0.25) = $325k

EVPI = $325k - $262.5k = $62.5k
```

### **Interpretation**
- "Market research is worth AT MOST $62.5k. If it costs $100k, don't buy it."
- Used by: Consulting firms pricing market research studies

---

## Uncertainty Criteria (No Probability Information)

### **Maximax (Best-Case Scenario)**
- **Decision rule:** For each alternative, find its BEST possible payoff. Choose the alternative with the overall BEST payoff.
- **Formula:** `max(max_payoff_per_alternative)`
- **Psychology:** Optimistic, risk-seeking
- **Real-world:** Entrepreneurs, startup founders, inventors
- **Example:**
  ```
  Strategy A: max = $500k
  Strategy B: max = $300k
  Strategy C: max = $200k
  → Choose A (Maximax = $500k)
  ```

### **Maximin (Worst-Case Scenario)**
- **Decision rule:** For each alternative, assume the WORST possible outcome. Choose the alternative with the best worst-case.
- **Formula:** `max(min_payoff_per_alternative)`
- **Psychology:** Pessimistic, risk-averse
- **Real-world:** Banks, insurance companies, military
- **Example:**
  ```
  Strategy A: min = -$100k
  Strategy B: min = +$100k ← Best worst-case
  Strategy C: min = +$200k ← Actually the best!
  → Choose C (Maximin = $200k)
  ```
- **Also called:** "Wald's criterion," "Security level criterion"

### **Laplace (Principle of Insufficient Reason)**
- **Decision rule:** Treat all states as equally likely. Calculate average payoff for each alternative. Choose the best average.
- **Formula:** `max(mean_payoff_per_alternative)` where all states get probability 1/n
- **Psychology:** Neutral/balanced
- **Philosophy:** "Without information, assume uniform distribution"
- **Example (3 states equally likely):**
  ```
  Strategy A: avg = ($500k + $250k - $100k) / 3 = $216.7k
  Strategy B: avg = ($300k + $300k + $100k) / 3 = $233.3k ← Best
  Strategy C: avg = ($200k + $200k + $200k) / 3 = $200k
  → Choose B (Laplace = $233.3k)
  ```

### **Minimax Regret (Savage)**
- **Decision rule:** For each state, calculate "regret" (best payoff - your payoff). For each alternative, find its maximum regret. Choose the alternative that minimizes this maximum regret.
- **Formula:**
  ```
  Regret_ij = max_payoff_in_state_j - Payoff_ij
  Max_regret_i = max(Regret_ij for all j)
  Choose: min(Max_regret_i)
  ```
- **Psychology:** Avoid the scenario where you regret most
- **Example:**
  ```
  Regret matrix:
           Boom    Stable    Recession
  Strat A: $0     $50k      $300k      (max regret = $300k)
  Strat B: $200k  $0        $100k      (max regret = $200k) ← Best
  Strat C: $300k  $100k     $0         (max regret = $300k)
  → Choose B (Minimax Regret = $200k)
  ```

---

## Probability Concepts

### **Probability Distribution**
- **Definition:** A mathematical function showing how likely different outcomes are.
- **Continuous (PDF):** For continuous variables (e.g., price, weight)
  - Example: Normal distribution (bell curve)
- **Discrete (PMF):** For count variables (e.g., number of customers)
  - Example: Poisson distribution, Binomial distribution

### **Normal Distribution (Gaussian)**
- **Shape:** Bell curve, symmetric
- **Parameters:** Mean (μ), Standard Deviation (σ)
- **Real-world:** Height, test scores, measurement errors, return on investment
- **Dashboard:** Auto-fitted to your data

### **Binomial Distribution**
- **Shape:** Discrete; number of successes in n trials
- **Parameters:** n (trials), p (success probability per trial)
- **Real-world:** Number of defects in 100 products (each 5% defect rate)
- **Example:** Flip a coin 10 times; Binomial = number of heads

### **Poisson Distribution**
- **Shape:** Discrete; count of rare events in fixed time/space
- **Parameter:** λ (lambda, average count)
- **Real-world:** Number of customer complaints per week, server crashes per month
- **Example:** 3 complaints/week on average → Poisson(λ=3)

---

## Utility & Risk Preference

### **Utility (Preference Strength)**
- **Definition:** A numerical measure of satisfaction/happiness from a payoff.
- **Key idea:** Money → Utility is NOT linear; $1M to a billionaire ≠ $1M to a student
- **Formula:** U(Payoff) = strength of preference for that payoff

### **Risk Averse**
- **Behavior:** Prefers guaranteed outcome over uncertain lottery with same expected value
- **Utility curve:** Concave (diminishing returns) — each extra dollar gives less happiness
- **Example:** Prefer guaranteed $50k over 50% chance of $100k
- **Real-world:** Insurance buyers, conservative investors
- **Curve shape:**
  ```
      Utility
        |
        |     ╱╱ (diminishing slope)
        |   ╱╱
        | ╱╱
        |╱
        └──────── Payoff
  ```

### **Risk Neutral**
- **Behavior:** Indifferent between guaranteed and uncertain outcome with same EV
- **Utility curve:** Linear
- **Example:** Indifferent between guaranteed $50k vs 50% chance of $100k (both have EV=$50k)
- **Real-world:** Perfect rationality (rarely true)
- **Curve shape:**
  ```
      Utility
        |
        |            ╱ (linear slope)
        |         ╱
        |      ╱
        |   ╱
        └──────── Payoff
  ```

### **Risk Seeking**
- **Behavior:** Prefers uncertain lottery over guaranteed outcome with same expected value
- **Utility curve:** Convex (increasing returns) — each extra dollar gives more excitement
- **Example:** Prefer 50% chance of $100k over guaranteed $50k
- **Real-world:** Gamblers, entrepreneurs, startups
- **Curve shape:**
  ```
      Utility
        |
        |                ╱╱ (steepening slope)
        |             ╱╱
        |          ╱╱
        |       ╱╱
        └──────── Payoff
  ```

---

## Monte Carlo Simulation

### **Definition**
Run thousands of random simulations based on probability distributions to estimate outcomes.

### **How it works:**
1. Model inputs as probability distributions (e.g., "Price ~ Normal(mean=$50, std=$5)")
2. Randomly sample from each distribution 10,000 times
3. Calculate outcomes for each sample
4. Analyze the histogram of outcomes

### **Output metrics:**
- **5th percentile:** Only 5% of outcomes worse than this
- **50th percentile (median):** Average outcome
- **95th percentile:** Only 5% of outcomes better than this
- **Standard deviation:** Spread/variability

### **Example:**
```
You manufacture phone cases.
Cost ~ Normal(mean=$5, std=$0.5)
Price ~ Normal(mean=$15, std=$1)
Demand ~ Poisson(mean=1000)

Profit = (Price - Cost) × Demand

Run 10,000 simulations:
→ Profit histogram shows range: $8,000 to $12,000
→ Most likely: $10,000
→ Worst 5% of outcomes: < $8,500
```

### **Why useful:**
- Handles complex, non-linear systems
- Captures full distribution of outcomes (not just average)
- Easy to do sensitivity analysis ("What if cost ±10%?")

---

## Sensitivity Analysis

### **Definition**
Test how robust your decision is if assumptions change.

### **Question it answers:**
- "If market probability was 0.3 instead of 0.4, would recommendation change?"
- "How much can costs rise before this strategy becomes unprofitable?"

### **Dashboard approach:**
- In Monte Carlo module: Vary input distributions
- See how output changes
- More stable outputs = more robust decision

---

## Model-Driven vs. Data-Driven DSS

### **Data-Driven DSS**
- **Focus:** Explore data you have
- **Process:** Descriptive statistics → visualizations → patterns
- **Questions:** "What is in our data?", "Are these correlated?"
- **Output:** Insights about historical data
- **Dashboard module:** Data-Driven DSS

### **Model-Driven DSS**
- **Focus:** Build mathematical models for decisions
- **Process:** Define decision problem → apply quantitative methods → recommend
- **Questions:** "What should we choose?", "What's the expected outcome?"
- **Output:** Recommended alternative
- **Dashboard modules:** All others (Payoff Table, EV & EOL, Uncertainty, etc.)

---

## Testing & Correctness

### **Property-Based Testing (279 tests)**
- **Approach:** Not just "does code run," but "does it behave correctly?"
- **Example property:** "EV of any alternative ≥ min payoff in that alternative"
  - Tested 1000+ random payoff matrices
  - ALL satisfy this property
- **Tool used:** Hypothesis (Python library)
- **Confidence:** If all 279 tests pass, mathematical correctness is verified

---

## Neobrutalism UI/UX Design

### **Definition**
Modern design aesthetic combining:
- Bold, high-contrast colors (Lime Green, Hot Pink, Cyan, Yellow)
- Thick black borders (4px)
- Maximalist approach (larger type, more space)
- No anti-aliasing or "soft" edges

### **Why this choice?**
- **Data visibility:** Colors scream "pay attention"
- **Accessibility:** High contrast helps colorblind users
- **Memorable:** Bold = memorable for presentations
- **Clarity:** No distracting flourishes; content is king

---

## Acronyms & Abbreviations

| Acronym | Full Form | Explanation |
|---------|-----------|-------------|
| **DSS** | Decision Support System | Computer system helping decision-making |
| **EV** | Expected Value | Weighted average payoff |
| **EOL** | Expected Opportunity Loss | Average regret from wrong choice |
| **EVPI** | Expected Value of Perfect Information | Max price for perfect info |
| **PDF** | Probability Density Function | Continuous distribution |
| **PMF** | Probability Mass Function | Discrete distribution |
| **MLE** | Maximum Likelihood Estimation | Method to fit distribution |
| **ROI** | Return on Investment | Profit ÷ Investment |
| **NPV** | Net Present Value | Future cash flows discounted |
| **KS-test** | Kolmogorov-Smirnov Test | Goodness-of-fit test |

---

**Questions? Feedback? GitHub Issues: https://github.com/anggatamr/Decision-Support-System---With-Kiro/issues**
