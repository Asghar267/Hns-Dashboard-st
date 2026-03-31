import pyodbc
import streamlit as st
import os
import requests
from typing import Optional, List, Dict, Any
import pandas as pd
import time
import logging
import threading
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------
# Connection String Helpers
# -------------------------------
def _build_kdsdb_conn_str() -> str:
    """Build kdsdb connection string with environment overrides.

    Supported env vars:
      - KDSDB_CONN_STR (full connection string, takes precedence)
      - KDSDB_SERVER (default: localhost)
      - KDSDB_DATABASE (default: KDS_DB)
      - KDSDB_AUTH (windows|sql; default: windows locally, sql on cloud)
      - KDSDB_UID / KDSDB_PWD (for sql auth)
      - KDSDB_DRIVER (default: ODBC Driver 17 for SQL Server)
      - KDSDB_DRIVER_WINDOWS (default: SQL Server)
    """
    explicit = os.environ.get("KDSDB_CONN_STR")
    if explicit:
        return explicit

    server = os.environ.get("KDSDB_SERVER", "localhost")
    # Default aligns with the repo schema setup and local deployments.
    database = os.environ.get("KDSDB_DATABASE", "KDS_DB")

    default_auth = "sql" if is_streamlit_cloud() else "windows"
    auth = os.environ.get("KDSDB_AUTH", default_auth).strip().lower()

    driver_sql = os.environ.get("KDSDB_DRIVER", "ODBC Driver 17 for SQL Server")
    driver_windows = os.environ.get("KDSDB_DRIVER_WINDOWS", "SQL Server")

    base = [
        f"SERVER={server};",
        f"DATABASE={database};",
        f"Connection Timeout={DatabaseConfig.CONNECTION_TIMEOUT};",
        "MARS_Connection=yes;",
    ]

    if auth == "windows":
        base.insert(0, f"DRIVER={{{driver_windows}}};")
        base.append("Trusted_Connection=yes;")
        return "".join(base)

    uid = os.environ.get("KDSDB_UID", "sa")
    pwd = os.environ.get("KDSDB_PWD", "your_password")
    base.insert(0, f"DRIVER={{{driver_sql}}};")
    base.extend(
        [
            f"UID={uid};",
            f"PWD={pwd};",
            "Encrypt=no;",
        ]
    )
    return "".join(base)

# -------------------------------
# Enhanced Configuration
# -------------------------------
class DatabaseConfig:
    """Enhanced database configuration with performance settings"""
    
    # Connection timeouts (in seconds)
    CONNECTION_TIMEOUT = int(os.environ.get('DB_CONNECTION_TIMEOUT', '60'))
    QUERY_TIMEOUT = int(os.environ.get('DB_QUERY_TIMEOUT', '120'))
    POOL_TIMEOUT = int(os.environ.get('DB_POOL_TIMEOUT', '30'))
    
    # Retry settings
    MAX_RETRIES = int(os.environ.get('DB_MAX_RETRIES', '3'))
    RETRY_DELAY = float(os.environ.get('DB_RETRY_DELAY', '1.0'))
    RETRY_BACKOFF = float(os.environ.get('DB_RETRY_BACKOFF', '2.0'))
    
    # Pool settings
    POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', '10'))
    MAX_OVERFLOW = int(os.environ.get('DB_MAX_OVERFLOW', '20'))
    POOL_RECYCLE = int(os.environ.get('DB_POOL_RECYCLE', '3600'))  # 1 hour
    
    # Performance settings
    ENABLE_CACHING = os.environ.get('DB_ENABLE_CACHING', 'true').lower() == 'true'
    CACHE_TTL = int(os.environ.get('DB_CACHE_TTL', '300'))  # 5 minutes
    ENABLE_COMPRESSION = os.environ.get('DB_ENABLE_COMPRESSION', 'false').lower() == 'true'
    
    # Fallback settings
    FALLBACK_CSV_DIR = os.environ.get(
        'FALLBACK_CSV_DIR',
        os.path.join(os.path.dirname(__file__), '..', 'sales_dashboard', 'sales_data_export')
    )
    
    # Monitoring
    ENABLE_MONITORING = os.environ.get('DB_ENABLE_MONITORING', 'true').lower() == 'true'
    SLOW_QUERY_THRESHOLD = float(os.environ.get('DB_SLOW_QUERY_THRESHOLD', '5.0'))

# -------------------------------
# Environment Detection
# -------------------------------
def is_streamlit_cloud() -> bool:
    """Check if running on Streamlit Cloud"""
    return os.environ.get('STREAMLIT_CLOUD') == 'true'

def is_local_development() -> bool:
    """Check if running in local development"""
    return not is_streamlit_cloud()

# -------------------------------
# Connection Pool with Enhanced Management
# -------------------------------
class EnhancedConnectionPool:
    """Enhanced connection pool with monitoring and health checks"""
    
    def __init__(self):
        self.connections = {}
        self.lock = threading.Lock()
        self.connection_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'failed_connections': 0,
            'total_queries': 0,
            'failed_queries': 0,
            'total_query_time': 0.0,
            'last_health_check': None
        }
    
    def get_connection(self, db_name: str):
        """Get or create a database connection with health monitoring"""
        with self.lock:
            if db_name not in self.connections:
                try:
                    if db_name == "candelahns":
                        self.connections[db_name] = self._create_candelahns_connection()
                    elif db_name == "kdsdb":
                        self.connections[db_name] = self._create_kdsdb_connection()
                    else:
                        raise ValueError(f"Unknown database: {db_name}")
                    
                    self.connection_stats['total_connections'] += 1
                    self.connection_stats['active_connections'] += 1
                    logger.info(f"Created new connection for {db_name}")
                    
                except Exception as e:
                    self.connection_stats['failed_connections'] += 1
                    logger.error(f"Failed to create connection for {db_name}: {e}")
                    raise
            
            # Health check before returning connection
            healthy, err = self._is_connection_healthy(self.connections[db_name])
            if not healthy:
                if err is not None:
                    logger.warning(
                        f"Connection for {db_name} is unhealthy, recreating. Health error: {err}",
                        exc_info=True,
                    )
                else:
                    logger.warning(f"Connection for {db_name} is unhealthy, recreating...")
                try:
                    self.connections[db_name].close()
                except:
                    pass
                self.connections[db_name] = self._create_connection(db_name)
            
            return self.connections[db_name]

    def _create_connection(self, db_name: str) -> pyodbc.Connection:
        """Internal factory used by health-check recreation path."""
        if db_name == "candelahns":
            return self._create_candelahns_connection()
        if db_name == "kdsdb":
            return self._create_kdsdb_connection()
        raise ValueError(f"Unknown database: {db_name}")
    
    def _create_candelahns_connection(self) -> pyodbc.Connection:
        """Create enhanced Candelahns connection with optimized settings"""
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=103.86.55.183,2001;"
            "DATABASE=Candelahns;"
            "UID=ReadOnlyUser;"
            "PWD=902729@Rafy;"
            "Encrypt=no;"
            "TrustServerCertificate=yes;"
            f"Connection Timeout={DatabaseConfig.CONNECTION_TIMEOUT};"
            "MARS_Connection=yes;"
            "MultipleActiveResultSets=yes;"
        )
        
        conn = pyodbc.connect(conn_str, autocommit=False)
        # Default query timeout for all cursors created from this connection.
        try:
            conn.timeout = int(DatabaseConfig.QUERY_TIMEOUT)
        except Exception:
            pass
        
        # Set additional connection properties for performance
        cursor = conn.cursor()
        cursor.execute("SET NOCOUNT ON")  # Reduce network traffic
        cursor.execute("SET ARITHABORT ON")  # Consistent query plans
        cursor.execute("SET LOCK_TIMEOUT 30000")  # 30 second lock timeout
        cursor.close()
        
        return conn
    
    def _create_kdsdb_connection(self) -> pyodbc.Connection:
        """Create enhanced Candelahns_Targets connection"""
        conn_str = _build_kdsdb_conn_str()
        
        conn = pyodbc.connect(conn_str, autocommit=False)
        try:
            conn.timeout = int(DatabaseConfig.QUERY_TIMEOUT)
        except Exception:
            pass
        return conn
    
    def _is_connection_healthy(self, conn: pyodbc.Connection) -> tuple[bool, Exception | None]:
        """Check if connection is still healthy"""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True, None
        except Exception as e:
            return False, e
    
    def close_all(self):
        """Close all connections"""
        with self.lock:
            for conn in self.connections.values():
                try:
                    conn.close()
                except:
                    pass
            self.connections.clear()
            self.connection_stats['active_connections'] = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        with self.lock:
            stats = self.connection_stats.copy()
            stats['pool_size'] = len(self.connections)
            stats['avg_query_time'] = (
                stats['total_query_time'] / max(stats['total_queries'], 1)
            )
            return stats

# Global enhanced connection pool
enhanced_pool = EnhancedConnectionPool()

# -------------------------------
# Enhanced API Proxy Client
# -------------------------------
class EnhancedDatabaseAPIClient:
    """Enhanced HTTP client for database API proxy with retry logic"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'HNS-Dashboard/2.0'
        })
    
    def execute_query(self, query: str, params: Optional[List] = None, timeout: Optional[int] = None) -> List[Dict]:
        """Execute SQL query via API proxy with retry logic"""
        timeout = timeout or DatabaseConfig.QUERY_TIMEOUT
        
        for attempt in range(DatabaseConfig.MAX_RETRIES):
            try:
                start_time = time.time()
                
                response = self.session.post(
                    f"{self.base_url}/query",
                    json={
                        "query": query,
                        "params": params or [],
                        "timeout": timeout
                    },
                    timeout=timeout,
                    stream=False
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Log performance metrics
                query_time = time.time() - start_time
                if DatabaseConfig.ENABLE_MONITORING:
                    logger.info(f"API Query completed in {query_time:.2f}s")
                    if query_time > DatabaseConfig.SLOW_QUERY_THRESHOLD:
                        logger.warning(f"Slow API query detected: {query_time:.2f}s")
                
                return result
                
            except requests.exceptions.RequestException as e:
                if attempt == DatabaseConfig.MAX_RETRIES - 1:
                    logger.error(f"API Proxy Error after {DatabaseConfig.MAX_RETRIES} attempts: {str(e)}")
                    raise
                else:
                    delay = DatabaseConfig.RETRY_DELAY * (DatabaseConfig.RETRY_BACKOFF ** attempt)
                    logger.warning(f"API request failed, retrying in {delay}s: {str(e)}")
                    time.sleep(delay)
            except Exception as e:
                logger.error(f"Unexpected API error: {str(e)}")
                raise
    
    def fetch_dataframe(self, query: str, params: Optional[List] = None) -> pd.DataFrame:
        """Fetch data as pandas DataFrame with compression support"""
        data = self.execute_query(query, params)
        
        if DatabaseConfig.ENABLE_COMPRESSION and len(str(data)) > 10000:  # Large result
            logger.info("Using compressed data transfer")
        
        return pd.DataFrame(data)

# -------------------------------
# Enhanced Database Connection
# -------------------------------
class EnhancedDatabaseConnection:
    """Enhanced database connection with retry logic and monitoring"""
    
    def __init__(self, connection_type: str):
        self.connection_type = connection_type
        self._native_conn = None
        self._api_client = None
        self._query_stats = []
        
        # Initialize connection with retry logic
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize connection with retry logic"""
        for attempt in range(DatabaseConfig.MAX_RETRIES):
            try:
                if is_streamlit_cloud():
                    if os.environ.get('DB_API_PROXY'):
                        self._api_client = EnhancedDatabaseAPIClient(os.environ['DB_API_PROXY'])
                        logger.info("Using API proxy connection")
                        break
                    else:
                        # Try direct connection first
                        self._native_conn = self._create_native_connection()
                        logger.info("Using direct connection in cloud")
                        break
                else:
                    # Local development - use native connection
                    self._native_conn = self._create_native_connection()
                    logger.info("Using native connection locally")
                    break
                    
            except Exception as e:
                if attempt == DatabaseConfig.MAX_RETRIES - 1:
                    logger.error(f"Failed to initialize connection after {DatabaseConfig.MAX_RETRIES} attempts: {e}")
                    raise
                else:
                    delay = DatabaseConfig.RETRY_DELAY * (DatabaseConfig.RETRY_BACKOFF ** attempt)
                    logger.warning(f"Connection attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                    time.sleep(delay)
    
    def _create_native_connection(self) -> pyodbc.Connection:
        """Create native pyodbc connection with enhanced settings"""
        try:
            if self.connection_type == "kdsdb":
                return self._connect_kdsdb()
            elif self.connection_type == "candelahns":
                return self._connect_candelahns()
            else:
                raise ValueError(f"Unknown connection type: {self.connection_type}")
        except pyodbc.Error as e:
            logger.error(f"Native connection failed for {self.connection_type}: {e}")
            raise
    
    def _connect_candelahns(self) -> pyodbc.Connection:
        """Connect to Candelahns DB with enhanced settings"""
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=103.86.55.183,2001;"
            "DATABASE=Candelahns;"
            "UID=ReadOnlyUser;"
            "PWD=902729@Rafy;"
            "Encrypt=no;"
            "TrustServerCertificate=yes;"
            f"Connection Timeout={DatabaseConfig.CONNECTION_TIMEOUT};"
            f"Query Timeout={DatabaseConfig.QUERY_TIMEOUT};"
            "MARS_Connection=yes;"
            "MultipleActiveResultSets=yes;"
            "Pooling=yes;"
            f"Max Pool Size={DatabaseConfig.POOL_SIZE};"
            f"Min Pool Size=1;"
            f"Connection Lifetime={DatabaseConfig.POOL_RECYCLE};"
        )
        
        conn = pyodbc.connect(conn_str, autocommit=False)
        
        # Set performance optimizations
        cursor = conn.cursor()
        cursor.execute("SET NOCOUNT ON")
        cursor.execute("SET ARITHABORT ON")
        cursor.execute("SET LOCK_TIMEOUT 30000")  # 30 second lock timeout
        cursor.execute("SET ROWCOUNT 0")  # Remove row limit
        cursor.close()
        
        return conn
    
    def _connect_kdsdb(self) -> pyodbc.Connection:
        """Connect to Candelahns_Targets with enhanced settings"""
        conn_str = _build_kdsdb_conn_str()
        
        return pyodbc.connect(conn_str, autocommit=False)
    
    def execute_with_retry(self, query: str, params: Optional[List] = None, timeout: Optional[int] = None) -> Any:
        """Execute query with retry logic and monitoring"""
        timeout = timeout or DatabaseConfig.QUERY_TIMEOUT
        start_time = time.time()
        
        for attempt in range(DatabaseConfig.MAX_RETRIES):
            try:
                if self._native_conn:
                    cursor = self._native_conn.cursor()
                    cursor.execute(query, params or ())
                    result = cursor.fetchall()
                    cursor.close()
                    
                    # Log query performance
                    query_time = time.time() - start_time
                    self._log_query_performance(query, query_time, success=True)
                    
                    return result
                    
                elif self._api_client:
                    return self._api_client.execute_query(query, params, timeout)
                    
            except Exception as e:
                query_time = time.time() - start_time
                self._log_query_performance(query, query_time, success=False, error=str(e))
                
                if attempt == DatabaseConfig.MAX_RETRIES - 1:
                    logger.error(f"Query failed after {DatabaseConfig.MAX_RETRIES} attempts: {e}")
                    raise
                else:
                    delay = DatabaseConfig.RETRY_DELAY * (DatabaseConfig.RETRY_BACKOFF ** attempt)
                    logger.warning(f"Query attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                    time.sleep(delay)
    
    def fetch_dataframe_with_retry(self, query: str, params: Optional[List] = None, timeout: Optional[int] = None) -> pd.DataFrame:
        """Fetch DataFrame with retry logic and monitoring"""
        timeout = timeout or DatabaseConfig.QUERY_TIMEOUT
        start_time = time.time()
        
        for attempt in range(DatabaseConfig.MAX_RETRIES):
            try:
                if self._native_conn:
                    df = pd.read_sql(query, self._native_conn, params=params)
                    
                    # Log query performance
                    query_time = time.time() - start_time
                    self._log_query_performance(query, query_time, success=True, rows=len(df))
                    
                    return df
                    
                elif self._api_client:
                    return self._api_client.fetch_dataframe(query, params, timeout)
                    
            except Exception as e:
                query_time = time.time() - start_time
                self._log_query_performance(query, query_time, success=False, error=str(e))
                
                if attempt == DatabaseConfig.MAX_RETRIES - 1:
                    logger.error(f"DataFrame fetch failed after {DatabaseConfig.MAX_RETRIES} attempts: {e}")
                    raise
                else:
                    delay = DatabaseConfig.RETRY_DELAY * (DatabaseConfig.RETRY_BACKOFF ** attempt)
                    logger.warning(f"DataFrame fetch attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                    time.sleep(delay)
    
    def _log_query_performance(self, query: str, query_time: float, success: bool, error: str = None, rows: int = 0):
        """Log query performance metrics"""
        query_info = {
            'timestamp': datetime.now(),
            'query_type': query.strip().split()[0].upper() if query.strip() else 'UNKNOWN',
            'query_time': query_time,
            'success': success,
            'error': error,
            'rows': rows,
            'connection_type': self.connection_type
        }
        
        self._query_stats.append(query_info)
        
        # Update global stats
        enhanced_pool.connection_stats['total_queries'] += 1
        enhanced_pool.connection_stats['total_query_time'] += query_time
        
        if not success:
            enhanced_pool.connection_stats['failed_queries'] += 1
        
        # Log slow queries
        if query_time > DatabaseConfig.SLOW_QUERY_THRESHOLD:
            logger.warning(f"Slow query detected ({query_time:.2f}s): {query[:100]}...")
        
        # Keep only last 1000 queries in memory
        if len(self._query_stats) > 1000:
            self._query_stats = self._query_stats[-500:]
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query performance statistics"""
        if not self._query_stats:
            return {}
        
        successful_queries = [q for q in self._query_stats if q['success']]
        failed_queries = [q for q in self._query_stats if not q['success']]
        
        stats = {
            'total_queries': len(self._query_stats),
            'successful_queries': len(successful_queries),
            'failed_queries': len(failed_queries),
            'success_rate': len(successful_queries) / len(self._query_stats) * 100 if self._query_stats else 0,
            'avg_query_time': sum(q['query_time'] for q in successful_queries) / max(len(successful_queries), 1),
            'max_query_time': max((q['query_time'] for q in successful_queries), default=0),
            'min_query_time': min((q['query_time'] for q in successful_queries), default=0),
            'slow_queries': len([q for q in successful_queries if q['query_time'] > DatabaseConfig.SLOW_QUERY_THRESHOLD])
        }
        
        return stats
    
    def close(self):
        """Close connection"""
        if self._native_conn:
            self._native_conn.close()
            enhanced_pool.connection_stats['active_connections'] = max(0, enhanced_pool.connection_stats['active_connections'] - 1)

# -------------------------------
# Enhanced Wrapper Functions
# -------------------------------
@st.cache_resource
def get_enhanced_connection_candelahns() -> EnhancedDatabaseConnection:
    """Get enhanced Candelahns DB connection"""
    return EnhancedDatabaseConnection("candelahns")

@st.cache_resource
def get_enhanced_connection_kdsdb() -> EnhancedDatabaseConnection:
    """Get enhanced KDS_DB connection"""
    return EnhancedDatabaseConnection("kdsdb")

# -------------------------------
# Performance Monitoring
# -------------------------------
def get_performance_metrics() -> Dict[str, Any]:
    """Get comprehensive performance metrics"""
    pool_stats = enhanced_pool.get_stats()
    
    # Get connection-specific stats
    candelahns_conn = get_enhanced_connection_candelahns()
    kdsdb_conn = get_enhanced_connection_kdsdb()
    
    return {
        'pool_stats': pool_stats,
        'candelahns_stats': candelahns_conn.get_query_stats(),
        'kdsdb_stats': kdsdb_conn.get_query_stats(),
        'config': {
            'connection_timeout': DatabaseConfig.CONNECTION_TIMEOUT,
            'query_timeout': DatabaseConfig.QUERY_TIMEOUT,
            'max_retries': DatabaseConfig.MAX_RETRIES,
            'pool_size': DatabaseConfig.POOL_SIZE,
            'slow_query_threshold': DatabaseConfig.SLOW_QUERY_THRESHOLD
        }
    }

# -------------------------------
# Health Check
# -------------------------------
def health_check() -> Dict[str, Any]:
    """Perform comprehensive health check"""
    try:
        # Test Candelahns connection
        candelahns_conn = get_enhanced_connection_candelahns()
        candelahns_stats = candelahns_conn.get_query_stats()
        
        # Test KDS connection
        kdsdb_conn = get_enhanced_connection_kdsdb()
        kdsdb_stats = kdsdb_conn.get_query_stats()
        
        # Pool stats
        pool_stats = enhanced_pool.get_stats()
        
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'connections': {
                'candelahns': 'connected' if candelahns_stats else 'disconnected',
                'kdsdb': 'connected' if kdsdb_stats else 'disconnected'
            },
            'pool_stats': pool_stats,
            'recent_queries': {
                'candelahns': candelahns_stats.get('successful_queries', 0),
                'kdsdb': kdsdb_stats.get('successful_queries', 0)
            }
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
