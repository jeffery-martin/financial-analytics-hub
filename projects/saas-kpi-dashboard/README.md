# 💼 SaaS KPI & Unit Economics Dashboard

A financial analytics project built to simulate and analyze SaaS unit economics using Python, PySpark, and Delta Lake-style logic. Designed to reflect the type of modeling and insight generation that powers data-driven GTM, retention, and monetization strategy at high-growth software companies. 

This project includes a full pipeline for generating, enriching, and segmenting SaaS data—delivering visibility into CAC, LTV, churn risk, health scoring, and customer behavior across segments. Driven by the pipeline is a dashboard visualizing the core unit economics and customer health metrics. Designed to provide strategic visibility into revenue efficiency, retention trends, and GTM performance across customer segments.

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

## 🔐 Data Disclaimer

> All data is 100% simulated and anonymized for demo purposes only. No real customer, usage, or financial data is included.

---

## 🚀 Future Enhancements

- Multi-period cohort retention analysis
- Scenario analysis for pricing & plan structure changes
- Simulate pricing experiment data for A/B-style impact modeling

---
