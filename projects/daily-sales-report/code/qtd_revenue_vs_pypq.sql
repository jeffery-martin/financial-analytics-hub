CREATE OR REPLACE TABLE analytics.gold.qtd_rev_vs_pypq
USING DELTA
AS

-- STEP 1: Build a unified, categorized revenue dataset
WITH ProductCategoryMapping AS (

  -- 1a. Categorize product lines from SAP-reported data
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
    Revenue AS Revenue
  FROM analytics.gold.sap_data
  WHERE PRODUCT_GROUP != 'Product 1'
    AND FISCAL_YEAR IN ('FY2024', 'FY2025', 'FY2026')

  UNION ALL

  -- 1b. Split Product 1 revenue into New Product
  SELECT
    DATEADD(pbd.SNAPSHOT_DATE, -1) AS Date,
    pbd.FISCAL_YEAR AS FY,
    pbd.FISCAL_QTR AS Qtr,
    'DTC New Product' AS Category,
    (pbd.Revenue * (split.Percent_NewProduct_QTD / 100)) AS Revenue
  FROM analytics.gold.sap_data pbd
  LEFT JOIN analytics.gold.dtc_product_qtd_split split
    ON DATEADD(pbd.SNAPSHOT_DATE, -1) = split.PIPELINE_DATE
  WHERE pbd.PRODUCT_GROUP = 'Product 1'
    AND pbd.FISCAL_YEAR IN ('FY2024', 'FY2025', 'FY2026')

  UNION ALL

  -- 1c. LY Product
  SELECT
    DATEADD(pbd.SNAPSHOT_DATE, -1) AS Date,
    pbd.FISCAL_YEAR AS FY,
    pbd.FISCAL_QTR AS Qtr,
    'DTC LY Product' AS Category,
    (pbd.Revenue * (split.Percent_LYProduct_QTD / 100)) AS Revenue
  FROM analytics.gold.sap_data pbd
  LEFT JOIN analytics.gold.dtc_product_qtd_split split
    ON DATEADD(pbd.SNAPSHOT_DATE, -1) = split.PIPELINE_DATE
  WHERE pbd.PRODUCT_GROUP = 'Product 1'
    AND pbd.FISCAL_YEAR IN ('FY2024', 'FY2025', 'FY2026')

  UNION ALL

  -- 1d. Regional markets
  SELECT
    Date,
    FiscalYear AS FY,
    FiscalQuarter AS Qtr,
    Category,
    Revenue
  FROM analytics.gold.qtd_rev_r12
  WHERE FiscalYear IN ('FY2024', 'FY2025', 'FY2026')
),

-- STEP 2: Revenue roll-ups
RevenueDataBase AS (
  SELECT
    Date, FY, Qtr, Category,
    SUM(Revenue) AS Revenue
  FROM ProductCategoryMapping
  WHERE Category IS NOT NULL
  GROUP BY Date, FY, Qtr, Category

  UNION ALL

  -- 2b. Direct "Total DTC" from raw data
  SELECT
    DATEADD(SNAPSHOT_DATE, -1) AS Date,
    FISCAL_YEAR AS FY,
    FISCAL_QTR AS Qtr,
    'Total DTC' AS Category,
    SUM(Revenue)
  FROM analytics.gold.sap_data
  WHERE (PRODUCT_GROUP LIKE 'DTC%' OR PRODUCT_GROUP = 'HPS Accessory')
    AND FISCAL_YEAR IN ('FY2024', 'FY2025', 'FY2026')
  GROUP BY Date, FY, Qtr

  UNION ALL

  -- 2c. Region X
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

-- STEP 3: Add Total Super Region
RevenueData AS (
  SELECT * FROM RevenueDataBase
  UNION ALL
  SELECT
    Date, FY, Qtr, 'Total Super Region' AS Category,
    SUM(Revenue)
  FROM RevenueDataBase
  WHERE Category IN ('Total Region X', 'Region 1', 'Region 2')
  GROUP BY Date, FY, Qtr
),

-- STEP 4: Enhanced date logic
EnhancedDateTable AS (
  WITH max_selling_days_per_quarter AS (
    SELECT FIRST_DAY_IN_FISCAL_QTR, MAX(FISCAL_QTR_WORK_DAY_NO) AS SellingDaysInQuarter
    FROM analytics.gold.date
    GROUP BY FIRST_DAY_IN_FISCAL_QTR
  ),
  current_with_selling_days AS (
    SELECT d1.*, sdq.SellingDaysInQuarter
    FROM analytics.gold.date d1
    LEFT JOIN max_selling_days_per_quarter sdq
      ON d1.FIRST_DAY_IN_FISCAL_QTR = sdq.FIRST_DAY_IN_FISCAL_QTR
  ),
  prior_with_selling_days AS (
    SELECT d3.DAY AS PriorQuarterDate, d3.FIRST_DAY_IN_FISCAL_QTR AS PriorQuarterStart, d3.FISCAL_QTR_WORK_DAY_NO AS SellingDays
    FROM analytics.gold.date d3
  ),
  dates_with_extras AS (
    SELECT
      d1.DAY,
      CONCAT('Q', CAST(RIGHT(d1.FISCAL_QTR, 1) AS STRING), ' Wk', CAST(d1.FIS_WK_IN_QTR_NO AS STRING)) AS QuarterWeek,
      DATE_FORMAT(d1.DAY, 'E') AS Weekday,
      CASE WHEN pmod(DAYOFWEEK(d1.DAY) + 5, 7) + 1 IN (6, 7) THEN FALSE ELSE TRUE END AS IsSellingDay
    FROM current_with_selling_days d1
  )
  SELECT
    CAST(d1.DAY AS DATE) AS Date,
    d1.FISCAL_YEAR AS FiscalYear,
    d1.FISCAL_QTR AS FiscalQuarter,
    d1.FISCAL_QTR_WORK_DAY_NO AS SellingDays,
    d1.FIRST_DAY_IN_PREV_FISCAL_QTR AS FirstDayInPreviousFiscalQuarter,
    d1.LAST_YEAR_DAY_US AS PriorYearDate,
    d3.PriorQuarterDate AS PriorQuarterDateWithSameSellingDays
  FROM current_with_selling_days d1
  LEFT JOIN prior_with_selling_days d3
    ON d1.FIRST_DAY_IN_PREV_FISCAL_QTR = d3.PriorQuarterStart
    AND d1.FISCAL_QTR_WORK_DAY_NO = d3.SellingDays
  LEFT JOIN dates_with_extras dte
    ON d1.DAY = dte.DAY
  WHERE d1.FISCAL_YEAR IN ('FY2024', 'FY2025', 'FY2026')
),

-- STEP 5: Final revenue + variance build
FinalRevenue AS (
  SELECT
    r.Date,
    r.FY,
    r.Qtr,
    edt.SellingDays,
    r.Category,
    r.Revenue,
    b.Backorder, 
    (r.Revenue + b.Backorder) AS Production,
    pq.Revenue AS PriorQuarterRevenue,
    py.Revenue AS PriorYearRevenue,
    (r.Revenue - pq.Revenue) AS RevenueVsPriorQuarter,
    (r.Revenue - py.Revenue) AS RevenueVsPriorYear,
    ROUND((r.Revenue - pq.Revenue) / NULLIF(pq.Revenue, 0) * 100, 1) AS RevenueVsPriorQuarterPercent,
    ROUND((r.Revenue - py.Revenue) / NULLIF(py.Revenue, 0) * 100, 1) AS RevenueVsPriorYearPercent
  FROM RevenueData r
  LEFT JOIN analytics.gold.backorders b
    ON r.Date = b.Date AND r.Category = b.Category
  LEFT JOIN EnhancedDateTable edt
    ON r.Date = edt.Date
  LEFT JOIN RevenueData pq
    ON edt.PriorQuarterDateWithSameSellingDays = pq.Date AND r.Category = pq.Category
  LEFT JOIN RevenueData py
    ON edt.PriorYearDate = py.Date AND r.Category = py.Category
)

-- STEP 6: Final output
SELECT *
FROM FinalRevenue
WHERE SellingDays IS NOT NULL
ORDER BY Date DESC;