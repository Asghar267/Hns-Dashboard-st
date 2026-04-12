"""
Configuration Module
Constants and configuration settings
"""
import os

# ========================
# BRANCH CONFIGURATION
# Branch configuration
# ========================
SELECTED_BRANCH_IDS = [2, 3, 4, 6, 8, 10, 14, 15]

BRANCH_NAMES = {
    2: "Khadda Main Branch",
    3: "FESTIVAL",
    4: "Rahat Commercial",
    6: "TOWER",
    8: "North Nazimabad",
    10: "MALIR",
    14: "FESTIVAL 2",
    15: "Tipu Sultan",
}

# Branches to hide/remove from UI selection (matched against DB `tblDefShops.shop_name`).
# Kept case-insensitive and whitespace-normalized in the filtering logic.
EXCLUDED_BRANCH_NAMES = {
    "wastages",
    "franchise",
    "highway",
    "saba avenue",
    "dry store",
    "cold store",
}

# ========================
# RAMZAN DEALS CONFIGURATION
# ========================
RAMZAN_DEALS_PRODUCT_IDS = [701, 703, 704, 705, 706, 707, 708, 709]

# Persistent category include/exclude filters (used by dashboard queries)
DEFAULT_EXCLUDED_CATEGORY_IDS = []
CATEGORY_FILTERS_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "config", "category_filters.json")
)

# ========================
# BLOCKED CUSTOMERS & COMMENTS
# ========================
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

# ========================
# ORDER TYPES
# ========================
ORDER_TYPES = {
    'Food Panda': 'Food Panda',
    'Takeaway': 'Takeaway',
    'Web Online Paid Order': 'Web Online Paid Order',
    'Dine IN': 'Dine IN',
    'Credit Card South': 'Credit Card South',
    'HNS Credit Card': 'HNS Credit Card',
    'Delivery': 'Delivery',
    'Cash Web Online Order': 'Cash Web Online Order',
    'Others': None
}

# ========================
# FRESH PICK PRODUCTS
# ========================
# Fresh Pick removed from this deployment
FRESH_PICK_PRODUCTS = []    

# ========================
# PRODUCT CATEGORIES
# ========================
SALE_CATEGORIES = [
    "SALES - BAR B Q",
    "SALES - CHINESE",
    "SALES - FAST FOOD",
    "SALES - HANDI",
    "SALES - JUICES SHAKES & DESSERTS",
    "SALES - KARAHI",
    "SALES - TANDOOR",
    "SALES - ROLL",
    "SALES - NASHTA",
    "Deal",
    "Breakfast",
    "SALES - BEVERAGES"
]

QTY_CATEGORIES = [
    "SALES - SIDE ORDER",
    "SALES - BEVERAGES"
]

# Products to hide from chef reports
HIDDEN_PRODUCTS = [
    'Sales - Employee Food',
    'Deals',
    'Modifiers'
]

# ========================
# DEFAULT TARGETS
# ========================
DEFAULT_BRANCH_TARGETS = {
    8: 18600000,   # North Nazimabad
    10: 13175000   # Jinnah Avenue (Malir)
}

# ========================
# UI CONFIGURATION
# ========================
COLORS = {
    'primary': '#1f77b4',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# Achievement thresholds
ACHIEVEMENT_THRESHOLDS = {
    'excellent': 100,
    'good': 70,
    'warning': 50,
    'poor': 0
}

# ========================
# CACHE SETTINGS
# ========================
CACHE_TTL_SECONDS = 300  # 5 minutes
CACHE_TTL_TARGETS = 600  # 10 minutes for targets

# ========================
# EXPORT SETTINGS
# ========================
EXPORT_FORMATS = ['Excel']

# ========================
# DATE FORMATS
# ========================
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DISPLAY_DATE_FORMAT = "%B %d, %Y"

# ========================
# QUERY LIMITS
# ========================
MAX_DATE_RANGE_DAYS = 365
DEFAULT_TOP_N = 10

# ========================
# SESSION SETTINGS
# ========================
SESSION_TIMEOUT_MINUTES = 60
AUTO_REFRESH_INTERVAL_SECONDS = 600

# ========================
# COMMISSION RATES
# ========================
DEFAULT_QR_COMMISSION_RATE = 2.0  # 2%

# ========================
# CHART SETTINGS
# ========================
CHART_HEIGHT_DEFAULT = 400
CHART_HEIGHT_LARGE = 600
CHART_HEIGHT_SMALL = 300

# ========================
# TABLE SETTINGS
# ========================
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 500

# ========================
# PERFORMANCE MONITORING
# ========================
SLOW_QUERY_THRESHOLD_SECONDS = 3.0
LOG_QUERY_TIMES = True

# ========================
# APP CONFIGURATION
# ========================
class AppConfig:
    """Application configuration class"""
    
    class DASHBOARD:
        title = "HNS Dashboard"
        page_icon = "📊"
        layout = "wide"
        initial_sidebar_state = "expanded"
    
    @staticmethod
    def get_branch_options():
        """Get branch selection options"""
        return [
            {"label": "Khadda Main Branch", "value": 2},
            {"label": "FESTIVAL", "value": 3},
            {"label": "Rahat Commercial", "value": 4},
            {"label": "TOWER", "value": 6},
            {"label": "North Nazimabad", "value": 8},
            {"label": "MALIR", "value": 10},
            {"label": "FESTIVAL 2", "value": 14},
            {"label": "Tipu Sultan", "value": 15},
        ]
    
    DEFAULT_BRANCHES = [2, 3, 4, 6, 8, 10, 14, 15]
