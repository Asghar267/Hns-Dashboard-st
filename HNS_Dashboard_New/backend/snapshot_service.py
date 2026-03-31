
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from database import run_query, get_targets
from typing import List, Dict, Any

# Configure matplotlib for headless use
import matplotlib
matplotlib.use('Agg')

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 150

OUTPUT_DIR = Path("snapshots")

def format_currency(value: float) -> str:
    return f"PKR {float(value):,.0f}"

def save_figure(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)

async def generate_branch_performance_snapshot(start_date: str, end_date: str, branch_ids: List[int]):
    """Generate a single summary image for branch performance"""
    
    # Fetch data (simplified overview logic)
    query = f"""
    SELECT
        sh.shop_id,
        sh.shop_name,
        COUNT(DISTINCT s.sale_id) AS total_sales,
        SUM(s.Nt_amount) AS total_Nt_amount
    FROM tblDefShops sh WITH (NOLOCK)
    LEFT JOIN tblSales s WITH (NOLOCK) ON sh.shop_id = s.shop_id 
        AND s.sale_date BETWEEN ? AND ?
    WHERE sh.shop_id IN ({", ".join(["?"] * len(branch_ids))})
    GROUP BY sh.shop_id, sh.shop_name
    """
    params = [start_date, end_date] + branch_ids
    df = run_query(query, params=tuple(params))
    
    # Merge targets
    dt = pd.to_datetime(end_date)
    targets = get_targets(dt.year, dt.month)
    df_targets = targets["branch_targets"]
    
    if not df_targets.empty:
        df = df.merge(df_targets, on="shop_id", how="left").fillna(0)
    else:
        df["monthly_target"] = 0
        
    df["achievement_pct"] = (df["total_Nt_amount"] / df["monthly_target"] * 100).fillna(0)
    
    # Create plot
    n = len(df)
    fig, ax = plt.subplots(figsize=(10, 2 + n * 0.5))
    ax.axis('off')
    
    title = f"HNS BRANCH PERFORMANCE\n{start_date} to {end_date}"
    plt.title(title, fontsize=16, weight='bold', pad=20)
    
    table_data = []
    headers = ["Branch", "Sales", "Target", "Ach%"]
    
    for _, r in df.iterrows():
        table_data.append([
            r['shop_name'],
            format_currency(r['total_Nt_amount']),
            format_currency(r['monthly_target']),
            f"{r['achievement_pct']:.1f}%"
        ])
        
    table = ax.table(
        cellText=table_data,
        colLabels=headers,
        loc='center',
        cellLoc='left'
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    
    # Style
    for (r, c), cell in table.get_celld().items():
        if r == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#2563eb')
        else:
            cell.set_facecolor('#f8fafc' if r % 2 == 0 else 'white')
            
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"performance_{timestamp}.png"
    filepath = OUTPUT_DIR / filename
    
    save_figure(fig, filepath)
    return str(filepath)

async def run_snapshot_pipeline():
    """Run full snapshot generation sequence"""
    # In a real scenario, this would use current filter context
    # For now, we use a default range
    today = datetime.now().strftime("%Y-%m-%d")
    first_of_month = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    
    # Get all active branches
    branches_df = run_query("SELECT shop_id FROM tblDefShops WHERE shop_id IS NOT NULL")
    branch_ids = branches_df['shop_id'].tolist()
    
    try:
        path = await generate_branch_performance_snapshot(first_of_month, today, branch_ids)
        print(f"Snapshot generated: {path}")
        return path
    except Exception as e:
        print(f"Error generating snapshot: {e}")
        raise e
