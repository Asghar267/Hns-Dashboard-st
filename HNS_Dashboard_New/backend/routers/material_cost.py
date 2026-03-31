from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import run_query, get_db
from utils import placeholders, build_filter_clause
import pandas as pd
import numpy as np

router = APIRouter(prefix="/material-cost", tags=["material-cost"])

# Material cost commission data (hardcoded as in original project)
MATERIAL_COST_COMMISSION_DATA = [
    {"product_code": 137, "product_name": "Banana Shake", "material_cost": 175.0, "commission": 50},
    {"product_code": 289, "product_name": "BBQ Sauce Dip", "material_cost": 19.3, "commission": 60},
    {"product_code": 11, "product_name": "Beef Behari Cheese Roll", "material_cost": 253.4, "commission": 10},
    {"product_code": 235, "product_name": "Buffalo Wings", "material_cost": 596.9, "commission": 50},
    {"product_code": 960, "product_name": "Chadder Broast ( Breast )", "material_cost": 475.1, "commission": 50},
    {"product_code": 959, "product_name": "Chadder Broast ( Leg )", "material_cost": 470.1, "commission": 70},
    {"product_code": 555, "product_name": "Channa Tarkari", "material_cost": 53.9, "commission": 20},
    {"product_code": 260, "product_name": "Chatni Bowl", "material_cost": 178.2, "commission": 20},
    {"product_code": 91, "product_name": "Cheese Slice", "material_cost": 25.0, "commission": 15},
    {"product_code": 87, "product_name": "Cheese Sauce Dip", "material_cost": 39.1, "commission": 50},
    {"product_code": 136, "product_name": "Chekoo Shake", "material_cost": 120.5, "commission": 70},
    {"product_code": 17, "product_name": "Chicken Behari Cheese Roll", "material_cost": 159.7, "commission": 50},
    {"product_code": 36, "product_name": "Chicken Behari Kabab", "material_cost": 300.8, "commission": 50},
    {"product_code": 20, "product_name": "Chicken Crispy Cheese Roll", "material_cost": 199.8, "commission": 50},
    {"product_code": 40, "product_name": "Chicken Masala Boti", "material_cost": 317.1, "commission": 100},
    {"product_code": 60, "product_name": "Chicken Pineapple Salad", "material_cost": 512.5, "commission": 50},
    {"product_code": 14, "product_name": "Chicken Reshmi Kabab Cheese Roll", "material_cost": 135.9, "commission": 50},
    {"product_code": 13, "product_name": "Chicken Reshmi Kabab Garlic Roll", "material_cost": 147.6, "commission": 50},
    {"product_code": 68, "product_name": "Chicken Supreme Burger", "material_cost": 421.2, "commission": 70},
    {"product_code": 201, "product_name": "Chicken Tikka Wash ( Breast)", "material_cost": 214.8, "commission": 50},
    {"product_code": 203, "product_name": "Chicken Tikka Wash Leg", "material_cost": 214.9, "commission": 50},
    {"product_code": 135, "product_name": "Date Shake", "material_cost": 155.9, "commission": 50},
    {"product_code": 162, "product_name": "Disposable Glass with Ice", "material_cost": 21.7, "commission": 10},
    {"product_code": 227, "product_name": "Fish Crackers Basket", "material_cost": 58.7, "commission": 10},
    {"product_code": 61, "product_name": "Fruit Salad", "material_cost": 449.1, "commission": 50},
    {"product_code": 271, "product_name": "Fusion Platter (3)", "material_cost": 849.9, "commission": 80},
    {"product_code": 953, "product_name": "Garlic Mayo Broast ( Leg ) Topping", "material_cost": 439.2, "commission": 50},
    {"product_code": 957, "product_name": "Garlic Mayo Broast ( Breast ) Topping", "material_cost": 509.2, "commission": 50},
    {"product_code": 955, "product_name": "Garlic Mayo Fries Topping", "material_cost": 255.4, "commission": 30},
    {"product_code": 79, "product_name": "Golden Nuggets (10 Pcs)", "material_cost": 299.6, "commission": 100},
    {"product_code": 127, "product_name": "Grape Fruit", "material_cost": 233.8, "commission": 10},
    {"product_code": 803, "product_name": "Green Masala Chicken", "material_cost": 309.1, "commission": 30},
    {"product_code": 66, "product_name": "Grilled Breast Burger", "material_cost": 336.2, "commission": 50},
    {"product_code": 90, "product_name": "Hot Dog Bun", "material_cost": 32.0, "commission": 5},
    {"product_code": 166, "product_name": "Kheer", "material_cost": 170.3, "commission": 10},
    {"product_code": 255, "product_name": "Kunafa", "material_cost": 343.6, "commission": 50},
    {"product_code": 230, "product_name": "Mix Vegetable Handi", "material_cost": 338.2, "commission": 50},
    {"product_code": 231, "product_name": "Mix Vegetable Pulao", "material_cost": 197.0, "commission": 50},
    {"product_code": 106, "product_name": "Mutton Biryani", "material_cost": 979.0, "commission": 150},
    {"product_code": 129, "product_name": "Orange Juice", "material_cost": 173.0, "commission": 15},
    {"product_code": 140, "product_name": "Oreo Shake", "material_cost": 340.6, "commission": 20},
    {"product_code": 103, "product_name": "Palak Paneer Handi", "material_cost": 539.4, "commission": 100},
    {"product_code": 232, "product_name": "Paneer Makhni Handi", "material_cost": 810.3, "commission": 50},
    {"product_code": 233, "product_name": "Paneer Vegetable Karahi", "material_cost": 440.9, "commission": 50},
    {"product_code": 234, "product_name": "Peri Bite", "material_cost": 394.5, "commission": 50},
    {"product_code": 198, "product_name": "Peshawari Chicken Karahi", "material_cost": 430.1, "commission": 100},
    {"product_code": 199, "product_name": "Peshawari Mutton Karahi", "material_cost": 1276.9, "commission": 100},
    {"product_code": 131, "product_name": "Pineapple Shake", "material_cost": 192.2, "commission": 10},
    {"product_code": 109, "product_name": "Plain Rice", "material_cost": 102.0, "commission": 50},
    {"product_code": 101, "product_name": "Red Handi", "material_cost": 396.0, "commission": 150},
    {"product_code": 26, "product_name": "Seekh Kabab Cheese Roll", "material_cost": 158.8, "commission": 30},
    {"product_code": 25, "product_name": "Seekh Kabab Garlic Mayo Roll", "material_cost": 170.5, "commission": 30},
    {"product_code": 94, "product_name": "Special Chicken Karahi", "material_cost": 480.0, "commission": 100},
    {"product_code": 147, "product_name": "The Mighty Meat Platter", "material_cost": 3437.8, "commission": 200},
    {"product_code": 951, "product_name": "The Velvet Stack Burger", "material_cost": 512.2, "commission": 50},
    {"product_code": 192, "product_name": "Thunder Fries Topping", "material_cost": 173.2, "commission": 60},
    {"product_code": 115, "product_name": "Vanilla Single Scoop", "material_cost": 53.7, "commission": 30},
    {"product_code": 855, "product_name": "Volcano Drums", "material_cost": 431.2, "commission": 30},
    {"product_code": 566, "product_name": "Palak Paneer Nashta", "material_cost": 183.93, "commission": 50},
    {"product_code": 701, "product_name": "Iftar Deal 1 ( Serve 2)", "material_cost": 1689, "commission": 100},
    {"product_code": 703, "product_name": "Iftar Deal 2 (Serve3)", "material_cost": 2717, "commission": 100},
    {"product_code": 704, "product_name": "Iftar Deal 3 ( Serve 4)", "material_cost": 3218, "commission": 100},
    {"product_code": 705, "product_name": "Iftar Deal 4 ( Serve 5)", "material_cost": 2774, "commission": 100},
    {"product_code": 706, "product_name": "SEHRI DEAL 1 (SERVE 2)", "material_cost": 1156, "commission": 100},
    {"product_code": 707, "product_name": "SEHRI DEAL 2 SERVE 3", "material_cost": 2056, "commission": 100},
    {"product_code": 708, "product_name": "SEHRI DEAL 3 SERVE 4", "material_cost": 1679, "commission": 100},
    {"product_code": 709, "product_name": "SEHRI DEAL 4 SERVE 5", "material_cost": 2706, "commission": 100},
]

def _commission_values_sql() -> str:
    def _esc(name: str) -> str:
        return str(name).replace("'", "''")
    rows = ",\n                ".join(
        f"({int(item['product_code'])}, '{_esc(item['product_name'])}', {float(item['material_cost'])}, {float(item['commission'])})"
        for item in MATERIAL_COST_COMMISSION_DATA
    )
    return f"""
            SELECT product_code, product_name, material_cost, commission
            FROM (
                VALUES
                {rows}
            ) AS mcc(product_code, product_name, material_cost, commission)
    """

def _product_match_expression() -> str:
    return (
        "COALESCE("
        "CASE WHEN p.Product_code NOT LIKE '%[^0-9]%' AND p.Product_code <> '' THEN CAST(p.Product_code AS INT) END, "
        "CASE WHEN li.Product_code NOT LIKE '%[^0-9]%' AND li.Product_code <> '' THEN CAST(li.Product_code AS INT) END"
        ")"
    )

@router.get("/setup")
async def get_commission_setup():
    """Get the built-in product commission matrix"""
    return MATERIAL_COST_COMMISSION_DATA

@router.get("/branch-summary")
async def get_branch_summary(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    data_mode: str = "Unfiltered"
):
    """Fetch branch-wise material cost commission summary"""
    filter_clause, filter_params = build_filter_clause(data_mode)
    mcc_sql = _commission_values_sql()
    product_match = _product_match_expression()
    
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        sh.shop_name,
        SUM(li.qty) AS total_units_sold,
        SUM(li.qty * li.Unit_price) AS total_sales,
        SUM(li.qty * mcc.material_cost) AS total_material_cost,
        SUM(li.qty * mcc.commission) AS total_commission
    FROM tblSales s WITH (NOLOCK)
    INNER JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
    LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
    LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
    LEFT JOIN tblDefShops sh WITH (NOLOCK) ON s.shop_id = sh.shop_id
    INNER JOIN ({mcc_sql}) mcc ON {product_match} = mcc.product_code
    WHERE s.sale_date BETWEEN ? AND ?
        AND s.shop_id IN ({placeholders(len(branch_ids))})
        {filter_clause}
    GROUP BY sh.shop_name
    """
    
    params = [start_date, end_date] + branch_ids + filter_params
    
    try:
        df = run_query(query, params=tuple(params))
        if not df.empty:
            df["avg_commission_rate"] = (df["total_commission"] / df["total_material_cost"] * 100).fillna(0).round(2)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/employee-summary")
async def get_employee_summary(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    data_mode: str = "Unfiltered"
):
    """Fetch employee-wise material cost commission summary"""
    filter_clause, filter_params = build_filter_clause(data_mode)
    mcc_sql = _commission_values_sql()
    product_match = _product_match_expression()
    
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
        sh.shop_name,
        SUM(li.qty) AS total_units_sold,
        SUM(li.qty * li.Unit_price) AS total_sales,
        SUM(li.qty * mcc.material_cost) AS total_material_cost,
        SUM(li.qty * mcc.commission) AS total_commission
    FROM tblSales s WITH (NOLOCK)
    INNER JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
    LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
    LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
    LEFT JOIN tblDefShopEmployees e WITH (NOLOCK) ON s.employee_id = e.shop_employee_id
    LEFT JOIN tblDefShops sh WITH (NOLOCK) ON s.shop_id = sh.shop_id
    INNER JOIN ({mcc_sql}) mcc ON {product_match} = mcc.product_code
    WHERE s.sale_date BETWEEN ? AND ?
        AND s.shop_id IN ({placeholders(len(branch_ids))})
        {filter_clause}
    GROUP BY e.field_name, sh.shop_name
    """
    
    params = [start_date, end_date] + branch_ids + filter_params
    
    try:
        df = run_query(query, params=tuple(params))
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/product-summary")
async def get_product_summary(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    data_mode: str = "Unfiltered"
):
    """Fetch product-wise material cost commission summary"""
    filter_clause, filter_params = build_filter_clause(data_mode)
    mcc_sql = _commission_values_sql()
    product_match = _product_match_expression()
    
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        {product_match} AS product_code,
        mcc.product_name,
        mcc.material_cost,
        mcc.commission,
        SUM(li.qty) AS total_units_sold,
        SUM(li.qty * li.Unit_price) AS total_sales,
        SUM(li.qty * mcc.material_cost) AS total_material_cost,
        SUM(li.qty * mcc.commission) AS total_commission
    FROM tblSales s WITH (NOLOCK)
    INNER JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
    LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
    LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
    INNER JOIN ({mcc_sql}) mcc ON {product_match} = mcc.product_code
    WHERE s.sale_date BETWEEN ? AND ?
        AND s.shop_id IN ({placeholders(len(branch_ids))})
        {filter_clause}
    GROUP BY {product_match}, mcc.product_name, mcc.material_cost, mcc.commission
    """
    
    params = [start_date, end_date] + branch_ids + filter_params
    
    try:
        df = run_query(query, params=tuple(params))
        if not df.empty:
            df["commission_rate"] = (df["commission"] / df["material_cost"] * 100).fillna(0).round(2)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
