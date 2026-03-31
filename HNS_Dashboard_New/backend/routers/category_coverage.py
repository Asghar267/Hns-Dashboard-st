from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import run_query
from utils import placeholders, build_filter_clause
import pandas as pd

router = APIRouter(prefix="/category", tags=["category"])

@router.get("/coverage")
async def get_category_coverage(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    data_mode: str = "Unfiltered"
):
    """Fetch category coverage across branches"""
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        sh.shop_name,
        COALESCE(t.field_name, '(Unmapped)') AS category_name,
        SUM(li.qty * li.Unit_price) AS category_sales
    FROM tblSales s WITH (NOLOCK)
    JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
    LEFT JOIN tblDefShops sh WITH (NOLOCK) ON s.shop_id = sh.shop_id
    LEFT JOIN (
        SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name 
        FROM TempProductBarcode WITH (NOLOCK)
    ) t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      {filter_clause}
    GROUP BY sh.shop_name, t.field_name
    ORDER BY sh.shop_name, category_sales DESC
    """

    params = [start_date, end_date] + branch_ids + filter_params
    
    try:
        df = run_query(query, params=tuple(params))
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
