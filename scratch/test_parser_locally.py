import sys
import os
import json

# Add current dir to path
sys.path.append(os.getcwd())

from modules.blink_reporting import safe_json_order_fields

def test_parser():
    # Load test.json
    with open('test.json', 'r') as f:
        content = f.read()
    
    # Parse it
    price, qty, count, time_val, ok = safe_json_order_fields(content)
    
    print(f"Price found: {price}")
    print(f"Qty found: {qty}")
    print(f"Item count: {count}")
    print(f"Success: {ok}")
    
    if price == 794.0:
        print("✅ Correct: Found top-level total_price (794)")
    elif price == 345.0:
        print("❌ Bug: Found item-level total_price (345) instead of top-level!")
    else:
        print(f"❓ Unexpected price: {price}")

if __name__ == "__main__":
    test_parser()
