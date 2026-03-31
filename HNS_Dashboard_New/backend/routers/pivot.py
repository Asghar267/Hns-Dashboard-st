from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import run_query
from utils import placeholders, build_filter_clause
import pandas as pd
from datetime import datetime, date

router = APIRouter(prefix="/pivot", tags=["pivot"])

@router.get("/branch-category")
async def get_branch_category_pivot(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    metric: str = "Sales",
    data_mode: str = "Unfiltered"
):
    """Fetch Branch x Category pivot data"""
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    # We need line items for this
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    WITH filtered_sales AS (
        SELECT s.sale_id, s.shop_id, s.Nt_amount
        FROM tblSales s WITH (NOLOCK)
        WHERE s.sale_date BETWEEN ? AND ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
            {filter_clause}
    ),
    line_totals AS (
        SELECT li.sale_id, SUM(li.qty * li.Unit_price) AS line_total
        FROM tblSalesLineItems li WITH (NOLOCK)
        JOIN filtered_sales fs ON fs.sale_id = li.sale_id
        WHERE li.Unit_price > 0
        GROUP BY li.sale_id
    )
    SELECT 
        sh.shop_name,
        COALESCE(t.field_name, '(Unmapped)') AS product,
        SUM(li.qty) AS total_qty,
        SUM((li.qty * li.Unit_price) / NULLIF(lt.line_total, 0) * fs.Nt_amount) AS total_revenue
    FROM filtered_sales fs
    JOIN tblDefShops sh ON fs.shop_id = sh.shop_id
    JOIN tblSalesLineItems li WITH (NOLOCK) ON fs.sale_id = li.sale_id
    JOIN line_totals lt ON lt.sale_id = fs.sale_id
    LEFT JOIN (
        SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name 
        FROM TempProductBarcode WITH (NOLOCK) 
        UNION ALL 
        SELECT 2642, '0570', 'Deals'
    ) t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
    GROUP BY sh.shop_name, t.field_name
    """
    
    params = [start_date, end_date] + branch_ids + filter_params
    
    try:
        df = run_query(query, params=tuple(params))
        if df.empty:
            return []
            
        value_col = "total_revenue" if metric == "Sales" else "total_qty"
        
        # Pivot the data
        pivoted = df.pivot_table(
            index="shop_name",
            columns="product",
            values=value_col,
            aggfunc="sum",
            fill_value=0
        )
        
        # Add Grand Totals
        pivoted["Grand Total"] = pivoted.sum(axis=1)
        pivoted.loc["Grand Total"] = pivoted.sum(axis=0)
        
        return pivoted.reset_index().to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/branch-day")
async def get_branch_day_pivot(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    data_mode: str = "Unfiltered"
):
    """Fetch Branch x Day pivot data"""
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT 
        sh.shop_name,
        CAST(s.sale_date AS DATE) as date,
        SUM(s.Nt_amount) as total_sales
    FROM tblSales s WITH (NOLOCK)
    JOIN tblDefShops sh ON s.shop_id = sh.shop_id
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      {filter_clause}
    GROUP BY sh.shop_name, CAST(s.sale_date AS DATE)
    """
    
    params = [start_date, end_date] + branch_ids + filter_params
    
    try:
        df = run_query(query, params=tuple(params))
        if df.empty:
            return []
            
        # Pivot the data
        pivoted = df.pivot_table(
            index="shop_name",
            columns="date",
            values="total_sales",
            aggfunc="sum",
            fill_value=0
        )
        
        # Add Grand Totals
        pivoted["Grand Total"] = pivoted.sum(axis=1)
        pivoted.loc["Grand Total"] = pivoted.sum(axis=0)
        
        pivoted = pivoted.reset_index()
        
        # Convert date columns to strings for JSON
        pivoted.columns = [str(col) if isinstance(col, (datetime, pd.Timestamp, date)) else col for col in pivoted.columns]
        
        return pivoted.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/month-branch")
async def get_month_branch_pivot(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    data_mode: str = "Unfiltered"
):
    """Fetch Month x Branch pivot data"""
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT 
        sh.shop_name,
        FORMAT(s.sale_date, 'yyyy-MM') as month,
        SUM(s.Nt_amount) as total_sales
    FROM tblSales s WITH (NOLOCK)
    JOIN tblDefShops sh ON s.shop_id = sh.shop_id
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      {filter_clause}
    GROUP BY sh.shop_name, FORMAT(s.sale_date, 'yyyy-MM')
    """
    
    params = [start_date, end_date] + branch_ids + filter_params
    
    try:
        df = run_query(query, params=tuple(params))
        if df.empty:
            return []
            
        # Pivot the data
        pivoted = df.pivot_table(
            index="month",
            columns="shop_name",
            values="total_sales",
            aggfunc="sum",
            fill_value=0
        )
        
        # Add Grand Totals
        pivoted["Grand Total"] = pivoted.sum(axis=1)
        pivoted.loc["Grand Total"] = pivoted.sum(axis=0)
        
        return pivoted.reset_index().to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
