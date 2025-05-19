CREATE OR REPLACE TABLE analytics.gold.backorders
USING DELTA
AS

WITH ProductCategoryMapping AS (

  SELECT
    DATEADD(b.SNAPSHOT_DATE, -1) AS Date,
    d.FISCAL_YEAR AS FY,
    d.FISCAL_QTR AS Qtr,
    CASE 
      WHEN CHANNEL = 'DTC' AND PRODUCT IN ('Product A', 'Product B', 'other product') THEN 'DTC Product 2'
      WHEN CHANNEL = 'DTC' AND PRODUCT IN ('Product C', 'Product D', 'Other acc') THEN 'DTC Product 3'
      WHEN CHANNEL = 'DTC' AND PRODUCT = 'X9 Sensor' THEN 'DTC X9'
      WHEN (CHANNEL = 'DTC' OR CHANNEL = 'HPS') AND PRODUCT = 'Accessory' THEN 'DTC Accessory'
      WHEN CHANNEL = 'DTC' AND PRODUCT IN ('other', 'software') THEN 'DTC Other'
      WHEN CHANNEL = 'HPS' AND PRODUCT != 'Accessory' THEN 'HPS Excl Accessory'
      ELSE NULL
    END AS Category,
    (ORDER_QUANTITY - SHIPPED_QUANTITY_TODAY) * UNIT_PRICE AS Backorder
  FROM analytics.gold.eod_open_orders b
  JOIN analytics.gold.date d
    ON d.day = DATEADD(b.SNAPSHOT_DATE, -1)
  WHERE d.FISCAL_YEAR IN ('FY2024', 'FY2025', 'FY2026')
    AND PRODUCT != 'Product 1'

  UNION ALL

  SELECT
    DATEADD(b.SNAPSHOT_DATE, -1) AS Date,
    d.FISCAL_YEAR AS FY,
    d.FISCAL_QTR AS Qtr,
    'DTC New Product' AS Category,
    ((ORDER_QUANTITY - SHIPPED_QUANTITY_TODAY) * UNIT_PRICE * (split.Percent_NewProduct_QTD / 100)) AS Backorder
  FROM analytics.gold.eod_open_orders b
  JOIN analytics.gold.date d
    ON d.day = DATEADD(b.SNAPSHOT_DATE, -1)
  LEFT JOIN analytics.gold.dtc_product_qtd_split split
    ON DATEADD(b.SNAPSHOT_DATE, -1) = split.PIPELINE_DATE
  WHERE d.FISCAL_YEAR IN ('FY2024', 'FY2025', 'FY2026')
    AND PRODUCT = 'Product 1'
    AND CHANNEL = 'DTC'

  UNION ALL

  SELECT
    DATEADD(b.SNAPSHOT_DATE, -1) AS Date,
    d.FISCAL_YEAR AS FY,
    d.FISCAL_QTR AS Qtr,
    'DTC LY Product' AS Category,
    ((ORDER_QUANTITY - SHIPPED_QUANTITY_TODAY) * UNIT_PRICE * (split.Percent_LYProduct_QTD / 100)) AS Backorder
  FROM analytics.gold.eod_open_orders b
  JOIN analytics.gold.date d
    ON d.day = DATEADD(b.SNAPSHOT_DATE, -1)
  LEFT JOIN analytics.gold.dtc_product_qtd_split split
    ON DATEADD(b.SNAPSHOT_DATE, -1) = split.PIPELINE_DATE
  WHERE d.FISCAL_YEAR IN ('FY2024', 'FY2025', 'FY2026')
    AND PRODUCT = 'Product 1'
    AND CHANNEL = 'DTC'

),

DistinctDates AS (
  SELECT DISTINCT Date, FY, Qtr
  FROM ProductCategoryMapping
  WHERE Category IS NOT NULL
),

BackorderBasePreTotals AS (
  SELECT
    Date,
    FY,
    Qtr,
    Category,
    SUM(Backorder) AS Backorder
  FROM ProductCategoryMapping
  WHERE Category IS NOT NULL
  GROUP BY Date, FY, Qtr, Category
),

BackorderWithTotalDTC AS (
  SELECT * FROM BackorderBasePreTotals

  UNION ALL

  SELECT
    Date,
    FY,
    Qtr,
    'Total DTC' AS Category,
    SUM(Backorder) AS Backorder
  FROM BackorderBasePreTotals
  WHERE Category IN (
    'DTC Product 2', 'DTC Product 3', 'DTC X9', 'DTC Accessory', 'DTC Other', 'DTC New Product', 'DTC LY Product'
  )
  GROUP BY Date, FY, Qtr
),

BackorderBase AS (
  SELECT * FROM BackorderWithTotalDTC

  UNION ALL

  SELECT
    Date,
    FY,
    Qtr,
    'Total Region X' AS Category,
    SUM(Backorder) AS Backorder
  FROM BackorderWithTotalDTC
  WHERE Category IN ('Total DTC', 'HPS Excl Accessory')
  GROUP BY Date, FY, Qtr
),

DummyRegionBackorders AS (
  SELECT Date, FY, Qtr, 'Region 1' AS Category, 0.0 AS Backorder FROM DistinctDates
  UNION ALL
  SELECT Date, FY, Qtr, 'Region 2' AS Category, 0.0 AS Backorder FROM DistinctDates
),

TotalSuperRegionBackorder AS (
  SELECT
    Date,
    FY,
    Qtr,
    'Total Super Region' AS Category,
    SUM(Backorder) AS Backorder
  FROM (
    SELECT * FROM BackorderBase WHERE Category = 'Total Region X'
    UNION ALL
    SELECT * FROM DummyRegionBackorders
  )
  GROUP BY Date, FY, Qtr
)

SELECT
  Date,
  FY,
  Qtr,
  Category,
  COALESCE(Backorder, 0.0) AS Backorder
FROM (
  SELECT * FROM BackorderBase
  UNION ALL
  SELECT * FROM DummyRegionBackorders
  UNION ALL
  SELECT * FROM TotalSuperRegionBackorder
)
ORDER BY Date DESC;

CREATE OR REPLACE TABLE analytics.gold.backorders
USING DELTA
AS

WITH ProductCategoryMapping AS (

  SELECT
    DATEADD(b.SNAPSHOT_DATE, -1) AS Date,
    d.FISCAL_YEAR AS FY,
    d.FISCAL_QTR AS Qtr,
    CASE 
      WHEN CHANNEL = 'DTC' AND PRODUCT IN ('Product A', 'Product B', 'other product') THEN 'DTC Product 2'
      WHEN CHANNEL = 'DTC' AND PRODUCT IN ('Product C', 'Product D', 'Other acc') THEN 'DTC Product 3'
      WHEN CHANNEL = 'DTC' AND PRODUCT = 'X9 Sensor' THEN 'DTC X9'
      WHEN (CHANNEL = 'DTC' OR CHANNEL = 'HPS') AND PRODUCT = 'Accessory' THEN 'DTC Accessory'
      WHEN CHANNEL = 'DTC' AND PRODUCT IN ('other', 'software') THEN 'DTC Other'
      WHEN CHANNEL = 'HPS' AND PRODUCT != 'Accessory' THEN 'HPS Excl Accessory'
      ELSE NULL
    END AS Category,
    (ORDER_QUANTITY - SHIPPED_QUANTITY_TODAY) * UNIT_PRICE AS Backorder
  FROM analytics.gold.eod_open_orders b
  JOIN analytics.gold.date d
    ON d.day = DATEADD(b.SNAPSHOT_DATE, -1)
  WHERE d.FISCAL_YEAR IN ('FY2024', 'FY2025', 'FY2026')
    AND PRODUCT != 'Product 1'

  UNION ALL

  SELECT
    DATEADD(b.SNAPSHOT_DATE, -1) AS Date,
    d.FISCAL_YEAR AS FY,
    d.FISCAL_QTR AS Qtr,
    'DTC New Product' AS Category,
    ((ORDER_QUANTITY - SHIPPED_QUANTITY_TODAY) * UNIT_PRICE * (split.Percent_NewProduct_QTD / 100)) AS Backorder
  FROM analytics.gold.eod_open_orders b
  JOIN analytics.gold.date d
    ON d.day = DATEADD(b.SNAPSHOT_DATE, -1)
  LEFT JOIN analytics.gold.dtc_product_qtd_split split
    ON DATEADD(b.SNAPSHOT_DATE, -1) = split.PIPELINE_DATE
  WHERE d.FISCAL_YEAR IN ('FY2024', 'FY2025', 'FY2026')
    AND PRODUCT = 'Product 1'
    AND CHANNEL = 'DTC'

  UNION ALL

  SELECT
    DATEADD(b.SNAPSHOT_DATE, -1) AS Date,
    d.FISCAL_YEAR AS FY,
    d.FISCAL_QTR AS Qtr,
    'DTC LY Product' AS Category,
    ((ORDER_QUANTITY - SHIPPED_QUANTITY_TODAY) * UNIT_PRICE * (split.Percent_LYProduct_QTD / 100)) AS Backorder
  FROM analytics.gold.eod_open_orders b
  JOIN analytics.gold.date d
    ON d.day = DATEADD(b.SNAPSHOT_DATE, -1)
  LEFT JOIN analytics.gold.dtc_product_qtd_split split
    ON DATEADD(b.SNAPSHOT_DATE, -1) = split.PIPELINE_DATE
  WHERE d.FISCAL_YEAR IN ('FY2024', 'FY2025', 'FY2026')
    AND PRODUCT = 'Product 1'
    AND CHANNEL = 'DTC'

),

DistinctDates AS (
  SELECT DISTINCT Date, FY, Qtr
  FROM ProductCategoryMapping
  WHERE Category IS NOT NULL
),

BackorderBasePreTotals AS (
  SELECT
    Date,
    FY,
    Qtr,
    Category,
    SUM(Backorder) AS Backorder
  FROM ProductCategoryMapping
  WHERE Category IS NOT NULL
  GROUP BY Date, FY, Qtr, Category
),

BackorderWithTotalDTC AS (
  SELECT * FROM BackorderBasePreTotals

  UNION ALL

  SELECT
    Date,
    FY,
    Qtr,
    'Total DTC' AS Category,
    SUM(Backorder) AS Backorder
  FROM BackorderBasePreTotals
  WHERE Category IN (
    'DTC Product 2', 'DTC Product 3', 'DTC X9', 'DTC Accessory', 'DTC Other', 'DTC New Product', 'DTC LY Product'
  )
  GROUP BY Date, FY, Qtr
),

BackorderBase AS (
  SELECT * FROM BackorderWithTotalDTC

  UNION ALL

  SELECT
    Date,
    FY,
    Qtr,
    'Total Region X' AS Category,
    SUM(Backorder) AS Backorder
  FROM BackorderWithTotalDTC
  WHERE Category IN ('Total DTC', 'HPS Excl Accessory')
  GROUP BY Date, FY, Qtr
),

DummyRegionBackorders AS (
  SELECT Date, FY, Qtr, 'Region 1' AS Category, 0.0 AS Backorder FROM DistinctDates
  UNION ALL
  SELECT Date, FY, Qtr, 'Region 2' AS Category, 0.0 AS Backorder FROM DistinctDates
),

TotalSuperRegionBackorder AS (
  SELECT
    Date,
    FY,
    Qtr,
    'Total Super Region' AS Category,
    SUM(Backorder) AS Backorder
  FROM (
    SELECT * FROM BackorderBase WHERE Category = 'Total Region X'
    UNION ALL
    SELECT * FROM DummyRegionBackorders
  )
  GROUP BY Date, FY, Qtr
)

SELECT
  Date,
  FY,
  Qtr,
  Category,
  COALESCE(Backorder, 0.0) AS Backorder
FROM (
  SELECT * FROM BackorderBase
  UNION ALL
  SELECT * FROM DummyRegionBackorders
  UNION ALL
  SELECT * FROM TotalSuperRegionBackorder
)
ORDER BY Date DESC;
