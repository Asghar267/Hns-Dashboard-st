import os
import sys
import pandas as pd

# Add the project root to sys.path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.config import (
    FRESH_PICK_PRODUCTS,
    FRESH_PICK_SALES_ITEM_NAMES,
    FRESH_PICK_VENDOR_ALIASES
)

def verify_mappings():
    print("--- FRESH PICK CONFIGURATION VERIFICATION ---")
    
    print("\nCanonical Products (Targets):")
    for p in FRESH_PICK_PRODUCTS:
        print(f"  - {p}")
        
    print("\nSales Database Item Variants:")
    for v in FRESH_PICK_SALES_ITEM_NAMES:
        print(f"  - {v}")
        
    print("\nVendor Aliases:")
    for k, v in FRESH_PICK_VENDOR_ALIASES.items():
        print(f"  - {k} -> {v}")

    # Simulated filter_names logic from database.py
    filter_names = []
    for name in (FRESH_PICK_PRODUCTS or []) + (FRESH_PICK_SALES_ITEM_NAMES or []):
        text = str(name or "").strip().lower()
        if text:
            filter_names.append(text)
    filter_names = list(dict.fromkeys(filter_names))
    
    print("\nGenerated Filter Names for SQL (LOWER/TRIM):")
    for fn in filter_names:
        print(f"  - '{fn}'")

    # Test cases
    test_products = [
        "Chicken Breast Boneless",
        "Chicken Neck & Rib Cage",
        "Whole Chicken Skin-on"
    ]
    
    print("\nTesting matches for key items:")
    for tp in test_products:
        hit = tp.strip().lower() in filter_names
        print(f"  - '{tp}' match: {hit}")

if __name__ == "__main__":
    verify_mappings()
