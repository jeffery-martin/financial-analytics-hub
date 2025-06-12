# 📊 SaaS KPI Dashboard: Data Generation & Analytics

This project simulates a complete end-to-end SaaS data pipeline. It generates synthetic customer-level data and visualizes KPIs through an interactive dashboard. Designed to reflect the type of modeling and insight generation that powers data-driven GTM, retention, and monetization strategy at high-growth software companies.

This project includes a full pipeline for generating, enriching, and segmenting SaaS data—delivering visibility into CAC, LTV, churn risk, health scoring, and customer behavior across segments. Driven by this pipeline is a dashboard visualizing the core unit economics and customer health metrics. It is specifically designed to provide strategic visibility into revenue efficiency, retention trends, and GTM performance across customer segments.

---

## 🌟 Project Overview

The core of this project involves:

* **Synthetic Data Generation**: A robust Python script that creates customer-level data, including acquisition details, subscription events, payment history, product usage, and support interactions.
* **Data Aggregation & Preparation**: Processing raw, large datasets (like usage events) into smaller, more efficient summary files for optimal dashboard performance.
* **Interactive Dashboarding**: Building a dynamic web application using Streamlit and Plotly to present key SaaS metrics and trends.

---

## 🎯 Objectives

Simulate realistic customer-level SaaS data with features like plan, billing, tenure, usage, and support history.

Calculate core SaaS KPIs at the customer level and aggregate them for segment analysis:

* Customer Acquisition Cost (CAC)
* Lifetime Value (LTV)
* CAC Payback Period
* LTV\:CAC Ratio
* Usage & Support Sentiment Metrics
* Customer Health Score & Churn Flag (0 = unhealthy, 1 = very healthy)

Build a dynamic and intuitive KPI dashboard for strategic visibility into revenue efficiency, retention trends, and Go-To-Market (GTM) performance.

---

## 📈 Data Generation (`data_generator_v2.py`)

The `data_generator_v2.py` script simulates various aspects of a SaaS business:

* **Customers**: Companies of different sizes, channels, and CAC.
* **Subscription Plans**: Four pricing tiers with different base prices and churn rates.
* **Customer Lifetime & Churn**: Modeled using base churn and seasonal effects.
* **Expansion Events**: Seat increases and plan upgrades.
* **Add-ons**: Optional features with monthly and one-time pricing.
* **Payments**: Monthly/annual recurring and one-time payments.
* **Usage Events**: Scaled by plan and seats.
* **Support Interactions**: Including resolution status and sentiment.

Tuning targets a realistic LTV\:CAC ratio (aiming for 4-10x).

---

## 📊 Data Aggregation (`aggregate_usage.py`)

Raw usage events can exceed 1GB. This script:

* Loads the raw `usage_events.csv` locally (can be adapted to automated ETL jobs).
* Aggregates data:

  * Monthly Usage Summary
  * Top Features Summary
  * Customer Usage Summary
* Saves results as compact CSVs for fast dashboard loading.

---

## 🔹 Interactive Dashboard (`saas_dashboard.py`)

Built with Streamlit + Plotly, includes:

* **Global Date Filter**
* **Executive Summary**
* **Customer Acquisition & Segmentation**
* **Subscriptions & MRR**
* **Payments & Revenue**
* **Product Usage & Engagement**
* **Support & Sentiment Analysis**
* **Detailed Data Views**

---

## ⚙️ Technology Stack

* **Python**
* **pandas**, **numpy**
* **Faker**, **datetime**, **dateutil**
* **Streamlit**, **Plotly Express**
* **Git & GitHub**
* **Streamlit Community Cloud**

---

## 📁 Project Structure

```
projects/saas-kpi-dashboard/
├── README.md
├── aggregate_usage.py
├── customer_usage_summary.csv
├── data_generator_v2.py
├── monthly_usage_summary.csv
├── payments.csv
├── requirements.txt
├── saas_dashboard.py
├── subscriptions.csv
├── support_interactions.csv
├── top_features_summary.csv
├── unit_economics.csv
└── unit_economics_by_segment.csv
```

---

## 📊 Key Metrics Visualized

* Customer Acquisition Cost (CAC)
* Lifetime Value (LTV)
* CAC Payback Period (Months)
* LTV\:CAC Ratio
* Overall Churn Rate (%)
* Customer Health Score
* Total Usage Events & Trends
* Top Used Features
* Support Interaction Status & Sentiment
* Monthly Recurring Revenue (MRR) Trend
* Acquisition Channel Distribution
* Subscription Plan & Type Distribution
* Payment Status & Revenue by Method

---

## 🎯 Sample Use Cases

* **GTM Strategy**: Efficiency of acquisition channels by segment.
* **Product & Customer Success**: Usage and support drivers of churn.
* **Monetization & Financial Health**: Segment-level LTV\:CAC trends.
* **Retention**: Billing and plan structures with best retention rates.

---

## 📅 Example Dashboard Analysis

* **Total Customers**: 1,133
* **Overall Churn Rate**: 49.87%

  * High churn; realistic for synthetic or freemium data
* **Average LTV/CAC**: 9.57x

  * Extremely healthy SaaS benchmark
* **Average CAC**: \$1,915.33

  * Realistic for B2B
* **Average LTV**: \$14,882.59
* **CAC Payback**: 9.92 months

  * Strong (target < 12-18 months)
* **Customer Health Score**: 0.41

  * Low-moderate; opportunity to improve satisfaction/retention

---

## 🚀 Future Enhancements

* Multi-period Cohort Analysis *(High Priority)*
* Pricing Experiment Simulations
* Scenario Modeling ("what-if")
* Predictive Churn Modeling with ML

---

## 🔐 Data Disclaimer

All data is synthetic and anonymized. No real customers or financials.

---

## 📈 Live Dashboard

[https://financial-analytics.streamlit.app](https://financial-analytics.streamlit.app)

---

## 👤 Connect & Feedback

I'm passionate about building data analytics solutions for business insights. Connect with me:

* [LinkedIn](https://www.linkedin.com/in/jeffery-martin/)
* [GitHub](https://github.com/jtmartin18/financial-analytics-hub)
