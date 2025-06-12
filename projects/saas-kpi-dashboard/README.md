📊 SaaS KPI Dashboard: Data Generation & Analytics
This project showcases a complete end-to-end pipeline for generating synthetic SaaS (Software-as-a-Service) customer data and visualizing key performance indicators (KPIs) through an interactive dashboard. Designed to reflect the type of modeling and insight generation that powers data-driven GTM, retention, and monetization strategy at high-growth software companies.

This project includes a full pipeline for generating, enriching, and segmenting SaaS data—delivering visibility into CAC, LTV, churn risk, health scoring, and customer behavior across segments. Driven by this pipeline is a dashboard visualizing the core unit economics and customer health metrics. It is specifically designed to provide strategic visibility into revenue efficiency, retention trends, and GTM performance across customer segments.

Project Overview
The core of this project involves:

Synthetic Data Generation: A robust Python script that creates customer-level data, including acquisition details, subscription events, payment history, product usage, and support interactions.

Data Aggregation & Preparation: Processing raw, large datasets (like usage events) into smaller, more efficient summary files for optimal dashboard performance.

Interactive Dashboarding: Building a dynamic web application using Streamlit and Plotly to present key SaaS metrics and trends.

🎯 Objectives
Simulate realistic customer-level SaaS data with features like plan, billing, tenure, usage, and support history.

Calculate core SaaS KPIs at the customer level and aggregate them for segment analysis:

Customer Acquisition Cost (CAC)

Lifetime Value (LTV)

CAC Payback Period

LTV:CAC Ratio

Usage & Support Sentiment Metrics

Customer Health Score & Churn Flag

Develop an efficient data pipeline to handle potentially large raw datasets by performing necessary aggregations.

Build a dynamic and intuitive KPI dashboard for strategic visibility into revenue efficiency, retention trends, and Go-To-Market (GTM) performance across customer segments.

Data Generation (data_generator_v2.py)
The data_generator_v2.py script is the engine behind the synthetic data. It simulates various aspects of a SaaS business:

Customers: Companies of different sizes (Startup to Enterprise), acquired through various channels, each with a calculated Customer Acquisition Cost (CAC).

Subscription Plans: Starter, Professional, Business, and Enterprise tiers with varying base prices, per-seat costs, and annual discounts.

Customer Lifetime & Churn: Modeled with base churn rates per plan and seasonal patterns, determining when customers might churn and why.

Expansion Events: Seat additions and plan upgrades as customers grow.

Add-ons: Optional features with their own monthly pricing and attachment rates, including one-time add-ons.

Payments: Recurring monthly/annual payments reflecting subscription terms, including successful, failed, and refunded transactions.

Usage Events: Granular data on feature usage by customers, scaled by plan and number of seats.

Support Interactions: Records of customer support tickets, their resolution status, time, and sentiment.

Key Metric Tuning: The generation logic has been specifically tuned to achieve a realistic LTV:CAC ratio (aiming for 4-10x) by carefully balancing generated revenue (LTV) against the simulated acquisition costs (CAC).

Data Aggregation (aggregate_usage.py)
A critical component of this project's efficiency is the aggregate_usage.py script. The raw usage_events.csv file can be quite large (e.g., over 1GB for 2,000 customers over three years), making it impractical for direct loading into a web dashboard due to memory and deployment constraints.

This script addresses this by:

Loading the large usage_events.csv locally.

Performing key aggregations:

Monthly Usage Summary: Total events, unique customers with usage, and average seats used per month.

Top Features Summary: Overall most frequently used features.

Customer Usage Summary: Per-customer aggregates like total events, active days, and average daily events.

Saving these aggregated results into much smaller CSV files, which are then used by the Streamlit dashboard. This ensures the dashboard remains fast, responsive, and deployable.

Interactive Dashboard (saas_dashboard.py)
The saas_dashboard.py script powers the interactive web dashboard built with Streamlit and Plotly. It provides a user-friendly interface to explore the generated SaaS data and key performance indicators:

Global Date Filter: Allows users to dynamically filter all displayed data by a specific date range.

Executive Summary: A concise overview of critical metrics.

Customer Acquisition & Segmentation: Visualizations of acquisition channels and customer distribution by company size.

Subscriptions & MRR: Trends in Monthly Recurring Revenue (MRR), and distribution of subscription plans and types (initial, expansion, add-on).

Payments & Revenue: Analysis of payment success rates and revenue breakdown by payment method.

Product Usage & Engagement: Key usage metrics, top used features, and usage trends over time (derived from the aggregated data).

Support & Sentiment Analysis: Insights into support interaction status, average resolution times, and customer sentiment.

Detailed Data Views: Expandable sections to view the raw (or aggregated) DataFrames.

⚙️ Technology Stack
Python: The core language for all data generation, aggregation, and dashboard logic.

pandas: For data manipulation and analysis.

numpy: For numerical operations and random distributions.

Faker: For generating realistic fake data (company names, emails, etc.).

datetime, dateutil: For date and time handling.

Streamlit: For building the interactive, web-based dashboard with minimal code.

Plotly Express: For creating beautiful, interactive, and web-ready data visualizations.

Git & GitHub: For version control and repository hosting.

Streamlit Community Cloud: For deploying the live web application.

📁 Project Structure
projects/saas-kpi-dashboard/
├── README.md                           <- This file
├── aggregate_usage.py                  <- Script for aggregating large usage data
├── customer_usage_summary.csv          <- Aggregated customer-level usage data
├── data_generator_v2.py                <- Main synthetic data generator script
├── monthly_usage_summary.csv           <- Aggregated monthly usage trends
├── payments.csv                        <- Simulated payment history
├── requirements.txt                    <- Python dependencies for the project
├── saas_dashboard.py                   <- Streamlit web dashboard script
├── subscriptions.csv                   <- Simulated subscription events
├── support_interactions.csv            <- Simulated support logs
├── top_features_summary.csv            <- Aggregated top product features
├── unit_economics.csv                  <- Simulated customer unit economics (LTV, CAC, etc.)
└── unit_economics_by_segment.csv       <- Aggregated unit economics by segment


📊 Key Metrics Visualized
Customer Acquisition Cost (CAC)

Lifetime Value (LTV)

CAC Payback Period (Months)

LTV:CAC Ratio

Overall Churn Rate (%)

Customer Health Score

Total Usage Events & Trends

Top Used Features

Support Interaction Status & Sentiment

Monthly Recurring Revenue (MRR) Trend

Acquisition Channel Distribution

Subscription Plan & Type Distribution

Payment Status & Revenue by Method

🎯 Sample Use Cases
This dashboard and underlying data pipeline enable you to answer critical business questions, supporting strategic decisions in:

Go-To-Market (GTM) Strategy: Which acquisition channels are most efficient? How does company size impact CAC and LTV?

Product & Customer Success: How do usage patterns and support interactions correlate with customer health and churn? What features are driving engagement?

Monetization & Financial Health: Which segments have the healthiest LTV:CAC ratios and shortest payback periods? How is MRR trending over time?

Retention: What plan structures or billing frequencies are most retention-efficient?

Analysis of Dashboard Results (Example)
Based on the latest generated data, here's an analysis of the key metrics displayed in the dashboard's Executive Summary:

Total Customers: 1,133

A solid base for statistical analysis of customer behavior, providing sufficient data points for meaningful aggregation.

Overall Churn Rate: 49.87%

Analysis: This rate is quite high for a typical SaaS business. While common in synthetic datasets or for early-stage/freemium products, it suggests significant churn challenges. In a real-world scenario, this would immediately trigger deep dives into customer onboarding, product-market fit, and customer success initiatives to identify root causes and improve retention.

Average LTV/CAC Ratio: 9.57x

Analysis: This is an excellent and highly desirable ratio for a SaaS company. Industry benchmarks often target 3x to 5x. A nearly 10x ratio indicates that the value generated by a customer over their lifetime is almost 10 times the cost to acquire them, suggesting very healthy unit economics. This strong ratio is a direct result of tuning the data generation script's CAC and churn parameters to reflect a successful business model.

Average CAC: $1,915.33

Analysis: This is a realistic Customer Acquisition Cost, especially for B2B SaaS, where acquiring a customer can involve significant sales and marketing effort (e.g., through sales teams, extensive marketing campaigns, or trade shows).

Average LTV: $14,882.59

Analysis: A robust Lifetime Value, reflecting the significant revenue generated by customers over their tenure. This LTV is indicative of a product that commands higher subscription tiers and retains customers long enough to generate substantial revenue, particularly relevant for mid-to-high-tier SaaS offerings.

Average CAC Payback (Months): 9.92

Analysis: This is a very strong payback period. Most SaaS companies aim for 12-18 months. Achieving profitability on a customer in under 10 months is highly efficient, indicating quick monetization of acquired customers and providing capital for reinvestment in growth.

Average Customer Health Score: 0.41

Analysis: On a normalized scale of 0-1, this score indicates that customers are, on average, in a lower-middle range of health. This metric aligns with the relatively high churn rate, suggesting that while the financial unit economics (LTV:CAC) are strong, there's still notable opportunity for improvement in customer satisfaction, engagement, and overall retention efforts to further reduce churn and potentially boost LTV.

🚀 Future Enhancements
Multi-period Cohort Analysis: Implement detailed retention cohorts (e.g., by acquisition month) to track retention curves over time.

Pricing Experiment Modeling: Add functionality to simulate different pricing strategies and analyze their hypothetical impact on LTV, CAC, and overall revenue.

Advanced Scenario Analysis: Develop tools for "what-if" modeling to explore the impact of changes in churn rates, expansion rates, or CAC on overall business health.

Predictive Churn Modeling: Integrate machine learning techniques to identify high-risk customers and predict churn probabilities.

🔐 Data Disclaimer
All data included in this project is 100% simulated and anonymized for demonstration and portfolio purposes only. No real customer, usage, or financial data is included.

How to Run (Local)
Clone the repository:

git clone https://github.com/your-username/financial-analytics-hub.git # Replace with your actual repo URL
cd financial-analytics-hub/projects/saas-kpi-dashboard


Install dependencies:

pip install -r requirements.txt


(Ensure requirements.txt contains streamlit, pandas, plotly, numpy, faker, python-dateutil).

Generate Data:

python data_generator_v2.py


This will create the raw CSV files in your saas-kpi-dashboard directory.

Aggregate Usage Data:

python aggregate_usage.py


This will process the large usage_events.csv into smaller summary files in the same directory.

Run the Dashboard:

streamlit run saas_dashboard.py


This will open the dashboard in your web browser.

Live Dashboard
(Once deployed on Streamlit Community Cloud, you would add the live link here:)
Live Dashboard: https://financial-analytics.streamlit.app

Connect & Feedback
I'm passionate about building data analytics solutions for business insights. Feel free to connect on LinkedIn or leave feedback on this project.

LinkedIn: https://www.linkedin.com/in/jeffery-martin/

