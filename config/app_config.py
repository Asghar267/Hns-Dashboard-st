"""
Application Configuration
Centralized configuration management for the dashboard
"""

import os
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class DataMode(Enum):
    """Data filtering modes"""
    ALL = "All"
    FILTERED = "Filtered"


@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    host: str = "localhost"
    port: int = 1433
    database: str = "candelahns"
    username: str = "sa"
    password: str = "123456789"
    driver: str = "ODBC Driver 17 for SQL Server"


@dataclass
class DashboardConfig:
    """Dashboard configuration"""
    title: str = "HNS Dashboard"
    page_icon: str = "🏪"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"
    theme: str = "light"


@dataclass
class StyleConfig:
    """CSS styling configuration"""
    primary_color: str = "#1E88E5"
    secondary_color: str = "#424242"
    background_color: str = "#FFFFFF"
    text_color: str = "#333333"
    font_family: str = "Arial, sans-serif"


class AppConfig:
    """Main application configuration class"""
    
    # Database configuration
    DATABASE = DatabaseConfig()
    
    # Dashboard configuration
    DASHBOARD = DashboardConfig()
    
    # Styling configuration
    STYLE = StyleConfig()
    
    # Default settings
    DEFAULT_START_DATE = "2025-01-01"
    DEFAULT_END_DATE = "2025-12-31"
    DEFAULT_BRANCHES = [2, 3, 4, 6, 8, 10, 14]
    DEFAULT_DATA_MODE = DataMode.ALL
    
# Navbar & Tab configurations
    NAVBAR_ITEMS = {
        "tabs": {
            "Overview": {"icon": "📊", "description": "Main dashboard overview with key metrics"},
            "Order Takers": {"icon": "👥", "description": "Order Taker performance analysis"},
            "Chef Sales": {"icon": "🍽️", "description": "Chef sales and product performance"},
            "Chef Targets": {"icon": "🎯", "description": "Chef sales targets"},
            "OT Targets": {"icon": "📈", "description": "Order taker targets"},
            "QR Commission": {"icon": "💳", "description": "QR/Blinkco commission analysis"},
            "Khadda Diagnostics": {"icon": "🔍", "description": "Khadda data diagnostics"},
            "Material Cost Commission": {"icon": "💰", "description": "Material cost commissions"},
            "Trends & Analytics": {"icon": "📊", "description": "Trends and analytics"},
            "Ramzan Deals": {"icon": "🌙", "description": "Ramzan special deals"},
            "Category Filters & Coverage": {"icon": "🔧", "description": "Category filters"},
            "Category Filters & Coverage": {"icon": "📋", "description": "Category coverage analysis"},
            "Pivot Tables": {"icon": "📋", "description": "Interactive pivot tables"},
            "User Management": {"icon": "👥", "description": "Admin user management", "admin_only": True}
        },
        "globals": [
            {"label": "Refresh", "icon": "🔄", "key": "refresh"},
            {"label": "Help", "icon": "❓", "key": "help"}
        ]
    }
    
    # Legacy TABS (deprecated - use NAVBAR_ITEMS)
    TABS = NAVBAR_ITEMS['tabs']
    
    # Export settings
    EXPORT = {
        "default_format": "xlsx",
        "include_timestamp": True,
        "max_rows_excel": 100000,
        "max_rows_csv": 1000000
    }
    
    # Chart settings
    CHARTS = {
        "default_height": 500,
        "color_scales": {
            "sales": "Blues",
            "commission": "Greens",
            "performance": "RdYlBu"
        },
        "gauge_thresholds": {
            "excellent": 90,
            "good": 70,
            "warning": 50,
            "poor": 0
        }
    }
    
    # Filter settings
    FILTERS = {
        "max_branches": 20,
        "search_debounce_ms": 300,
        "default_page_size": 100,
        "enable_live_search": True
    }
    
    @classmethod
    def get_branch_options(cls) -> List[Dict[str, int]]:
        """Get available branch options"""
        return [
            {"label": "Khadda Main Branch", "value": 2},
            {"label": "Festival", "value": 3},
            {"label": "Rahat Commercial", "value": 4},
            {"label": "Tower", "value": 6},
            {"label": "North Nazimabad", "value": 8},
            {"label": "Malir", "value": 10},
            {"label": "Festival 2", "value": 14}
        ]
    
    @classmethod
    def get_data_mode_options(cls) -> List[str]:
        """Get available data mode options"""
        return [mode.value for mode in DataMode]
    
    @classmethod
    def get_default_branch_names(cls) -> List[str]:
        """Get default branch names"""
        branch_options = cls.get_branch_options()
        default_branches = cls.DEFAULT_BRANCHES
        return [
            option["label"] for option in branch_options 
            if option["value"] in default_branches
        ]
    
    @classmethod
    def load_from_env(cls):
        """Load configuration from environment variables"""
        # Database config
        cls.DATABASE.host = os.getenv("DB_HOST", cls.DATABASE.host)
        cls.DATABASE.port = int(os.getenv("DB_PORT", cls.DATABASE.port))
        cls.DATABASE.database = os.getenv("DB_NAME", cls.DATABASE.database)
        cls.DATABASE.username = os.getenv("DB_USERNAME", cls.DATABASE.username)
        cls.DATABASE.password = os.getenv("DB_PASSWORD", cls.DATABASE.password)
        
        # Dashboard config
        cls.DASHBOARD.title = os.getenv("DASHBOARD_TITLE", cls.DASHBOARD.title)
        cls.DASHBOARD.page_icon = os.getenv("DASHBOARD_ICON", cls.DASHBOARD.page_icon)
        cls.DASHBOARD.layout = os.getenv("DASHBOARD_LAYOUT", cls.DASHBOARD.layout)
        
        # Style config
        cls.STYLE.primary_color = os.getenv("PRIMARY_COLOR", cls.STYLE.primary_color)
        cls.STYLE.secondary_color = os.getenv("SECONDARY_COLOR", cls.STYLE.secondary_color)
        cls.STYLE.background_color = os.getenv("BACKGROUND_COLOR", cls.STYLE.background_color)
        cls.STYLE.text_color = os.getenv("TEXT_COLOR", cls.STYLE.text_color)
        cls.STYLE.font_family = os.getenv("FONT_FAMILY", cls.STYLE.font_family)


# Load environment configuration on import
AppConfig.load_from_env()
