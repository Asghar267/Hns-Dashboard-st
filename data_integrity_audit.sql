-- SQL Script to Audit Data Integrity for QR Commission and Targets
-- Run this in SQL Server Management Studio (SSMS)

USE Candelahns;
GO

--------------------------------------------------
-- 1. QR COMMISSION AUDIT
--------------------------------------------------

PRINT '--- 1. QR Commission Audit ---';

-- 1.1 Check for sales with Blinkco external_ref_type but missing external_ref_id
PRINT '1.1 Sales with Blinkco type but missing external_ref_id:';
SELECT COUNT(*) as Missing_ID_Count
FROM tblSales
WHERE external_ref_type = 'Blinkco order'
  AND (external_ref_id IS NULL OR LTRIM(RTRIM(CONVERT(VARCHAR(64), external_ref_id))) = '');

-- 1.2 Check for sales with external_ref_id but missing external_ref_type
PRINT '1.2 Sales with external_ref_id but missing/incorrect external_ref_type:';
SELECT external_ref_type, COUNT(*) as Count
FROM tblSales
WHERE external_ref_id IS NOT NULL 
  AND LTRIM(RTRIM(CONVERT(VARCHAR(64), external_ref_id))) <> ''
  AND (external_ref_type <> 'Blinkco order' OR external_ref_type IS NULL)
GROUP BY external_ref_type;

-- 1.3 Check for orphaned external_ref_ids (no match in tblInitialRawBlinkOrder)
PRINT '1.3 Sales with external_ref_id but no matching raw JSON:';
SELECT TOP 10 s.sale_id, s.external_ref_id, s.sale_date
FROM tblSales s
LEFT JOIN dbo.tblInitialRawBlinkOrder rb ON LTRIM(RTRIM(CONVERT(VARCHAR(64), s.external_ref_id))) = LTRIM(RTRIM(CONVERT(VARCHAR(64), rb.BlinkOrderId)))
WHERE s.external_ref_type = 'Blinkco order'
  AND rb.BlinkOrderId IS NULL
ORDER BY s.sale_date DESC;

--------------------------------------------------
-- 2. EMPLOYEE DATA QUALITY
--------------------------------------------------

PRINT '--- 2. Employee Data Quality ---';

-- 2.1 Duplicate field_Code in tblDefShopEmployees
PRINT '2.1 Duplicate field_Code (Employee Codes):';
SELECT field_Code, COUNT(DISTINCT shop_employee_id) as Distinct_IDs
FROM tblDefShopEmployees
WHERE field_Code IS NOT NULL AND LTRIM(RTRIM(field_Code)) <> ''
GROUP BY field_Code
HAVING COUNT(DISTINCT shop_employee_id) > 1;

-- 2.2 Employees with missing field_Code
PRINT '2.2 Employees with missing field_Code:';
SELECT shop_id, COUNT(*) as Missing_Code_Count
FROM tblDefShopEmployees
WHERE field_Code IS NULL OR LTRIM(RTRIM(field_Code)) = ''
GROUP BY shop_id;

--------------------------------------------------
-- 3. TARGETS AUDIT (KDS_DB)
--------------------------------------------------
IF EXISTS (SELECT * FROM sys.databases WHERE name = 'KDS_DB')
BEGIN
    USE KDS_DB;
    PRINT '--- 3. Targets Audit (KDS_DB) ---';

    -- 3.1 Orphaned branch targets (shops not in tblDefShops)
    PRINT '3.1 Branch targets for non-existent shops:';
    SELECT t.shop_id, t.target_year, t.target_month
    FROM dbo.branch_targets t
    LEFT JOIN Candelahns.dbo.tblDefShops s ON t.shop_id = s.shop_id
    WHERE s.shop_id IS NULL;

    -- 3.2 Orphaned OT targets (employees not in tblDefShopEmployees)
    PRINT '3.2 OT targets for non-existent employees:';
    SELECT t.employee_id, t.shop_id
    FROM dbo.ot_targets t
    LEFT JOIN Candelahns.dbo.tblDefShopEmployees e ON t.employee_id = e.shop_employee_id AND t.shop_id = e.shop_id
    WHERE e.shop_employee_id IS NULL;

    -- 3.3 Targets with missing periods (Resolving the audited issue)
    PRINT '3.3 Targets with 0 or NULL amounts:';
    SELECT 'branch' as type, COUNT(*) as count FROM dbo.branch_targets WHERE monthly_target IS NULL OR monthly_target <= 0
    UNION ALL
    SELECT 'chef' as type, COUNT(*) as count FROM dbo.branch_chef_targets WHERE monthly_target IS NULL OR monthly_target <= 0
    UNION ALL
    SELECT 'ot' as type, COUNT(*) as count FROM dbo.ot_targets WHERE monthly_target IS NULL OR monthly_target <= 0;
END
GO
