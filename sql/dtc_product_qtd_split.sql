CREATE OR REPLACE TABLE analytics.gold.dtc_product_qtd_split
USING DELTA
AS

WITH DailyCounts AS (
    SELECT 
        CAST(PIPELINE_DATE as DATE) as PIPELINE_DATE,
        PIPELINE_WEEK,
        PIPELINE_MONTH,
        PIPELINE_QTR,
        PIPELINE_YEAR,
        SUM(CASE WHEN COMMISSION_CLASS_CODE != 'UPGRADE' AND Channel = 'DTC' THEN PIPELINE_COUNT ELSE 0 END) as NewProduct_Count,
        SUM(CASE WHEN COMMISSION_CLASS_CODE = 'UPGRADE' AND Channel = 'DTC' THEN PIPELINE_COUNT ELSE 0 END) as LYProduct_Count,
        SUM(CASE WHEN Channel = 'DTC' THEN PIPELINE_COUNT ELSE 0 END) as Total_DTC_Count
    FROM bizops.gold.commops_sales_order_and_processing_details
    WHERE COMMISSION_CLASS_CODE IN ('NEW_STANDARD', 'COMPETITIVE_UPGRADE', 'ACCESS_PROGRAM', 'OTHER_PROGRAM', 'UPGRADE')
    GROUP BY
        PIPELINE_DATE,
        PIPELINE_WEEK,
        PIPELINE_MONTH,
        PIPELINE_QTR,
        PIPELINE_YEAR
),

CumulativeQTD AS (
    SELECT
        PIPELINE_DATE,
        PIPELINE_WEEK,
        PIPELINE_MONTH,
        PIPELINE_QTR,
        PIPELINE_YEAR,
        NewProduct_Count,
        LYProduct_Count,
        Total_DTC_Count,
        SUM(NewProduct_Count) OVER (
            PARTITION BY PIPELINE_YEAR, PIPELINE_QTR 
            ORDER BY PIPELINE_DATE
        ) AS QTD_NewProduct_Cumulative,
        SUM(LYProduct_Count) OVER (
            PARTITION BY PIPELINE_YEAR, PIPELINE_QTR 
            ORDER BY PIPELINE_DATE
        ) AS QTD_LYProduct_Cumulative
    FROM DailyCounts
)

SELECT
    PIPELINE_DATE,
    PIPELINE_WEEK,
    PIPELINE_MONTH,
    PIPELINE_QTR,
    PIPELINE_YEAR,
    NewProduct_Count,
    LYProduct_Count,
    Total_DTC_Count,
    QTD_NewProduct_Cumulative,
    QTD_LYProduct_Cumulative,
    ROUND(100.0 * QTD_NewProduct_Cumulative / NULLIF(QTD_NewProduct_Cumulative + QTD_LYProduct_Cumulative,0),2) AS Percent_NewProduct_QTD,
    ROUND(100.0 * QTD_LYProduct_Cumulative / NULLIF(QTD_NewProduct_Cumulative + QTD_LYProduct_Cumulative,0),2) AS Percent_LYProduct_QTD
FROM CumulativeQTD
ORDER BY PIPELINE_DATE DESC;
