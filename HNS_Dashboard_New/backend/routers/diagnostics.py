from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import pandas as pd
import numpy as np
from database import run_query
from utils import placeholders, build_filter_clause
from blink_utils import prepare_blink_orders, build_split_report
from datetime import datetime

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])

@router.get("/khadda")
async def get_khadda_diagnostics(
    start_date: str = "2026-03-01",
    end_date: str = "2026-03-10",
    commission_rate: float = 2.0,
    data_mode: str = "Unfiltered"
):
    """Fetch Khadda diagnostics data including summaries"""
    shop_id = 2
    filter_clause, filter_params = build_filter_clause(data_mode)
    end_exclusive = (pd.to_datetime(end_date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 1. Total Sales by Employee
    total_query = f"""
    SELECT
        s.shop_id,
        sh.shop_name,
        COALESCE(e.shop_employee_id, 0) AS employee_id,
        LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
        COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
        COUNT(DISTINCT s.sale_id) AS total_transactions_all,
        SUM(s.Nt_amount) AS total_sales_all
    FROM tblSales s WITH (NOLOCK)
    LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
    LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
    WHERE s.sale_date >= ?
      AND s.sale_date < ?
      AND s.shop_id = ?
      {filter_clause}
    GROUP BY s.shop_id, sh.shop_name, e.shop_employee_id, e.field_Code, e.field_name
    """
    
    try:
        df_total = run_query(total_query, params=tuple([start_date, end_exclusive, shop_id] + filter_params))
        
        # 2. Blinkco transactions
        qr_query = f"""
        SELECT
            COALESCE(e.shop_employee_id, 0) AS employee_id,
            COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
            s.Nt_amount AS total_sale,
            s.sale_id,
            CAST(s.sale_date AS DATE) as sale_day
        FROM tblSales s WITH (NOLOCK)
        LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
        WHERE s.sale_date >= ?
          AND s.sale_date < ?
          AND s.shop_id = ?
          AND s.external_ref_type = 'Blinkco order'
          {filter_clause}
        """
        df_qr = run_query(qr_query, params=tuple([start_date, end_exclusive, shop_id] + filter_params))
        
        blinkco_summary = pd.DataFrame()
        daily_summary = pd.DataFrame()
        
        if not df_qr.empty:
            blinkco_summary = df_qr.groupby(['employee_id', 'employee_name']).agg(
                total_sales_blinkco=('total_sale', 'sum'),
                total_transactions_blinkco=('sale_id', 'count')
            ).reset_index()
            blinkco_summary['shop_id'] = shop_id
            blinkco_summary['shop_name'] = 'Khadda Main Branch'
            
            daily_summary = df_qr.groupby(['sale_day', 'employee_name']).agg(
                tx_count=('sale_id', 'count'),
                total_sale=('total_sale', 'sum')
            ).reset_index()
            daily_summary['sale_day'] = daily_summary['sale_day'].astype(str)

        # 3. Build split report
        df_split = build_split_report(df_total, blinkco_summary, commission_rate)
        
        return {
            "split_report": df_split.to_dict(orient="records"),
            "daily_summary": daily_summary.to_dict(orient="records") if not daily_summary.empty else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/multi-signal")
async def get_multi_signal_match(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    data_mode: str = "Unfiltered"
):
    """Fetch data for multi-signal matching including pool summary"""
    end_exclusive = (pd.to_datetime(end_date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    # 1. Get POS QR transactions (the ones we expect to match)
    qr_query = f"""
    SELECT
        s.sale_id,
        s.sale_date,
        s.shop_id,
        sh.shop_name,
        COALESCE(e.shop_employee_id, 0) AS employee_id,
        COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
        s.Nt_amount AS total_sale,
        LTRIM(RTRIM(CONVERT(varchar(64), s.external_ref_id))) AS external_ref_id
    FROM tblSales s WITH (NOLOCK)
    LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
    LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
    WHERE s.sale_date >= ?
      AND s.sale_date < ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      AND s.external_ref_type = 'Blinkco order'
      {filter_clause}
    """
    
    # 2. Get POS rows WITHOUT external_ref_id (the pool we might match against)
    no_ref_query = f"""
    SELECT
        s.sale_id,
        s.sale_date,
        s.shop_id,
        sh.shop_name,
        COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
        s.Nt_amount AS total_sale
    FROM tblSales s WITH (NOLOCK)
    LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
    LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
    WHERE s.sale_date >= ?
      AND s.sale_date < ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      AND (s.external_ref_id IS NULL OR LTRIM(RTRIM(CONVERT(varchar(64), s.external_ref_id))) = '')
      {filter_clause}
    """
    
    try:
        df_qr = run_query(qr_query, params=tuple([start_date, end_exclusive] + branch_ids + filter_params))
        df_no_ref = run_query(no_ref_query, params=tuple([start_date, end_exclusive] + branch_ids + filter_params))
        
        # 3. Get Blink Raw Orders for matching
        df_merged = pd.DataFrame()
        if not df_qr.empty:
            ref_ids = df_qr['external_ref_id'].unique().tolist()
            ref_ids = [r for r in ref_ids if r]
            
            if ref_ids:
                raw_query = f"""
                SELECT BlinkOrderId, OrderJson, CreatedAt
                FROM tblInitialRawBlinkOrder WITH (NOLOCK)
                WHERE LTRIM(RTRIM(CONVERT(varchar(64), BlinkOrderId))) IN ({placeholders(len(ref_ids))})
                """
                df_raw = run_query(raw_query, params=tuple(ref_ids))
                df_blink = prepare_blink_orders(df_raw)
                
                # POS line item stats for scoring
                pos_stats_query = f"""
                SELECT
                    s.sale_id,
                    SUM(li.qty) AS pos_total_qty,
                    COUNT(*) AS pos_item_lines
                FROM tblSales s WITH (NOLOCK)
                INNER JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
                WHERE s.sale_id IN ({placeholders(len(df_qr['sale_id'].unique()))})
                GROUP BY s.sale_id
                """
                df_pos_stats = run_query(pos_stats_query, params=tuple(df_qr['sale_id'].unique().tolist()))
                
                # Merge
                df_qr["_ext_ref_key"] = df_qr["external_ref_id"].astype(str).str.strip()
                df_blink["_blink_id_key"] = df_blink["BlinkOrderId"].astype(str).str.strip()
                df_merged = df_qr.merge(df_blink, left_on="_ext_ref_key", right_on="_blink_id_key", how="left")
                df_merged = df_merged.merge(df_pos_stats, on="sale_id", how="left")
                df_merged = df_merged.replace({np.nan: None})

        return {
            "matched_transactions": df_merged.to_dict(orient="records") if not df_merged.empty else [],
            "no_ref_pool": df_no_ref.to_dict(orient="records") if not df_no_ref.empty else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indoge-first")
async def get_indoge_first_match(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    data_mode: str = "Unfiltered"
):
    """Fetch data for Indoge-first (reverse) matching"""
    end_exclusive = (pd.to_datetime(end_date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    # 1. Get non-Blinkco sales (Candela pool)
    candela_query = f"""
    SELECT
        s.sale_id,
        s.sale_date,
        s.Nt_amount AS total_sale,
        LTRIM(RTRIM(CONVERT(varchar(64), s.external_ref_id))) AS external_ref_id
    FROM tblSales s WITH (NOLOCK)
    WHERE s.sale_date >= ?
      AND s.sale_date < ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      AND (s.external_ref_type <> 'Blinkco order' OR s.external_ref_type IS NULL)
      {filter_clause}
    """
    params = [start_date, end_exclusive] + branch_ids + filter_params
    
    try:
        df_cand = run_query(candela_query, params=tuple(params))
        df_cand['external_ref_id'] = df_cand['external_ref_id'].fillna('').astype(str).str.strip()
        df_pool = df_cand[df_cand['external_ref_id'] == ''].copy()
        
        # 2. Get ALL Blink raw orders for the period
        raw_query = """
        SELECT BlinkOrderId, OrderJson, CreatedAt
        FROM tblInitialRawBlinkOrder WITH (NOLOCK)
        WHERE CreatedAt >= ? AND CreatedAt < ?
        """
        df_raw = run_query(raw_query, params=(start_date, end_exclusive))
        df_blink = prepare_blink_orders(df_raw)
        
        # Prepare for response
        # We'll return both pools and let frontend do the matching for interactivity
        return {
            "candela_pool": df_pool.to_dict(orient="records"),
            "indoge_pool": df_blink.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
