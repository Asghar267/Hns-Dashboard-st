import pandas as pd
from modules.database import get_cached_line_items
from modules.config import HIDDEN_PRODUCTS

def exhaustive_audit():
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    # Use ALL branches for now to find the ratio
    branches = [2, 4, 8, 10, 14, 15]
    data_mode = 'Filtered'
    
    # Fetch raw data
    df_raw = get_cached_line_items(start_date, end_date, branches, data_mode, apply_category_filters=False)
    
    # Identify what's in "All Products" table vs what is missing
    summary = df_raw.groupby('product')['total_line_value_incl_tax'].sum().sort_values(ascending=False).reset_index()
    
    print("\n--- EVERY PRODUCT CATEGORY IN DATABASE (March) ---")
    print(summary)
    
    # Identify which ones are HIDDEN by HIDDEN_PRODUCTS
    print("\n--- CURRENT HIDDEN_PRODUCTS FILTER ---")
    print(f"Filter List: {HIDDEN_PRODUCTS}")
    
    hidden_revenue = summary[summary['product'].isin(HIDDEN_PRODUCTS)]
    print("\nRevenue being hidden by HIDDEN_PRODUCTS filter:")
    print(hidden_revenue)
    
    # Identify Unmapped/Unused
    print("\nRevenue in Unused/Unmapped:")
    special_hidden = summary[summary['product'].isin(['Unused', '(Unmapped)'])]
    print(special_hidden)
    
    # Finding the "Missing" revenue by comparing with user's list
    # User's list: Rolls, Fast Food, Handi, Bar B Q, Chinese, Beverages, Tandoor, Juices, Karahi, Deals, Side Orders, Nashta
    user_list = [
        "Sales - Rolls", "Sales - Fast Food", "Sales - Handi", "Sales - Bar B Q",
        "Sales - Chinese", "Sales - Beverages", "Sales-Tandoor", 
        "Sales - Juices Shakes & Desserts", "Sales - Karahi", "Deals", 
        "Sales Side Orders", "Sales-Nashta"
    ]
    
    print("\nRevenue in categories NOT in your current table:")
    missing = summary[~summary['product'].isin(user_list)]
    print(missing)

if __name__ == "__main__":
    exhaustive_audit()
