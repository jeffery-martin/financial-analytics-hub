-- Create (or overwrite) a new Delta table named 'conversion_by_territory' to store our results
CREATE OR REPLACE TABLE analytics.gold.conversion_by_territory
USING DELTA
AS

-- Step 1: Pull detailed order data from the system and standardize it
WITH BaseData AS (
    SELECT
        t.FISCAL_YEAR_ID AS FiscalYear,
        t.FIS_WK_IN_QTR_NO AS FiscalWeek,
        RIGHT(t.FISCAL_QTR_ID, 1) AS FiscalQuarter,
        CASE 
            WHEN opp.COMMISSION_CLASS_CODE = 'NEW_STANDARD' THEN 'NEW_STANDARD'
            WHEN opp.COMMISSION_CLASS_CODE = 'COMPETITIVE_UPGRADE' THEN 'COMPETITIVE_UPGRADE'
            WHEN opp.COMMISSION_CLASS_CODE = 'ACCESS_PROGRAM' THEN 'ACCESS_PROGRAM'
            WHEN opp.COMMISSION_CLASS_CODE = 'OTHER_PROGRAM' THEN 'OTHER_PROGRAM'
            WHEN opp.COMMISSION_CLASS_CODE = 'UPGRADE' THEN 'UPGRADE'
            ELSE 'OTHER'
        END AS Conversion_Type,
        opp.conv_count,
        LEFT(l.region, LENGTH(l.region) - 9) AS region,
        l.district,
        l.territory
    FROM analytics.gold.order_header opp
    INNER JOIN analytics.gold.pipeline_conversions t 
        ON CAST(opp.conv_date AS DATE) = CAST(t.DAY AS DATE)
    INNER JOIN analytics.gold.location l 
        ON opp.LOCATION_ID = l.LOCATION_ID
    WHERE 
        opp.COMMISSION_CLASS_CODE IS NOT NULL
        AND t.FISCAL_QTR_REL = 0
),

-- Step 2: Group the data by week and territory for "NEW_STANDARD" conversion types, and sum the volumes
Aggregated AS (
    SELECT
        region,
        district,
        territory,
        Conversion_Type,
        FiscalYear,
        FiscalQuarter,
        FiscalWeek,
        SUM(conv_count) AS Volume
    FROM BaseData
    WHERE Conversion_Type = 'NEW_STANDARD'
    GROUP BY region, district, territory, Conversion_Type, FiscalYear, FiscalQuarter, FiscalWeek
),

-- Step 3: For each region/district/territory and quarter, calculate average weekly volume (Quarter-To-Date)
FinalQTD AS (
    SELECT 
        region,
        district,
        territory,
        Conversion_Type,
        FiscalYear,
        FiscalQuarter,
        AVG(Volume) AS AvgVolumePerWeekQTD
    FROM Aggregated
    GROUP BY region, district, territory, Conv_Type, FiscalYear, FiscalQuarter
),

-- Step 4: For each region/district/territory and year, calculate average weekly volume (Year-To-Date)
FinalYTD AS (
    SELECT 
        region,
        district,
        territory,
        Conv_Type,
        FiscalYear,
        AVG(Volume) AS AvgVolumePerWeekYTD
    FROM Aggregated
    GROUP BY region, district, territory, Conv_Type, FiscalYear
)

-- Step 5: Join QTD and YTD results together and flag whether each territory meets the performance threshold
SELECT 
    q.region AS Region,
    q.district AS District,
    q.territory AS Territory,
    q.Conv_Type AS Type,
    q.FiscalYear,
    q.FiscalQuarter,
    q.AvgVolumePerWeekQTD,
    y.AvgVolumePerWeekYTD,
    CASE 
        WHEN q.AvgVolumePerWeekQTD >= 5.3 THEN 'Meets Threshold'
        ELSE 'Below Threshold'
    END AS BreakevenQTD,
    CASE 
        WHEN y.AvgVolumePerWeekYTD >= 5.3 THEN 'Meets Threshold'
        ELSE 'Below Threshold'
    END AS BreakevenYTD
FROM FinalQTD q
LEFT JOIN FinalYTD y
  ON q.region = y.region
  AND q.district = y.district
  AND q.territory = y.territory
  AND q.Conv_Type = y.Conv_Type
  AND q.FiscalYear = y.FiscalYear;
