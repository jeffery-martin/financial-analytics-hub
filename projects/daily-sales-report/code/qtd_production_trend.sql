-- FILE: qtd_production_trend.sql (SANITIZED)

CREATE OR REPLACE TABLE analytics.gold.qtd_production_trend
USING DELTA
AS

-- Step 1: Revenue Mapping
WITH ProductCategoryMapping AS (
  SELECT
    DATEADD(SNAPSHOT_DATE, -1) AS Date,
    FISCAL_YEAR AS FY,
    FISCAL_QTR AS Qtr,
    CASE 
      WHEN PRODUCT_GROUP IN ('Product A', 'Product B', 'other product') THEN 'DTC Product 2'
      WHEN PRODUCT_GROUP IN ('Product C', 'Product D', 'Other acc') THEN 'DTC Product 3'
      WHEN PRODUCT_GROUP IN ('X9 Sensor', 'X9 Transmitter') THEN 'DTC X9'
      WHEN PRODUCT_GROUP IN ('Accessory', 'HPS Accessory') THEN 'DTC Accessory'
      WHEN PRODUCT_GROUP IN ('other', 'software') THEN 'DTC Other'
      WHEN PRODUCT_GROUP LIKE 'DTC%' OR PRODUCT_GROUP = 'HPS Accessory' THEN 'Total DTC'
      WHEN PRODUCT_GROUP IN ('HPS Product 1', 'HPS Product A', 'HPS Product B', 'HPS other product', 'HPS Product C', 'HPS Product D', 'HPS X9 Sensor', 'HPS X9 Transmitter', 'HPS other', 'HPS Other acc') THEN 'HPS Excl Accessory'
      ELSE NULL
    END AS Category,
    Revenue
  FROM analytics.gold.sap_data
  WHERE FISCAL_YEAR IN ('FY2024', 'FY2025', 'FY2026')

  UNION ALL

  SELECT
    Date,
    FiscalYear AS FY,
    FiscalQuarter AS Qtr,
    Category,
    Revenue
  FROM analytics.gold.qtd_rev_r12
  WHERE Category IN ('Region 1', 'Region 2')
    AND FiscalYear IN ('FY2024', 'FY2025', 'FY2026')
),

-- Step 2: Aggregate Revenue
RevenueBase AS (
  SELECT
    Date,
    FY,
    Qtr,
    Category,
    SUM(Revenue) AS Revenue
  FROM ProductCategoryMapping
  WHERE Category IS NOT NULL
  GROUP BY Date, FY, Qtr, Category

  UNION ALL

  SELECT
    DATEADD(SNAPSHOT_DATE, -1) AS Date,
    FISCAL_YEAR AS FY,
    FISCAL_QTR AS Qtr,
    'Total Region X' AS Category,
    SUM(Revenue)
  FROM analytics.gold.sap_data
  WHERE FISCAL_YEAR IN ('FY2024', 'FY2025', 'FY2026')
  GROUP BY Date, FY, Qtr
),

-- Step 3: Add Region 1 + Region 2
RevenueData AS (
  SELECT * FROM RevenueBase

  UNION ALL

  SELECT
    Date,
    FY,
    Qtr,
    'Region 1 + Region 2' AS Category,
    SUM(Revenue) AS Revenue
  FROM RevenueBase
  WHERE Category IN ('Region 1', 'Region 2')
  GROUP BY Date, FY, Qtr
),

-- Step 4: Add Total Super Region
RevenueDataWithSuperRegion AS (
  SELECT * FROM RevenueData

  UNION ALL

  SELECT
    Date,
    FY,
    Qtr,
    'Total Super Region' AS Category,
    SUM(Revenue) AS Revenue
  FROM RevenueData
  WHERE Category IN ('Total Region X', 'Region 1 + Region 2')
  GROUP BY Date, FY, Qtr
),

-- Step 5: Add Backorders and Production
FinalOutput AS (
  SELECT
    r.Date,
    r.FY,
    r.Qtr,
    r.Category,
    r.Revenue,
    COALESCE(b.Backorder, 0) AS Backorder,
    r.Revenue + COALESCE(b.Backorder, 0) AS Production
  FROM RevenueDataWithSuperRegion r
  LEFT JOIN analytics.gold.backorders b
    ON r.Date = b.Date AND r.Category = b.Category
),

-- Step 6: AOP Quarterly Targets
AOP_QuarterlyTarget AS (
  SELECT
    Category,
    SUM(Target) AS QuarterlyTarget
  FROM analytics.gold.aop_q1
  WHERE Category IN ('Total DTC', 'HPS Excl Accessory', 'Total Region X', 'Region 1', 'Region 2')
  GROUP BY Category
),

-- Step 7: Add Rollups to AOP
AOP_With_R12 AS (
  SELECT
    'Region 1 + Region 2' AS Category,
    SUM(QuarterlyTarget) AS QuarterlyTarget
  FROM AOP_QuarterlyTarget
  WHERE Category IN ('Region 1', 'Region 2')

  UNION ALL

  SELECT * FROM AOP_QuarterlyTarget
  WHERE Category IN ('Total DTC', 'HPS Excl Accessory', 'Total Region X')
),

AOP_With_SuperRegion AS (
  SELECT
    'Total Super Region' AS Category,
    SUM(QuarterlyTarget) AS QuarterlyTarget
  FROM AOP_With_R12
  WHERE Category IN ('Total Region X', 'Region 1 + Region 2')

  UNION ALL

  SELECT * FROM AOP_With_R12
),

-- Step 8: Join Targets
RevenueWithTarget AS (
  SELECT
    f.Date,
    f.FY,
    f.Qtr,
    f.Category,
    f.Revenue,
    f.Backorder,
    f.Production,
    a.QuarterlyTarget
  FROM FinalOutput f
  LEFT JOIN AOP_With_SuperRegion a
    ON f.Category = a.Category
),

-- Step 9: Current Quarter
CurrentQtr AS (
  SELECT DISTINCT FISCAL_QTR AS CurrentQtr
  FROM analytics.cdh.dih
  WHERE DAY = CURRENT_DATE()
),

-- Step 10: % Metric Calculation
WithMetric AS (
  SELECT 
    rwt.*,
    MAX(rwt.Revenue) OVER (PARTITION BY rwt.Qtr, rwt.Category) AS MaxRevInQuarter,
    cq.CurrentQtr,
    CASE 
      WHEN rwt.Qtr = cq.CurrentQtr THEN rwt.Production / NULLIF(rwt.QuarterlyTarget, 0)
      ELSE rwt.Production / NULLIF(MAX(rwt.Revenue) OVER (PARTITION BY rwt.Qtr, rwt.Category), 0)
    END AS PercentMetric
  FROM RevenueWithTarget rwt
  CROSS JOIN CurrentQtr cq
),

-- Step 11: Join Week Info
WithMetricWithWeek AS (
  SELECT 
    m.*,
    d.FiscalWeek
  FROM WithMetric m
  LEFT JOIN analytics.gold.date d
    ON m.Date = d.Date
),

-- Step 12: Filter to max Date per FiscalWeek
FinalFiltered AS (
  SELECT *
  FROM (
    SELECT *,
      ROW_NUMBER() OVER (PARTITION BY FY, Qtr, FiscalWeek, Category ORDER BY Date DESC) AS rn
    FROM WithMetricWithWeek
  ) t
  WHERE rn = 1
)

-- Final Output
SELECT
  Date,
  FY,
  Qtr,
  FiscalWeek,
  Category,
  Revenue,
  Backorder,
  Production,
  QuarterlyTarget,
  ROUND(PercentMetric, 3) AS Percent
FROM FinalFiltered
WHERE Category IN (
  'Total DTC',
  'HPS Excl Accessory',
  'Total Region X',
  'Region 1 + Region 2',
  'Total Super Region'
)
ORDER BY Date DESC;
