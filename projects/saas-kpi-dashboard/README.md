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

# 💼 SaaS KPI & Unit Economics Dashboard

A financial analytics project built to simulate and analyze SaaS unit economics using Python, PySpark, and Delta Lake-style logic. Designed to reflect the type of modeling and insight generation that powers data-driven GTM, retention, and monetization strategy at high-growth software companies.

This project includes a full pipeline for generating, enriching, and segmenting SaaS data—delivering visibility into CAC, LTV, churn risk, health scoring, and customer behavior across segments.

---

## 🎯 Objectives

- Simulate realistic customer-level SaaS data with features like plan, billing, tenure, usage, and support history
- Calculate core SaaS KPIs at the customer level:
  - Customer Acquisition Cost (CAC)
  - Lifetime Value (LTV)
  - CAC Payback Period
  - LTV:CAC Ratio
  - Usage Score & Support Sentiment Score
  - Customer Health Score & Churn Flag
- Aggregate metrics by customer cohort and segment
- Build the foundation for a dynamic KPI dashboard in Power BI

---

## ⚙️ Tech Stack

- Python-based synthetic data generator
- PySpark notebooks for ETL and transformation logic
- Delta-style design with outputs for downstream dashboarding
- CSV-based structure for easy loading into BI tools
- Power BI dashboard (coming soon)

---

## 📁 Project Structure

```
projects/saas-kpi-dashboard/
├── README.md                          <- This file
├── aggregations.ipynb                 <- Segment-level aggregations
├── unit_economics.ipynb              <- Customer-level KPI calculations
├── saas_advanced_data_generator.py   <- Custom data generator script
├── customers.csv                      <- Simulated customer master data
├── subscriptions.csv                  <- Subscription-level events
├── payments.csv                       <- Payment history per customer
├── support_interactions.csv          <- Support logs with sentiment scoring
├── saas_dax_cheatsheet.md            <- DAX reference for Power BI metrics
```

---

## 📊 Sample Use Cases

This dataset and pipeline enables you to answer:

- Which segments have the healthiest LTV:CAC ratios?
- How does support sentiment correlate with churn?
- Where are CAC payback periods too long to sustain?
- What plan structures or billing frequencies are most retention-efficient?

---

## 🔐 Data Disclaimer

> All data is 100% simulated and anonymized for demo purposes only. No real customer, usage, or financial data is included.

---

## 🚀 Future Enhancements

- Add retention cohort and revenue waterfall logic
- Deploy a dashboard with dynamic filters by segment and time
- Simulate pricing experiment data for A/B-style impact modeling

---

Built to demonstrate my ability to model and communicate core SaaS economics using modern analytics tooling—from Python to PySpark to Power BI.
# 📊 SaaS KPI Dashboard (Power BI)

This dashboard visualizes the core unit economics and customer health metrics generated from the SaaS KPI data pipeline. Designed to provide strategic visibility into revenue efficiency, retention trends, and GTM performance across customer segments.

---

## 💼 Key Metrics Visualized

- **Customer Acquisition Cost (CAC)**
- **Lifetime Value (LTV)**
- **CAC Payback Period**
- **LTV:CAC Ratio**
- **Churn Rate & Retention by Month**
- **Customer Health Score**
- **Support Sentiment & Usage Scoring**

---

## 📈 Dashboard Pages

1. **Executive Overview**  
   High-level LTV, CAC, and retention insights with filters for plan, billing cadence, and company size.

2. **Customer Health & Churn**  
   Cohort-based churn tracking, usage activity, and support sentiment overlays.

3. **Segmented Unit Economics**  
   LTV:CAC and CAC Payback sliced by product tier, billing frequency, industry, and size.

4. **Acquisition Funnel** *(Planned)*  
   Visual flow of user acquisition by stage and associated cost-to-convert.

---

## 🧱 Data Sources

| File | Description |
|------|-------------|
| `customers.csv` | Master customer records |
| `subscriptions.csv` | Subscription terms, plans, billing cycle |
| `payments.csv` | Monthly recurring revenue and invoice data |
| `support_interactions.csv` | Support ticket logs with sentiment scores |
| Aggregated tables from: `unit_economics.ipynb`, `aggregations.ipynb`

---

## 🧮 Built With

- **Power BI** for interactive dashboarding
- **DAX** measures for dynamic KPI calculation
- **Python/PySpark** generated tables and pre-aggregated metrics

---

## 🔜 Coming Next

- Multi-period cohort retention analysis
- Scenario analysis for pricing & plan structure changes
- Embedded dashboard screenshots

---

> All visuals are based on fully synthetic data generated for demonstration purposes only.

