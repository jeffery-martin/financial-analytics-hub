CREATE OR REPLACE TABLE analytics.gold.revenue_by_region AS

  SELECT
  region_lookup.region_name AS Region,
  date.FiscalYear,
  date.FiscalQuarter,
  date.FiscalMonth,
  CAST(date.date AS DATE) AS Date,
  'Revenue' AS Category,
  CAST(sales_data.net_sales_credit_r AS DECIMAL) AS Amount
FROM analytics.gold.sales_data AS sales_data
INNER JOIN analytics.gold.date AS date
  ON sales_data.sales_credit_date = date.date
INNER JOIN analytics.gold.region_lookup AS region_lookup
  ON sales_data.office_id = region_lookup.office_id
WHERE
  sales_data.sales_force_id = 1
  AND region_lookup.sales_force_id = 1
  AND sales_data.sales_cycle_step_id = 12
  AND sales_data.fiscal_yr_id IN (2025, 2026, 2027)
  AND sales_data.sales_plan_type_name = 'Total Rev';
