from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import run_query
from utils import placeholders, build_filter_clause
import pandas as pd

router = APIRouter(prefix="/trends", tags=["trends"])

@router.get("/monthly")
async def get_monthly_trends(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    data_mode: str = "Unfiltered"
):
    """Fetch monthly sales trends"""
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        DATEFROMPARTS(YEAR(s.sale_date), MONTH(s.sale_date), 1) AS period_date,
        SUM(s.Nt_amount) AS total_sales
    FROM tblSales s WITH (NOLOCK)
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      {filter_clause}
    GROUP BY YEAR(s.sale_date), MONTH(s.sale_date)
    ORDER BY YEAR(s.sale_date), MONTH(s.sale_date)
    """

    params = [start_date, end_date] + branch_ids + filter_params
    
    try:
        df = run_query(query, params=tuple(params))
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/day-of-week")
async def get_dow_trends(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    data_mode: str = "Unfiltered"
):
    """Fetch day-of-week sales trends"""
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        DATENAME(weekday, s.sale_date) AS day_name,
        DATEPART(weekday, s.sale_date) AS day_index,
        SUM(s.Nt_amount) AS total_sales,
        COUNT(s.sale_id) AS total_orders
    FROM tblSales s WITH (NOLOCK)
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      {filter_clause}
    GROUP BY DATENAME(weekday, s.sale_date), DATEPART(weekday, s.sale_date)
    ORDER BY day_index
    """
    params = [start_date, end_date] + branch_ids + filter_params
    
    try:
        df = run_query(query, params=tuple(params))
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hourly")
async def get_hourly_trends(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    data_mode: str = "Unfiltered"
):
    """Fetch hourly sales trends"""
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    # Using TransactionTime if available, otherwise fallback to 0
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        DATEPART(hour, COALESCE(s.TransactionTime, s.sale_date)) AS hour,
        SUM(s.Nt_amount) AS total_sales,
        COUNT(s.sale_id) AS total_orders
    FROM tblSales s WITH (NOLOCK)
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      {filter_clause}
    GROUP BY DATEPART(hour, COALESCE(s.TransactionTime, s.sale_date))
    ORDER BY hour
    """
    params = [start_date, end_date] + branch_ids + filter_params
    
    try:
        df = run_query(query, params=tuple(params))
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
