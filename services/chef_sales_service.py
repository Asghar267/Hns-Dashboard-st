"""
Chef Sales Service
Handles Chef Sales and product performance business logic
"""

import pandas as pd
from typing import List
from modules.database import (
    get_cached_line_items,
)
from modules.utils import (
    format_currency
)


class ChefSalesService:
    """Service for Chef Sales-related operations"""
    
    @staticmethod
    def get_product_summary(start_date: str, end_date: str, selected_branches: List[int], data_mode: str) -> pd.DataFrame:
        """Get product summary data"""
        df_line_item = get_cached_line_items(start_date, end_date, selected_branches, data_mode)
        
        if df_line_item.empty:
            return df_line_item
            
        # Product analysis
        df_product_summary = df_line_item.groupby('product').agg({
            'total_qty': 'sum',
            'total_line_value_incl_tax': 'sum'
        }).reset_index()
        df_product_summary = df_product_summary.sort_values(
            'total_line_value_incl_tax', ascending=False
        )
        
        return df_product_summary
    
    @staticmethod
    def get_top_products(df_product_summary: pd.DataFrame, limit: int = 15) -> pd.DataFrame:
        """Get top products by revenue"""
        return df_product_summary.head(limit)
    
    @staticmethod
    def get_branch_products(df_line_item: pd.DataFrame) -> pd.DataFrame:
        """Get products by branch"""
        display_branch_products = df_line_item.copy()
        display_branch_products = display_branch_products.rename(
            columns={
                'shop_name': 'Branch',
                'product': 'Product',
                'total_qty': 'Total Qty',
                'total_line_value_incl_tax': 'Total Sales'
            }
        )
        display_branch_products['Total Qty'] = display_branch_products['Total Qty'].apply(lambda x: f"{x:,.0f}")
        display_branch_products['Total Sales'] = display_branch_products['Total Sales'].apply(lambda x: format_currency(x))
        display_branch_products = display_branch_products.sort_values(['Branch', 'Total Sales'], ascending=[True, False])
        
        return display_branch_products
    
    @staticmethod
    def get_category_distribution(df_product_summary: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
        """Get category distribution for pie chart"""
        return df_product_summary.head(limit)
    
    @staticmethod
    def filter_products_by_search(df_product_summary: pd.DataFrame, search: str) -> pd.DataFrame:
        """Filter products by search term"""
        if search:
            return df_product_summary[
                df_product_summary['product'].str.contains(search, case=False, na=False)
            ]
        return df_product_summary

    @staticmethod
    def get_reconciliation_data(df_line_item: pd.DataFrame, df_branch: pd.DataFrame) -> pd.DataFrame:
        """Reconcile Chef sales totals with Overview branch totals"""
        if df_line_item.empty or df_branch.empty:
            return pd.DataFrame()
            
        try:
            df_chef_branch = (
                df_line_item.groupby(['shop_id', 'shop_name'], as_index=False)
                .agg({'total_line_value_incl_tax': 'sum'})
                .rename(columns={'total_line_value_incl_tax': 'chef_sales_total'})
            )

            df_overview_branch = df_branch[['shop_id', 'shop_name', 'total_Nt_amount']].copy()
            df_overview_branch['total_Nt_amount'] = pd.to_numeric(
                df_overview_branch['total_Nt_amount'], errors='coerce'
            ).fillna(0.0)
            df_overview_branch = df_overview_branch.rename(columns={'total_Nt_amount': 'overview_sales_total'})

            df_reconcile = df_overview_branch.merge(
                df_chef_branch,
                on=['shop_id', 'shop_name'],
                how='left'
            )
            df_reconcile['chef_sales_total'] = pd.to_numeric(df_reconcile['chef_sales_total'], errors='coerce').fillna(0.0)
            df_reconcile['difference'] = df_reconcile['overview_sales_total'] - df_reconcile['chef_sales_total']
            df_reconcile = df_reconcile.sort_values('shop_id')
            
            return df_reconcile
        except Exception as e:
            print(f"Error in get_reconciliation_data: {e}")
            return pd.DataFrame()
