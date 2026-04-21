"""
Targets Service
Handles business logic for Chef Targets, OT Targets, and Daily Product Targets
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta
from calendar import monthrange
from typing import List
from modules.database import pool, build_filter_clause, placeholders

class TargetService:
    """Service for target-related operations and analysis"""

    @staticmethod
    def get_chef_targets_analysis(
        shop_id: int, 
        target_year: int, 
        target_month: int,
        chef_targets: pd.DataFrame,
        df_line_item: pd.DataFrame,
        sale_categories: List[str],
        qty_categories: List[str]
    ) -> pd.DataFrame:
        """Analyze chef targets achievement for a specific branch and period"""
        if chef_targets.empty or df_line_item.empty:
            return pd.DataFrame()

        df_chef_filtered = chef_targets[chef_targets['shop_id'] == shop_id].copy()
        if df_chef_filtered.empty:
            return pd.DataFrame()

        try:
            conn_kds = pool.get_connection("kdsdb")
            categories = pd.read_sql("SELECT * FROM dbo.chef_sale", conn_kds)
            
            # Merge targets with categories
            df_targets_with_categories = df_chef_filtered.merge(categories, on='category_id', how='left')
            
            # Filter to only show specified categories
            allowed_categories = sale_categories + qty_categories
            df_targets_with_categories = df_targets_with_categories[
                df_targets_with_categories['category_name'].isin(allowed_categories)
            ]
            
            def _normalize_target_type(v) -> str:
                s = str(v or "").strip().lower()
                if not s:
                    return ""
                if s.startswith("q") or "qty" in s or "quantity" in s:
                    return "quantity"
                if s.startswith("s") or "sale" in s or "amount" in s or "value" in s:
                    return "amount"
                return "amount"

            # Prefer DB-provided target_type when present (e.g. 'quantity'), otherwise fallback to category lists.
            has_db_type = "target_type" in df_targets_with_categories.columns and df_targets_with_categories["target_type"].notna().any()
            if has_db_type:
                norm = df_targets_with_categories["target_type"].map(_normalize_target_type)
                fallback = df_targets_with_categories['category_name'].apply(
                    lambda cat: 'amount' if cat in sale_categories else ('quantity' if cat in qty_categories else 'amount')
                )
                df_targets_with_categories["target_type"] = norm.where(norm.astype(str).str.len() > 0, fallback)
            else:
                df_targets_with_categories['target_type'] = df_targets_with_categories['category_name'].apply(
                    lambda cat: 'amount' if cat in sale_categories else ('quantity' if cat in qty_categories else 'amount')
                )
            
            # Get sales data for this branch
            df_sales_this_branch = df_line_item[df_line_item['shop_id'] == shop_id].copy()
            products_to_hide = ['Sales - Employee Food', 'Modifiers']
            df_sales_this_branch = df_sales_this_branch[~df_sales_this_branch['product'].isin(products_to_hide)]
            
            # Clean names for merging
            def clean_name(name):
                name = str(name).upper()
                name = name.replace("SALES -", "").replace("SALES", "").strip()
                name = name.replace("SIDE ORDERS", "SIDE ORDER")
                name = name.replace("-", " ")
                words = name.split()
                cleaned_words = []
                for word in words:
                    if word == 'ROLLS': word = 'ROLL'
                    elif word == 'ORDERS': word = 'ORDER'
                    elif word == 'SIDES': word = 'SIDE'
                    elif word == 'DEALS': word = 'DEAL'
                    elif word == 'NASHTA': word = 'BREAKFAST'
                    cleaned_words.append(word)
                return ' '.join(cleaned_words)
            
            df_sales_this_branch['product_clean'] = df_sales_this_branch['product'].apply(clean_name)
            df_targets_with_categories['category_clean'] = df_targets_with_categories['category_name'].apply(clean_name)
            
            # Merge
            df_res = df_targets_with_categories.merge(
                df_sales_this_branch, 
                left_on='category_clean', 
                right_on='product_clean', 
                how='left'
            ).fillna({'total_line_value_incl_tax': 0, 'total_qty': 0})
            
            df_res['product'] = df_res['product'].fillna(df_res['category_name'])
            
            # Calculate Current
            df_res['Current Sale'] = df_res.apply(
                lambda row: row['total_line_value_incl_tax'] if row['target_type'] == 'amount' else row['total_qty'],
                axis=1
            )
            
            # Final columns
            df_res = df_res.rename(columns={'target_amount': 'Target', 'target_type': 'Type', 'product': 'Product'})
            df_res['Target'] = pd.to_numeric(df_res['Target'], errors='coerce').fillna(0)
            df_res['Current Sale'] = pd.to_numeric(df_res['Current Sale'], errors='coerce').fillna(0)
            
            num_days = monthrange(target_year, target_month)[1]
            df_res['Daily Target'] = df_res['Target'] / num_days
            df_res['Remaining'] = df_res['Target'] - df_res['Current Sale']
            df_res['Achievement %'] = df_res.apply(
                lambda row: (row['Current Sale'] / row['Target'] * 100) if row['Target'] > 0 else 0,
                axis=1
            )
            df_res['Bonus'] = df_res.apply(
                lambda row: row['Current Sale'] * 0.5 if row['Achievement %'] >= 100 else 0, 
                axis=1
            )
            
            return df_res[['Product', 'Target', 'Daily Target', 'Type', 'Current Sale', 'Remaining', 'Achievement %', 'Bonus']]
            
        except Exception as e:
            print(f"Error in get_chef_targets_analysis: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_ot_targets_analysis(
        shop_id: int,
        target_year: int,
        target_month: int,
        ot_targets: pd.DataFrame,
        df_ot: pd.DataFrame,
        data_mode: str
    ) -> pd.DataFrame:
        """Analyze Order Taker target achievement"""
        if df_ot.empty:
            return pd.DataFrame()

        df_ot_branch = df_ot[df_ot['shop_id'] == shop_id].copy()
        if not ot_targets.empty:
            # Filter targets to the specific branch and period (already filtered by period in get_cached_targets)
            df_ot_targets_branch = ot_targets[ot_targets['shop_id'] == shop_id]
            
            # Use shop_id and employee_id as merge keys. 
            # If multiple targets exist for different periods, get_cached_targets should have handled it.
            df_ot_perf = df_ot_branch.merge(
                df_ot_targets_branch, 
                on=['shop_id', 'employee_id'], 
                how='left'
            ).fillna({'target_amount': 0})
        else:
            df_ot_perf = df_ot_branch
            df_ot_perf['target_amount'] = 0

        # Further refinement for yesterday and MTD per OT
        employee_ids = df_ot_perf['employee_id'].dropna().astype(int).unique().tolist()
        if not employee_ids:
            return df_ot_perf

        today = date.today()
        yesterday = today - timedelta(days=1)
        month_start = date(target_year, target_month, 1)
        
        try:
            conn = pool.get_connection("candelahns")
            filter_clause, filter_params = build_filter_clause(data_mode)

            def fetch_ot_sales_range(start_d: date, end_d: date) -> pd.DataFrame:
                end_next = end_d + timedelta(days=1)
                query = f"""
                SELECT s.employee_id, SUM(s.Nt_amount) AS total_sale
                FROM tblSales s
                WHERE s.sale_date >= ? AND s.sale_date < ?
                  AND s.shop_id = ?
                  AND s.employee_id IN ({placeholders(len(employee_ids))})
                {filter_clause}
                GROUP BY s.employee_id
                """
                params = [start_d.strftime("%Y-%m-%d"), end_next.strftime("%Y-%m-%d"), shop_id] + employee_ids + filter_params
                return pd.read_sql(query, conn, params=params)

            df_yest = fetch_ot_sales_range(yesterday, yesterday).rename(columns={'total_sale': 'Yesterday Sale'})
            df_mtd = fetch_ot_sales_range(month_start, today).rename(columns={'total_sale': 'MTD Sale'})

            df_ot_perf = df_ot_perf.merge(df_yest, on='employee_id', how='left')
            df_ot_perf = df_ot_perf.merge(df_mtd, on='employee_id', how='left')
            df_ot_perf = df_ot_perf.fillna({'Yesterday Sale': 0, 'MTD Sale': 0})

            # Calculations
            df_ot_perf['Daily Target'] = df_ot_perf['target_amount'] / monthrange(target_year, target_month)[1]
            df_ot_perf['Achievement %'] = (df_ot_perf['MTD Sale'] / df_ot_perf['target_amount'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
            
            return df_ot_perf[['employee_id', 'employee_name', 'Yesterday Sale', 'MTD Sale', 'target_amount', 'Daily Target', 'Achievement %']]

        except Exception as e:
            print(f"Error in get_ot_targets_analysis: {e}")
            return df_ot_perf

    @staticmethod
    def get_daily_product_targets(
        selected_branches: List[int],
        data_mode: str
    ) -> pd.DataFrame:
        """Get product targets based on 25% growth over previous day"""
        try:
            conn = pool.get_connection("candelahns")
            filter_clause, filter_params = build_filter_clause(data_mode)

            def fetch_range_sales(start_d: date, end_d: date) -> pd.DataFrame:
                end_next = end_d + timedelta(days=1)
                query = f"""
                SELECT
                    p.item_name AS product,
                    SUM(li.qty) AS total_qty
                FROM tblSales s WITH (NOLOCK)
                JOIN tblSalesLineItems li WITH (NOLOCK) ON s.sale_id = li.sale_id
                LEFT JOIN tblProductItem pi WITH (NOLOCK) ON li.Product_Item_ID = pi.Product_Item_ID
                LEFT JOIN tblDefProducts p WITH (NOLOCK) ON pi.Product_ID = p.product_id
                WHERE s.sale_date >= ? AND s.sale_date < ?
                  AND s.shop_id IN ({placeholders(len(selected_branches))})
                  AND p.item_name IS NOT NULL AND LTRIM(RTRIM(p.item_name)) <> ''
                {filter_clause}
                GROUP BY p.item_name
                """
                params = [start_d.strftime("%Y-%m-%d"), end_next.strftime("%Y-%m-%d")] + selected_branches + filter_params
                return pd.read_sql(query, conn, params=params)

            today = date.today()
            yesterday = today - timedelta(days=1)
            month_start = date(today.year, today.month, 1)

            df_today = fetch_range_sales(today, today).rename(columns={'total_qty': 'today_qty'})
            df_yest = fetch_range_sales(yesterday, yesterday).rename(columns={'total_qty': 'yesterday_qty'})
            df_mtd = fetch_range_sales(month_start, today).rename(columns={'total_qty': 'mtd_qty'})

            # Union products
            prods = set(df_mtd['product'].unique()) | set(df_yest['product'].unique()) | set(df_today['product'].unique())
            df_res = pd.DataFrame({'Product': list(prods)})
            
            df_res = df_res.merge(df_yest, left_on='Product', right_on='product', how='left').drop(columns=['product'])
            df_res = df_res.merge(df_today, left_on='Product', right_on='product', how='left').drop(columns=['product'])
            df_res = df_res.merge(df_mtd, left_on='Product', right_on='product', how='left').drop(columns=['product'])
            
            df_res = df_res.fillna(0)
            
            df_res['Today Target'] = df_res['yesterday_qty'] * 1.25
            df_res['Remaining'] = df_res['Today Target'] - df_res['today_qty']
            df_res['Achievement %'] = df_res.apply(
                lambda row: (row['today_qty'] / row['Today Target'] * 100) if row['Today Target'] > 0 else 0,
                axis=1
            )
            
            return df_res[['Product', 'yesterday_qty', 'Today Target', 'today_qty', 'Remaining', 'Achievement %']]

        except Exception as e:
            print(f"Error in get_daily_product_targets: {e}")
            return pd.DataFrame()
