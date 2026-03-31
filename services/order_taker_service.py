"""
Order Taker Service
Handles Order Taker-related business logic and calculations
"""

import pandas as pd
from typing import Dict, List
from modules.database import (
    get_cached_ot_data,
)


def exclude_employee_names(df: pd.DataFrame, column: str = "employee_name") -> pd.DataFrame:
    """Exclude non-attributed employee rows from analytics and tables."""
    if df is None or df.empty or column not in df.columns:
        return df
    normalized = df[column].astype(str).str.strip().str.lower()
    return df[~normalized.isin({"online/unassigned"})].copy()


class OrderTakerService:
    """Service for Order Taker-related operations"""
    
    @staticmethod
    def get_ot_summary(start_date: str, end_date: str, selected_branches: List[int], data_mode: str) -> pd.DataFrame:
        """Get Order Taker summary data"""
        df_ot = get_cached_ot_data(start_date, end_date, selected_branches, data_mode)
        
        if df_ot.empty:
            return df_ot
            
        # Exclude non-attributed rows
        df_ot = exclude_employee_names(df_ot, "employee_name")
        
        return df_ot
    
    @staticmethod
    def calculate_ot_metrics(df_ot: pd.DataFrame) -> Dict[str, float]:
        """Calculate Order Taker metrics"""
        total_ot_sales = df_ot['total_sale'].sum()
        unique_ots = df_ot['employee_id'].nunique()
        avg_sale_per_ot = total_ot_sales / unique_ots if unique_ots > 0 else 0
        
        return {
            'total_ot_sales': total_ot_sales,
            'unique_ots': unique_ots,
            'avg_sale_per_ot': avg_sale_per_ot
        }
    
    @staticmethod
    def get_top_performers(df_ot: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
        """Get top performing Order Takers"""
        return df_ot.sort_values('total_sale', ascending=False).head(limit)
    
    @staticmethod
    def filter_ot_by_search(df_ot: pd.DataFrame, search: str) -> pd.DataFrame:
        """Filter Order Takers by search term"""
        if search:
            return df_ot[
                df_ot['employee_name'].str.contains(search, case=False, na=False)
            ]
        return df_ot
