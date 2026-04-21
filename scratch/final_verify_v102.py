import pandas as pd
# Import with updated signature
from modules.database import get_cached_line_items
from modules.config import HIDDEN_PRODUCTS

def simulate():
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    branches = [2, 4, 14]
    data_mode = 'Filtered'
    
    # Use the same cache version as the dashboard
    df_raw = get_cached_line_items(
        start_date, end_date, branches, data_mode, 
        apply_category_filters=False, 
        cache_version=102
    )
    
    hidden_categories = ['Unused', '(Unmapped)']
    df_line_item = df_raw[~df_raw["product"].isin(hidden_categories)].copy()
    
    df_line = df_line_item.copy()
    if HIDDEN_PRODUCTS:
        df_line = df_line[~df_line["product"].isin(HIDDEN_PRODUCTS)].copy()
    
    total_sales = df_line["total_line_value_incl_tax"].sum()
    
    print(f"\n===== RESULTS FOR BRANCHES {branches} (v102) =====")
    print(f"Total Sales KPI: {total_sales:,.2f}")
    
    print("\nDetailed Breakdown (Top 20):")
    breakdown = df_line.groupby('product')['total_line_value_incl_tax'].sum().sort_values(ascending=False).reset_index()
    print(breakdown.head(20))

if __name__ == "__main__":
    simulate()
