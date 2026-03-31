-- SQL Script to Create Material Cost Commission Table
-- Run this in SQL Server Management Studio or your preferred SQL client

USE Candelahns;

-- Drop table if it exists
IF OBJECT_ID('dbo.MaterialCostCommission', 'U') IS NOT NULL 
    DROP TABLE dbo.MaterialCostCommission;

-- Create the table
CREATE TABLE dbo.MaterialCostCommission (
    product_code INT PRIMARY KEY,
    product_name NVARCHAR(255) NOT NULL,
    material_cost DECIMAL(10,2) NOT NULL,
    commission DECIMAL(10,2) NOT NULL,
    created_at DATETIME DEFAULT GETDATE()
);

-- Insert your product data
INSERT INTO dbo.MaterialCostCommission (product_code, product_name, material_cost, commission) VALUES
(137, 'Banana Shake', 175.0, 50),
(289, 'BBQ Sauce Dip', 19.3, 60),
(11, 'Beef Behari Cheese Roll', 253.4, 10),
(235, 'Buffalo Wings', 596.9, 50),
(960, 'Chadder Broast ( Breast )', 475.1, 50),
(959, 'Chadder Broast ( Leg )', 470.1, 70),
(555, 'Channa Tarkari', 53.9, 20),
(260, 'Chatni Bowl', 178.2, 20),
(91, 'Cheese Slice', 25.0, 15),
(87, 'Cheese Sauce Dip', 39.1, 50),
(136, 'Chekoo Shake', 120.5, 70),
(17, 'Chicken Behari Cheese Roll', 159.7, 50),
(36, 'Chicken Behari Kabab', 300.8, 50),
(20, 'Chicken Crispy Cheese Roll', 199.8, 50),
(40, 'Chicken Masala Boti', 317.1, 100),
(60, 'Chicken Pineapple Salad', 512.5, 50),
(14, 'Chicken Reshmi Kabab Cheese Roll', 135.9, 50),
(13, 'Chicken Reshmi Kabab Garlic Roll', 147.6, 50),
(68, 'Chicken Supreme Burger', 421.2, 70),
(201, 'Chicken Tikka Wash ( Breast)', 214.8, 50),
(203, 'Chicken Tikka Wash Leg', 214.9, 50),
(135, 'Date Shake', 155.9, 50),
(162, 'Disposable Glass with Ice', 21.7, 10),
(227, 'Fish Crackers Basket', 58.7, 10),
(61, 'Fruit Salad', 449.1, 50),
(271, 'Fusion Platter (3)', 849.9, 80),
(953, 'Garlic Mayo Broast ( Leg ) Topping', 439.2, 50),
(957, 'Garlic Mayo Broast ( Breast ) Topping', 509.2, 50),
(955, 'Garlic Mayo Fries Topping', 255.4, 30),
(79, 'Golden Nuggets (10 Pcs)', 299.6, 100),
(127, 'Grape Fruit', 233.8, 10),
(803, 'Green Masala Chicken', 309.1, 30),
(66, 'Grilled Breast Burger', 336.2, 50),
(90, 'Hot Dog Bun', 32.0, 5),
(166, 'Kheer', 170.3, 10),
(255, 'Kunafa', 343.6, 50),
(230, 'Mix Vegetable Handi', 338.2, 50),
(231, 'Mix Vegetable Pulao', 197.0, 50),
(106, 'Mutton Biryani', 979.0, 150),
(129, 'Orange Juice', 173.0, 15),
(140, 'Oreo Shake', 340.6, 20),
(103, 'Palak Paneer Handi', 539.4, 100),
(232, 'Paneer Makhni Handi', 810.3, 50),
(233, 'Paneer Vegetable Karahi', 440.9, 50),
(234, 'Peri Bite', 394.5, 50),
(198, 'Peshawari Chicken Karahi', 430.1, 100),
(199, 'Peshawari Mutton Karahi', 1276.9, 100),
(131, 'Pineapple Shake', 192.2, 10),
(109, 'Plain Rice', 102.0, 50),
(101, 'Red Handi', 396.0, 150),
(26, 'Seekh Kabab Cheese Roll', 158.8, 30),
(25, 'Seekh Kabab Garlic Mayo Roll', 170.5, 30),
(94, 'Special Chicken Karahi', 480.0, 100),
(147, 'The Mighty Meat Platter', 3437.8, 200),
(951, 'The Velvet Stack Burger', 512.2, 50),
(192, 'Thunder Fries Topping', 173.2, 60),
(115, 'Vanilla Single Scoop', 53.7, 30),
(855, 'Volcano Drums', 431.2, 30),
(566, 'Palak Paneer Nashta', 183.93, 50),
(701, 'Iftar Deal 1 ( Serve 2)', 1689, 100),
(703, 'Iftar Deal 2 (Serve3)', 2717, 100),
(704, 'Iftar Deal 3 ( Serve 4)', 3218, 100),
(705, 'Iftar Deal 4 ( Serve 5)', 2774, 100),
(706, 'SEHRI DEAL 1 (SERVE 2)', 1156, 100),
(707, 'SEHRI DEAL 2 SERVE 3', 2056, 100),
(708, 'SEHRI DEAL 3 SERVE 4', 1679, 100),
(709, 'SEHRI DEAL 4 SERVE 5', 2706, 100);

-- Verify the table was created successfully
SELECT COUNT(*) as Total_Products, 
       SUM(material_cost) as Total_Material_Cost,
       SUM(commission) as Total_Commission
FROM dbo.MaterialCostCommission;

-- Show sample data
SELECT TOP 10 * FROM dbo.MaterialCostCommission ORDER BY product_code;