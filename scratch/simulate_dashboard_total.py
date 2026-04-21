import pandas as pd
from modules.database import get_cached_line_items
from modules.config import HIDDEN_PRODUCTS

def simulate():
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    # branches = [2, 4, 14] # Assuming these are what user sees to get 55M
    branches = [2, 4, 8, 10, 14, 15]
    data_mode = 'Filtered'
    
    # 1. Fetch raw data (re-implementing ChefSalesTab.__init__)
    df_raw = get_cached_line_items(start_date, end_date, branches, data_mode, apply_category_filters=False)
    
    hidden_categories = ['Unused', '(Unmapped)']
    df_hidden = df_raw[df_raw["product"].isin(hidden_categories)].copy()
    df_line_item = df_raw[~df_raw["product"].isin(hidden_categories)].copy()
    
    # 2. Simulate render_chef_sales logic (filters)
    df_line = df_line_item.copy()
    # include_hidden = False in UI
    if HIDDEN_PRODUCTS:
        df_line = df_line[~df_line["product"].isin(HIDDEN_PRODUCTS)].copy()
    
    total_sales = df_line["total_line_value_incl_tax"].sum()
    
    print(f"Total Sales KPI: {total_sales:,.2f}")
    print("\nBreakdown by Product/Category in Total:")
    print(df_line.groupby('product')['total_line_value_incl_tax'].sum().sort_values(ascending=False))
    
    print("\nBreakdown of HIDDEN items (excluded from Total):")
    print(df_hidden.groupby('product')['total_line_value_incl_tax'].sum().sort_values(ascending=False))
    
    print("\nBreakdown of EXCLUDED via HIDDEN_PRODUCTS:")
    excluded = df_line_item[df_line_item["product"].isin(HIDDEN_PRODUCTS)]
    print(excluded.groupby('product')['total_line_value_incl_tax'].sum().sort_values(ascending=False))

if __name__ == "__main__":
    simulate()
