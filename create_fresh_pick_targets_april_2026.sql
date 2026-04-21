/*
Create/upgrade and seed Fresh Pick quantity targets in KDS_DB.

This script is idempotent:
- Creates dbo.fresh_pick_targets if missing.
- Adds target_year/target_month columns if the table already exists but lacks them.
- Upserts April 2026 targets by (target_year, target_month, vendor, product_name).
*/

USE [KDS_DB];
GO

IF OBJECT_ID('dbo.fresh_pick_targets', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.fresh_pick_targets (
        id INT IDENTITY(1,1) PRIMARY KEY,
        target_year INT NOT NULL,
        target_month INT NOT NULL,
        customer_name NVARCHAR(150) NOT NULL,
        product_name NVARCHAR(200) NOT NULL,
        monthly_target_qty DECIMAL(18,2) NOT NULL,
        daily_target_qty DECIMAL(18,2) NOT NULL,
        status NVARCHAR(20) NOT NULL CONSTRAINT DF_fresh_pick_targets_status DEFAULT ('Active'),
        created_at DATETIME NOT NULL CONSTRAINT DF_fresh_pick_targets_created_at DEFAULT (GETDATE()),
        updated_at DATETIME NULL
    );
END
GO

IF COL_LENGTH('dbo.fresh_pick_targets', 'target_year') IS NULL
BEGIN
    ALTER TABLE dbo.fresh_pick_targets
    ADD target_year INT NULL;

    UPDATE dbo.fresh_pick_targets
    SET target_year = 2026
    WHERE target_year IS NULL;
END
GO

IF COL_LENGTH('dbo.fresh_pick_targets', 'target_month') IS NULL
BEGIN
    ALTER TABLE dbo.fresh_pick_targets
    ADD target_month INT NULL;

    UPDATE dbo.fresh_pick_targets
    SET target_month = 4
    WHERE target_month IS NULL;
END
GO

IF EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.fresh_pick_targets')
      AND name = 'target_year'
      AND is_nullable = 1
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM dbo.fresh_pick_targets WHERE target_year IS NULL)
    BEGIN
        ALTER TABLE dbo.fresh_pick_targets
        ALTER COLUMN target_year INT NOT NULL;
    END
END
GO

IF EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.fresh_pick_targets')
      AND name = 'target_month'
      AND is_nullable = 1
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM dbo.fresh_pick_targets WHERE target_month IS NULL)
    BEGIN
        ALTER TABLE dbo.fresh_pick_targets
        ALTER COLUMN target_month INT NOT NULL;
    END
END
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE object_id = OBJECT_ID('dbo.fresh_pick_targets')
      AND name = 'UX_fresh_pick_targets_period_vendor_product'
)
BEGIN
    CREATE UNIQUE INDEX UX_fresh_pick_targets_period_customer_product
        ON dbo.fresh_pick_targets(target_year, target_month, customer_name, product_name);
END
GO

MERGE dbo.fresh_pick_targets AS tgt
USING (
    SELECT
        2026 AS target_year,
        4 AS target_month,
        src.customer_name,
        src.product_name,
        src.monthly_target_qty,
        src.daily_target_qty,
        N'Active' AS status
    FROM (VALUES
        (N'Cash Account', N'Chicken Breast Boneless', CAST(156 AS DECIMAL(18,2)), CAST(5 AS DECIMAL(18,2))),
        (N'Cash Account', N'Chicken Broast', CAST(35 AS DECIMAL(18,2)), CAST(1 AS DECIMAL(18,2))),
        (N'Cash Account', N'Chicken Karahi Cut', CAST(150 AS DECIMAL(18,2)), CAST(5 AS DECIMAL(18,2))),
        (N'Cash Account', N'Chicken Leg Boneless', CAST(34 AS DECIMAL(18,2)), CAST(1 AS DECIMAL(18,2))),
        (N'Cash Account', N'Chicken Neck & Rib Cage', CAST(35 AS DECIMAL(18,2)), CAST(1 AS DECIMAL(18,2))),
        (N'Cash Account', N'Chicken Tikka Cut', CAST(63 AS DECIMAL(18,2)), CAST(2 AS DECIMAL(18,2))),
        (N'Cash Account', N'Chicken Wings', CAST(50 AS DECIMAL(18,2)), CAST(2 AS DECIMAL(18,2))),
        (N'Cash Account', N'Whole Chicken', CAST(39 AS DECIMAL(18,2)), CAST(1 AS DECIMAL(18,2))),
        (N'ALA RAHI DHA', N'Whole Chicken Skin-on', CAST(277 AS DECIMAL(18,2)), CAST(9 AS DECIMAL(18,2))),
        (N'Jinnah Medical College Canteen', N'Chicken Breast Boneless', CAST(58 AS DECIMAL(18,2)), CAST(2 AS DECIMAL(18,2))),
        (N'Jinnah Medical College Canteen', N'Chicken Karahi Cut', CAST(76 AS DECIMAL(18,2)), CAST(3 AS DECIMAL(18,2))),
        (N'Jinnah Medical College Canteen', N'Chicken Broast', CAST(35 AS DECIMAL(18,2)), CAST(1 AS DECIMAL(18,2))),
        (N'Spicy One', N'Chicken Broast', CAST(50 AS DECIMAL(18,2)), CAST(2 AS DECIMAL(18,2)))
    ) AS src(customer_name, product_name, monthly_target_qty, daily_target_qty)
) AS src
ON tgt.target_year = src.target_year
AND tgt.target_month = src.target_month
AND tgt.customer_name = src.customer_name
AND tgt.product_name = src.product_name
WHEN MATCHED THEN
    UPDATE SET
        tgt.monthly_target_qty = src.monthly_target_qty,
        tgt.daily_target_qty = src.daily_target_qty,
        tgt.status = src.status,
        tgt.updated_at = GETDATE()
WHEN NOT MATCHED THEN
    INSERT (
        target_year,
        target_month,
        customer_name,
        product_name,
        monthly_target_qty,
        daily_target_qty,
        status
    )
    VALUES (
        src.target_year,
        src.target_month,
        src.customer_name,
        src.product_name,
        src.monthly_target_qty,
        src.daily_target_qty,
        src.status
    );
GO

SELECT
    target_year,
    target_month,
    customer_name,
    product_name,
    monthly_target_qty,
    daily_target_qty,
    status
FROM dbo.fresh_pick_targets
WHERE target_year = 2026
  AND target_month = 4
ORDER BY customer_name, product_name;
GO
