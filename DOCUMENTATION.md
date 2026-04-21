# HNS Sales Dashboard - Complete Documentation

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture & Design](#2-architecture--design)
3. [Installation & Setup](#3-installation--setup)
4. [Project Structure](#4-project-structure)
5. [Module Documentation](#5-module-documentation)
6. [Database Schema Reference](#6-database-schema-reference)
7. [Dashboard Tabs Guide](#7-dashboard-tabs-guide)
8. [API Reference](#8-api-reference)
9. [Configuration Guide](#9-configuration-guide)
10. [Deployment Guide](#10-deployment-guide)
11. [Troubleshooting](#11-troubleshooting)
12. [Security Considerations](#12-security-considerations)
13. [Performance Optimization](#13-performance-optimization)
14. [Version History](#14-version-history)
15. [Timezone Handling](#15-timezone-handling)

---

## 1. Project Overview

### 1.1 Purpose

The HNS Sales Dashboard is a comprehensive, production-ready sales analytics platform designed for HNS (Habib Nawaz Saeed) restaurant chain. It provides real-time insights into sales performance, target tracking, employee productivity, and business analytics across multiple branches.

### 1.2 Business Context

HNS is a multi-branch restaurant operation requiring:
- **Real-time sales monitoring** across 7 branches
- **Target vs achievement tracking** for branches, chefs, and order takers
- **QR/Online order commission calculations** (Blinkco integration)
- **Special campaign tracking** (Ramzan Deals)
- **Performance analytics** with forecasting capabilities

### 1.3 Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Branch Support** | 7 branches with individual and consolidated views |
| **Authentication System** | Secure login with session management |
| **Connection Pooling** | Optimized database connections with retry logic |
| **Query Caching** | 5-minute TTL caching for performance |
| **Dark Mode** | User preference support |
| **Export Options** | CSV, Excel, PDF exports |
| **Real-time Monitoring** | Health checks and performance metrics |
| **Cloud Compatible** | Streamlit Cloud deployment ready |

### 1.4 Branch Configuration

| Branch ID | Branch Name |
|-----------|-------------|
| 2 | Khadda Main Branch |
| 3 | FESTIVAL |
| 4 | Rahat Commercial |
| 6 | TOWER |
| 8 | North Nazimabad |
| 10 | MALIR |
| 14 | FESTIVAL 2 |

---

## 2. Architecture & Design

### 2.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HNS SALES DASHBOARD                          │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    PRESENTATION LAYER                        │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │   │
│  │  │ Overview │ │  OT Tab  │ │ Chef Tab │ │ QR Tab   │ ...   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    BUSINESS LOGIC LAYER                      │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │   │
│  │  │   Auth       │ │   Utils      │ │Visualization │        │   │
│  │  │  Module      │ │   Module     │ │   Module     │        │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    DATA ACCESS LAYER                         │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │   │
│  │  │  Database    │ │  Connection  │ │   SQL        │        │   │
│  │  │  Module      │ │   Cloud      │ │  Helpers     │        │   │
│  │  │  (Cached)    │ │  (Pool)      │ │              │        │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    DATA SOURCES                              │   │
│  │  ┌──────────────────┐    ┌──────────────────┐              │   │
│  │  │   Candelahns DB  │    │     KDS_DB       │              │   │
│  │  │   (Sales Data)   │    │   (Targets)      │              │   │
│  │  │   SQL Server     │    │   SQL Server     │              │   │
│  │  └──────────────────┘    └──────────────────┘              │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
User Request → Authentication → Session Validation → 
Cache Check → Database Query → Data Processing → 
Visualization → Response Rendering
```

### 2.3 Component Relationships

```
hns_dashboard.py
    ├── modules/auth.py (Authentication)
    ├── modules/config.py (Configuration Constants)
    ├── modules/database.py (Cached Queries)
    │       └── modules/connection_cloud.py (Connection Pool)
    ├── modules/visualization.py (Charts)
    ├── modules/utils.py (Helpers)
    └── config/credentials.json (User Data, local-only)
```

### 2.4 Caching Strategy

| Cache Type | TTL | Purpose |
|------------|-----|---------|
| `st.cache_data` | 300s (5 min) | Query results |
| `st.cache_data` | 600s (10 min) | Target data |
| `st.cache_resource` | Session | Connection pool |

---

## 3. Installation & Setup

### 3.1 Prerequisites

- **Python 3.8+** (3.10+ recommended)
- **SQL Server ODBC Driver 17** or SQL Server Native Client
- **Network access** to SQL Server instances
- **8GB+ RAM** recommended for local development

### 3.2 Dependencies

Create `requirements.txt`:

```txt
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.18.0
pyodbc>=5.0.0
numpy>=1.24.0
openpyxl>=3.1.0
prophet>=1.1.0  # Optional, for forecasting
requests>=2.31.0  # For API proxy mode
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3.3 ODBC Driver Installation

**Windows:**
```bash
# Download and install from Microsoft:
# https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

**Linux:**
```bash
# Ubuntu/Debian
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev
```

### 3.4 Configuration Setup

1. **Create config directory:**
```bash
mkdir -p HNS_Deshboard/config
```

2. **Bootstrap credentials** (`config/credentials.json`, local-only):
   - Set `HNS_DEFAULT_ADMIN_PASSWORD` in the environment
   - Start the app; it will create `config/credentials.json` automatically on first run
   - Use `config/credentials.example.json` as a safe reference for the expected shape

3. **Generate password hash:**
```python
import hashlib
password = "your_password"
hash_value = hashlib.sha256(password.encode()).hexdigest()
print(hash_value)
```

### 3.5 Running the Dashboard

```bash
cd HNS_Deshboard
streamlit run hns_dashboard.py
```

**Command line options:**
```bash
# Specific port
streamlit run hns_dashboard.py --server.port 8502

# External access
streamlit run hns_dashboard.py --server.address 0.0.0.0

# Disable file watcher (production)
streamlit run hns_dashboard.py --server.fileWatcherType none
```

---

## 4. Project Structure

```
HNS_Deshboard/
│
├── hns_dashboard.py          # Main dashboard application (1100+ lines)
├── connection_cloud.py       # Cloud-compatible DB connections
├── sqldatabase.py           # Lightweight SQL query helpers
├── ramzan_deals.py          # Standalone Ramzan deals module
├── README.md                # Basic project info
├── DOCUMENTATION.md         # This file
│
├── config/
│   ├── credentials.json     # User credentials (auto-generated)
│   └── category_filters.json # Saved filter settings
│
├── modules/
│   ├── __init__.py         # Package marker
│   ├── auth.py             # Authentication & session management
│   ├── config.py           # Configuration constants
│   ├── connection_cloud.py  # Connection pooling & cloud support
│   ├── database.py         # Cached database queries (25+ functions)
│   ├── sqldatabase.py      # SQL utilities for ad-hoc queries
│   ├── utils.py            # Formatting, calculations, exports
│   └── visualization.py    # Chart creation (10+ chart types)
│
└── __pycache__/            # Python bytecode cache
```

### 4.1 File Sizes & Responsibilities

| File | Lines | Purpose |
|------|-------|---------|
| `hns_dashboard.py` | ~1100 | Main UI, 11 dashboard tabs |
| `database.py` | ~700 | All cached query functions |
| `visualization.py` | ~500 | Chart creation utilities |
| `connection_cloud.py` | ~400 | Connection management |
| `config.py` | ~150 | Constants & settings |
| `utils.py` | ~250 | Helper functions |
| `auth.py` | ~100 | Authentication logic |

---

## 5. Module Documentation

### 5.1 Main Dashboard (`hns_dashboard.py`)

The main application file containing all dashboard UI and business logic.

#### Session State Variables

```python
st.session_state = {
    'dark_mode': bool,           # Dark mode toggle
    'auto_refresh': bool,        # Auto-refresh enabled
    'last_refresh': datetime,    # Last data refresh time
    'authenticated': bool,       # User authentication status
    'username': str,             # Current username
    'user': dict,                # User record from credentials
    'last_activity': datetime,   # Last activity timestamp
    'using_default_targets': bool # Whether using default targets
}
```

#### Key Functions

| Function | Description |
|----------|-------------|
| `load_custom_css()` | Loads dark/light mode CSS styles |
| `render_table()` | Consistent dataframe rendering |
| `exclude_employee_names()` | Filters out non-attributed employees |
| `month_name()` | Returns formatted month string |

### 5.2 Authentication Module (`modules/auth.py`)

Handles user authentication and session management.

#### Functions

```python
def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_credentials():
    """Initialize credentials file with default admin user"""
    # Creates config/credentials.json using HNS_DEFAULT_ADMIN_PASSWORD (from environment)

def verify_credentials(username: str, password: str) -> bool:
    """Verify username and password against stored hash"""

def get_user_record(username: str) -> dict:
    """Fetch complete user record including allowed_branches"""

def check_session_timeout() -> bool:
    """Check if session has exceeded timeout (7 days)"""

def authenticate_user():
    """Display login form and handle authentication"""

def logout_user():
    """Clear session state and log out user"""

def update_activity():
    """Update last activity timestamp"""
```

#### User Record Structure

```json
{
  "username": "admin",
  "password_hash": "sha256_hash_value",
  "role": "admin",
  "allowed_branches": "all",  // or [2, 3, 4, ...]
  "created_at": "2024-01-01T00:00:00"
}
```

### 5.3 Configuration Module (`modules/config.py`)

Central configuration constants for the entire application.

#### Branch Configuration

```python
SELECTED_BRANCH_IDS = [2, 3, 4, 6, 8, 10, 14]

BRANCH_NAMES = {
    2: "Khadda Main Branch",
    3: "FESTIVAL",
    4: "Rahat Commercial",
    6: "TOWER",
    8: "North Nazimabad",
    10: "MALIR",
    14: "FESTIVAL 2"
}
```

#### Category Configuration

```python
# Sale-based targets
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
    "Breakfast"
]

# Quantity-based targets
QTY_CATEGORIES = [
    "SALES - BEVERAGES",
    "SALES - SIDE ORDER"
]
```

#### Blocked Items Configuration

```python
BLOCKED_NAMES = [
    "Wali Jaan Personal Orders",
    "Raza Khan M.D",
    "Customer Discount 100%",
    # ... more blocked customer names
]

BLOCKED_COMMENTS = [
    "Wali Jaan Personal Orders",
    "100% Wali bhai",
    "Return N Cancellation (Aftert Preperation)",
    # ... more blocked comments
]
```

#### Performance Settings

```python
CACHE_TTL_SECONDS = 300          # 5 minutes
CACHE_TTL_TARGETS = 600          # 10 minutes
SLOW_QUERY_THRESHOLD_SECONDS = 3.0
SESSION_TIMEOUT_MINUTES = 60
AUTO_REFRESH_INTERVAL_SECONDS = 600
```

### 5.4 Database Module (`modules/database.py`)

Core data access layer with cached query functions.

#### Helper Functions

```python
def placeholders(n: int) -> str:
    """Generate SQL placeholders (?, ?, ...)"""

def build_filter_clause(data_mode: str) -> Tuple[str, List]:
    """Build WHERE clause for filtering blocked items"""

def build_category_name_filter_clause(category_alias: str = "t") -> Tuple[str, List]:
    """Build category include/exclude clause"""

def is_category_counted(category_name: str, included_names: List, excluded_names: List) -> bool:
    """Evaluate if category is counted based on rules"""

def get_saved_category_filters() -> Dict:
    """Load saved include/exclude filters from disk"""

def save_category_filters(settings: Dict) -> None:
    """Persist category filters to disk"""

def refresh_all_caches():
    """Clear all cached data"""
```

#### Cached Query Functions

| Function | TTL | Description |
|----------|-----|-------------|
| `get_cached_branch_summary()` | 300s | Branch-level sales summary |
| `get_cached_ot_data()` | 300s | Order taker performance data |
| `get_cached_line_items()` | 300s | Product/line item sales |
| `get_cached_order_types()` | 300s | Order type breakdown |
| `get_cached_qr_sales()` | 300s | QR/Blinkco sales data |
| `get_cached_employee_sales()` | 300s | Employee-wise sales breakdown |
| `get_cached_targets()` | 600s | All targets (branch, chef, OT) |
| `get_cached_monthly_sales()` | 600s | Monthly aggregated sales |
| `get_cached_daily_sales()` | 300s | Daily aggregated sales |
| `get_cached_daily_sales_by_branch()` | 300s | Daily sales by branch |
| `get_cached_daily_sales_by_products()` | 300s | Daily sales by product |
| `get_cached_product_monthly_sales()` | 300s | Product sales by month |
| `get_cached_product_monthly_sales_by_product()` | 300s | Product-level monthly sales |
| `get_cached_category_monthly_history()` | 300s | Category monthly history |
| `get_cached_top_products()` | 300s | Top/bottom products |
| `get_cached_category_filter_coverage()` | 300s | Category coverage analysis |
| `get_cached_ramzan_product_master()` | 300s | Ramzan product catalog |
| `get_cached_ramzan_deals_sales()` | 300s | Ramzan deals sales data |

#### Query Function Signatures

```python
@st.cache_data(ttl=300)
def get_cached_branch_summary(
    start_date: str,      # Format: "YYYY-MM-DD"
    end_date: str,        # Format: "YYYY-MM-DD"
    branch_ids: List[int],
    data_mode: str        # "Filtered" or "Unfiltered"
) -> pd.DataFrame:
    """Returns: shop_id, shop_name, total_sales, total_Nt_amount"""

@st.cache_data(ttl=600)
def get_cached_targets(
    year: int,
    month: int
) -> Tuple[Dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Returns: (branch_targets, chef_targets, ot_targets, fresh_targets)"""
```

### 5.5 Connection Module (`modules/connection_cloud.py`)

Manages database connections with pooling and cloud compatibility.

#### Environment Detection

```python
def is_streamlit_cloud() -> bool:
    """Check if running on Streamlit Cloud"""
    return os.environ.get('STREAMLIT_CLOUD') == 'true'

def is_local_development() -> bool:
    """Check if running in local development"""
    return not is_streamlit_cloud()
```

#### Configuration Classes

```python
class CloudConfig:
    """Configuration for cloud deployment"""
    API_PROXY_URL = os.environ.get('DB_API_PROXY', '')
    USE_DIRECT_CONNECTION = not API_PROXY_URL

class DatabaseConfig:
    """Database connection settings"""
    CONNECTION_TIMEOUT = 30
    QUERY_TIMEOUT = 60
    POOL_TIMEOUT = 10
    POOL_SIZE = 10
    MAX_OVERFLOW = 20
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    SLOW_QUERY_THRESHOLD = 5.0
```

#### Connection Pool

```python
class EnhancedConnectionPool:
    """Thread-safe connection pool with health monitoring"""
    
    def get_connection(self, db_type: str) -> pyodbc.Connection:
        """Get connection from pool"""
        
    def return_connection(self, db_type: str, conn: pyodbc.Connection):
        """Return connection to pool"""
        
    def get_stats(self) -> Dict:
        """Get pool statistics"""

# Global pool instance
enhanced_pool = EnhancedConnectionPool()
pool = enhanced_pool  # Alias for backward compatibility
```

#### Main Connection Functions

```python
@st.cache_resource
def get_connection_kdsdb() -> DatabaseConnection:
    """Get KDS_DB connection (cloud-compatible)"""

@st.cache_resource
def get_connection_candelahns() -> DatabaseConnection:
    """Get Candelahns DB connection (cloud-compatible)"""

def get_connection_candelahns_direct() -> pyodbc.Connection:
    """Get direct Candelahns connection (legacy)"""
```

#### Health Monitoring

```python
def health_check() -> Dict:
    """Perform health check on all connections"""
    return {
        'status': 'healthy' | 'unhealthy',
        'connections': {...},
        'pool_stats': {...}
    }

def get_performance_metrics() -> Dict:
    """Get performance metrics"""
    return {
        'pool_stats': {...},
        'candelahns_stats': {...},
        'kdsdb_stats': {...}
    }
```

### 5.6 Visualization Module (`modules/visualization.py`)

Chart creation utilities using Plotly.

#### Chart Functions

```python
def create_achievement_gauge(achievement: float, title: str) -> go.Figure:
    """Create gauge chart for achievement percentage
    
    Color coding:
    - achievement >= 100: Green
    - achievement >= 70: Yellow  
    - achievement < 70: Red
    """

def create_waterfall_chart(df_branch: pd.DataFrame) -> go.Figure:
    """Create waterfall chart for target breakdown"""

def create_heatmap(df_branch: pd.DataFrame) -> go.Figure:
    """Create heatmap for branch performance metrics"""

def create_sankey_diagram(df_order_types: pd.DataFrame) -> go.Figure:
    """Create Sankey diagram for order flow"""

def create_trend_chart(df_trend: pd.DataFrame, days: int) -> go.Figure:
    """Create trend analysis chart with moving average"""

def create_forecast_chart(df_sales: pd.DataFrame) -> go.Figure:
    """Create sales forecast with confidence intervals"""

def create_comparison_chart(df1: pd.DataFrame, df2: pd.DataFrame, 
                           labels: List[str]) -> go.Figure:
    """Create comparison chart between two periods"""

def create_monthly_sales_trend(df_monthly: pd.DataFrame, 
                               periods: int = 24, 
                               rolling: int = 3) -> go.Figure:
    """Create monthly sales trend with optional rolling average"""

def create_forecast_with_ci(df_history: pd.DataFrame, 
                            periods_ahead: int = 7, 
                            method: str = 'simple') -> go.Figure:
    """Create forecast with confidence interval
    
    Methods: 'simple' (linear) or 'prophet' (if installed)
    """

def create_product_time_series(df_product: pd.DataFrame, 
                               product_name: str, 
                               agg: str = 'daily', 
                               show_qty: bool = True, 
                               rolling: int = 7) -> go.Figure:
    """Create product-level time series with dual axis"""

def create_top_categories_small_multiples(df_cat_monthly: pd.DataFrame, 
                                          top_n: int = 8) -> go.Figure:
    """Create small multiples for top categories"""
```

### 5.7 Utils Module (`modules/utils.py`)

Helper functions for formatting, calculations, and exports.

#### Formatting Functions

```python
def format_currency(value: Union[int, float]) -> str:
    """Format number as PKR currency: PKR 1,234,567"""

def format_percentage(value: Union[int, float]) -> str:
    """Format number as percentage: 85.5%"""

def format_number(value: Union[int, float]) -> str:
    """Format number with thousand separators: 1,234,567"""
```

#### Calculation Functions

```python
def calculate_achievement(current: float, target: float) -> float:
    """Calculate achievement percentage"""

def calculate_growth(current: float, previous: float) -> float:
    """Calculate growth percentage"""

def calculate_variance(actual: float, budgeted: float) -> float:
    """Calculate variance (actual - budgeted)"""
```

#### Date Functions

```python
def get_date_presets(preset: str) -> Tuple[date, date]:
    """Get date range based on preset
    
    Presets: "Today", "Yesterday", "This Week", "Last Week",
             "This Month", "Last Month", "This Quarter", "This Year", "Custom"
    """
```

#### Export Functions

```python
def export_to_excel(df: pd.DataFrame, sheet_name: str) -> bytes:
    """Export DataFrame to Excel with formatting"""

def export_to_pdf(df: pd.DataFrame, title: str) -> bytes:
    """Export DataFrame to PDF (HTML-based)"""
```

#### Data Processing Functions

```python
def validate_date_range(start_date: date, end_date: date) -> bool:
    """Validate date range"""

def validate_dataframe(df: pd.DataFrame, required_columns: list) -> bool:
    """Validate DataFrame has required columns"""

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean DataFrame - remove nulls, duplicates"""

def aggregate_data(df: pd.DataFrame, group_by: list, agg_dict: dict) -> pd.DataFrame:
    """Aggregate DataFrame by specified columns"""

def generate_summary_stats(df: pd.DataFrame, value_column: str) -> dict:
    """Generate summary statistics for a column"""

def get_top_performers(df: pd.DataFrame, name_col: str, 
                       value_col: str, top_n: int = 10) -> pd.DataFrame:
    """Get top N performers"""

def get_bottom_performers(df: pd.DataFrame, name_col: str, 
                          value_col: str, bottom_n: int = 10) -> pd.DataFrame:
    """Get bottom N performers"""
```

---

## 6. Database Schema Reference

### 6.1 Candelahns Database (Primary)

Main sales database containing transactional data.

#### Core Tables

| Table | Description |
|-------|-------------|
| `tblSales` | Main sales transactions |
| `tblSalesLineItems` | Individual line items per sale |
| `tblDefShops` | Branch/location definitions |
| `tblDefShopEmployees` | Employee definitions |
| `tblDefProducts` | Product catalog |
| `tblProductItem` | Product item mappings |
| `TempProductBarcode` | Product barcode mappings |
| `tblInitialRawBlinkOrder` | Raw Blinkco order data |

#### tblSales Structure

| Column | Type | Description |
|--------|------|-------------|
| `sale_id` | int | Primary key |
| `sale_date` | datetime | Transaction timestamp |
| `shop_id` | int | Branch ID (FK to tblDefShops) |
| `employee_id` | int | Order taker ID (FK) |
| `Nt_amount` | decimal | Net amount |
| `Cust_name` | varchar | Customer name/type |
| `Additional_Comments` | varchar | Order notes |
| `external_ref_type` | varchar | External reference type |
| `external_ref_id` | varchar | External reference ID |

#### tblSalesLineItems Structure

| Column | Type | Description |
|--------|------|-------------|
| `sale_id` | int | FK to tblSales |
| `Product_Item_ID` | int | Product item ID |
| `Product_code` | varchar | Product code |
| `qty` | decimal | Quantity |
| `Unit_price` | decimal | Unit price |

### 6.2 KDS_DB Database (Targets)

Database containing target definitions.

#### Target Tables

| Table | Description |
|-------|-------------|
| `branch_targets` | Monthly branch targets |
| `branch_chef_targets` | Chef/category targets |
| `ot_targets` | Order taker targets |
| `chef_sale` | Category definitions |

#### branch_targets Structure

| Column | Type | Description |
|--------|------|-------------|
| `shop_id` | int | Branch ID |
| `target_year` | int | Target year |
| `target_month` | int | Target month (1-12) |
| `monthly_target` | decimal | Target amount |

#### branch_chef_targets Structure

| Column | Type | Description |
|--------|------|-------------|
| `shop_id` | int | Branch ID |
| `category_id` | int | Category ID (FK to chef_sale) |
| `target_year` | int | Target year |
| `target_month` | int | Target month |
| `monthly_target` | decimal | Target value |
| `target_type` | varchar | 'Sale' or 'Quantity' |

---

## 7. Dashboard Tabs Guide

### 7.1 Tab 1: Overview

**Purpose:** High-level branch performance summary with KPIs.

**Components:**
- Total sales, target, remaining, achievement KPI cards
- Top 5 highlights (Chef products, Line items, OT sales)
- Achievement gauge chart
- Branch performance heatmap
- Individual branch expandable cards
- Waterfall chart for target breakdown
- Daily sales by branch table (last 30 days)
- Order type distribution with Sankey diagram
- Export options (CSV, Excel, PDF)

**Key Metrics:**
```
Total Sales = Sum of all branch sales
Total Target = Sum of branch monthly targets
Remaining = Total Target - Total Sales
Achievement % = (Total Sales / Total Target) × 100
```

### 7.2 Tab 2: Order Takers

**Purpose:** Order taker performance analysis.

**Components:**
- Summary metrics (total OT sales, active OTs, average per OT)
- Top 10 performers bar chart
- Searchable OT table
- Export to CSV

**Data Exclusions:**
- "online/unassigned" employees filtered from analytics

### 7.3 Tab 3: Chef Sales

**Purpose:** Product-level sales analysis.

**Components:**
- Top 15 products by revenue bar chart
- Product category pie chart
- All products table
- Branch-wise product breakdown
- Reconciliation check (Chef vs Overview totals)
- Daily product targets (25% vs previous day)

**Target Calculation:**
```
Today Target = Yesterday_Qty × 1.25
Next Day Target = Yesterday_Qty × 1.25
Remaining = Today Target - Current Sale
Achievement % = (Current Sale / Today Target) × 100
```

### 7.4 Tab 4: Chef Targets

**Purpose:** Chef/category target vs achievement analysis.

**Components:**
- Branch selection dropdown
- Target period display
- Product targets table with bonus calculation
- Target vs Achievement bar chart

**Bonus Calculation:**
```
Bonus = Current_Sale × 0.5 if Achievement >= 100%, else 0
```

### 7.5 Tab 5: OT Targets

**Purpose:** Order taker target tracking.

**Components:**
- Branch selection
- Filter options (hide zero sales/target)
- Per-day target calculations
- Yesterday achieved, MTD sale
- Remaining days, next day target
- Top 10 OT performance chart

**Daily Target Math:**
```
Per-Day Target = Monthly Target / Days in Month
Today Target = Per-Day Target
Remaining Target = Monthly Target - MTD Sale
Next Day Target = Remaining Target / Remaining Days
```

### 7.6 Tab 6: QR Commission

**Purpose:** Blinkco/QR order commission analysis.

**Components:**
- Commission rate input (default 2%)
- Summary metrics (total QR sales, commissions, transactions)
- Detailed transaction table with match status
- Employee-wise totals with shop
- Branch-wise totals
- Multiple export options

**Commission Calculation:**
```
Candelahns_commission = total_sale × (commission_rate / 100)
Indoge_commission = Indoge_total_price × (commission_rate / 100)
Match % = (1 - |difference| / Indoge_total) × 100
```

### 7.7 Tab 7: Trends & Analytics

**Purpose:** Time-series analysis and forecasting.

**Components:**
- Performance summary bar chart
- Monthly trend with forecast
- Forecast method selector (simple/Prophet)
- Forecast horizon slider (1-30 days)
- Line item name analysis
- Top products by product name
- Top/Bottom 10 product trend charts
- Product explorer with detailed series
- Low-performing products analysis
- Comparison table (current vs previous month)

**Branch Filter:** Radio button for All/individual branches

### 7.8 Tab 8: Ramzan Deals

**Purpose:** Special campaign tracking for Ramzan products.

**Components:**
- Date range selection
- Branch multiselect
- Product multiselect (Product codes: 701, 703-709)
- Summary metrics
- Branch-wise sales table
- Product-wise overall sales
- Export options

**Product IDs:**
```python
RAMZAN_DEALS_PRODUCT_IDS = [701, 703, 704, 705, 706, 707, 708, 709]
```

### 7.9 Tab 9: Category Filters

**Purpose:** Configure include/exclude category rules.

**Components:**
- Included category IDs multiselect
- Excluded category IDs multiselect
- Save/Reset buttons
- Current configuration display

**Persistence:** Settings saved to `config/category_filters.json`

### 7.10 Tab 10: Category Coverage

**Purpose:** Analyze impact of category filters on sales calculations.

**Components:**
- Included/Excluded rules display
- Summary metrics (included/excluded categories, excluded sales impact)
- Included categories table
- Excluded categories table

**Status Types:**
- "Included" - Counted in totals
- "Excluded (explicit)" - In exclude list
- "Excluded (not in include list)" - Not in include list when include is active

### 7.11 Tab 11: Pivot Tables

**Purpose:** Interactive pivot analysis.

**Pivot Types:**
- Branch x Category
- Branch x Day
- Month x Branch

**Metrics:**
- Sales (total_Nt_amount)
- Quantity (total_qty)

**Features:**
- Grand totals row/column
- Download pivot as CSV

### 7.12 Tab 12: Shifts

**Purpose:** Shift-wise sales analysis (Morning, Lunch, Dinner).

**Components:**
- Summary metric cards for total Morning, Lunch, and Dinner sales.
- Shift distribution by branch bar chart.
- Sales intensity heatmap (Shift vs Branch).
- Detailed shift performance table with branch share percentages.

**Shift Definitions (PKT):**
- **Morning**: 06:00 AM – 12:00 PM
- **Lunch**: 12:00 PM – 05:00 PM
- **Dinner**: 05:00 PM – 06:00 AM (Next Day)

**Timezone Adjustment:**
Database timestamps are adjusted by +6 hours to convert from Greenland Standard Time (UTC-1) to Pakistani Time (UTC+5).

---

## 8. API Reference

### 8.1 Authentication Functions

```python
# modules/auth.py

def hash_password(password: str) -> str:
    """Hash password using SHA-256.
    
    Args:
        password: Plain text password
        
    Returns:
        SHA-256 hash string
    """

def verify_credentials(username: str, password: str) -> bool:
    """Verify username and password.
    
    Args:
        username: User's username
        password: Plain text password
        
    Returns:
        True if credentials valid, False otherwise
    """

def get_user_record(username: str) -> dict:
    """Get user record by username.
    
    Args:
        username: User's username
        
    Returns:
        User record dict or empty dict if not found
    """

def authenticate_user() -> None:
    """Display login form and handle authentication.
    Sets session state on success.
    """

def logout_user() -> None:
    """Clear session and log out user."""

def check_session_timeout() -> bool:
    """Check if session has timed out.
    
    Returns:
        True if session expired (7 days), False otherwise
    """
```

### 8.2 Database Functions

```python
# modules/database.py

def get_cached_branch_summary(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str
) -> pd.DataFrame:
    """Fetch branch summary with caching.
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        branch_ids: List of branch IDs
        data_mode: "Filtered" or "Unfiltered"
        
    Returns:
        DataFrame with columns: shop_id, shop_name, total_sales, total_Nt_amount
    """

def get_cached_ot_data(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str
) -> pd.DataFrame:
    """Fetch order taker data.
    
    Returns:
        DataFrame with columns: shop_id, shop_name, employee_id, 
        employee_name, total_sale
    """

def get_cached_line_items(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str
) -> pd.DataFrame:
    """Fetch line item sales data.
    
    Returns:
        DataFrame with columns: shop_id, shop_name, product, 
        total_qty, total_line_value_incl_tax
    """

def get_cached_targets(
    year: int,
    month: int
) -> Tuple[Dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Fetch all targets.
    
    Args:
        year: Target year
        month: Target month (1-12)
        
    Returns:
        Tuple of (branch_targets_dict, chef_targets_df, 
                  ot_targets_df, fresh_targets_df)
    """

def get_cached_qr_sales(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str
) -> pd.DataFrame:
    """Fetch QR/Blinkco sales.
    
    Returns:
        DataFrame with Blinkco order data
    """

def get_cached_daily_sales(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str
) -> pd.DataFrame:
    """Fetch daily aggregated sales.
    
    Returns:
        DataFrame with columns: day, total_Nt_amount
    """

def get_cached_monthly_sales(
    start_date: str,
    end_date: str,
    branch_ids: List[int],
    data_mode: str
) -> pd.DataFrame:
    """Fetch monthly aggregated sales.
    
    Returns:
        DataFrame with columns: period_date, year, month, total_Nt_amount
    """

def refresh_all_caches() -> None:
    """Clear all Streamlit data caches."""
```

### 8.3 Connection Functions

```python
# modules/connection_cloud.py

def get_connection_candelahns() -> DatabaseConnection:
    """Get Candelahns DB connection from pool.
    
    Returns:
        DatabaseConnection wrapper instance
    """

def get_connection_kdsdb() -> DatabaseConnection:
    """Get KDS_DB connection from pool.
    
    Returns:
        DatabaseConnection wrapper instance
    """

def health_check() -> Dict:
    """Perform health check on all connections.
    
    Returns:
        {
            'status': 'healthy' | 'unhealthy',
            'connections': {...},
            'pool_stats': {...}
        }
    """

def get_performance_metrics() -> Dict:
    """Get performance metrics.
    
    Returns:
        {
            'pool_stats': {
                'pool_size': int,
                'active_connections': int,
                'total_queries': int,
                'avg_query_time': float
            },
            'candelahns_stats': {...},
            'kdsdb_stats': {...}
        }
    """
```

### 8.4 Visualization Functions

```python
# modules/visualization.py

def create_achievement_gauge(
    achievement: float,
    title: str
) -> go.Figure:
    """Create gauge chart for achievement percentage.
    
    Args:
        achievement: Achievement percentage (0-150+)
        title: Chart title
        
    Returns:
        Plotly Figure object
    """

def create_waterfall_chart(
    df_branch: pd.DataFrame
) -> go.Figure:
    """Create waterfall chart for target breakdown.
    
    Args:
        df_branch: DataFrame with shop_name, total_Nt_amount
        
    Returns:
        Plotly Figure object
    """

def create_forecast_with_ci(
    df_history: pd.DataFrame,
    periods_ahead: int = 7,
    method: str = 'simple'
) -> go.Figure:
    """Create forecast with confidence interval.
    
    Args:
        df_history: DataFrame with day/date and total_Nt_amount
        periods_ahead: Number of periods to forecast
        method: 'simple' (linear) or 'prophet'
        
    Returns:
        Plotly Figure with forecast and CI band
    """

def create_monthly_sales_trend(
    df_monthly: pd.DataFrame,
    periods: int = 24,
    rolling: int = 3
) -> go.Figure:
    """Create monthly sales trend chart.
    
    Args:
        df_monthly: DataFrame with period_date, total_Nt_amount
        periods: Number of periods to display
        rolling: Rolling average window
        
    Returns:
        Plotly Figure object
    """
```

### 8.5 Utility Functions

```python
# modules/utils.py

def format_currency(value: Union[int, float]) -> str:
    """Format number as PKR currency.
    
    Args:
        value: Numeric value
        
    Returns:
        Formatted string: "PKR 1,234,567"
    """

def format_percentage(value: Union[int, float]) -> str:
    """Format number as percentage.
    
    Returns:
        Formatted string: "85.5%"
    """

def get_date_presets(preset: str) -> Tuple[date, date]:
    """Get date range from preset.
    
    Args:
        preset: One of "Today", "Yesterday", "This Week", 
                "Last Week", "This Month", "Last Month",
                "This Quarter", "This Year", "Custom"
        
    Returns:
        Tuple of (start_date, end_date)
    """

def export_to_excel(
    df: pd.DataFrame,
    sheet_name: str
) -> bytes:
    """Export DataFrame to Excel.
    
    Returns:
        Excel file bytes
    """

def calculate_achievement(
    current: float,
    target: float
) -> float:
    """Calculate achievement percentage.
    
    Returns:
        Achievement percentage or 0 if target is 0
    """
```

---

## 9. Configuration Guide

### 9.1 Branch Configuration

Edit `modules/config.py`:

```python
SELECTED_BRANCH_IDS = [2, 3, 4, 6, 8, 10, 14]

BRANCH_NAMES = {
    2: "Khadda Main Branch",
    3: "FESTIVAL",
    # Add or modify branches as needed
}
```

### 9.2 Category Filters

#### Sale-Based Categories (Revenue Targets)
```python
SALE_CATEGORIES = [
    "SALES - BAR B Q",
    "SALES - CHINESE",
    # Add categories where targets are revenue-based
]
```

#### Quantity-Based Categories
```python
QTY_CATEGORIES = [
    "SALES - BEVERAGES",
    "SALES - SIDE ORDER"
]
```

### 9.3 Blocked Items

Add customer names or comments to exclude:

```python
BLOCKED_NAMES = [
    "Wali Jaan Personal Orders",
    "Your blocked customer name here"
]

BLOCKED_COMMENTS = [
    "100% Discount",
    "Your blocked comment here"
]
```

### 9.4 Default Targets

Set default targets when database targets unavailable:

```python
DEFAULT_BRANCH_TARGETS = {
    8: 18600000,   # North Nazimabad
    10: 13175000   # MALIR
}
```

### 9.5 Ramzan Deals Products

Configure Ramzan campaign products:

```python
RAMZAN_DEALS_PRODUCT_IDS = [701, 703, 704, 705, 706, 707, 708, 709]
```

### 9.6 Performance Settings

```python
# Cache settings
CACHE_TTL_SECONDS = 300          # Query cache: 5 minutes
CACHE_TTL_TARGETS = 600          # Target cache: 10 minutes

# Session settings
SESSION_TIMEOUT_MINUTES = 60     # Session timeout
AUTO_REFRESH_INTERVAL_SECONDS = 600  # Auto-refresh: 10 minutes

# Performance thresholds
SLOW_QUERY_THRESHOLD_SECONDS = 3.0  # Log slow queries above this
```

### 9.7 User Management

Users are stored in `config/credentials.json` (local-only; not committed):

```json
{
  "users": [
    {
      "username": "admin",
      "password_hash": "sha256_hash_value",
      "role": "admin",
      "allowed_branches": "all",
      "created_at": "2024-01-01T00:00:00"
    },
    {
      "username": "branch_user",
      "password_hash": "...",
      "role": "user",
      "allowed_branches": [8, 10],
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

**allowed_branches values:**
- `"all"` - Access to all branches
- `[2, 3, 4]` - Access to specific branches only

---

## 10. Deployment Guide

### 10.1 Local Development

```bash
# Clone/navigate to project
cd HNS_Deshboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run hns_dashboard.py
```

### 10.2 Streamlit Cloud Deployment

1. **Prepare repository:**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

2. **Create `.streamlit/config.toml`:**
```toml
[server]
port = 8501
headless = true

[theme]
base = "light"
```

3. **Set environment variables** in Streamlit Cloud:
```
STREAMLIT_CLOUD=true
DB_API_PROXY=https://your-api-proxy.com
```

4. **Deploy** via Streamlit Cloud dashboard.

### 10.3 Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install ODBC driver
RUN apt-get update && apt-get install -y \
    unixodbc-dev \
    curl \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "hns_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t hns-dashboard .
docker run -p 8501:8501 hns-dashboard
```

### 10.4 Production Considerations

1. **Disable file watcher:**
```bash
streamlit run hns_dashboard.py --server.fileWatcherType none
```

2. **Use secrets management:**
```python
# .streamlit/secrets.toml
[database]
candelahns_password = "your_password"
kdsdb_password = "your_password"
```

3. **Enable HTTPS:**
```bash
streamlit run hns_dashboard.py --server.sslCertFile cert.pem --server.sslKeyFile key.pem
```

---

## 11. Troubleshooting

### 11.1 Connection Issues

**Problem:** "Database connection failed"

**Solutions:**
1. Verify SQL Server is running and accessible
2. Check firewall rules for port 2001
3. Verify ODBC driver is installed
4. Check credentials in connection strings

```bash
# Test ODBC connection
python -c "import pyodbc; print(pyodbc.drivers())"
```

**Problem:** "Login timeout expired"

**Solutions:**
1. Increase `CONNECTION_TIMEOUT` in config
2. Check network latency
3. Verify SQL Server allows remote connections

### 11.2 Performance Issues

**Problem:** Slow dashboard loading

**Solutions:**
1. Check query execution times in Performance tab
2. Reduce date range in filters
3. Clear caches and refresh
4. Check database indexes

```python
# Add indexes (on SQL Server)
CREATE INDEX IX_tblSales_date ON tblSales(sale_date);
CREATE INDEX IX_tblSales_shop ON tblSales(shop_id);
```

**Problem:** Memory usage high

**Solutions:**
1. Reduce `POOL_SIZE` in connection config
2. Clear caches periodically
3. Limit concurrent users

### 11.3 Authentication Issues

**Problem:** "Invalid username or password"

**Solutions:**
1. Verify `HNS_DEFAULT_ADMIN_PASSWORD` is set (for first-run bootstrap) and that `config/credentials.json` exists
2. Regenerate password hash
3. Check JSON format is valid

```python
# Generate new password hash
import hashlib
print(hashlib.sha256("new_password".encode()).hexdigest())
```

**Problem:** Session timeout too frequent

**Solution:** Increase `SESSION_TIMEOUT_DAYS` in `auth.py`

### 11.4 Data Issues

**Problem:** Missing data in reports

**Solutions:**
1. Check date range filters
2. Verify branch selection
3. Check blocked customers/comments list
4. Review category filter settings

**Problem:** Incorrect calculations

**Solutions:**
1. Check filter mode (Filtered vs Unfiltered)
2. Verify category include/exclude rules
3. Review line item allocation formula

### 11.5 Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `pyodbc.Error: ('01000', ...)` | Connection issue | Check network/driver |
| `KeyError: 'shop_name'` | Missing column | Verify query structure |
| `pd.errors.EmptyDataError` | No data returned | Check filters/dates |
| `JSONDecodeError` | Invalid JSON | Validate config files |

---

## 12. Security Considerations

### 12.1 Authentication

- **Password hashing:** SHA-256 (consider bcrypt for production)
- **Session management:** 7-day timeout
- **Activity tracking:** Last activity timestamp

### 12.2 Credential Management

**DO NOT** hardcode credentials in source code. Use:

1. **Environment variables:**
```python
import os
password = os.environ.get('DB_PASSWORD')
```

2. **Streamlit secrets:**
```python
# .streamlit/secrets.toml
[database]
password = "your_password"

# In code
import streamlit as st
password = st.secrets["database"]["password"]
```

3. **Encrypted config files:**
```python
from cryptography.fernet import Fernet
# Encrypt sensitive data at rest
```

### 12.3 Network Security

- Use TLS/SSL for database connections
- Implement VPN for remote access
- Restrict database user permissions (read-only where possible)

### 12.4 Data Protection

- No sensitive data logged
- Credentials not exposed in error messages
- Session state cleared on logout

---

## 13. Performance Optimization

### 13.1 Database Level

```sql
-- Add covering indexes
CREATE INDEX IX_tblSales_covering 
ON tblSales(sale_date, shop_id, employee_id) 
INCLUDE (Nt_amount, external_ref_type);

-- Update statistics
UPDATE STATISTICS tblSales;
```

### 13.2 Application Level

1. **Connection Pooling:**
```python
# Already implemented in connection_cloud.py
POOL_SIZE = 10
MAX_OVERFLOW = 20
```

2. **Query Caching:**
```python
# Use appropriate TTL
@st.cache_data(ttl=300)  # 5 minutes for frequently changing data
@st.cache_data(ttl=600)  # 10 minutes for targets
```

3. **Lazy Loading:**
```python
# Load data on-demand in tabs
if st.session_state.current_tab == "Overview":
    df = get_cached_branch_summary(...)
```

### 13.3 Caching Strategy

| Data Type | Recommended TTL |
|-----------|-----------------|
| Branch summary | 300s |
| OT data | 300s |
| Line items | 300s |
| Targets | 600s |
| Daily sales | 300s |
| Monthly sales | 600s |

### 13.4 Query Optimization

1. **Use NOLOCK hint** for read-only queries:
```sql
SELECT ... FROM tblSales s WITH (NOLOCK)
```

2. **Limit date ranges** in queries
3. **Use CTEs** for complex aggregations
4. **Avoid SELECT *** - specify columns

---

## 14. Version History

### v2.0 (Current)
- Complete rewrite with connection pooling
- Enhanced error handling and recovery
- Performance monitoring and health checks
- Modular architecture
- Improved security and credential management
- 11 dashboard tabs with advanced analytics
- Prophet forecasting integration
- Category filter management
- Ramzan deals tracking
- Pivot table analysis

### v1.0 (Previous)
- Basic dashboard functionality
- Direct database connections
- Limited error handling
- No performance optimization

---

## Appendix A: Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `STREAMLIT_CLOUD` | Cloud deployment flag | `false` |
| `DB_API_PROXY` | API proxy URL for cloud | `""` |
| `FALLBACK_CSV_DIR` | CSV fallback directory | `../sales_data_export` |

## Appendix B: File Permissions

```
HNS_Deshboard/
├── config/
│   ├── credentials.json    # Read/Write (application)
│   └── category_filters.json # Read/Write (application)
├── modules/
│   └── *.py               # Read-only (execution)
└── *.py                   # Read-only (execution)
```

## Appendix C: Support & Maintenance

### Regular Tasks
1. Monitor performance metrics daily
2. Review query logs weekly
3. Update credentials monthly
4. Backup configuration regularly
5. Review and optimize slow queries

### Health Check Commands
```python
# In dashboard Performance tab:
health_status = health_check()
metrics = get_performance_metrics()
```

---

**Document Version:** 1.0  
**Last Updated:** February 2025  
**Author:** HNS Development Team
