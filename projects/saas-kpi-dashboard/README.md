# SaaS KPI Dashboard Project

This project simulates a realistic SaaS (Software-as-a-Service) business model to demonstrate analytical capabilities across acquisition, revenue, churn, expansion, and support. The dataset is entirely synthetic but modeled after best practices in B2B SaaS strategy.

---

## 📌 Objective
To show deep understanding of subscription-based, seat-based, and usage-based SaaS metrics by building a full-stack analytics project with simulated data, semantic modeling, and Power BI dashboards.

I do not come from a SaaS company background, but this project reflects:
- A strong grasp of **recurring revenue** modeling (MRR, ARR)
- Fluency in **churn mechanics** and retention-based forecasting
- Familiarity with **pricing strategies** by plan tier and user count
- Insight into **product usage telemetry**, feature adoption, and support effectiveness

> **Note:** This project uses a snowflake schema to fully represent relationships across revenue, usage, and support. In a production BI setting, this could be refactored into a star schema for optimization.

---

## 📊 Dataset Structure
The following CSVs were generated using a Python-based SaaS data simulator:

| File                        | Description |
|-----------------------------|-------------|
| `customers.csv`             | Customer firmographics, acquisition channel, trial info |
| `subscriptions.csv`         | Initial subscriptions, plan upgrades, seat expansions |
| `payments.csv`              | Monthly or annual billing records and statuses |
| `support_interactions.csv`  | Tickets by type, resolution status, sentiment |

> ⚠️ `usage_events.csv` (1GB+) was excluded from GitHub due to size limits.  
> 📥 [Download usage_events.csv from Google Drive](https://drive.google.com/file/d/1tyMmYg3rY6yupsCEscW0DMi7MWcURxe1/view?usp=drive_link)

---

## 🧠 Key Concepts Modeled

### ✅ Subscription-Based Revenue
Each customer has one or more subscriptions, charged monthly or annually depending on their billing preference. Revenue is calculated from:
- Plan base price + per-seat price
- Discounts for annual billing
- Seasonal churn likelihoods

### ✅ Seat-Based Pricing
Pricing scales with seat count. Larger companies have higher seat tendencies and more upgrade probability. Expansion events include:
- Additional seat purchases
- Upgrades to higher-tier plans

### ✅ Usage-Based Signals *(simulated)*
Although the usage table isn't in GitHub, it includes:
- Logins, report generations, API calls, file uploads, etc.
- Feature-specific adoption likelihood by plan tier
- Monthly usage frequency tied to engagement and renewal prediction

### ✅ CAC, LTV, and Churn
Each customer includes acquisition cost (simulated from a log-normal distribution), churn likelihood (seasonally adjusted), and expected lifetime value (LTV = MRR × 36).

### ✅ Support Interactions
Support tickets are categorized by:
- Issue type (billing, onboarding, technical)
- Sentiment and resolution time
- Volume correlated with retention and customer health

---

## 📈 Output Goals (Next Phase)
Using Microsoft Fabric + Power BI, this dataset will be transformed into a full dashboard featuring:
- ARR / MRR trends
- CAC to LTV ratio
- Customer churn by segment
- Feature adoption heatmaps
- Support ticket volume by channel

---

## 🧰 Tools Used
- Python (Pandas, NumPy, Faker) for simulation
- Google Colab for data generation and saving to Drive
- Microsoft Fabric for Lakehouse and Semantic Model
- Power BI for dashboard visualizations

---

## 💡 Why This Project Matters
Understanding SaaS metrics is core to modern digital businesses. This project shows:
- Ability to simulate business logic and behavioral data
- Comfort with revenue modeling, pricing tiers, and retention analytics
- Proficiency in translating raw events into board-level KPIs

Even without prior SaaS work experience, I can break down the mechanics behind:
- Net Revenue Retention
- Cohort-based churn curves
- Pricing levers by customer size
- Product-led growth signals

> This repo serves as the foundation for my `jeffmartin.studio` data portfolio.
