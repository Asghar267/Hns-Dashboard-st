import sys
import os
import json

# Add current dir to path
sys.path.append(os.getcwd())

from modules.blink_reporting import safe_json_order_fields

def test_variant():
    # Scenario: Top level has grand_total, item level has total_price
    # Keys in code: "total_price", "totalPrice", "total", "grand_total", ...
    # Bug: _walk_find_key will find total_price in items before it ever sees grand_total if it recurses.
    
    malicious_json = {
        "blink_order_id": "TEST123",
        "products": [
            {
                "name": "Item 1",
                "total_price": 500  # <--- Smaller price
            }
        ],
        "grand_total": 1200 # <--- Real total
    }
    
    content = json.dumps(malicious_json)
    price, qty, count, time_val, ok = safe_json_order_fields(content)
    
    print(f"Scenario 1: grand_total at top, total_price in items")
    print(f"Price found: {price}")
    if price == 1200.0:
        print("RESULT: Correct (Found 1200)")
    elif price == 500.0:
        print("RESULT: BUG (Found 500 from item)")
    
    # Another scenario: total at top level, but totalPrice in items
    another_json = {
        "products": [{"totalPrice": 100}],
        "total": 1500
    }
    price2, *_ = safe_json_order_fields(json.dumps(another_json))
    print(f"\nScenario 2: total at top, totalPrice in items")
    print(f"Price found: {price2}")
    if price2 == 1500.0:
        print("RESULT: Correct (Found 1500)")
    elif price2 == 100.0:
        print("RESULT: BUG (Found 100 from item)")

if __name__ == "__main__":
    test_variant()
