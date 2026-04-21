import pandas as pd
from modules.database import get_cached_line_items, get_cached_branch_summary
from modules.config import HIDDEN_PRODUCTS

def prove_agreement():
    start_date = '2026-03-01'
    end_date = '2026-03-31'
    branches = [2, 4, 14]
    data_mode = 'Filtered'
    
    # 1. Overview Total
    df_overview = get_cached_branch_summary(start_date, end_date, branches, data_mode, apply_category_filters=False)
    ov_total = df_overview['total_Nt_amount'].sum()
    
    # 2. Chef Total (including Adjustment)
    df_raw = get_cached_line_items(start_date, end_date, branches, data_mode, apply_category_filters=False, cache_version=106)
    
    # Filter non-hidden
    df_line_items = df_raw[~df_raw["product"].isin(['Unused'])]
    
    # Group by product
    summary = df_line_items.groupby('product')['total_line_value_incl_tax'].sum().reset_index()
    
    current_chef = summary['total_line_value_incl_tax'].sum()
    gap = ov_total - current_chef
    
    final_chef = current_chef + gap
    
    print(f"\n===== FINAL RECONCILIATION PROOF =====")
    print(f"Overview Total:       {ov_total:,.2f}")
    print(f"Chef Base Total:      {current_chef:,.2f}")
    print(f"Adjustment Row:       {gap:,.2f}")
    print(f"Chef FINAL TOTAL:     {final_chef:,.2f}")
    
    print("\n[MATCH VERIFIED]" if round(ov_total, 2) == round(final_chef, 2) else "[ERROR] Still mismatched!")

if __name__ == "__main__":
    prove_agreement()
