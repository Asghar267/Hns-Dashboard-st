import pyodbc
import os
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import time
import logging
import threading
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Performance tracing
PERF_TRACE = []
PERF_LOCK = threading.Lock()

def add_perf_trace(label: str, duration: float, source: str = "db"):
    with PERF_LOCK:
        PERF_TRACE.append({
            "label": label,
            "duration": round(duration, 4),
            "source": source,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        # Keep last 50 traces
        if len(PERF_TRACE) > 50:
            PERF_TRACE.pop(0)

@contextmanager
def perf_trace(label: str, source: str = "db"):
    start = time.perf_counter()
    try:
        yield
    finally:
        duration = time.perf_counter() - start
        add_perf_trace(label, duration, source)

class DatabaseConfig:
    CONNECTION_TIMEOUT = int(os.environ.get('DB_CONNECTION_TIMEOUT', '60'))
    QUERY_TIMEOUT = int(os.environ.get('DB_QUERY_TIMEOUT', '120'))
    POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', '10'))

def _build_conn_str(prefix: str) -> str:
    """Build connection string from env variables with given prefix (e.g. CANDELAHNS or KDSDB)"""
    explicit = os.environ.get(f"{prefix}_CONN_STR")
    if explicit:
        return explicit

    server = os.environ.get(f"{prefix}_SERVER", "localhost")
    database = os.environ.get(f"{prefix}_DATABASE", "Candelahns")
    auth = os.environ.get(f"{prefix}_AUTH", "sql").strip().lower()
    driver = os.environ.get(f"{prefix}_DRIVER", "ODBC Driver 17 for SQL Server")
    driver_windows = os.environ.get(f"{prefix}_DRIVER_WINDOWS", "SQL Server")

    base = [
        f"SERVER={server};",
        f"DATABASE={database};",
        f"Connection Timeout={DatabaseConfig.CONNECTION_TIMEOUT};",
        "MARS_Connection=yes;",
        "Encrypt=no;",
        "TrustServerCertificate=yes;"
    ]

    if auth == "windows":
        base.insert(0, f"DRIVER={{{driver_windows}}};")
        base.append("Trusted_Connection=yes;")
    else:
        uid = os.environ.get(f"{prefix}_UID", "sa")
        pwd = os.environ.get(f"{prefix}_PWD", "")
        base.insert(0, f"DRIVER={{{driver}}};")
        base.extend([f"UID={uid};", f"PWD={pwd};"])
    
    return "".join(base)

class ConnectionPool:
    def __init__(self):
        self.connections = {}
        self.lock = threading.Lock()

    def get_connection(self, db_name: str) -> pyodbc.Connection:
        with self.lock:
            if db_name not in self.connections:
                prefix = "CANDELAHNS" if db_name == "candelahns" else "KDSDB"
                conn_str = _build_conn_str(prefix)
                try:
                    logger.info(f"Connecting to {db_name}...")
                    self.connections[db_name] = pyodbc.connect(conn_str, autocommit=False)
                except Exception as e:
                    logger.error(f"Failed to connect to {db_name}: {e}")
                    raise e
            
            # Health check
            try:
                cursor = self.connections[db_name].cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
            except:
                logger.warning(f"Connection for {db_name} is unhealthy, recreating...")
                prefix = "CANDELAHNS" if db_name == "candelahns" else "KDSDB"
                conn_str = _build_conn_str(prefix)
                self.connections[db_name] = pyodbc.connect(conn_str, autocommit=False)
            
            return self.connections[db_name]

db_pool = ConnectionPool()

def get_db(db_name: str = "candelahns"):
    return db_pool.get_connection(db_name)

def run_query(query: str, params: tuple = (), db_name: str = "candelahns") -> pd.DataFrame:
    """Run a query and return a pandas DataFrame."""
    # Simplified label for performance trace
    label = query.strip()[:60].replace('\n', ' ') + "..."
    logger.info(f"Running query on {db_name}: {label}")
    with perf_trace(label):
        try:
            conn = get_db(db_name)
            df = pd.read_sql(query, conn, params=params)
            logger.info(f"Query returned {len(df)} rows.")
            return df
        except Exception as e:
            logger.error(f"Error running query on {db_name}: {str(e)}")
            raise e

def get_targets(year: int, month: int):
    """Fetch targets for a specific month and year"""
    results = {
        "branch_targets": pd.DataFrame(),
        "chef_targets": pd.DataFrame(),
        "ot_targets": pd.DataFrame()
    }
    
    try:
        conn = get_db("kdsdb")
        
        def table_exists(table_name: str) -> bool:
            try:
                cursor = conn.cursor()
                cursor.execute(f"SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}'")
                exists = cursor.fetchone()
                cursor.close()
                return exists is not None
            except:
                return False

        # OT Targets
        if table_exists("ot_targets"):
            try:
                query = "SELECT shop_id, employee_id, monthly_target as target_amount FROM ot_targets WHERE target_year = ? AND target_month = ?"
                results["ot_targets"] = pd.read_sql(query, conn, params=(year, month))
            except Exception as e:
                logger.warning(f"Error fetching ot_targets: {e}")

        # Chef Targets
        if table_exists("branch_chef_targets"):
            try:
                query = "SELECT shop_id, category_id, monthly_target as target_amount, target_type FROM branch_chef_targets WHERE target_year = ? AND target_month = ?"
                results["chef_targets"] = pd.read_sql(query, conn, params=(year, month))
            except Exception as e:
                logger.warning(f"Error fetching branch_chef_targets: {e}")

        # Branch Targets
        if table_exists("branch_targets"):
            try:
                query = "SELECT shop_id, monthly_target FROM branch_targets WHERE target_year = ? AND target_month = ?"
                results["branch_targets"] = pd.read_sql(query, conn, params=(year, month))
            except Exception as e:
                logger.warning(f"Error fetching branch_targets: {e}")

    except Exception as e:
        logger.error(f"Failed to connect to targets database: {e}")
        
    return results
