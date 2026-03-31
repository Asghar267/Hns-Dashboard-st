from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any
from database import db_pool, run_query, PERF_TRACE
from snapshot_service import run_snapshot_pipeline
import os
from datetime import datetime

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/perf-trace")
async def get_perf_trace():
    """Get recent performance traces"""
    return PERF_TRACE

@router.get("/health")
async def health_check():
    """Check database connection health"""
    results = {}
    for db_name in ["candelahns", "kdsdb"]:
        try:
            conn = db_pool.get_connection(db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            results[db_name] = "healthy"
        except Exception as e:
            results[db_name] = f"unhealthy: {str(e)}"
    
    return results

@router.get("/metrics")
async def get_metrics():
    """Get performance metrics (simulated from pool stats)"""
    # In a real app, we'd track these in the ConnectionPool
    return {
        "pool_size": 10,
        "active_connections": len(db_pool.connections),
        "total_queries": 1250,  # Simulated
        "avg_query_time": "0.45s",
        "uptime": "24h 15m"
    }

@router.post("/snapshots")
async def generate_snapshots(background_tasks: BackgroundTasks):
    """Trigger snapshot generation in background"""
    background_tasks.add_task(run_snapshot_pipeline)
    return {"message": "Snapshot generation started in background"}
