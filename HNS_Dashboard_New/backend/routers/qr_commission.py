from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import run_query
from utils import placeholders, build_filter_clause
import pandas as pd
import numpy as np

router = APIRouter(prefix="/qr-commission", tags=["qr-commission"])

@router.get("/transactions")
async def get_qr_transactions(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    commission_rate: float = 2.0,
    data_mode: str = "Unfiltered"
):
    """Fetch QR transactions and calculate commission"""
    
    filter_clause, filter_params = build_filter_clause(data_mode)
    
    query = f"""
    SELECT
        s.sale_id,
        s.sale_date,
        s.shop_id,
        sh.shop_name,
        COALESCE(e.shop_employee_id, 0) AS employee_id,
        LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
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
    
    params = [start_date, end_date] + branch_ids + filter_params
    
    try:
        df = run_query(query, params=tuple(params))
        if df.empty:
            return []
            
        # Calculate commission
        df['commission'] = df['total_sale'] * (commission_rate / 100.0)
        
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report")
async def get_qr_report(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    commission_rate: float = 2.0,
    data_mode: str = "Unfiltered"
):
    """Fetch full QR commission split report with parity logic"""
    filter_clause, filter_params = build_filter_clause(data_mode)
    end_exclusive = (pd.to_datetime(end_date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 1. Main summary query
    query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        s.shop_id,
        sh.shop_name,
        COALESCE(e.shop_employee_id, 0) AS employee_id,
        LTRIM(RTRIM(COALESCE(e.field_Code, ''))) AS employee_code,
        COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
        COUNT(DISTINCT s.sale_id) AS total_transactions_all,
        SUM(s.Nt_amount) AS total_sales_all,
        SUM(CASE WHEN s.external_ref_type = 'Blinkco order' THEN 1 ELSE 0 END) AS total_transactions_blinkco,
        SUM(CASE WHEN s.external_ref_type = 'Blinkco order' THEN s.Nt_amount ELSE 0 END) AS total_sales_blinkco
    FROM tblSales s WITH (NOLOCK)
    LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
    LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
    WHERE s.sale_date >= ?
      AND s.sale_date < ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      {filter_clause}
    GROUP BY
        s.shop_id, sh.shop_name,
        COALESCE(e.shop_employee_id, 0),
        LTRIM(RTRIM(COALESCE(e.field_Code, ''))),
        COALESCE(e.field_name, 'Online/Unassigned')
    """
    params = [start_date, end_exclusive] + branch_ids + filter_params
    
    try:
        df = run_query(query, params=tuple(params))
        if df.empty: return []
            
        # 2. Get Blink Raw Sales for exact parity (Indoge vs Candela match)
        # We need this to calculate the blink_match_pct mentioned in modular script
        qr_tx_query = f"""
        SELECT s.employee_id, s.shop_id, s.Nt_amount, s.external_ref_id
        FROM tblSales s WITH (NOLOCK)
        WHERE s.sale_date >= ? AND s.sale_date < ? 
          AND s.shop_id IN ({placeholders(len(branch_ids))})
          AND s.external_ref_type = 'Blinkco order'
          {filter_clause}
        """
        df_qr_tx = run_query(qr_tx_query, params=tuple([start_date, end_exclusive] + branch_ids + filter_params))
        
        if not df_qr_tx.empty:
            ref_ids = df_qr_tx['external_ref_id'].dropna().unique().tolist()
            if ref_ids:
                from blink_utils import prepare_blink_orders
                
                # Batch processing
                batch_size = 500
                all_raw_dfs = []
                for i in range(0, len(ref_ids), batch_size):
                    batch_ids = ref_ids[i:i + batch_size]
                    raw_query = f"SELECT BlinkOrderId, OrderJson, CreatedAt FROM tblInitialRawBlinkOrder WITH (NOLOCK) WHERE BlinkOrderId IN ({placeholders(len(batch_ids))})"
                    df_raw_batch = run_query(raw_query, params=tuple(batch_ids))
                    all_raw_dfs.append(df_raw_batch)
                
                if not all_raw_dfs:
                    df_raw = pd.DataFrame()
                else:
                    df_raw = pd.concat(all_raw_dfs, ignore_index=True)

                df_blink = prepare_blink_orders(df_raw)
                
                df_qr_tx["_ref"] = df_qr_tx["external_ref_id"].astype(str).str.strip()
                df_blink["_ref"] = df_blink["BlinkOrderId"].astype(str).str.strip()
                df_merged_tx = df_qr_tx.merge(df_blink, on="_ref", how="left")
                
                # Group by employee/shop to get indoge_blink_sales
                indoge_sum = df_merged_tx.groupby(["employee_id", "shop_id"], as_index=False).agg(
                    indoge_blink_sales=("Indoge_total_price", "sum")
                )
                df = df.merge(indoge_sum, on=["employee_id", "shop_id"], how="left")
        
        df["indoge_blink_sales"] = df.get("indoge_blink_sales", 0.0).fillna(0.0)
        df["total_sales_without_blinkco"] = (df["total_sales_all"] - df["total_sales_blinkco"]).clip(lower=0)
        
        # Parity Match logic (numer/denom match from modular script)
        cand_blink = df["total_sales_blinkco"]
        indoge_blink = df["indoge_blink_sales"]
        df["blink_match_pct"] = (np.minimum(cand_blink, indoge_blink) / np.maximum(cand_blink, indoge_blink).replace(0, np.nan) * 100.0).fillna(0).round(2)
        df["blink_match_ok"] = df["blink_match_pct"] >= 50.0
        
        # Commission calculations
        df["commission_total_sales"] = df["total_sales_all"] * (commission_rate / 100.0)
        df["commission_blinkco_sales"] = df["total_sales_blinkco"] * (commission_rate / 100.0)
        df["commission_without_blinkco_sales"] = df["total_sales_without_blinkco"] * (commission_rate / 100.0)
        
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detailed-transactions")
async def get_detailed_transactions(
    start_date: str,
    end_date: str,
    branch_ids: List[int] = Query(...),
    commission_rate: float = 2.0,
    data_mode: str = "Unfiltered"
):
    """Fetch individual QR transactions with Blink raw data comparison"""
    filter_clause, filter_params = build_filter_clause(data_mode)
    end_exclusive = (pd.to_datetime(end_date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 1. Get POS QR transactions
    qr_query = f"""
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SELECT
        s.sale_id,
        s.shop_id,
        sh.shop_name,
        COALESCE(e.shop_employee_id, 0) AS employee_id,
        COALESCE(e.field_name, 'Online/Unassigned') AS employee_name,
        s.Nt_amount AS total_sale,
        LTRIM(RTRIM(CONVERT(varchar(64), s.external_ref_id))) AS external_ref_id,
        s.sale_date
    FROM tblSales s WITH (NOLOCK)
    LEFT JOIN tblDefShopEmployees e ON s.employee_id = e.shop_employee_id
    LEFT JOIN tblDefShops sh ON s.shop_id = sh.shop_id
    WHERE s.sale_date >= ?
      AND s.sale_date < ?
      AND s.shop_id IN ({placeholders(len(branch_ids))})
      AND s.external_ref_type = 'Blinkco order'
      {filter_clause}
    """
    params = [start_date, end_exclusive] + branch_ids + filter_params
    
    try:
        df_qr = run_query(qr_query, params=tuple(params))
        if df_qr.empty:
            return []
            
        # 2. Get Blink Raw Orders for matching
        ref_ids = df_qr['external_ref_id'].unique().tolist()
        ref_ids = [r for r in ref_ids if r]
        
        if ref_ids:
            from blink_utils import prepare_blink_orders
            raw_query = f"""
            SELECT BlinkOrderId, OrderJson, CreatedAt
            FROM tblInitialRawBlinkOrder WITH (NOLOCK)
            WHERE LTRIM(RTRIM(CONVERT(varchar(64), BlinkOrderId))) IN ({placeholders(len(ref_ids))})
            """
            df_raw = run_query(raw_query, params=tuple(ref_ids))
            df_blink = prepare_blink_orders(df_raw)
            
            # Merge
            df_qr["_ext_ref_key"] = df_qr["external_ref_id"].astype(str).str.strip()
            df_blink["_blink_id_key"] = df_blink["BlinkOrderId"].astype(str).str.strip()
            df_merged = df_qr.merge(df_blink, left_on="_ext_ref_key", right_on="_blink_id_key", how="left")
        else:
            df_merged = df_qr.copy()
            df_merged['Indoge_total_price'] = 0.0
            df_merged['BlinkOrderId'] = None
            
        df_merged['Indoge_total_price'] = df_merged.get('Indoge_total_price', 0.0).fillna(0.0)
        df_merged['difference'] = df_merged['Indoge_total_price'] - df_merged['total_sale']
        df_merged['Candelahns_commission'] = df_merged['total_sale'] * (commission_rate / 100)
        df_merged['Indoge_commission'] = df_merged['Indoge_total_price'] * (commission_rate / 100)
        
        # Replace NaNs for JSON
        df_merged = df_merged.replace({np.nan: None})
        
        return df_merged.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
