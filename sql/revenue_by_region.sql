CREATE OR REPLACE TABLE analytics.gold.revenue_by_region AS

  SELECT
  region_lookup.region_name AS Region,
  fiscal_calendar.fiscal_yr_id AS FiscalYear,
  fiscal_calendar.fiscal_qtr_id AS FiscalQuarter,
  fiscal_calendar.fiscal_mnth_id AS FiscalMonth,
  CAST(fiscal_calendar.fiscal_date AS DATE) AS Date,
  'Revenue' AS Category,
  CAST(sales_data.net_sales_credit_r AS DECIMAL) AS Amount
FROM analytics.gold.sales_data AS sales_data
INNER JOIN analytics.gold.fiscal_calendar AS fiscal_calendar
  ON sales_data.sales_credit_date = fiscal_calendar.fiscal_date
INNER JOIN analytics.gold.region_lookup AS region_lookup
  ON sales_data.office_id = region_lookup.office_id
WHERE
  sales_data.sales_force_id = 1
  AND region_lookup.sales_force_id = 1
  AND sales_data.sales_cycle_step_id = 12
  AND sales_data.fiscal_yr_id IN (2025, 2026, 2027)
  AND sales_data.sales_plan_type_name = 'Total Rev';
