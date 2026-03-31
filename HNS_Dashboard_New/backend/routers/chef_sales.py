from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import run_query, get_targets, get_db
from utils import placeholders, build_filter_clause
from datetime import datetime
import pandas as pd

router = APIRouter(prefix="/chef-sales", tags=["chef-sales"])

@router.get("/summary")
async def get_chef_summary(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    data_mode: str = "Unfiltered"
):
    """Fetch chef sales summary aggregated by product category across branches"""
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    # Using the weighted allocation logic from original overview highlights
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
        sh.shop_name as branch,
        COALESCE(t.field_name, '(Unmapped)') AS product,
        SUM(li.qty) as total_qty,
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
    GROUP BY sh.shop_name, COALESCE(t.field_name, '(Unmapped)')
    ORDER BY total_revenue DESC
    """

    params = [start_date, end_date] + branch_ids + filter_params
    
    try:
        df = run_query(query, params=tuple(params))
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_chef_performance(
    year: int,
    month: int,
    start_date: str,
    end_date: str,
    shop_id: int,
    data_mode: str = "Unfiltered"
):
    """Fetch Chef performance (sales vs target) for a specific branch and month"""
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    # 1. Fetch Sales for the period (by category)
    sales_query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    WITH filtered_sales AS (
        SELECT s.sale_id, s.shop_id, s.Nt_amount
        FROM tblSales s WITH (NOLOCK)
        WHERE s.sale_date BETWEEN ? AND ?
            AND s.shop_id = ?
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
        COALESCE(t.field_name, '(Unmapped)') AS category_name,
        SUM(li.qty) AS total_qty,
        SUM((li.qty * li.Unit_price) / NULLIF(lt.line_total, 0) * fs.Nt_amount) AS total_revenue
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
    """
    sales_params = [start_date, end_date, shop_id] + filter_params
    
    try:
        df_sales = run_query(sales_query, params=tuple(sales_params))
        
        # 2. Fetch MTD Sales
        first_day_of_month = f"{year}-{month:02d}-01"
        today = datetime.now().strftime("%Y-%m-%d")
        mtd_query = f"""
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
        WITH filtered_sales AS (
            SELECT s.sale_id, s.shop_id, s.Nt_amount
            FROM tblSales s WITH (NOLOCK)
            WHERE s.sale_date BETWEEN ? AND ?
                AND s.shop_id = ?
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
            COALESCE(t.field_name, '(Unmapped)') AS category_name,
            SUM(li.qty) AS mtd_qty,
            SUM((li.qty * li.Unit_price) / NULLIF(lt.line_total, 0) * fs.Nt_amount) AS mtd_revenue
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
        """
        mtd_params = [first_day_of_month, today, shop_id] + filter_params
        df_mtd = run_query(mtd_query, params=tuple(mtd_params))
        
        # 3. Fetch Targets
        from database import get_targets
        targets = get_targets(year, month)
        df_targets = targets["chef_targets"]
        df_targets = df_targets[df_targets["shop_id"] == shop_id]
        
        # Mapping category names to IDs would be ideal, but for now we'll return both
        # The frontend will need to handle the mapping if possible, or we assume categories match names.
        
        # Let's get category names from KDSDB
        conn_kds = get_db("kdsdb")
        df_cats = pd.read_sql("SELECT category_id, category_name FROM dbo.chef_sale", conn_kds)
        df_targets = df_targets.merge(df_cats, on="category_id", how="left")
        
        # Merge targets with sales
        df_perf = df_targets.merge(df_sales, left_on="category_name", right_on="category_name", how="left")
        df_perf = df_perf.merge(df_mtd, on="category_name", how="left")
        
        df_perf = df_perf.fillna(0)
        
        # Calculations
        df_perf["current"] = df_perf.apply(
            lambda r: r["total_revenue"] if r["target_type"] == "Sale" else r["total_qty"], axis=1
        )
        df_perf["remaining"] = (df_perf["target_amount"] - df_perf["current"]).clip(lower=0)
        df_perf["achievement_pct"] = (df_perf["current"] / df_perf["target_amount"] * 100).fillna(0).replace([float('inf'), -float('inf')], 0)
        df_perf["bonus"] = df_perf.apply(
            lambda r: (0.1 * r["target_amount"]) if (r["target_type"] == "Sale" and r["achievement_pct"] >= 100) else 0,
            axis=1
        )
        
        return df_perf.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
