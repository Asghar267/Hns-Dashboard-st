import pandas as pd

from modules.foodpanda_reconciliation import reconcile_foodpanda_orders


def test_reconcile_picks_closest_date_then_amount_then_sale_id():
    df_excel = pd.DataFrame(
        {
            "Order Code": ["qtov-1"],
            "excel_order_code_norm": ["qtov-1"],
            "excel_order_date": [pd.Timestamp("2026-03-10")],
            "excel_order_amount": [100.0],
        }
    )

    df_db = pd.DataFrame(
        {
            "sale_id": [10, 11, 12],
            "sale_date": [
                pd.Timestamp("2026-03-09"),
                pd.Timestamp("2026-03-10"),
                pd.Timestamp("2026-03-10"),
            ],
            "NT_amount": [99.0, 101.0, 100.0],
            "adjustment_comments": ["qtov-1", "qtov-1", "qtov-1"],
            "Additional_Comments": ["", "", ""],
            "external_ref_id": ["", "", ""],
            "db_order_code_norm": ["qtov-1", "qtov-1", "qtov-1"],
        }
    )

    r = reconcile_foodpanda_orders(df_excel, df_db, tolerance_pkr=1.0)
    # Closest date are rows 11 and 12; pick higher amount first (101) over 100.
    assert int(r.full.iloc[0]["sale_id_sort"]) == 11


def test_reconcile_statuses():
    df_excel = pd.DataFrame(
        {
            "Order Code": ["a", "b", "c"],
            "excel_order_code_norm": ["a", "b", "c"],
            "excel_order_date": [pd.Timestamp("2026-03-10")] * 3,
            "excel_order_amount": [100.0, 100.0, 100.0],
        }
    )
    df_db = pd.DataFrame(
        {
            "sale_id": [1, 2],
            "sale_date": [pd.Timestamp("2026-03-10"), pd.Timestamp("2026-03-10")],
            "NT_amount": [100.0, 110.0],
            "adjustment_comments": ["a", "b"],
            "Additional_Comments": ["", ""],
            "external_ref_id": ["", ""],
            "db_order_code_norm": ["a", "b"],
        }
    )

    r = reconcile_foodpanda_orders(df_excel, df_db, tolerance_pkr=1.0)
    statuses = dict(zip(r.full["excel_order_code_norm"], r.full["match_status"]))
    assert statuses["a"] == "matched_ok"
    assert statuses["b"] == "matched_price_mismatch"
    assert statuses["c"] == "unmatched"

