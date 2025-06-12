import streamlit as st
import pandas as pd
import plotly.express as px
import os # To handle file paths

# --- Configuration for Streamlit Page ---
# Set the page configuration for a wide layout and a title
st.set_page_config(
    page_title="SaaS KPI Dashboard",
    page_icon="📊",
    layout="wide", # Use "wide" layout for more dashboard space
    initial_sidebar_state="expanded" # Keep sidebar expanded by default
)

# --- Define the path to your data files ---
# IMPORTANT: Update this path to where your CSV files are located!
# Since all CSVs are now in the same directory as the Streamlit script in your GitHub repo,
# you can use "." for the current directory.
DATA_DIR = "."

# --- Data Loading Function with Caching ---
# @st.cache_data decorator caches the DataFrame so it's loaded only once,
# improving performance on subsequent reruns of the app.
@st.cache_data
def load_data():
    """
    Loads all necessary CSV files into pandas DataFrames.
    Ensures date columns are parsed correctly.
    """
    try:
        customers_df = pd.read_csv(os.path.join(DATA_DIR, 'unit_economics.csv'))
        subscriptions_df = pd.read_csv(os.path.join(DATA_DIR, 'subscriptions.csv'))
        payments_df = pd.read_csv(os.path.join(DATA_DIR, 'payments.csv'))

        # Load aggregated usage data instead of the large raw file
        monthly_usage_summary_df = pd.read_csv(os.path.join(DATA_DIR, 'monthly_usage_summary.csv'))
        top_features_summary_df = pd.read_csv(os.path.join(DATA_DIR, 'top_features_summary.csv'))
        customer_usage_summary_df = pd.read_csv(os.path.join(DATA_DIR, 'customer_usage_summary.csv'))

        support_df = pd.read_csv(os.path.join(DATA_DIR, 'support_interactions.csv'))
        segments_df = pd.read_csv(os.path.join(DATA_DIR, 'unit_economics_by_segment.csv'))

        # Convert date columns to datetime objects for easier manipulation
        date_cols_customers = ['acquisition_date']
        for col in date_cols_customers:
            if col in customers_df.columns:
                customers_df[col] = pd.to_datetime(customers_df[col], errors='coerce')

        date_cols_subs = ['start_date', 'end_date']
        for col in date_cols_subs:
            if col in subscriptions_df.columns:
                subscriptions_df[col] = pd.to_datetime(subscriptions_df[col], errors='coerce')

        date_cols_payments = ['payment_date']
        for col in date_cols_payments:
            if col in payments_df.columns:
                payments_df[col] = pd.to_datetime(payments_df[col], errors='coerce')

        # Convert 'Month' column in monthly_usage_summary_df to datetime
        if 'Month' in monthly_usage_summary_df.columns:
            monthly_usage_summary_df['Month'] = pd.to_datetime(monthly_usage_summary_df['Month'], errors='coerce')

        date_cols_support = ['interaction_date']
        for col in date_cols_support:
            if col in support_df.columns:
                support_df[col] = pd.to_datetime(support_df[col], errors='coerce')

        return customers_df, subscriptions_df, payments_df, \
               monthly_usage_summary_df, top_features_summary_df, customer_usage_summary_df, \
               support_df, segments_df
    except FileNotFoundError:
        st.error(f"Error: One or more CSV files not found in '{DATA_DIR}'. "
                 f"Please ensure your data is in the correct directory and the path is set correctly.")
        st.stop() # Stop the app if data can't be loaded
    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")
        st.stop()

# Load data at the start of the script, updating variable names for usage data
customers_df, subscriptions_df, payments_df, \
monthly_usage_summary_df, top_features_summary_df, customer_usage_summary_df, \
support_df, segments_df = load_data()

# --- Title and Introduction ---
st.title("📊 SaaS KPI Dashboard")
st.markdown("""
Welcome to the comprehensive SaaS KPI Dashboard! This interactive tool leverages synthetic data to provide
insights into key metrics crucial for understanding a SaaS business's performance. Explore customer acquisition,
subscription dynamics, revenue, product usage, and support efficiency.
---
""")

# --- Global Filters (Sidebar) ---
st.sidebar.header("Global Filters")

# Date Range Slider for filtering data across all sections
# Now using monthly_usage_summary_df for overall date range determination
min_date = min(
    customers_df['acquisition_date'].min(),
    subscriptions_df['start_date'].min(),
    payments_df['payment_date'].min(),
    monthly_usage_summary_df['Month'].min(), # Use Month from monthly_usage_summary
    support_df['interaction_date'].min()
)
max_date = max(
    customers_df['acquisition_date'].max(),
    subscriptions_df['start_date'].max(),
    payments_df['payment_date'].max(),
    monthly_usage_summary_df['Month'].max(), # Use Month from monthly_usage_summary
    support_df['interaction_date'].max()
)

# Ensure min_date and max_date are not NaT (Not a Time)
if pd.isna(min_date): min_date = pd.to_datetime('2022-01-01')
if pd.isna(max_date): max_date = pd.to_datetime('2024-12-31')


date_range = st.sidebar.slider(
    "Select Date Range:",
    value=(min_date.to_pydatetime().date(), max_date.to_pydatetime().date()), # Convert to Python date objects
    format="YYYY-MM-DD"
)

start_date_filter = pd.to_datetime(date_range[0])
end_date_filter = pd.to_datetime(date_range[1])

# Filter all DataFrames based on the selected date range
# For customers, filter by acquisition_date
filtered_customers_df = customers_df[
    (customers_df['acquisition_date'] >= start_date_filter) &
    (customers_df['acquisition_date'] <= end_date_filter)
]

# For subscriptions, filter by start_date
filtered_subscriptions_df = subscriptions_df[
    (subscriptions_df['start_date'] >= start_date_filter) &
    (subscriptions_df['start_date'] <= end_date_filter)
]

# For payments, filter by payment_date
filtered_payments_df = payments_df[
    (payments_df['payment_date'] >= start_date_filter) &
    (payments_df['payment_date'] <= end_date_filter)
]

# For usage summary, filter by Month
filtered_monthly_usage_summary_df = monthly_usage_summary_df[
    (monthly_usage_summary_df['Month'] >= start_date_filter) &
    (monthly_usage_summary_df['Month'] <= end_date_filter)
]

# For support, filter by interaction_date
filtered_support_df = support_df[
    (support_df['interaction_date'] >= start_date_filter) &
    (support_df['interaction_date'] <= end_date_filter)
]

# Note: top_features_summary_df and customer_usage_summary_df are not filtered by date range
# directly here because they represent overall aggregates. If you needed
# date-range specific top features or customer usage summaries,
# you would need to re-aggregate from the original large file within the date range,
# which is generally not feasible for large files in a dashboard.
# The current approach assumes these aggregations are for the entire dataset,
# or are sufficiently small that they don't cause performance issues if re-calculated.

# --- Section: Executive Summary (Key Metrics) ---
st.header("Executive Summary")
st.markdown("A quick overview of the most critical SaaS KPIs.")

# Calculate summary metrics from filtered data
total_customers = filtered_customers_df['customer_id'].nunique()
churn_rate = filtered_customers_df['Churned'].mean() * 100 if not filtered_customers_df.empty else 0
avg_cac = filtered_customers_df['CAC'].mean() if not filtered_customers_df.empty else 0
avg_ltv = filtered_customers_df['LTV'].mean() if not filtered_customers_df.empty else 0
avg_ltv_cac_ratio = filtered_customers_df['LTV_CAC_Ratio'].mean() if not filtered_customers_df.empty else 0
avg_payback_months = filtered_customers_df['CAC_Payback_Months'].mean() if not filtered_customers_df.empty else 0
avg_health_score = filtered_customers_df['Customer_Health_Score'].mean() if not filtered_customers_df.empty else 0

# Use columns for a clean metric display
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Customers", value=f"{total_customers:,}")
    st.metric(label="Average CAC", value=f"${avg_cac:,.2f}")

with col2:
    st.metric(label="Overall Churn Rate", value=f"{churn_rate:,.2f}%")
    st.metric(label="Average LTV", value=f"${avg_ltv:,.2f}")

with col3:
    st.metric(label="Average LTV/CAC Ratio", value=f"{avg_ltv_cac_ratio:,.2f}x")
    st.metric(label="Average CAC Payback (Months)", value=f"{avg_payback_months:,.2f}")

with col4:
    st.metric(label="Average Customer Health Score", value=f"{avg_health_score:,.2f}")
    st.write("") # Placeholder for alignment or future metric

st.markdown("---") # Visual separator

# --- Section: Customer Acquisition & Segmentation ---
st.header("Customer Acquisition & Segmentation")
st.markdown("Insights into how customers are acquired and their demographic breakdown.")

acquisition_col1, acquisition_col2 = st.columns(2)

with acquisition_col1:
    st.subheader("Acquisition Channels Distribution")
    if not filtered_customers_df.empty:
        channel_counts = filtered_customers_df['acquisition_channel'].value_counts().reset_index()
        channel_counts.columns = ['Channel', 'Customers']
        fig_channel = px.pie(channel_counts, values='Customers', names='Channel',
                             title='Customer Acquisition by Channel',
                             hole=0.3) # Donut chart for better aesthetics
        fig_channel.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_channel, use_container_width=True)
    else:
        st.info("No customer data for the selected date range.")

with acquisition_col2:
    st.subheader("Customers by Company Size")
    if not filtered_customers_df.empty:
        size_counts = filtered_customers_df['company_size'].value_counts().reset_index()
        size_counts.columns = ['Company Size', 'Customers']
        fig_size = px.bar(size_counts, x='Company Size', y='Customers',
                          title='Customers by Company Size Category',
                          color='Company Size')
        st.plotly_chart(fig_size, use_container_width=True)
    else:
        st.info("No customer data for the selected date range.")

st.markdown("---")

# --- Section: Subscriptions & MRR ---
st.header("Subscriptions & MRR")
st.markdown("Track subscription growth, plan popularity, and monthly recurring revenue.")

# Calculate MRR over time
if not filtered_subscriptions_df.empty:
    # Ensure start_date is treated as the monthly point for MRR calculation
    filtered_subscriptions_df['month_year'] = filtered_subscriptions_df['start_date'].dt.to_period('M')

    # Calculate MRR for each month a subscription was active
    mrr_timeline = []
    # Create a monthly date range from the min start date to max end date (or filter end date)
    min_sub_date = filtered_subscriptions_df['start_date'].min()
    max_sub_date = filtered_subscriptions_df['end_date'].max()
    # Ensure we don't go beyond the global filter end date for active subscriptions
    if pd.isna(max_sub_date): # If all subscriptions are active
        max_sub_date = end_date_filter
    else:
        max_sub_date = min(max_sub_date, end_date_filter)

    # Use a loop to iterate month by month and sum MRR for active subscriptions
    current_mrr_month = min_sub_date.to_period('M')
    while current_mrr_month <= max_sub_date.to_period('M'):
        mrr_for_month = 0
        for _, sub in filtered_subscriptions_df.iterrows():
            sub_start_month = sub['start_date'].to_period('M')
            sub_end_month = sub['end_date'].to_period('M') if pd.notna(sub['end_date']) else pd.to_datetime(end_date_filter).to_period('M')

            if sub_start_month <= current_mrr_month <= sub_end_month:
                mrr_for_month += sub['monthly_price']
        mrr_timeline.append({'Month': current_mrr_month.to_timestamp(), 'MRR': mrr_for_month})
        current_mrr_month += 1 # Move to next month

    mrr_df = pd.DataFrame(mrr_timeline)

    if not mrr_df.empty:
        st.subheader("Monthly Recurring Revenue (MRR) Trend")
        fig_mrr = px.line(mrr_df, x='Month', y='MRR', title='MRR Over Time',
                          labels={'MRR': 'MRR ($)', 'Month': 'Month'})
        fig_mrr.update_traces(mode='lines+markers')
        st.plotly_chart(fig_mrr, use_container_width=True)
    else:
        st.info("No subscription data to calculate MRR for the selected date range.")

sub_kpi_col1, sub_kpi_col2 = st.columns(2)

with sub_kpi_col1:
    st.subheader("Plan Distribution")
    if not filtered_subscriptions_df.empty:
        plan_counts = filtered_subscriptions_df[filtered_subscriptions_df['subscription_type'] == 'initial']['plan_name'].value_counts().reset_index()
        plan_counts.columns = ['Plan', 'Customers']
        fig_plan_dist = px.bar(plan_counts, x='Plan', y='Customers', title='Initial Plan Distribution', color='Plan')
        st.plotly_chart(fig_plan_dist, use_container_width=True)
    else:
        st.info("No subscription data for the selected date range.")

with sub_kpi_col2:
    st.subheader("Subscription Type Distribution")
    if not filtered_subscriptions_df.empty:
        sub_type_counts = filtered_subscriptions_df['subscription_type'].value_counts().reset_index()
        sub_type_counts.columns = ['Type', 'Count']
        fig_sub_type = px.pie(sub_type_counts, values='Count', names='Type',
                              title='Distribution of Subscription Types',
                              hole=0.3)
        fig_sub_type.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_sub_type, use_container_width=True)
    else:
        st.info("No subscription data for the selected date range.")

st.markdown("---")

# --- Section: Payments & Revenue ---
st.header("Payments & Revenue")
st.markdown("Analyze payment success, methods, and revenue flow.")

payment_col1, payment_col2 = st.columns(2)

with payment_col1:
    st.subheader("Payment Status Distribution")
    if not filtered_payments_df.empty:
        payment_status_counts = filtered_payments_df['status'].value_counts().reset_index()
        payment_status_counts.columns = ['Status', 'Count']
        fig_payment_status = px.bar(payment_status_counts, x='Status', y='Count',
                                    title='Payment Status Distribution',
                                    color='Status',
                                    color_discrete_map={'successful': 'green', 'failed': 'red', 'refunded': 'orange'})
        st.plotly_chart(fig_payment_status, use_container_width=True)
    else:
        st.info("No payment data for the selected date range.")

with payment_col2:
    st.subheader("Revenue by Payment Method")
    if not filtered_payments_df.empty:
        revenue_by_method = filtered_payments_df[filtered_payments_df['status'] == 'successful'].groupby('payment_method')['amount'].sum().reset_index()
        revenue_by_method.columns = ['Method', 'Total Revenue']
        fig_payment_method = px.pie(revenue_by_method, values='Total Revenue', names='Method',
                                    title='Total Revenue by Payment Method',
                                    hole=0.3)
        fig_payment_method.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_payment_method, use_container_width=True)
    else:
        st.info("No successful payments for the selected date range.")

st.markdown("---")

# --- Section: Usage & Engagement ---
st.header("Product Usage & Engagement")
st.markdown("Understand how customers interact with your product features.")

usage_kpi_col1, usage_kpi_col2, usage_kpi_col3 = st.columns(3)

with usage_kpi_col1:
    # Use Total_Usage_Events from the monthly summary
    total_usage_events = filtered_monthly_usage_summary_df['Total_Usage_Events'].sum() if not filtered_monthly_usage_summary_df.empty else 0
    st.metric("Total Usage Events", f"{total_usage_events:,}")

with usage_kpi_col2:
    # Use Unique_Customers_With_Usage from the monthly summary
    customers_with_usage = filtered_monthly_usage_summary_df['Unique_Customers_With_Usage'].sum() if not filtered_monthly_usage_summary_df.empty else 0
    st.metric("Customers with Usage", f"{customers_with_usage:,}")

with usage_kpi_col3:
    # Use Avg_Daily_Events_Per_Customer from customer_usage_summary_df
    avg_daily_events_overall = customer_usage_summary_df['Avg_Daily_Events_Per_Customer'].mean() if not customer_usage_summary_df.empty else 0
    st.metric("Avg. Daily Events/Customer (Overall)", f"{avg_daily_events_overall:,.2f}")


st.subheader("Top Used Features (Overall)")
if not top_features_summary_df.empty:
    # Use the pre-aggregated top features
    fig_features = px.bar(top_features_summary_df.head(10), x='Feature', y='Count',
                          title='Top 10 Most Used Features',
                          color='Count', # Color by count for visual hierarchy
                          color_continuous_scale=px.colors.sequential.Teal)
    st.plotly_chart(fig_features, use_container_width=True)
else:
    st.info("No top features data available.")

st.subheader("Usage Events Over Time")
if not filtered_monthly_usage_summary_df.empty:
    # Use the filtered monthly usage summary for the trend chart
    fig_usage_trend = px.line(filtered_monthly_usage_summary_df, x='Month', y='Total_Usage_Events',
                              title='Total Usage Events by Month',
                              labels={'Total_Usage_Events': 'Total Events', 'Month': 'Month'})
    fig_usage_trend.update_traces(mode='lines+markers')
    st.plotly_chart(fig_usage_trend, use_container_width=True)
else:
    st.info("No monthly usage data for the selected date range.")

st.markdown("---")

# --- Section: Support & Sentiment ---
st.header("Support & Sentiment Analysis")
st.markdown("Insights into customer support interactions and sentiment.")

support_kpi_col1, support_kpi_col2, support_kpi_col3 = st.columns(3)

with support_kpi_col1:
    total_interactions = filtered_support_df['interaction_id'].nunique() if not filtered_support_df.empty else 0
    st.metric("Total Support Interactions", f"{total_interactions:,}")

with support_kpi_col2:
    avg_resolution_time = filtered_support_df['resolution_time_hours'].mean() if not filtered_support_df.empty else 0
    st.metric("Avg. Resolution Time (Hours)", f"{avg_resolution_time:,.2f}")

with support_kpi_col3:
    avg_sentiment_score = filtered_support_df['sentiment_score'].mean() if not filtered_support_df.empty else 0
    st.metric("Avg. Sentiment Score (0-1)", f"{avg_sentiment_score:,.2f}")

support_chart_col1, support_chart_col2 = st.columns(2)

with support_chart_col1:
    st.subheader("Interaction Status Distribution")
    if not filtered_support_df.empty:
        status_counts = filtered_support_df['resolution_status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig_status = px.bar(status_counts, x='Status', y='Count',
                            title='Support Interaction Status',
                            color='Status',
                            color_discrete_map={'Resolved': 'blue', 'Pending': 'grey', 'Escalated': 'red'})
        st.plotly_chart(fig_status, use_container_width=True)
    else:
        st.info("No support interaction data for the selected date range.")

with support_chart_col2:
    st.subheader("Customer Sentiment Distribution")
    if not filtered_support_df.empty:
        sentiment_counts = filtered_support_df['sentiment_rating'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        fig_sentiment = px.pie(sentiment_counts, values='Count', names='Sentiment',
                               title='Customer Sentiment from Interactions',
                               hole=0.3,
                               color_discrete_map={'Positive': 'lightgreen', 'Neutral': 'lightblue', 'Negative': 'salmon'})
        fig_sentiment.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_sentiment, use_container_width=True)
    else:
        st.info("No support interaction data for the selected date range.")

st.markdown("---")

# --- Section: Detailed Data View (Expanders) ---
st.header("Detailed Data Views")
st.markdown("Explore the raw and aggregated data used in this dashboard.")

with st.expander("View Customers Data"):
    st.dataframe(filtered_customers_df)

with st.expander("View Subscriptions Data"):
    st.dataframe(filtered_subscriptions_df)

with st.expander("View Payments Data"):
    st.dataframe(filtered_payments_df)

with st.expander("View Monthly Usage Summary Data"):
    st.dataframe(filtered_monthly_usage_summary_df)

with st.expander("View Top Features Summary Data"):
    st.dataframe(top_features_summary_df)

with st.expander("View Customer Usage Summary Data"):
    st.dataframe(customer_usage_summary_df)

with st.expander("View Support Interactions Data"):
    st.dataframe(filtered_support_df)

st.markdown("---")
st.success("Dashboard generated successfully!")
