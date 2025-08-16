CREATE OR REPLACE TABLE analytics.gold.date
USING DELTA
AS
WITH max_selling_days_per_quarter AS (
    SELECT
        FIRST_DAY_IN_FISCAL_QTR,
        MAX(FISCAL_QTR_WORK_DAY_NO) AS SellingDaysInQuarter
    FROM analytics.gold.date
    GROUP BY FIRST_DAY_IN_FISCAL_QTR
),

current_with_selling_days_left AS (
    SELECT
        d1.*,
        sdq.SellingDaysInQuarter,
        (sdq.SellingDaysInQuarter - d1.FISCAL_QTR_WORK_DAY_NO) AS SellingDaysLeft
    FROM analytics.gold.date d1
    LEFT JOIN max_selling_days_per_quarter sdq
        ON d1.FIRST_DAY_IN_FISCAL_QTR = sdq.FIRST_DAY_IN_FISCAL_QTR
),

prior_with_selling_days_left_ranked AS (
    SELECT
        d3.DAY AS PriorQuarterDate,
        d3.FIRST_DAY_IN_FISCAL_QTR AS PriorQuarterStart,
        MAX(d4.FISCAL_QTR_WORK_DAY_NO) OVER (PARTITION BY d3.FIRST_DAY_IN_FISCAL_QTR) AS PriorSellingDaysInQuarter,
        (MAX(d4.FISCAL_QTR_WORK_DAY_NO) OVER (PARTITION BY d3.FIRST_DAY_IN_FISCAL_QTR) - d3.FISCAL_QTR_WORK_DAY_NO) AS PriorSellingDaysLeft,
        ROW_NUMBER() OVER (
            PARTITION BY d3.FIRST_DAY_IN_FISCAL_QTR, 
                         (MAX(d4.FISCAL_QTR_WORK_DAY_NO) OVER (PARTITION BY d3.FIRST_DAY_IN_FISCAL_QTR) - d3.FISCAL_QTR_WORK_DAY_NO)
            ORDER BY d3.DAY
        ) AS rn
    FROM analytics.gold.date d3
    LEFT JOIN analytics.gold.date d4
        ON d3.FIRST_DAY_IN_FISCAL_QTR = d4.FIRST_DAY_IN_FISCAL_QTR
),

prior_with_selling_days_left AS (
    SELECT *
    FROM prior_with_selling_days_left_ranked
    WHERE rn = 1
),

dates_with_extras AS (
    SELECT
        d1.DAY,
        CONCAT('Q', CAST(RIGHT(d1.FISCAL_QTR, 1) AS STRING), ' Wk', CAST(d1.FIS_WK_IN_QTR_NO AS STRING)) AS QuarterWeek,
        DATE_FORMAT(d1.DAY, 'E') AS Weekday,
        CASE 
            WHEN pmod(DAYOFWEEK(d1.DAY) + 5, 7) + 1 IN (6, 7) THEN FALSE
            ELSE TRUE
        END AS IsSellingDay
    FROM current_with_selling_days_left d1
)

SELECT
    CAST(d1.DAY AS DATE) AS Date,
    CAST(RIGHT(d1.FISCAL_YEAR, 4) AS INT) AS FiscalYear,
    d1.FISCAL_QTR AS FiscalQuarter,
    CAST(RIGHT(d1.FISCAL_QTR, 1) AS INT) AS FiscalQuarterNumber,
    d1.FISCAL_MONTH_NO AS FiscalMonthNumber,
    d1.FISCAL_MONTH AS FiscalMonthName,
    d1.FIS_WK_IN_QTR_NO AS FiscalWeek,
    d1.FISCAL_DAY_NO AS FiscalDayNumber,

    dte.QuarterWeek,
    dte.Weekday,
    dte.IsSellingDay,

    d1.FISCAL_QTR_WORK_DAY_NO AS SellingDays,
    d1.SellingDaysInQuarter,
    ROUND((d1.FISCAL_QTR_WORK_DAY_NO / NULLIF(d1.SellingDaysInQuarter, 0)) * 100, 1) AS PercentCompleteInFiscalQuarter,

    d1.SellingDaysLeft,

    d1.FIRST_DAY_IN_FISCAL_QTR AS FirstDayInFiscalQuarter,
    d1.FIRST_DAY_IN_PREV_FISCAL_QTR AS FirstDayInPreviousFiscalQuarter,

    d1.LAST_YEAR_DAY_US AS PriorYearDate,
    d2.FIRST_DAY_IN_FISCAL_QTR AS FirstDayInPriorFiscalYearFiscalQuarter,

    d3.PriorQuarterDate AS PriorQuarterDateWithSameSellingDaysLeft

FROM current_with_selling_days_left d1

LEFT JOIN analytics.gold.date d2
    ON d1.LAST_YEAR_DAY_US = d2.DAY

LEFT JOIN prior_with_selling_days_left d3
    ON d1.FIRST_DAY_IN_PREV_FISCAL_QTR = d3.PriorQuarterStart
    AND d1.SellingDaysLeft = d3.PriorSellingDaysLeft

LEFT JOIN dates_with_extras dte
    ON d1.DAY = dte.DAY

WHERE d1.FISCAL_YEAR IN ('FY2024', 'FY2025', 'FY2026', 'FY2027', 'FY2028')

ORDER BY Date DESC;
