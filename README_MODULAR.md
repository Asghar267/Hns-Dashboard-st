# HNS Dashboard - Modular Architecture

This document describes the modularized version of the HNS Dashboard, which has been refactored to improve maintainability, scalability, and code organization.

## Architecture Overview

The dashboard has been restructured into a modular architecture with the following key components:

### 📁 Directory Structure

```
HNS_Deshboard/
├── hns_dashboard_modular.py     # Main application entry point
├── hns_dashboard.py              # Original monolithic version
├── modules/                      # Core business logic modules
│   ├── database.py              # Database operations and caching
│   ├── utils.py                 # Utility functions
│   ├── visualization.py         # Chart and visualization functions
│   ├── config.py               # Configuration constants
│   ├── auth.py                 # Authentication logic
│   ├── connection_cloud.py     # Database connection management
│   ├── material_cost_commission.py # Material cost commission logic
│   └── blink_reporting.py      # Blink/QR commission reporting
├── services/                     # Business logic services
│   ├── branch_service.py       # Branch-related operations
│   ├── order_taker_service.py  # Order taker operations
│   ├── chef_sales_service.py   # Chef sales operations
│   └── qr_commission_service.py # QR commission operations
├── components/                   # Reusable UI components
│   └── ui_components.py        # Streamlit UI components
└── config/                      # Configuration management
    └── app_config.py           # Application configuration
```

## 🏗️ Architecture Benefits

### 1. **Separation of Concerns**
- **Services**: Handle business logic and data processing
- **Components**: Provide reusable UI elements
- **Modules**: Contain core functionality and utilities
- **Config**: Centralized configuration management

### 2. **Improved Maintainability**
- Each service focuses on a specific domain
- UI components are reusable across tabs
- Configuration is centralized and easily modifiable
- Clear separation between data, logic, and presentation

### 3. **Enhanced Scalability**
- Easy to add new tabs or features
- Services can be extended independently
- Components can be reused across different parts
- Configuration can be easily modified

### 4. **Better Testing**
- Each module can be tested independently
- Services have clear interfaces
- Components are isolated and testable
- Configuration is easily mockable

## 📋 Module Descriptions

### Core Modules (`modules/`)

#### `database.py`
- Database connection management
- Query execution and caching
- Data retrieval functions
- Connection pooling

#### `utils.py`
- Currency and percentage formatting
- Date handling utilities
- Data export functions
- Common helper functions

#### `visualization.py`
- Chart creation functions
- Plotly-based visualizations
- Dashboard-specific charts
- Data visualization utilities

#### `config.py`
- Application constants
- Configuration values
- Default settings
- Enumerations

#### `auth.py`
- User authentication
- Session management
- Permission handling
- Security utilities

### Services (`services/`)

#### `BranchService`
- Branch performance analysis
- Target management
- Branch-specific calculations
- Branch data processing

#### `OrderTakerService`
- Order taker performance tracking
- Sales attribution
- OT-specific metrics
- Employee sales analysis

#### `ChefSalesService`
- Product sales analysis
- Category performance
- Chef-specific reporting
- Menu item tracking

#### `QRCommissionService`
- QR/Blink commission calculations
- Transaction analysis
- Commission reporting
- Payment processing metrics

### Components (`components/`)

#### `ui_components.py`
- **MetricsCard**: Reusable metric display components
- **ChartComponents**: Chart rendering utilities
- **TableComponents**: Data table display functions
- **ExportComponents**: Export functionality
- **FilterComponents**: Filter UI elements

### Configuration (`config/`)

#### `app_config.py`
- Application settings
- Database configuration
- Dashboard configuration
- Style configuration
- Environment variables

## 🚀 Usage

### Running the Modular Dashboard

```bash
# Run the modular version
python hns_dashboard_modular.py

# Run the original version (for comparison)
python hns_dashboard.py
```

### Adding New Features

1. **New Tab**: Create a new service in `services/` and add the tab to the main application
2. **New Component**: Add to `components/ui_components.py` for reuse across tabs
3. **New Utility**: Add to appropriate module in `modules/`
4. **New Configuration**: Add to `config/app_config.py`

### Example: Adding a New Service

```python
# services/new_feature_service.py
class NewFeatureService:
    def __init__(self):
        pass
    
    def get_data(self, params):
        # Business logic here
        pass
    
    def process_data(self, data):
        # Data processing here
        pass
```

```python
# hns_dashboard_modular.py
from services.new_feature_service import NewFeatureService

# In main():
new_service = NewFeatureService()
# Use the service in a new tab
```

## 🔧 Configuration

The application uses a centralized configuration system:

```python
from config.app_config import AppConfig

# Access configuration
title = AppConfig.DASHBOARD.title
branches = AppConfig.DEFAULT_BRANCHES
db_config = AppConfig.DATABASE
```

## 📊 Performance Improvements

The modular architecture provides several performance benefits:

1. **Lazy Loading**: Services are only imported when needed
2. **Caching**: Database queries are cached at the module level
3. **Optimized Imports**: Only necessary modules are imported
4. **Memory Efficiency**: Better memory management through separation

## 🧪 Testing Strategy

Each module can be tested independently:

```python
# Test a service
from services.branch_service import BranchService

def test_branch_service():
    service = BranchService()
    data = service.get_branch_performance()
    assert data is not None

# Test a component
from components.ui_components import MetricsCard

def test_metrics_card():
    # Test component rendering
    pass
```

## 🔄 Migration Guide

To migrate from the monolithic version:

1. **Copy Configuration**: Move configuration to `config/app_config.py`
2. **Extract Services**: Identify business logic and create services
3. **Create Components**: Extract reusable UI elements
4. **Update Imports**: Update import statements in main application
5. **Test Thoroughly**: Ensure all functionality works correctly

## 📈 Future Enhancements

The modular architecture enables easy addition of:

- **New Data Sources**: Add new database modules
- **Advanced Analytics**: Create specialized analysis services
- **Real-time Updates**: Implement WebSocket services
- **Mobile Support**: Create responsive components
- **API Endpoints**: Add REST API services

## 🤝 Contributing

When contributing to the modular version:

1. Follow the existing module structure
2. Create appropriate services for new business logic
3. Extract reusable components when possible
4. Update configuration as needed
5. Write tests for new modules

## 📞 Support

For questions about the modular architecture:
- Review the existing module implementations
- Check the configuration examples
- Test with the provided test cases
- Refer to this documentation for guidance