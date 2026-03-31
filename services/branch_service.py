"""
Branch Service
Handles branch-related business logic and calculations
"""

import pandas as pd
from typing import Dict, List
from modules.database import (
    get_cached_branch_summary,
    get_cached_daily_sales_by_branch,
    get_cached_product_monthly_sales_by_product,
    get_cached_line_items,
    get_cached_ot_data
)


class BranchService:
    """Service for branch-related operations"""
    
    @staticmethod
    def get_branch_summary(start_date: str, end_date: str, selected_branches: List[int], data_mode: str, branch_targets: Dict[int, float] = None) -> pd.DataFrame:
        """Get branch summary with targets and calculations"""
        df_branch = get_cached_branch_summary(start_date, end_date, selected_branches, data_mode)
        
        if df_branch.empty:
            return df_branch
            
        # Add targets
        df_branch_display = df_branch.copy()
        df_branch_display['total_Nt_amount'] = df_branch_display['total_Nt_amount'].astype(float)
        
        if branch_targets:
            df_branch_display['Monthly_Target'] = df_branch_display['shop_id'].map(branch_targets).fillna(0).astype(float)
        else:
            df_branch_display['Monthly_Target'] = 0.0
        
        # Merge FESTIVAL (ID 3) + FESTIVAL 2 (ID 14) for overview
        festival_mask = df_branch_display['shop_id'] == 3
        festival2_mask = df_branch_display['shop_id'] == 14
        if festival_mask.any() and festival2_mask.any():
            festival2_sales = df_branch_display.loc[festival2_mask, 'total_Nt_amount'].sum()
            df_branch_display.loc[festival_mask, 'total_Nt_amount'] += festival2_sales
            df_branch_display.loc[festival_mask, 'shop_name'] = "FESTIVAL"
            df_branch_display = df_branch_display.loc[~festival2_mask].copy()
            
        # Calculate derived metrics
        df_branch_display['Remaining_Target'] = df_branch_display['Monthly_Target'] - df_branch_display['total_Nt_amount']
        df_branch_display['Achievement_%'] = df_branch_display.apply(
            lambda row: (row['total_Nt_amount'] / row['Monthly_Target'] * 100) if row['Monthly_Target'] > 0 else 0,
            axis=1
        )
            
        return df_branch_display
    
    @staticmethod
    def calculate_summary_metrics(df_branch: pd.DataFrame) -> Dict[str, float]:
        """Calculate summary metrics for branches"""
        total_sales = df_branch['total_Nt_amount'].sum()
        total_target = df_branch['Monthly_Target'].sum() if 'Monthly_Target' in df_branch.columns else 0
        total_remaining = total_target - total_sales
        overall_achievement = (total_sales / total_target * 100) if total_target > 0 else 0
        
        return {
            'total_sales': total_sales,
            'total_target': total_target,
            'total_remaining': total_remaining,
            'overall_achievement': overall_achievement
        }
    
    @staticmethod
    def get_top_highlights(start_date: str, end_date: str, selected_branches: List[int], data_mode: str) -> Dict[str, pd.DataFrame]:
        """Get top 5 highlights for the dashboard"""
        highlights = {}
        
        # Top 5 Chef Sales (by product revenue)
        df_line_item = get_cached_line_items(start_date, end_date, selected_branches, data_mode)
        if not df_line_item.empty:
            df_top_products = df_line_item.groupby('product', as_index=False).agg({
                'total_line_value_incl_tax': 'sum'
            }).sort_values('total_line_value_incl_tax', ascending=False).head(5)
            highlights['chef_sales'] = df_top_products
        
        # Top 5 Line Item Sub-Products (product names)
        try:
            from datetime import datetime
            current_year = datetime.now().year
            current_month = datetime.now().month
            
            df_top_items = get_cached_product_monthly_sales_by_product(
                current_year, current_month, selected_branches, data_mode, category=None
            )
            if df_top_items is not None and not df_top_items.empty:
                highlights['line_items'] = df_top_items.head(5)
        except Exception:
            pass
        
        # Top 5 OT Sales
        df_ot = get_cached_ot_data(start_date, end_date, selected_branches, data_mode)
        if not df_ot.empty:
            df_top_ot = df_ot.sort_values('total_sale', ascending=False).head(5)
            highlights['ot_sales'] = df_top_ot
        
        return highlights
    
    @staticmethod
    def get_daily_sales_by_branch(start_date: str, end_date: str, selected_branches: List[int], data_mode: str) -> pd.DataFrame:
        """Get daily sales by branch for last 30 days"""
        df_daily_branch = get_cached_daily_sales_by_branch(start_date, end_date, selected_branches, data_mode)
        
        if df_daily_branch.empty:
            return df_daily_branch
            
        # Pivot to Date x Branch for easier viewing
        pivot_daily = (
            df_daily_branch
            .pivot_table(index='day', columns='shop_name', values='total_Nt_amount', aggfunc='sum')
            .sort_index()
            .fillna(0)
        )
        display_daily = pivot_daily.reset_index().rename(columns={'day': 'Date'})
        display_daily['Date'] = display_daily['Date'].dt.strftime("%Y-%m-%d")
        
        return display_daily

    @staticmethod
    def get_performance_heatmap_data(df_branch: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for branch performance heatmap"""
        if df_branch.empty:
            return pd.DataFrame()
            
        df = df_branch.copy()
        df['Achievement_%'] = (df['total_Nt_amount'] / df['Monthly_Target'] * 100).fillna(0)
        return df[['shop_name', 'total_Nt_amount', 'Monthly_Target', 'Achievement_%']]
