import pandas as pd
import os

# --- Define Paths ---
# IMPORTANT: Make sure this DATA_DIR points to the folder
# where your original 'usage_events.csv' (and other CSVs) are located.
DATA_DIR = "/Users/jeffmartin/Library/Mobile Documents/com~apple~CloudDocs/PyCharm"

# Define the output directory for the aggregated CSVs.
# You can use the same DATA_DIR or a new subfolder if you prefer.
OUTPUT_DIR = DATA_DIR

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Loading usage_events.csv from: {DATA_DIR}")

# --- Load the large usage_events.csv file ---
# We'll load it, but immediately process it to reduce memory footprint if possible,
# or handle it in chunks if truly massive and direct load fails.
# For 1GB, direct pd.read_csv should generally work on most machines with 8GB+ RAM.
try:
    usage_df = pd.read_csv(os.path.join(DATA_DIR, 'usage_events.csv'))
    # Convert 'event_date' to datetime objects
    usage_df['event_date'] = pd.to_datetime(usage_df['event_date'], errors='coerce')
    # Drop rows where event_date couldn't be parsed
    usage_df.dropna(subset=['event_date'], inplace=True)
    print(f"Loaded {len(usage_df)} rows from usage_events.csv.")
except FileNotFoundError:
    print(f"Error: 'usage_events.csv' not found at {os.path.join(DATA_DIR, 'usage_events.csv')}")
    print("Please ensure the DATA_DIR variable is set correctly.")
    exit()
except Exception as e:
    print(f"An error occurred while loading usage_events.csv: {e}")
    exit()

# --- Aggregation 1: Monthly Usage Summary ---
# This will summarize total events, unique customers, and average seats used per month.
print("Aggregating monthly usage summary...")
monthly_usage_summary = usage_df.groupby(pd.Grouper(key='event_date', freq='ME')).agg( # Changed 'M' to 'ME'
    Total_Usage_Events=('event_id', 'count'),
    Unique_Customers_With_Usage=('customer_id', 'nunique'),
    Average_Seats_Used=('seats_used', 'mean')
).reset_index()
monthly_usage_summary.rename(columns={'event_date': 'Month'}, inplace=True)

# Save the monthly summary
monthly_summary_filename = os.path.join(OUTPUT_DIR, 'monthly_usage_summary.csv')
monthly_usage_summary.to_csv(monthly_summary_filename, index=False)
print(f"Saved monthly_usage_summary.csv with {len(monthly_usage_summary)} rows to: {monthly_summary_filename}")


# --- Aggregation 2: Top Features Used (Overall) ---
# This will identify the most frequently used features across the entire dataset.
print("Aggregating top features used...")
top_features = usage_df['feature_used'].value_counts().reset_index()
top_features.columns = ['Feature', 'Count']

# Save the top features summary
top_features_filename = os.path.join(OUTPUT_DIR, 'top_features_summary.csv')
top_features.to_csv(top_features_filename, index=False)
print(f"Saved top_features_summary.csv with {len(top_features)} rows to: {top_features_filename}")


# --- Aggregation 3: Customer-level Usage Summary ---
# Summarize usage metrics for each customer, to be potentially merged with unit_economics.
print("Aggregating customer-level usage summary...")
customer_usage_summary = usage_df.groupby('customer_id').agg(
    Total_Events_Per_Customer=('event_id', 'count'),
    Active_Days_In_Usage=('event_date', lambda x: x.dt.date.nunique()), # This is correct, operating on event_date
    Avg_Seats_Used_Per_Event=('seats_used', 'mean')
).reset_index()

# Calculate Avg_Daily_Events_Per_Customer in a separate step after initial aggregation
customer_usage_summary['Avg_Daily_Events_Per_Customer'] = customer_usage_summary['Total_Events_Per_Customer'] / customer_usage_summary['Active_Days_In_Usage']

# Handle potential division by zero if a customer only has one event (Active_Days_In_Usage = 1)
# or if Active_Days_In_Usage is 0 (though unlikely if Total_Events_Per_Customer > 0)
customer_usage_summary['Avg_Daily_Events_Per_Customer'] = customer_usage_summary['Avg_Daily_Events_Per_Customer'].fillna(0)
customer_usage_summary.loc[customer_usage_summary['Active_Days_In_Usage'] == 0, 'Avg_Daily_Events_Per_Customer'] = 0


# Save the customer usage summary
customer_usage_filename = os.path.join(OUTPUT_DIR, 'customer_usage_summary.csv')
customer_usage_summary.to_csv(customer_usage_filename, index=False)
print(f"Saved customer_usage_summary.csv with {len(customer_usage_summary)} rows to: {customer_usage_filename}")

print("\nUsage data aggregation complete!")
