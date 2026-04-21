import os
import sys
import pandas as pd
from datetime import date

# Add current dir to path
sys.path.append(os.getcwd())

from services.targets_service import TargetService
from modules.database import get_cached_line_items, get_cached_targets
from modules.config import SALE_CATEGORIES, QTY_CATEGORIES

def verify_breakfast():
    year, month = 2026, 4
    start_date = "2026-04-01"
    end_date = "2026-04-17"
    shop_id = 2 # Khadda
    
    # 1. Get cached data
    _, chef_targets, _, _ = get_cached_targets(year, month)
    df_line_item = get_cached_line_items(start_date, end_date, [shop_id], "Filtered", apply_category_filters=False)
    
    if chef_targets is None or chef_targets.empty:
        print("No targets found.")
        return
    if df_line_item is None or df_line_item.empty:
        print("No sales data found.")
        return
        
    # 2. Run analysis
    analysis = TargetService.get_chef_targets_analysis(
        shop_id, year, month, chef_targets, df_line_item, SALE_CATEGORIES, QTY_CATEGORIES
    )
    
    if analysis.empty:
        print("Analysis returned empty.")
        return
        
    print("\n--- Chef Targets Analysis (Breakfast Check) ---")
    # Filter for Breakfast/Nashta related products
    breakfast_check = analysis[analysis['Product'].str.contains('Breakfast|Nashta', case=False, na=False)]
    if breakfast_check.empty:
        print("No 'Breakfast' or 'Nashta' related product found in analysis.")
        print("Available Products:", analysis['Product'].unique().tolist())
    else:
        print(breakfast_check)

if __name__ == "__main__":
    verify_breakfast()
