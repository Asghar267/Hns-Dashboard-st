-- SQL Query to get total sales of employees with and without Blinko sales or external ref IDs within a date range
-- This query provides comprehensive sales analysis including:
-- - Total sales for each employee
-- - Sales with Blinkco orders (external_ref_type = 'Blinkco order')
-- - Sales without Blinkco orders
-- - External reference ID details
-- - Branch information
-- - Employment status within the date range

DECLARE @start_date DATE = '2026-01-01'; -- Replace with desired start date
DECLARE @end_date DATE = '2026-01-31';   -- Replace with desired end date

WITH EmployeeSales AS (
    SELECT
        s.shop_id,
        sh.shop_name,
        COALESCE(e.shop_employee_id, 0) AS employee_id,
        LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
        COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
        s.sale_date,
        s.Nt_amount AS total_sale,
        s.external_ref_id,
        s.external_ref_type,
        CASE 
            WHEN s.external_ref_type = 'Blinkco order' THEN 1 
            ELSE 0 
        END AS is_blinkco_order,
        CASE 
            WHEN s.external_ref_type = 'Blinkco order' THEN s.Nt_amount 
            ELSE 0 
        END AS blinkco_sale_amount,
        CASE 
            WHEN s.external_ref_type <> 'Blinkco order' OR s.external_ref_type IS NULL THEN s.Nt_amount 
            ELSE 0 
        END AS non_blinkco_sale_amount
    FROM tblSales s
    LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
    LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
    WHERE s.sale_date BETWEEN @start_date AND @end_date
),
EmployeeEmployment AS (
    SELECT
        shop_employee_id,
        field_name,
        start_date AS employment_start_date,
        end_date AS employment_end_date
    FROM tblDefShopEmployees
    WHERE field_name NOT IN ('online/unassigned')
)
SELECT
    es.shop_id,
    es.shop_name,
    es.employee_id,
    es.employee_code,
    es.employee_name,
    COUNT(DISTINCT es.sale_date) AS total_sales_days,
    COUNT(DISTINCT es.sale_id) AS total_transactions,
    SUM(es.total_sale) AS total_sales_amount,
    SUM(es.blinkco_sale_amount) AS total_blinkco_sales,
    SUM(es.non_blinkco_sale_amount) AS total_non_blinkco_sales,
    COUNT(CASE WHEN es.is_blinkco_order = 1 THEN 1 END) AS blinkco_transactions,
    COUNT(CASE WHEN es.is_blinkco_order = 0 THEN 1 END) AS non_blinkco_transactions,
    COUNT(DISTINCT es.external_ref_id) AS total_external_ref_ids,
    COUNT(DISTINCT CASE WHEN es.is_blinkco_order = 1 THEN es.external_ref_id END) AS blinkco_external_ref_ids,
    COUNT(DISTINCT CASE WHEN es.is_blinkco_order = 0 THEN es.external_ref_id END) AS non_blinkco_external_ref_ids,
    MIN(es.sale_date) AS first_sale_date,
    MAX(es.sale_date) AS last_sale_date,
    AVG(es.total_sale) AS avg_daily_sales,
    CASE 
        WHEN ee.employment_start_date IS NOT NULL 
        AND ee.employment_end_date IS NOT NULL 
        AND ee.employment_start_date <= @end_date 
        AND (ee.employment_end_date >= @start_date OR ee.employment_end_date IS NULL) 
        THEN 'Active'
        ELSE 'Inactive'
    END AS employment_status
FROM EmployeeSales es
LEFT JOIN EmployeeEmployment ee ON es.employee_id = ee.shop_employee_id AND es.employee_name = ee.field_name
GROUP BY
    es.shop_id,
    es.shop_name,
    es.employee_id,
    es.employee_code,
    es.employee_name,
    CASE 
        WHEN ee.employment_start_date IS NOT NULL 
        AND ee.employment_end_date IS NOT NULL 
        AND ee.employment_start_date <= @end_date 
        AND (ee.employment_end_date >= @start_date OR ee.employment_end_date IS NULL) 
        THEN 'Active'
        ELSE 'Inactive'
    END
ORDER BY
    total_sales_amount DESC,
    es.shop_name,
    es.employee_name;