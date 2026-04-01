"""
Visualization Module
Advanced charts: Gauges, Waterfall, Heatmaps, Sankey, Forecasts
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Optional

# ========================
# GAUGE CHARTS
# ========================
def create_achievement_gauge(achievement: float, title: str) -> go.Figure:
    """Create a gauge chart for achievement percentage"""
    
    # Determine color based on achievement
    if achievement >= 100:
        color = "#28a745"  # Green
    elif achievement >= 70:
        color = "#ffc107"  # Yellow
    else:
        color = "#dc3545"  # Red
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=achievement,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20}},
        delta={'reference': 100, 'increasing': {'color': "green"}},
        number={'suffix': "%", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [None, 150], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#ffebee'},
                {'range': [50, 70], 'color': '#fff9c4'},
                {'range': [70, 100], 'color': '#e8f5e9'},
                {'range': [100, 150], 'color': '#c8e6c9'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'family': "Arial"}
    )
    
    return fig

# ========================
# WATERFALL CHART
# ========================
def create_waterfall_chart(df_branch: pd.DataFrame) -> go.Figure:
    """Create waterfall chart for target breakdown"""
    
    if df_branch.empty:
        return go.Figure()
    
    # Prepare data
    branches = df_branch['shop_name'].tolist()
    sales = df_branch['total_Nt_amount'].tolist()
    
    # Calculate cumulative
    cumulative = [0]
    for sale in sales:
        cumulative.append(cumulative[-1] + sale)
    
    # Targets may not be present in some contexts; keep chart resilient.
    if "Monthly_Target" in df_branch.columns:
        _ = df_branch["Monthly_Target"].sum()
    
    # Create waterfall
    fig = go.Figure()
    
    # Add bars for each branch
    for i, (branch, sale) in enumerate(zip(branches, sales)):
        fig.add_trace(go.Waterfall(
            name=branch,
            orientation="v",
            measure=["relative"],
            x=[branch],
            y=[sale],
            text=[sale],
            textposition='inside',
            texttemplate='%{text:,.0f}',
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": "#dc3545"}},
            increasing={"marker": {"color": "#28a745"}},
            totals={"marker": {"color": "#1f77b4"}},
        ))
    
    # Add total
    fig.add_trace(go.Waterfall(
        name="Total",
        orientation="v",
        measure=["total"],
        x=["Total"],
        y=[sum(sales)],
        text=[sum(sales)],
        textposition='inside',
        texttemplate='%{text:,.0f}',
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        totals={"marker": {"color": "#1f77b4"}},
    ))
    
    fig.update_layout(
        title="Sales Contribution by Branch",
        showlegend=False,
        height=500,
        xaxis_title="Branch",
        yaxis_title="Sales (PKR)",
        yaxis=dict(tickformat=',.0f')
    )
    
    return fig

# ========================
# HEATMAP
# ========================
def create_heatmap(df_branch: pd.DataFrame) -> go.Figure:
    """Create heatmap for branch performance metrics"""
    
    if df_branch.empty:
        return go.Figure()
    
    # Prepare data
    metrics = ['total_Nt_amount', 'Monthly_Target', 'Achievement_%']
    metric_labels = ['Current Sales', 'Target', 'Achievement %']
    
    # Normalize data for heatmap
    data = []
    for metric in metrics:
        if metric in df_branch.columns:
            values = df_branch[metric].values
            # Normalize to 0-100 scale for better visualization
            if metric == 'Achievement_%':
                normalized = values
            else:
                max_val = values.max()
                normalized = (values / max_val * 100) if max_val > 0 else values
            data.append(normalized)
        else:
            data.append(np.zeros(len(df_branch)))
    
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=df_branch['shop_name'],
        y=metric_labels,
        colorscale='RdYlGn',
        text=data,
        texttemplate='%{text:.1f}',
        textfont={"size": 12},
        colorbar=dict(title="Score")
    ))
    
    fig.update_layout(
        title="Branch Performance Heatmap",
        xaxis_title="Branch",
        yaxis_title="Metric",
        height=400
    )
    
    return fig

# ========================
# SANKEY DIAGRAM
# ========================
def create_sankey_diagram(df_order_types: pd.DataFrame) -> go.Figure:
    """Create Sankey diagram for order flow"""
    
    if df_order_types.empty:
        return go.Figure()
    
    # Prepare nodes
    order_types = df_order_types['order_type'].tolist()
    sales = df_order_types['total_sales'].tolist()
    
    # Create nodes
    all_nodes = ['Total Sales'] + order_types
    node_colors = ['#1f77b4'] + ['#' + '%06x' % np.random.randint(0, 0xFFFFFF) for _ in order_types]
    
    # Create links
    sources = [0] * len(order_types)  # All from 'Total Sales'
    targets = list(range(1, len(order_types) + 1))
    values = sales
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color='rgba(0,0,0,0.2)'
        )
    )])
    
    fig.update_layout(
        title="Order Type Flow",
        font_size=12,
        height=500
    )
    
    return fig

# ========================
# TREND CHART
# ========================
def create_trend_chart(df_trend: pd.DataFrame, days: int) -> go.Figure:
    """Create trend analysis chart"""
    
    # This would need actual daily data
    # For now, create a placeholder
    
    fig = go.Figure()
    
    # Add trace for sales trend
    fig.add_trace(go.Scatter(
        x=list(range(days)),
        y=[100000 + i * 5000 + np.random.randint(-10000, 10000) for i in range(days)],
        mode='lines+markers',
        name='Daily Sales',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=6)
    ))
    
    # Add moving average
    ma_values = [100000 + i * 5000 for i in range(days)]
    fig.add_trace(go.Scatter(
        x=list(range(days)),
        y=ma_values,
        mode='lines',
        name='7-Day Moving Average',
        line=dict(color='#ff7f0e', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title=f"Sales Trend - Last {days} Days",
        xaxis_title="Days",
        yaxis_title="Sales (PKR)",
        yaxis=dict(tickformat=',.0f'),
        height=400,
        hovermode='x unified'
    )
    
    return fig


# ========================
# NEW: FUNCTION CONTRACTS / STUBS
# These are lightweight contracts (no plotting logic) describing the
# inputs/outputs and intended behavior for the new charts we discussed.
# Implementations should follow the docstrings below and return a
# Plotly `go.Figure`.
# ========================

def create_monthly_sales_trend(df_monthly: pd.DataFrame, periods: int = 24, rolling: Optional[int] = 3) -> go.Figure:
    """Contract: Monthly Sales Trend

    Inputs
    - df_monthly: DataFrame with columns: period_date (datetime first-of-month), year (int), month (int), total_Nt_amount (float)
    - periods: number of months to display (default 24)
    - rolling: rolling-window for moving average (months). If None, no rolling avg.

    Output
    - go.Figure: line chart with optional area fill, markers, and rolling average trace

    Notes
    - Data should be pre-aggregated at month level (GROUP BY year, month)
    - Missing months should be filled with zeros before plotting
    - Include support for optional previous-year overlay in the calling code
    """
    # Implementation: expects df_monthly with period_date, total_Nt_amount
    if df_monthly is None or df_monthly.empty:
        return go.Figure()

    df = df_monthly.copy()
    # Ensure datetime
    if 'period_date' in df.columns:
        df['period_date'] = pd.to_datetime(df['period_date'])
    else:
        # Try to construct from year/month
        if 'year' in df.columns and 'month' in df.columns:
            df['period_date'] = pd.to_datetime(df.apply(lambda r: f"{int(r['year'])}-{int(r['month']):02d}-01", axis=1))
        else:
            return go.Figure()

    df = df.sort_values('period_date')

    # Limit to last `periods` entries
    if len(df) > periods:
        df = df.iloc[-periods:]

    x = df['period_date']
    y = df['total_Nt_amount'] if 'total_Nt_amount' in df.columns else df.iloc[:, -1]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='lines+markers',
        name='Sales',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        hovertemplate='%{x|%b %Y}: PKR %{y:,.0f}<extra></extra>'
    ))

    # Rolling average
    if rolling and rolling > 1:
        ma = y.rolling(window=rolling, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=x,
            y=ma,
            mode='lines',
            name=f'{rolling}-period MA',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            hovertemplate='%{x|%b %Y}: PKR %{y:,.0f}<extra></extra>'
        ))

    # Layout
    fig.update_layout(
        title=f'Monthly Sales Trend - Last {len(df)} Periods',
        xaxis=dict(title='Period', rangeselector=dict(
            buttons=[
                dict(count=6, label='6M', step='month', stepmode='backward'),
                dict(count=12, label='12M', step='month', stepmode='backward'),
                dict(count=24, label='24M', step='month', stepmode='backward'),
                dict(step='all')
            ]
        ), rangeslider=dict(visible=True), type='date'),
        yaxis=dict(title='Sales (PKR)', tickformat=',.0f'),
        height=420,
        hovermode='x unified'
    )

    return fig


def create_top_categories_small_multiples(df_cat_monthly: pd.DataFrame, top_n: int = 8) -> go.Figure:
    """Contract: Top N Categories — Small Multiples

    Inputs
    - df_cat_monthly: DataFrame columns: period_date, category (line_item), total_Nt_amount
    - top_n: number of top categories (by latest period) to show

    Output
    - go.Figure containing faceted/small-multiple line charts for the top N categories

    Notes
    - Implementation should query top-N by latest month, then fetch history for those categories only.
    """
    if df_cat_monthly is None or df_cat_monthly.empty:
        return go.Figure()

    df = df_cat_monthly.copy()
    # Expect columns: period_date, category, total_Nt_amount
    if 'period_date' in df.columns:
        df['period_date'] = pd.to_datetime(df['period_date'])
    # Determine latest period
    latest = df['period_date'].max() if 'period_date' in df.columns else None
    if latest is not None:
        df_latest = df[df['period_date'] == latest]
    else:
        # Fallback: aggregate by category and pick top
        df_latest = df.groupby('category', as_index=False)['total_Nt_amount'].sum()

    top_cats = df_latest.sort_values('total_Nt_amount', ascending=False).head(top_n)
    top_list = top_cats['category'].tolist()

    df_top_hist = df[df['category'].isin(top_list)].copy()
    # Use facet plotting via plotly express
    try:
        fig = px.line(
            df_top_hist,
            x='period_date',
            y='total_Nt_amount',
            color='category',
            facet_col='category',
            facet_col_wrap=4,
            title=f'Top {len(top_list)} Categories - Time Series',
            labels={'total_Nt_amount': 'Sales (PKR)', 'period_date': 'Period'}
        )
        fig.update_traces(showlegend=False)
        fig.update_yaxes(matches=None)
        fig.update_layout(height=300 + (len(top_list)//4)*150, showlegend=False)
        return fig
    except Exception:
        # Fallback single combined plot
        fig = px.line(df_top_hist, x='period_date', y='total_Nt_amount', color='category', title='Top Categories')
        fig.update_layout(height=500)
        return fig


def create_product_time_series(df_product: pd.DataFrame, product_name: str, agg: str = 'daily', show_qty: bool = True, rolling: Optional[int] = 7) -> go.Figure:
    """Contract: Product-level Time Series (single-product explorer)

    Inputs
    - df_product: DataFrame with date, product_name, total_Nt_amount, total_qty, avg_unit_price (optional)
    - product_name: product to display
    - agg: aggregation level 'daily'|'weekly'|'monthly'
    - show_qty: whether to include qty on second axis
    - rolling: moving average window in periods

    Output
    - go.Figure with dual-axis (sales left, qty right) and optional moving averages

    Notes
    - Should be loaded on-demand (lazy) for performance
    """
    if df_product is None or df_product.empty:
        return go.Figure()

    df = df_product.copy()
    # Filter by product_name if provided in long-form
    if 'product_name' in df.columns and product_name:
        df = df[df['product_name'] == product_name]
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    elif 'day' in df.columns:
        df['date'] = pd.to_datetime(df['day'])

    df = df.sort_values('date')

    fig = go.Figure()
    # Sales trace
    if 'total_Nt_amount' in df.columns:
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['total_Nt_amount'],
            name='Sales',
            marker_color='#1f77b4',
            yaxis='y1',
            hovertemplate='%{x|%Y-%m-%d}: PKR %{y:,.0f}<extra></extra>'
        ))

    # Qty trace on secondary axis
    if show_qty and 'total_qty' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['total_qty'],
            name='Qty',
            mode='lines+markers',
            line=dict(color='#ff7f0e', width=2),
            yaxis='y2',
            hovertemplate='%{x|%Y-%m-%d}: %{y:,.0f} qty<extra></extra>'
        ))

    # Rolling average for sales
    if rolling and 'total_Nt_amount' in df.columns and rolling > 1:
        ma = df['total_Nt_amount'].rolling(window=rolling, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=ma,
            name=f'{rolling}-day MA',
            mode='lines',
            line=dict(color='#2ca02c', width=2, dash='dash'),
            hovertemplate='%{x|%Y-%m-%d}: PKR %{y:,.0f}<extra></extra>'
        ))

    # Layout with secondary y-axis
    fig.update_layout(
        title=f"{product_name} - Sales & Qty",
        xaxis=dict(title='Date'),
        yaxis=dict(title='Sales (PKR)', tickformat=',.0f'),
        yaxis2=dict(title='Quantity', overlaying='y', side='right'),
        height=450,
        hovermode='x unified'
    )

    return fig


def create_forecast_with_ci(df_history: pd.DataFrame, periods_ahead: int = 7, method: str = 'simple') -> go.Figure:
    """Contract: Forecast with Confidence Interval

    Inputs
    - df_history: DataFrame with date and total_Nt_amount (daily or weekly)
    - periods_ahead: how many future points to forecast
    - method: 'simple'|'ma'|'prophet' etc. (implementation-dependent)

    Output
    - go.Figure with historical line, forecast line, and shaded CI band

    Notes
    - Start with simple moving-average + linear trend; optionally plug in Prophet/ETS later
    - Return should include textual metrics (MAE/RMSE) accessible in the figure layout
    """
    if df_history is None or df_history.empty:
        return go.Figure()

    df = df_history.copy()
    if 'day' in df.columns:
        df['day'] = pd.to_datetime(df['day'])
        df = df.sort_values('day')
        x = df['day']
        y = df['total_Nt_amount']
    elif 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        x = df['date']
        y = df['total_Nt_amount']
    else:
        return go.Figure()

    # Try advanced method (Prophet) if requested and available
    if method == 'prophet':
        try:
            try:
                from prophet import Prophet
            except Exception:
                from fbprophet import Prophet  # type: ignore

            # Prepare dataframe for Prophet
            df_prop = pd.DataFrame({'ds': x.values, 'y': y.values})
            # Fit model (keep it minimal to avoid long runtimes)
            m = Prophet(daily_seasonality=True, weekly_seasonality=True, yearly_seasonality=False)
            with np.warnings.catch_warnings():
                np.warnings.filterwarnings('ignore')
                m.fit(df_prop)

            future = m.make_future_dataframe(periods=periods_ahead)
            fcst = m.predict(future)

            # Build figure
            hist_dates = df_prop['ds']
            hist_vals = df_prop['y']

            fcst_future = fcst[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].iloc[-periods_ahead:]

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist_dates, y=hist_vals, mode='lines+markers', name='Historical', line=dict(color='#1f77b4')))
            fig.add_trace(go.Scatter(x=fcst_future['ds'], y=fcst_future['yhat'], mode='lines+markers', name='Forecast (Prophet)', line=dict(color='#2ca02c', dash='dash')))
            fig.add_trace(go.Scatter(
                x=list(fcst_future['ds']) + list(fcst_future['ds'][::-1]),
                y=list(fcst_future['yhat_upper']) + list(fcst_future['yhat_lower'][::-1]),
                fill='toself',
                fillcolor='rgba(44,160,44,0.15)',
                line=dict(color='rgba(255,255,255,0)'),
                name='95% CI',
                showlegend=True
            ))

            # Simple in-sample MAE
            try:
                in_sample = m.predict(df_prop)
                residuals = df_prop['y'].values - in_sample['yhat'].values
                mae = float(np.mean(np.abs(residuals))) if len(residuals) > 0 else 0.0
            except Exception:
                mae = 0.0

            fig.update_layout(title='Forecast (Prophet) with 95% CI', xaxis_title='Date', yaxis_title='Sales (PKR)', height=420)
            fig.update_layout(annotations=[dict(
                x=0.99, y=0.01, xanchor='right', yanchor='bottom', xref='paper', yref='paper',
                text=f'MAE (in-sample): {mae:,.0f}', showarrow=False, font=dict(size=10, color='#6c757d')
            )])

            return fig
        except Exception:
            # Fallback to simple method if Prophet is unavailable or fails
            method = 'simple'

    # Simple linear trend forecast on last window (default / fallback)
    window = min(len(y), 30)
    y_recent = pd.to_numeric(y.iloc[-window:], errors="coerce")
    x_numeric = np.arange(len(y_recent))
    # Linear fit
    try:
        finite_mask = np.isfinite(y_recent.values)
        if int(finite_mask.sum()) >= 2:
            coefs = np.polyfit(x_numeric[finite_mask], y_recent.values[finite_mask], 1)
            slope, intercept = float(coefs[0]), float(coefs[1])
        else:
            slope = 0.0
            intercept = float(np.nanmean(y_recent.values)) if int(finite_mask.sum()) >= 1 else 0.0
    except Exception:
        slope = 0.0
        intercept = float(np.nanmean(y_recent.values)) if np.isfinite(np.nanmean(y_recent.values)) else 0.0

    # Forecast points
    future_idx = np.arange(len(y_recent), len(y_recent) + periods_ahead)
    forecast_vals = intercept + slope * future_idx

    # Estimate residual std from recent window
    residuals = y_recent.values - (intercept + slope * x_numeric)
    std = residuals.std(ddof=1) if len(residuals) > 1 else 0
    z = 1.96
    upper = forecast_vals + z * std
    lower = np.maximum(0, forecast_vals - z * std)

    # Build x axis for forecast
    last_date = x.iloc[-1]
    # Assume daily frequency if day/date
    future_dates = [last_date + pd.Timedelta(days=i+1) for i in range(periods_ahead)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers', name='Historical', line=dict(color='#1f77b4')))
    fig.add_trace(go.Scatter(x=future_dates, y=forecast_vals, mode='lines+markers', name='Forecast', line=dict(color='#2ca02c', dash='dash')))
    # CI band
    fig.add_trace(go.Scatter(
        x=future_dates + future_dates[::-1],
        y=list(upper) + list(lower[::-1]),
        fill='toself',
        fillcolor='rgba(44,160,44,0.15)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=True,
        name='95% CI'
    ))

    fig.update_layout(title='Forecast with 95% CI', xaxis_title='Date', yaxis_title='Sales (PKR)', height=420)
    # Add simple error metric
    mae = float(np.mean(np.abs(residuals))) if len(residuals) > 0 else 0.0
    fig.update_layout(annotations=[dict(
        x=0.99, y=0.01, xanchor='right', yanchor='bottom', xref='paper', yref='paper',
        text=f'MAE: {mae:,.0f}', showarrow=False, font=dict(size=10, color='#6c757d')
    )])

    return fig


def create_product_sparklines(df_products: pd.DataFrame, top_n: int = 20) -> go.Figure:
    """Contract: Product Sparklines Grid

    Inputs
    - df_products: DataFrame where each row contains product_name and a short time-series (or long-form rows with date)
    - top_n: number of products to show

    Output
    - go.Figure containing a grid/subplot of small sparklines for quick scanning

    Notes
    - Sparkline cells should be clickable to open the detailed product explorer
    """
    if df_products is None or df_products.empty:
        return go.Figure()

    df = df_products.copy()
    # Expect long-form: product_name/Product, date/day, total_Nt_amount
    # Determine product column name
    prod_col = 'Product' if 'Product' in df.columns else ('product_name' if 'product_name' in df.columns else None)
    date_col = 'date' if 'date' in df.columns else ('day' if 'day' in df.columns else ('period_date' if 'period_date' in df.columns else None))
    value_col = 'total_Nt_amount' if 'total_Nt_amount' in df.columns else None
    if not prod_col or not date_col or not value_col:
        return go.Figure()

    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col])
    df_latest = df[df[date_col] == df[date_col].max()]
    top_products = df_latest.groupby(prod_col)[value_col].sum().sort_values(ascending=False).head(top_n).index.tolist()

    df_top = df[df[prod_col].isin(top_products)].copy()

    # Create subplots grid
    from plotly.subplots import make_subplots
    cols = 4
    rows = (len(top_products) + cols - 1) // cols
    fig = make_subplots(rows=rows, cols=cols, shared_xaxes=False, shared_yaxes=False,
                        subplot_titles=top_products)

    prod_index = {p: i for i, p in enumerate(top_products)}
    for p in top_products:
        sub = df_top[df_top[prod_col] == p].sort_values(date_col)
        r = prod_index[p] // cols + 1
        c = prod_index[p] % cols + 1
        fig.add_trace(go.Scatter(x=sub[date_col], y=sub[value_col], mode='lines', showlegend=False), row=r, col=c)
        # small marker for last value
        if not sub.empty:
            fig.add_trace(go.Scatter(x=[sub[date_col].iloc[-1]], y=[sub[value_col].iloc[-1]], mode='markers', marker=dict(size=6), showlegend=False), row=r, col=c)

    fig.update_layout(height=120 * rows + 100, title=f'Top {len(top_products)} Product Sparklines')
    # Tidy up axes
    for i in range(1, rows * cols + 1):
        axis_x = f'xaxis{i}'
        axis_y = f'yaxis{i}'
        if axis_x in fig['layout']:
            fig['layout'][axis_x]['showticklabels'] = False
        if axis_y in fig['layout']:
            fig['layout'][axis_y]['showticklabels'] = False

    return fig

# ========================
# FORECAST CHART
# ========================
def create_forecast_chart(df_sales: pd.DataFrame) -> go.Figure:
    """Create sales forecast using simple moving average"""
    
    # Placeholder implementation
    # In production, use actual time series forecasting
    
    historical_days = 30
    forecast_days = 7
    
    # Generate sample data
    historical = [100000 + i * 3000 + np.random.randint(-8000, 8000) for i in range(historical_days)]
    
    # Simple forecast (average of last 7 days + trend)
    last_week_avg = np.mean(historical[-7:])
    trend = (historical[-1] - historical[-8]) / 7
    forecast = [last_week_avg + trend * i for i in range(1, forecast_days + 1)]
    
    # Confidence interval
    std = np.std(historical[-7:])
    upper_bound = [f + 1.96 * std for f in forecast]
    lower_bound = [max(0, f - 1.96 * std) for f in forecast]
    
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=list(range(historical_days)),
        y=historical,
        mode='lines+markers',
        name='Historical Sales',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=4)
    ))
    
    # Forecast
    forecast_x = list(range(historical_days, historical_days + forecast_days))
    fig.add_trace(go.Scatter(
        x=forecast_x,
        y=forecast,
        mode='lines+markers',
        name='Forecast',
        line=dict(color='#2ca02c', width=2, dash='dash'),
        marker=dict(size=6, symbol='diamond')
    ))
    
    # Confidence interval
    fig.add_trace(go.Scatter(
        x=forecast_x + forecast_x[::-1],
        y=upper_bound + lower_bound[::-1],
        fill='toself',
        fillcolor='rgba(44, 160, 44, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='95% Confidence Interval',
        showlegend=True
    ))
    
    fig.update_layout(
        title="7-Day Sales Forecast",
        xaxis_title="Days",
        yaxis_title="Sales (PKR)",
        yaxis=dict(tickformat=',.0f'),
        height=400,
        hovermode='x unified'
    )
    
    return fig

# ========================
# COMPARISON CHART
# ========================
def create_comparison_chart(df1: pd.DataFrame, df2: pd.DataFrame, labels: List[str]) -> go.Figure:
    """Create comparison chart between two periods"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name=labels[0],
        x=df1['shop_name'],
        y=df1['total_Nt_amount'],
        text=df1['total_Nt_amount'],
        textposition='inside',
        texttemplate='%{text:,.0f}',
        textfont={'color': 'white'},
        marker_color='#1f77b4'
    ))
    
    fig.add_trace(go.Bar(
        name=labels[1],
        x=df2['shop_name'],
        y=df2['total_Nt_amount'],
        text=df2['total_Nt_amount'],
        textposition='inside',
        texttemplate='%{text:,.0f}',
        textfont={'color': 'white'},
        marker_color='#ff7f0e'
    ))
    
    fig.update_layout(
        title=f"Branch Sales Comparison: {labels[0]} vs {labels[1]}",
        xaxis_title="Branch",
        yaxis_title="Sales (PKR)",
        yaxis=dict(tickformat=',.0f'),
        barmode='group',
        height=500
    )
    
    return fig
