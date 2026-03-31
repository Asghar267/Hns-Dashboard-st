from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import run_query
from utils import placeholders, build_filter_clause
import pandas as pd

router = APIRouter(prefix="/ramzan", tags=["ramzan"])

@router.get("/deals")
async def get_ramzan_deals(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    data_mode: str = "Unfiltered"
):
    """Fetch Ramzan specific deals sales performance"""
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT 
        sh.shop_name,
        li.Product_code,
        t.field_name as product_name,
        SUM(li.qty) as total_qty,
        SUM(li.qty * li.Unit_price) as total_sales
    FROM tblSales s WITH (NOLOCK)
    JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
    LEFT JOIN tblDefShops sh WITH (NOLOCK) ON s.shop_id = sh.shop_id
    LEFT JOIN (
        SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name 
        FROM TempProductBarcode WITH (NOLOCK)
    ) t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      AND t.field_name LIKE '%Ramzan%'
      {filter_clause}
    GROUP BY sh.shop_name, li.Product_code, t.field_name
    ORDER BY total_sales DESC
    """

    params = [start_date, end_date] + branch_ids + filter_params
    
    try:
        df = run_query(query, params=tuple(params))
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_ramzan_summary(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    data_mode: str = "Unfiltered"
):
    """Fetch branch-wise and product-wise ramzan deals performance"""
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    # Ramzan deals product codes from config
    ramzan_product_codes = [2060, 2061, 2062, 2063, 2064, 2065, 2066, 2067, 2068, 2069, 2070]
    
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT 
        sh.shop_name,
        li.Product_code,
        p.item_name as item_name,
        SUM(li.qty) as total_qty,
        SUM(li.qty * li.Unit_price) as total_sales
    FROM tblSales s WITH (NOLOCK)
    JOIN tblDefShops sh ON s.shop_id = sh.shop_id
    JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
    LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
    LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      AND li.Product_code IN ({placeholders(len(ramzan_product_codes))})
      {filter_clause}
    GROUP BY sh.shop_name, li.Product_code, p.item_name
    """
    
    params = [start_date, end_date] + branch_ids + ramzan_product_codes + filter_params
    
    try:
        df = run_query(query, params=tuple(params))
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
