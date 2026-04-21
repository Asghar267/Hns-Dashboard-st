/*
Create and seed Call Center targets in KDS_DB.
*/

USE [KDS_DB];
GO

IF OBJECT_ID('dbo.call_center_targets', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.call_center_targets (
        id INT IDENTITY(1,1) PRIMARY KEY,
        target_year INT NOT NULL,
        target_month INT NOT NULL,
        sale_point NVARCHAR(100) NOT NULL,
        daily_target DECIMAL(18,2) NOT NULL,
        monthly_target DECIMAL(18,2) NOT NULL,
        status NVARCHAR(20) NOT NULL CONSTRAINT DF_call_center_targets_status DEFAULT ('Active'),
        created_at DATETIME NOT NULL CONSTRAINT DF_call_center_targets_created_at DEFAULT (GETDATE()),
        updated_at DATETIME NULL
    );

    CREATE UNIQUE INDEX UX_call_center_targets_period_point
        ON dbo.call_center_targets(target_year, target_month, sale_point);
END
GO

MERGE dbo.call_center_targets AS tgt
USING (
    SELECT
        2026 AS target_year,
        4 AS target_month,
        N'Call Center' AS sale_point,
        CAST(473333 AS DECIMAL(18,2)) AS daily_target,
        CAST(14200000 AS DECIMAL(18,2)) AS monthly_target,
        N'Active' AS status
) AS src
ON tgt.target_year = src.target_year
AND tgt.target_month = src.target_month
AND tgt.sale_point = src.sale_point
WHEN MATCHED THEN
    UPDATE SET
        tgt.daily_target = src.daily_target,
        tgt.monthly_target = src.monthly_target,
        tgt.status = src.status,
        tgt.updated_at = GETDATE()
WHEN NOT MATCHED THEN
    INSERT (target_year, target_month, sale_point, daily_target, monthly_target, status)
    VALUES (src.target_year, src.target_month, src.sale_point, src.daily_target, src.monthly_target, src.status);
GO
