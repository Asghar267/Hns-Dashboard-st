# HNS Sales Dashboard - Enhanced Version

## Overview

This is an optimized, production-ready sales dashboard for HNS (Habib Nawaz Saeed) with advanced features including connection pooling, caching, performance monitoring, and enhanced error handling.

## Key Features

### 🚀 Performance Optimizations
- **Connection Pooling**: Reuses database connections to reduce overhead
- **Query Caching**: Caches expensive queries for 5 minutes to improve response times
- **Connection Timeouts**: Configurable timeouts to prevent hanging queries
- **Retry Logic**: Automatic retry mechanism for failed connections
- **Resource Management**: Proper connection cleanup and resource management

### 🛡️ Enhanced Error Handling
- **Graceful Degradation**: Dashboard continues working even if some data sources fail
- **Detailed Error Messages**: Clear error messages with troubleshooting guidance
- **Connection Health Monitoring**: Real-time health checks and performance metrics
- **Fallback Mechanisms**: Built-in fallbacks when primary connections fail

### 📊 Advanced Analytics
- **Real-time Data**: Live connection to SQL Server databases
- **Multi-branch Support**: Support for all HNS branches with user-based access control
- **Advanced Visualizations**: Interactive charts and graphs using Plotly
- **Performance Monitoring**: Built-in performance metrics and health checks

### 🔧 Technical Improvements
- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **Configuration Management**: Centralized configuration for all database settings
- **Logging**: Comprehensive logging for debugging and monitoring
- **Security**: Secure credential management and connection handling

## Architecture

```
HNS_Deshboard/
├── hns_dashboard.py          # Main dashboard application
├── sqldatabase.py           # Legacy database functions (preserved)
├── config/                  # Configuration files
│   ├── credentials.json     # App users (local-only; not committed)
│   ├── credentials.example.json  # Template only (safe to commit)
│   └── config.py           # Application configuration
├── modules/                 # Modular components
│   ├── connection_cloud.py # Enhanced connection management
│   ├── database.py         # Cached database queries
│   ├── visualization.py    # Chart and graph utilities
│   ├── utils.py           # Utility functions
│   ├── config.py          # Configuration constants
│   └── auth.py            # Authentication system
└── README.md              # This file
```

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Required Packages**:
   ```bash
   pip install streamlit pandas plotly pyodbc
   ```

3. **SQL Server Drivers**: Ensure SQL Server ODBC drivers are installed on the system

## Run Locally

1. **Create and activate a virtual environment** (optional but recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install streamlit pandas plotly pyodbc
   ```

3. **Start the app**:
   ```bash
   streamlit run hns_dashboard_modular.py
   ```

### Setup

1. **Clone or download** the dashboard files to your local machine
2. **Configure Credentials & Databases**:
   - App login users live in `config/credentials.json` (local-only). If it doesn't exist, the app bootstraps it using `HNS_DEFAULT_ADMIN_PASSWORD`.
   - Database connectivity is configured via environment variables (see `config/app_config.py` and `modules/connection_cloud.py`).

3. **Run the Dashboard**:
   ```bash
   cd HNS_Deshboard
   streamlit run hns_dashboard.py
   ```

## Configuration

### Database Configuration

Set environment variables (examples):

- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USERNAME`, `DB_PASSWORD` (see `config/app_config.py`)
- `KDSDB_SERVER`, `KDSDB_DATABASE`, `KDSDB_AUTH`, `KDSDB_UID`, `KDSDB_PWD` (see `modules/connection_cloud.py`)
- `CANDELAHNS_PWD` (see `modules/connection_cloud.py`)
- `CALL_CENTER_DB_SERVER`, `CALL_CENTER_DB_NAME`, `CALL_CENTER_DB_UID`, `CALL_CENTER_DB_PWD` (see `dashboard_tabs/call_center_tab.py`)

### Connection Settings

Edit `modules/config.py` to adjust connection parameters:

```python
# Connection timeouts (in seconds)
CONNECTION_TIMEOUT = 30
QUERY_TIMEOUT = 60
POOL_TIMEOUT = 10

# Pool settings
POOL_SIZE = 10
MAX_OVERFLOW = 20

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 2

# Performance thresholds
SLOW_QUERY_THRESHOLD = 5.0
```

## Usage

### Dashboard Features

1. **Overview Tab**: 
   - Branch performance summary
   - Sales targets and achievements
   - Order type analysis
   - Export capabilities

2. **Order Takers Tab**:
   - OT performance tracking
   - Sales by employee
   - Performance comparisons

3. **Chef Sales Tab**:
   - Product-level sales analysis
   - Category performance
   - Daily targets tracking

4. **Chef Targets Tab**:
   - Target vs achievement analysis
   - Bonus calculations
   - Performance charts

5. **OT Targets Tab**:
   - Daily and monthly targets
   - Performance tracking
   - Achievement percentages

6. **QR Commission Tab**:
   - Blinkco order analysis
   - Commission calculations
   - Transaction matching

7. **Trends & Analytics Tab**:
   - Sales trend analysis
   - Product comparisons
   - Forecasting capabilities

### Performance Monitoring

The dashboard includes built-in performance monitoring:

- **Health Check**: Real-time connection health status
- **Performance Metrics**: Query times, connection pool stats
- **Connection Settings**: View current connection configuration
- **Auto-refresh**: Optional automatic data refresh

### Troubleshooting

#### Common Issues

1. **Connection Timeouts**:
   - Check network connectivity to SQL Server
   - Verify database environment variables (e.g. `DB_PASSWORD`, `KDSDB_PWD`, `CANDELAHNS_PWD`, `CALL_CENTER_DB_PWD`)
   - Increase `CONNECTION_TIMEOUT` in `modules/config.py`

2. **Slow Performance**:
   - Monitor query execution times in Performance tab
   - Check database server performance
   - Consider increasing connection pool size

3. **Authentication Errors**:
   - Verify user credentials and permissions
   - Check if user has access to required branches
   - Contact system administrator for access issues

#### Error Recovery

The dashboard includes several recovery mechanisms:

- **Automatic Retries**: Failed connections are automatically retried
- **Graceful Degradation**: Dashboard continues with available data
- **Fallback Targets**: Built-in default targets when database targets unavailable
- **Connection Health**: Real-time monitoring and alerts

## Security

### Credential Management
- App login users are stored in `config/credentials.json` (local-only; not committed)
- Database credentials are supplied via environment variables and should not be hardcoded
- Connection strings are properly formatted and secured

### Access Control
- User-based authentication system
- Branch-specific access control
- Session timeout and activity monitoring

### Data Protection
- No sensitive data is cached or logged
- Connection pooling prevents credential exposure
- Secure connection protocols (TLS/SSL)

## Performance Optimization

### Best Practices

1. **Connection Management**:
   - Use connection pooling to reduce overhead
   - Set appropriate timeouts to prevent hanging queries
   - Monitor connection pool usage

2. **Query Optimization**:
   - Use cached queries for frequently accessed data
   - Implement proper indexing on database tables
   - Monitor slow queries and optimize as needed

3. **Caching Strategy**:
   - Cache expensive queries for 5 minutes
   - Use appropriate cache invalidation strategies
   - Monitor cache hit rates

4. **Resource Monitoring**:
   - Regularly check connection pool statistics
   - Monitor query execution times
   - Set up alerts for performance degradation

### Performance Monitoring

The dashboard provides comprehensive performance monitoring:

- **Connection Pool Stats**: Pool size, active connections, total queries
- **Query Performance**: Average query time, slow query count, success rate
- **Health Status**: Real-time connection health checks
- **Resource Usage**: Memory and CPU usage monitoring

## Maintenance

### Regular Tasks

1. **Monitor Performance**: Check performance metrics regularly
2. **Update Credentials**: Rotate database credentials as needed
3. **Review Logs**: Check application logs for errors or warnings
4. **Database Maintenance**: Ensure database indexes are optimized
5. **Backup Configuration**: Regularly backup configuration files

### Updates and Upgrades

1. **Database Schema Changes**: Update queries if database schema changes
2. **Library Updates**: Keep Python libraries updated
3. **Security Patches**: Apply security updates promptly
4. **Performance Tuning**: Regularly review and optimize performance

## Support

For technical support or questions:

1. **Check Logs**: Review application logs for error details
2. **Performance Metrics**: Use built-in monitoring to diagnose issues
3. **Configuration**: Verify all configuration files are correct
4. **Network**: Ensure network connectivity to database servers
5. **Documentation**: Refer to this README for setup and troubleshooting

## Version History

### v2.0 (Current)
- Complete rewrite with connection pooling
- Enhanced error handling and recovery
- Performance monitoring and health checks
- Modular architecture
- Improved security and credential management

### v1.0 (Previous)
- Basic dashboard functionality
- Direct database connections
- Limited error handling
- No performance optimization

## License

This project is for internal use by HNS (Habib Nawaz Saeed). All rights reserved.

## Contact

For support and questions, contact the development team.
