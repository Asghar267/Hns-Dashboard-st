from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import run_query
from utils import placeholders, build_filter_clause
import pandas as pd
from datetime import datetime, date
import calendar

router = APIRouter(prefix="/overview", tags=["overview"])

def get_month_days_info(target_date_str: str):
    """Calculate total days and remaining days in the month of the target date"""
    dt = pd.to_datetime(target_date_str)
    _, total_days = calendar.monthrange(dt.year, dt.month)
    
    # If target date is today or in the future, use its day
    # If target date is in the past, remaining days is 0
    today = date.today()
    if dt.date() < today:
        remaining_days = 0
    else:
        remaining_days = total_days - dt.day + 1
        
    return total_days, remaining_days

@router.get("/summary")
async def get_branch_summary(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    data_mode: str = "Unfiltered"
):
    """Fetch branch summary including targets and achievement"""
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    # Deriving year and month from end_date for targets
    try:
        end_dt = pd.to_datetime(end_date)
        year, month = int(end_dt.year), int(end_dt.month)
        total_days, remaining_days = get_month_days_info(end_date)
    except:
        now = datetime.now()
        year, month = now.year, now.month
        total_days, remaining_days = 30, 15

    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    WITH shop_sales AS (
        SELECT
            s.shop_id,
            COUNT(DISTINCT s.sale_id) AS total_sales,
            SUM(s.Nt_amount) AS total_Nt_amount
        FROM tblSales s WITH (NOLOCK)
        WHERE s.sale_date BETWEEN ? AND ?
            AND s.shop_id IN ({placeholders(len(branch_ids))})
            {filter_clause}
        GROUP BY s.shop_id
    )
    SELECT
        sh.shop_id,
        sh.shop_name,
        COALESCE(ss.total_sales, 0) AS total_sales,
        COALESCE(ss.total_Nt_amount, 0) AS total_Nt_amount
    FROM tblDefShops sh WITH (NOLOCK)
    LEFT JOIN shop_sales ss ON sh.shop_id = ss.shop_id
    WHERE sh.shop_id IN ({placeholders(len(branch_ids))})
    ORDER BY sh.shop_id
    """

    params = [start_date, end_date] + branch_ids + filter_params + branch_ids
    
    try:
        df = run_query(query, params=tuple(params))
        
        # Merge targets
        from database import get_targets
        targets = get_targets(year, month)
        df_targets = targets["branch_targets"]
        
        if not df_targets.empty:
            df = df.merge(df_targets, on="shop_id", how="left")
            df["monthly_target"] = df["monthly_target"].fillna(0)
        else:
            df["monthly_target"] = 0
            
        # Add achievement and remaining
        df["remaining_target"] = (df["monthly_target"] - df["total_Nt_amount"]).clip(lower=0)
        df["achievement_pct"] = (df["total_Nt_amount"] / df["monthly_target"] * 100).fillna(0).replace([float('inf'), -float('inf')], 0)
        
        # Projection logic
        df["required_daily"] = (df["remaining_target"] / max(1, remaining_days)).fillna(0)
        df["avg_daily"] = (df["total_Nt_amount"] / max(1, end_dt.day)).fillna(0)
        df["month_end_projection"] = (df["avg_daily"] * total_days).fillna(0)
        df["projection_gap"] = (df["month_end_projection"] - df["monthly_target"])
        
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/highlights")
async def get_overview_highlights(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    data_mode: str = "Unfiltered"
):
    """Fetch top 5 highlights for Chef Sales, Product Sales, and OT Sales"""
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    # 1. Top 5 Chef Sales (Product Categories)
    chef_query = f"""
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
    SELECT TOP 5
        COALESCE(t.field_name, '(Unmapped)') AS product,
        SUM((li.qty * li.Unit_price) / NULLIF(lt.line_total, 0) * fs.Nt_amount) AS sales
    FROM filtered_sales fs
    JOIN tblSalesLineItems li WITH (NOLOCK) ON fs.sale_id = li.sale_id
    JOIN line_totals lt ON lt.sale_id = fs.sale_id
    LEFT JOIN (
        SELECT Product_Item_ID, CAST(Product_code AS VARCHAR(50)) as Product_code, CAST(field_name AS VARCHAR(100)) as field_name 
        FROM TempProductBarcode WITH (NOLOCK) 
        UNION ALL 
        SELECT 2642, '0570', 'Deals'
    ) t ON li.Product_Item_ID = t.Product_Item_ID AND li.Product_code = t.Product_code
    GROUP BY COALESCE(t.field_name, '(Unmapped)')
    ORDER BY sales DESC
    """
    
    # 2. Top 5 Line Items (Sub-Products)
    product_query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT TOP 5
        p.item_name as product,
        SUM(li.qty * li.Unit_price) as sales
    FROM tblSales s WITH (NOLOCK)
    JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
    LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
    LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      {filter_clause}
    GROUP BY p.item_name
    ORDER BY sales DESC
    """
    
    # 3. Top 5 OT Sales
    ot_query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT TOP 5
        COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
        SUM(s.Nt_amount) AS sales
    FROM tblSales s WITH (NOLOCK)
    LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      {filter_clause}
    GROUP BY e.field_name
    ORDER BY sales DESC
    """
    
    params = [start_date, end_date] + branch_ids + filter_params
    
    try:
        chef_df = run_query(chef_query, params=tuple(params))
        product_df = run_query(product_query, params=tuple(params))
        ot_df = run_query(ot_query, params=tuple(params))
        
        return {
            "chef_top": chef_df.to_dict(orient="records"),
            "product_top": product_df.to_dict(orient="records"),
            "ot_top": ot_df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/order-types")
async def get_order_type_analysis(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    data_mode: str = "Unfiltered"
):
    """Fetch order type distribution for Sankey and metrics"""
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT 
        CASE 
            WHEN s.OrderTypeID = 1 THEN 'Dine IN'
            WHEN s.OrderTypeID = 2 THEN 'Take Away'
            WHEN s.OrderTypeID = 3 THEN 'Delivery'
            WHEN s.OrderTypeID = 4 THEN 'Food Panda'
            ELSE 'Other'
        END as order_type,
        COUNT(s.sale_id) as total_orders,
        SUM(s.Nt_amount) as total_sales
    FROM tblSales s WITH (NOLOCK)
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      {filter_clause}
    GROUP BY s.OrderTypeID
    """
    params = [start_date, end_date] + branch_ids + filter_params
    
    try:
        df = run_query(query, params=tuple(params))
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/daily-sales")
async def get_daily_sales(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    data_mode: str = "Unfiltered"
):
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT 
        CAST(s.sale_date AS DATE) as date,
        SUM(s.Nt_amount) as total_sales
    FROM tblSales s WITH (NOLOCK)
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      {filter_clause}
    GROUP BY CAST(s.sale_date AS DATE)
    ORDER BY date
    """
    params = [start_date, end_date] + branch_ids + filter_params
    try:
        df = run_query(query, params=tuple(params))
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
