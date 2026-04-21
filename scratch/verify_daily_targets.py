import os
import sys
import pandas as pd
from datetime import date

# Add current dir to path
sys.path.append(os.getcwd())

from services.targets_service import TargetService
from modules.database import get_cached_line_items, get_cached_targets
from modules.config import SALE_CATEGORIES, QTY_CATEGORIES

def verify_daily_targets():
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
        
    # 2. Run analysis
    analysis = TargetService.get_chef_targets_analysis(
        shop_id, year, month, chef_targets, df_line_item, SALE_CATEGORIES, QTY_CATEGORIES
    )
    
    if analysis.empty:
        print("Analysis returned empty.")
        return
        
    print("\n--- Chef Targets Analysis (Daily Target Check) ---")
    print(analysis[['Product', 'Target', 'Daily Target', 'Type']].head(10))
    
    if 'Daily Target' in analysis.columns:
        print("\n✅ Success: 'Daily Target' column is present.")
        # Check calculation for first row
        row0 = analysis.iloc[0]
        expected = row0['Target'] / 30 # April has 30 days
        if abs(row0['Daily Target'] - expected) < 0.01:
            print(f"✅ Calculation correct for {row0['Product']}: {row0['Daily Target']:.2f}")
        else:
            print(f"❌ Calculation incorrect. Expected {expected}, got {row0['Daily Target']}")
    else:
        print("\n❌ Error: 'Daily Target' column is missing.")

if __name__ == "__main__":
    verify_daily_targets()
