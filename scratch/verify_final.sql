SET NOCOUNT ON;
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

DECLARE @StartDate DATETIME = '2026-04-01';
DECLARE @EndDate DATETIME = '2026-04-17';

-- Employees to check
DECLARE @EmpTable TABLE (EmpID INT);
INSERT INTO @EmpTable VALUES (362), (304), (341), (368);

PRINT '--- VERIFICATION RESULTS ---';
PRINT 'Comparing RAW Totals (Your Query) vs FILTERED Totals (Dashboard)';
PRINT '';

-- 1. Summary Comparison
SELECT 
    e.field_name AS [Employee],
    COUNT(s.sale_id) AS [Raw_Count],
    SUM(s.Nt_amount) AS [Raw_Total],
    SUM(CASE 
        WHEN s.Cust_name IN ('Wali Jaan Personal Orders', 'Raza Khan M.D', 'Customer Discount 100%', 'Daraksha Mobile 100%', 'DHA Police Discount 100%', 'HNS Product Marketing 100%', 'Home Food Order (Madam)', 'Home Food Orders', 'Home Food Orders (Raza Khan)', 'Home Food Orders (Shehryar Khan)', 'Home Food Orders (Umair Sb)', 'Rangers mobile 100%', 'Return N Cancellation (Aftert Preperation)', 'Return N Cancellation (without preperation)')
          OR s.Additional_Comments IN ('Wali Jaan Personal Orders', '100% Wali bhai', 'Return N Cancellation (Aftert Preperation)', 'Return N Cancellation (without preperation)', '100% Discount Wali Bhai Personal Order', 'Customer Order Change Then Return', 'marketing order in day', 'HNS Product Marketing 100%', 'Mistake')
        THEN 0 ELSE s.Nt_amount END) AS [Filtered_Total],
    SUM(s.Nt_amount) - SUM(CASE 
        WHEN s.Cust_name IN ('Wali Jaan Personal Orders', 'Raza Khan M.D', 'Customer Discount 100%', 'Daraksha Mobile 100%', 'DHA Police Discount 100%', 'HNS Product Marketing 100%', 'Home Food Order (Madam)', 'Home Food Orders', 'Home Food Orders (Raza Khan)', 'Home Food Orders (Shehryar Khan)', 'Home Food Orders (Umair Sb)', 'Rangers mobile 100%', 'Return N Cancellation (Aftert Preperation)', 'Return N Cancellation (without preperation)')
          OR s.Additional_Comments IN ('Wali Jaan Personal Orders', '100% Wali bhai', 'Return N Cancellation (Aftert Preperation)', 'Return N Cancellation (without preperation)', '100% Discount Wali Bhai Personal Order', 'Customer Order Change Then Return', 'marketing order in day', 'HNS Product Marketing 100%', 'Mistake')
        THEN 0 ELSE s.Nt_amount END) AS [Blocked_Difference]
FROM tblSales s WITH (NOLOCK)
INNER JOIN tblDefShopEmployees e WITH (NOLOCK) ON s.employee_id = e.shop_employee_id
WHERE s.sale_date >= @StartDate AND s.sale_date < @EndDate
  AND s.shop_id IN (1, 2, 3, 4, 5, 6, 7)
  AND s.external_ref_type = 'Blinkco order'
  AND e.shop_employee_id IN (SELECT EmpID FROM @EmpTable)
GROUP BY e.field_name
ORDER BY [Raw_Total] DESC;

PRINT '';
PRINT '--- TOP BLOCKED TRANSACTIONS (REASON FOR DIFFERENCE) ---';
SELECT TOP 15
    e.field_name AS [Employee],
    s.Cust_name AS [Blocked_Cust],
    s.Nt_amount AS [Amount],
    s.sale_date
FROM tblSales s WITH (NOLOCK)
INNER JOIN tblDefShopEmployees e WITH (NOLOCK) ON s.employee_id = e.shop_employee_id
WHERE s.sale_date >= @StartDate AND s.sale_date < @EndDate
  AND e.shop_employee_id IN (SELECT EmpID FROM @EmpTable)
  AND s.external_ref_type = 'Blinkco order'
  AND (
      s.Cust_name IN ('Wali Jaan Personal Orders', 'Raza Khan M.D', 'Customer Discount 100%', 'Daraksha Mobile 100%', 'DHA Police Discount 100%', 'HNS Product Marketing 100%', 'Home Food Order (Madam)', 'Home Food Orders', 'Home Food Orders (Raza Khan)', 'Home Food Orders (Shehryar Khan)', 'Home Food Orders (Umair Sb)', 'Rangers mobile 100%', 'Return N Cancellation (Aftert Preperation)', 'Return N Cancellation (without preperation)')
      OR s.Additional_Comments IN ('Wali Jaan Personal Orders', '100% Wali bhai', 'Return N Cancellation (Aftert Preperation)', 'Return N Cancellation (without preperation)', '100% Discount Wali Bhai Personal Order', 'Customer Order Change Then Return', 'marketing order in day', 'HNS Product Marketing 100%', 'Mistake')
  )
ORDER BY s.Nt_amount DESC;
