-- SQL Script to Create Missing/Custom Dashboard Tables
-- This script should be run in SQL Server Management Studio (SSMS)

--------------------------------------------------
-- 1. TABLES IN Candelahns DATABASE (Reference Schema)
--------------------------------------------------
USE Candelahns;
GO

-- 1.1 Raw Blink Order Storage (Custom)
IF OBJECT_ID('dbo.tblInitialRawBlinkOrder', 'U') IS NOT NULL 
    DROP TABLE dbo.tblInitialRawBlinkOrder;
GO

CREATE TABLE dbo.tblInitialRawBlinkOrder (
    BlinkOrderId NVARCHAR(64) PRIMARY KEY,
    OrderJson NVARCHAR(MAX) NOT NULL,
    CreatedAt DATETIME NOT NULL DEFAULT GETDATE()
);
GO

-- Performance Optimization: Index for date range filtering
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_tblInitialRawBlinkOrder_CreatedAt' AND object_id = OBJECT_ID('dbo.tblInitialRawBlinkOrder'))
    CREATE INDEX IX_tblInitialRawBlinkOrder_CreatedAt ON dbo.tblInitialRawBlinkOrder(CreatedAt);
GO

-- 1.2 Standard Candelahns Tables (Schema Reference)
-- Note: These usually exist in Candel POS, provided here for complete environment setup.

-- Employee Master
IF OBJECT_ID('dbo.tblDefShopEmployees', 'U') IS NULL
CREATE TABLE dbo.tblDefShopEmployees (
    shop_employee_id INT PRIMARY KEY,
    shop_id INT,
    field_Code NVARCHAR(50),
    field_name NVARCHAR(255),
    start_date DATETIME,
    end_date DATETIME
);
GO

-- Shop Master
IF OBJECT_ID('dbo.tblDefShops', 'U') IS NULL
CREATE TABLE dbo.tblDefShops (
    shop_id INT PRIMARY KEY,
    shop_name NVARCHAR(255)
);
GO

-- Sales Master
IF OBJECT_ID('dbo.tblSales', 'U') IS NULL
CREATE TABLE dbo.tblSales (
    sale_id INT PRIMARY KEY,
    shop_id INT,
    employee_id INT,
    sale_date DATETIME,
    Nt_amount DECIMAL(18, 2),
    external_ref_id NVARCHAR(64),
    external_ref_type NVARCHAR(50),
    Cust_name NVARCHAR(255),
    Additional_Comments NVARCHAR(MAX)
);
GO

-- Sales Line Items
IF OBJECT_ID('dbo.tblSalesLineItems', 'U') IS NULL
CREATE TABLE dbo.tblSalesLineItems (
    sale_id INT,
    Product_Item_ID INT,
    Product_code NVARCHAR(50),
    qty DECIMAL(18, 2),
    Unit_price DECIMAL(18, 2)
);
GO

-- Product Master
IF OBJECT_ID('dbo.tblDefProducts', 'U') IS NULL
CREATE TABLE dbo.tblDefProducts (
    product_id INT PRIMARY KEY,
    Product_code NVARCHAR(50),
    item_name NVARCHAR(255)
);
GO

-- Product Item Mapping
IF OBJECT_ID('dbo.tblProductItem', 'U') IS NULL
CREATE TABLE dbo.tblProductItem (
    Product_Item_ID INT PRIMARY KEY,
    Product_ID INT
);
GO

-- Temporary/Mapping Table for Barcodes
IF OBJECT_ID('dbo.TempProductBarcode', 'U') IS NULL
CREATE TABLE dbo.TempProductBarcode (
    Product_Item_ID INT,
    Product_code NVARCHAR(50),
    field_name NVARCHAR(255) -- Usually used for Category or specific mapping
);
GO

-- 1.3 Material Cost Commission Table (Custom)
IF OBJECT_ID('dbo.MaterialCostCommission', 'U') IS NOT NULL 
    DROP TABLE dbo.MaterialCostCommission;
GO

CREATE TABLE dbo.MaterialCostCommission (
    product_code INT PRIMARY KEY,
    product_name NVARCHAR(255) NOT NULL,
    material_cost DECIMAL(18, 2) NOT NULL,
    commission DECIMAL(18, 2) NOT NULL,
    created_at DATETIME DEFAULT GETDATE()
);
GO

-- Performance Optimization: Recommended Indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_tblSales_ExternalRef' AND object_id = OBJECT_ID('dbo.tblSales'))
    CREATE INDEX IX_tblSales_ExternalRef ON dbo.tblSales(external_ref_id, external_ref_type);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_tblDefShopEmployees_FieldCode' AND object_id = OBJECT_ID('dbo.tblDefShopEmployees'))
    CREATE INDEX IX_tblDefShopEmployees_FieldCode ON dbo.tblDefShopEmployees(field_Code);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_tblSales_DateShop' AND object_id = OBJECT_ID('dbo.tblSales'))
    CREATE INDEX IX_tblSales_DateShop ON dbo.tblSales(sale_date, shop_id);
GO


--------------------------------------------------
-- 2. TABLES IN KDS_DB DATABASE
--------------------------------------------------
-- Note: Create KDS_DB if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'KDS_DB')
    CREATE DATABASE KDS_DB;
GO

USE KDS_DB;
GO

-- 2.1 Chef Sales Categories
IF OBJECT_ID('dbo.chef_sale', 'U') IS NOT NULL 
    DROP TABLE dbo.chef_sale;
GO

CREATE TABLE dbo.chef_sale (
    category_id INT PRIMARY KEY IDENTITY(1,1),
    category_name NVARCHAR(100) NOT NULL UNIQUE
);
GO

-- 2.2 Branch Monthly Targets
IF OBJECT_ID('dbo.branch_targets', 'U') IS NOT NULL 
    DROP TABLE dbo.branch_targets;
GO

CREATE TABLE dbo.branch_targets (
    shop_id INT NOT NULL,
    target_year INT NOT NULL,
    target_month INT NOT NULL,
    monthly_target DECIMAL(18, 2) NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    PRIMARY KEY (shop_id, target_year, target_month)
);
GO

-- 2.3 Chef Category Targets per Branch
IF OBJECT_ID('dbo.branch_chef_targets', 'U') IS NOT NULL 
    DROP TABLE dbo.branch_chef_targets;
GO

CREATE TABLE dbo.branch_chef_targets (
    shop_id INT NOT NULL,
    category_id INT NOT NULL,
    target_year INT NOT NULL,
    target_month INT NOT NULL,
    monthly_target DECIMAL(18, 2) NOT NULL,
    target_type NVARCHAR(50) DEFAULT 'Sale', -- 'Sale' or 'Quantity'
    created_at DATETIME DEFAULT GETDATE(),
    PRIMARY KEY (shop_id, category_id, target_year, target_month),
    FOREIGN KEY (category_id) REFERENCES dbo.chef_sale(category_id)
);
GO

-- 2.4 Order Taker (OT) Targets
-- Resolution: Added target_year and target_month for historical tracking
IF OBJECT_ID('dbo.ot_targets', 'U') IS NOT NULL 
    DROP TABLE dbo.ot_targets;
GO

CREATE TABLE dbo.ot_targets (
    shop_id INT NOT NULL,
    employee_id INT NOT NULL,
    target_year INT NOT NULL,
    target_month INT NOT NULL,
    monthly_target DECIMAL(18, 2) NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    PRIMARY KEY (shop_id, employee_id, target_year, target_month)
);
GO

-- Performance Optimization: Index for fast target lookups
CREATE INDEX IX_ot_targets_Period ON dbo.ot_targets(target_year, target_month);
GO

--------------------------------------------------
-- 3. DATA INTEGRITY AUDIT - SAMPLE SEED DATA
--------------------------------------------------
-- Seed Chef Sale Categories
INSERT INTO dbo.chef_sale (category_name) VALUES 
('BBQ'), ('CHICKEN TIKKA'), ('ROLLS'), ('BURGERS'), ('BEVERAGES'), ('DESSERTS');
GO

-- Seed Sample Branch Targets
-- (Example for North Nazimabad - Shop ID 8)
INSERT INTO dbo.branch_targets (shop_id, target_year, target_month, monthly_target)
VALUES (8, 2026, 3, 18600000.00);
GO
