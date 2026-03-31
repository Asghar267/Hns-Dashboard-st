from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import run_query, get_targets
from utils import placeholders, build_filter_clause
from datetime import datetime, timedelta
import pandas as pd

router = APIRouter(prefix="/order-takers", tags=["order-takers"])

@router.get("/summary")
async def get_ot_summary(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    data_mode: str = "Unfiltered"
):
    """Fetch order taker and cashier sales performance with targets and projections"""
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    # Deriving year and month from end_date for targets
    try:
        end_dt = pd.to_datetime(end_date)
        year, month = int(end_dt.year), int(end_dt.month)
        
        import calendar
        from datetime import date
        _, total_days = calendar.monthrange(year, month)
        today = date.today()
        if end_dt.date() < today:
            remaining_days = 0
        else:
            remaining_days = total_days - end_dt.day + 1
    except:
        year, month = datetime.now().year, datetime.now().month
        total_days, remaining_days = 30, 15

    # Query for both OTs and Cashiers
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT 
        s.shop_id,
        sh.shop_name,
        COALESCE(e.shop_employee_id, 0) AS employee_id,
        COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
        COALESCE(e.field_Code, 'N/A') as employee_code,
        SUM(s.Nt_amount) AS total_sale,
        COUNT(s.sale_id) as total_orders
    FROM tblSales s WITH (NOLOCK)
    LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
    LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      {filter_clause}
    GROUP BY s.shop_id, sh.shop_name, e.shop_employee_id, e.field_name, e.field_Code
    ORDER BY total_sale DESC
    """

    params = [start_date, end_date] + branch_ids + filter_params
    
    try:
        df = run_query(query, params=tuple(params))
        
        # Merge targets
        from database import get_targets
        targets = get_targets(year, month)
        df_targets = targets["ot_targets"]
        
        if not df_targets.empty:
            # Aggregate targets by employee if needed, but usually employee_id is unique per target record
            df = df.merge(df_targets, on=["shop_id", "employee_id"], how="left")
            df["target_amount"] = df["target_amount"].fillna(0)
        else:
            df["target_amount"] = 0
            
        # Add achievement and remaining
        df["remaining_target"] = (df["target_amount"] - df["total_sale"]).clip(lower=0)
        df["achievement_pct"] = (df["total_sale"] / df["target_amount"] * 100).fillna(0).replace([float('inf'), -float('inf')], 0)
        
        # Projections
        df["per_day_target"] = df["target_amount"] / total_days
        df["next_day_target"] = (df["remaining_target"] / max(1, remaining_days)).fillna(0)
        
        # Performance Indicators (Current vs Required)
        df["avg_daily"] = (df["total_sale"] / max(1, end_dt.day)).fillna(0)
        df["performance_index"] = (df["avg_daily"] / df["per_day_target"] * 100).fillna(0)
        
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_ot_performance(
    year: int,
    month: int,
    start_date: str,
    end_date: str,
    shop_id: int,
    data_mode: str = "Unfiltered"
):
    """Fetch OT performance (sales vs target) with detailed projections"""
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    # 1. Fetch Sales for the period
    sales_query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT 
        s.employee_id,
        e.field_name as employee_name,
        SUM(s.Nt_amount) AS total_sale
    FROM tblSales s WITH (NOLOCK)
    LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
    WHERE s.sale_date BETWEEN ? AND ?
      AND s.shop_id = ?
      {filter_clause}
    GROUP BY s.employee_id, e.field_name
    """
    sales_params = [start_date, end_date, shop_id] + filter_params
    
    try:
        df_sales = run_query(sales_query, params=tuple(sales_params))
        
        # 2. Fetch MTD Sales
        first_day_of_month = f"{year}-{month:02d}-01"
        ref_date = datetime.now()
        yesterday_date = (ref_date - timedelta(days=1)).strftime("%Y-%m-%d")
        
        mtd_query = f"""
        SELECT 
            s.employee_id,
            SUM(s.Nt_amount) AS mtd_sale
        FROM tblSales s WITH (NOLOCK)
        WHERE s.sale_date >= ? AND s.sale_date < ?
          AND s.shop_id = ?
          {filter_clause}
        GROUP BY s.employee_id
        """
        # MTD is from 1st to today (exclusive of tomorrow)
        mtd_params = [first_day_of_month, ref_date.strftime("%Y-%m-%d"), shop_id] + filter_params
        df_mtd = run_query(mtd_query, params=tuple(mtd_params))
        
        # 3. Fetch Yesterday Sales
        yest_query = f"""
        SELECT 
            s.employee_id,
            SUM(s.Nt_amount) AS yesterday_sale
        FROM tblSales s WITH (NOLOCK)
        WHERE s.sale_date >= ? AND s.sale_date < ?
          AND s.shop_id = ?
          {filter_clause}
        GROUP BY s.employee_id
        """
        yest_params = [yesterday_date, ref_date.strftime("%Y-%m-%d"), shop_id] + filter_params
        df_yest = run_query(yest_query, params=tuple(yest_params))
        
        # 4. Fetch Targets
        from database import get_targets
        targets = get_targets(year, month)
        df_targets = targets["ot_targets"]
        df_targets = df_targets[df_targets["shop_id"] == shop_id]
        
        # Merge everything
        if df_sales.empty:
            return []
            
        df_perf = df_sales.merge(df_targets, on="employee_id", how="left")
        df_perf = df_perf.merge(df_mtd, on="employee_id", how="left")
        df_perf = df_perf.merge(df_yest, on="employee_id", how="left")
        
        # Projections
        import calendar
        days_in_month = calendar.monthrange(year, month)[1]
        remaining_days = max(0, (datetime(year, month, days_in_month) - ref_date).days + 1)
        
        df_perf["target_amount"] = df_perf["target_amount"].fillna(0)
        df_perf["mtd_sale"] = df_perf["mtd_sale"].fillna(0)
        df_perf["yesterday_sale"] = df_perf["yesterday_sale"].fillna(0)
        df_perf["employee_name"] = df_perf["employee_name"].fillna(df_perf["employee_id"].astype(str).apply(lambda x: f"ID: {x}"))
        
        df_perf["per_day_target"] = df_perf["target_amount"] / days_in_month
        df_perf["remaining_target"] = (df_perf["target_amount"] - df_perf["mtd_sale"]).clip(lower=0)
        df_perf["next_day_target"] = df_perf.apply(
            lambda row: (row["remaining_target"] / remaining_days) if remaining_days > 0 else 0,
            axis=1
        )
        df_perf["achievement_pct"] = (df_perf["total_sale"] / df_perf["target_amount"] * 100).fillna(0).replace([float('inf'), -float('inf')], 0)
        
        return df_perf.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
