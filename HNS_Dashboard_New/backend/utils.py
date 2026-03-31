from typing import List, Tuple

BLOCKED_NAMES = [
    "Wali Jaan Personal Orders",
    "Raza Khan M.D",
    "Customer Discount 100%",
    "Daraksha Mobile 100%",
    "DHA Police Discount 100%",
    "HNS Product Marketing 100%",
    "Home Food Order (Madam)",
    "Home Food Orders",
    "Home Food Orders (Raza Khan)",
    "Home Food Orders (Shehryar Khan)",
    "Home Food Orders (Umair Sb)",
    "Rangers mobile 100%",
    "Return N Cancellation (Aftert Preperation)",
    "Return N Cancellation (without preperation)"
]

BLOCKED_COMMENTS = [
    "Wali Jaan Personal Orders",
    "100% Wali bhai",
    "Return N Cancellation (Aftert Preperation)",
    "Return N Cancellation (without preperation)",
    "100% Discount Wali Bhai Personal Order",
    "Customer Order Change Then Return",
    "marketing order in day",
    "HNS Product Marketing 100%",
    "Mistake"
]

def placeholders(n: int) -> str:
    """Generate SQL placeholders"""
    return ", ".join(["?"] * n) if n > 0 else ""

def build_filter_clause(data_mode: str) -> Tuple[str, List]:
    """Build WHERE clause for filtering blocked items."""
    clause = ""
    params = []
    
    if data_mode == "Filtered":
        if BLOCKED_NAMES:
            clause += f" AND s.Cust_name NOT IN ({placeholders(len(BLOCKED_NAMES))})"
            params.extend(BLOCKED_NAMES)
        if BLOCKED_COMMENTS:
            clause += f" AND (s.Additional_Comments NOT IN ({placeholders(len(BLOCKED_COMMENTS))}) OR s.Additional_Comments IS NULL)"
            params.extend(BLOCKED_COMMENTS)
    
    return clause, params
