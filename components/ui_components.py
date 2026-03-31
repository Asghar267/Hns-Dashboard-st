"""
UI Components
Reusable UI components for the dashboard
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional
import streamlit as st


class MetricsCard:
    """Reusable metrics card component"""
    
    @staticmethod
    def render_metric_card(label: str, value: str, delta: Optional[str] = None, 
                          delta_color: str = "normal", width: str = "small"):
        """Render a single metric card"""
        st.metric(
            label=label,
            value=value,
            delta=delta,
            delta_color=delta_color
        )

    @staticmethod
    def render_metric(label: str, value: str, delta: Optional[str] = None):
        """Alias for render_metric_card for simpler usage"""
        st.metric(label=label, value=value, delta=delta)
    
    @staticmethod
    def render_summary_metrics(metrics: List[Dict]):
        """Render multiple metrics in a row with enhanced premium styling"""
        cols = st.columns(len(metrics))
        for i, metric in enumerate(metrics):
            with cols[i]:
                # Determine accent color based on label/value
                val_color = "#14b8a6"  # Default Teal
                label_lower = metric['label'].lower()
                val_str = str(metric['value']).replace('%', '').replace(',', '').replace('PKR', '').strip()
                
                try:
                    val_num = float(val_str)
                except:
                    val_num = 0

                if 'achievement' in label_lower:
                    if val_num >= 100: val_color = "#22c55e"
                    elif val_num >= 70: val_color = "#f59e0b"
                    else: val_color = "#ef4444"
                elif 'remaining' in label_lower:
                    if val_num <= 0: val_color = "#22c55e"
                    else: val_color = "#ef4444"
                
                st.markdown(f"""
                    <div style="
                        background: var(--background-color, #ffffff);
                        padding: 1.25rem 1.5rem;
                        border-radius: 14px;
                        border: 1px solid var(--border-color, #e2e8f0);
                        border-top: 4px solid {val_color};
                        box-shadow: 0 1px 4px rgba(15,23,42,0.06);
                        margin-bottom: 0.75rem;
                    ">
                        <div style="font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; color: #64748b; margin-bottom: 0.5rem;">
                            {metric['label']}
                        </div>
                        <div style="font-size: 1.75rem; font-weight: 800; color: var(--text-color, #0f172a); letter-spacing: -0.03em; line-height: 1.1;">
                            {metric['value']}
                        </div>
                        <div style="margin-top: 0.75rem; height: 3px; width: 36px; background: {val_color}; border-radius: 2px;"></div>
                    </div>
                """, unsafe_allow_html=True)



class ChartComponents:
    """Reusable chart components"""
    
    @staticmethod
    def render_bar_chart(data: pd.DataFrame, x_col: str, y_col: str, title: str, 
                        color_col: Optional[str] = None, orientation: str = 'h',
                        height: int = 500):
        """Render a bar chart"""
        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            orientation=orientation,
            title=title,
            color=color_col,
            color_continuous_scale='Blues' if color_col else None,
            text=x_col if orientation == 'h' else y_col
        )
        
        if orientation == 'h':
            fig.update_traces(
                texttemplate=' %{text:,.0f}',
                textposition='inside',
                textfont_size=11,
                textfont_color='white',
                insidetextanchor='middle'
            )
        
        fig.update_layout(
            showlegend=False,
            height=height,
            xaxis_title="Sales (PKR)" if orientation == 'h' else x_col,
            yaxis_title="Product" if orientation == 'h' else y_col
        )
        
        st.plotly_chart(fig, width="stretch")
    
    @staticmethod
    def render_pie_chart(df: pd.DataFrame, value_col: str, label_col: str, title: str):
        """Render a pie chart"""
        fig = px.pie(
            df, 
            values=value_col, 
            names=label_col, 
            title=title
        )
        st.plotly_chart(fig, width="stretch")
    
    @staticmethod
    def render_line_chart(df: pd.DataFrame, value_col: str, label_col: str, title: str, color_col: Optional[str] = None):
        """Render a line chart with optional multiple series"""
        fig = px.line(
            df, 
            x=label_col, 
            y=value_col, 
            color=color_col,
            title=title
        )
        st.plotly_chart(fig, width="stretch")
    
    @staticmethod
    def render_gauge_chart(value: float, title: str, max_value: float = 100):
        """Render a gauge chart"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': title},
            gauge={
                'axis': {'range': [None, max_value]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        st.plotly_chart(fig, width="stretch")

    @staticmethod
    def render_achievement_gauge(achievement: float, title: str):
        """Render an advanced achievement gauge chart"""
        from modules.visualization import create_achievement_gauge
        fig = create_achievement_gauge(achievement, title)
        st.plotly_chart(fig, width="stretch", key=f"gauge_{title.replace(' ', '_').lower()}")

    @staticmethod
    def render_waterfall_chart(df_branch: pd.DataFrame):
        """Render a waterfall chart for branch sales contribution"""
        from modules.visualization import create_waterfall_chart
        fig = create_waterfall_chart(df_branch)
        st.plotly_chart(fig, width="stretch")

    @staticmethod
    def render_heatmap(df_branch: pd.DataFrame):
        """Render a performance heatmap for branches"""
        from modules.visualization import create_heatmap
        fig = create_heatmap(df_branch)
        st.plotly_chart(fig, width="stretch")

    @staticmethod
    def render_sankey_diagram(df_order_types: pd.DataFrame):
        """Render a Sankey diagram for order flow"""
        from modules.visualization import create_sankey_diagram
        fig = create_sankey_diagram(df_order_types)
        st.plotly_chart(fig, width="stretch")


class TableComponents:
    """Reusable table components"""
    
    @staticmethod
    def render_data_table(data: pd.DataFrame, title: str = "", width: str = "stretch",
                         height: Optional[int] = None, hide_index: bool = True,
                         column_config: Optional[Dict] = None):
        """Render a consistent dataframe table"""
        if title:
            st.subheader(title)
        
        kwargs = {
            "width": width,
            "hide_index": hide_index
        }
        if height is not None:
            kwargs["height"] = height
        if column_config is not None:
            kwargs["column_config"] = column_config
        
        st.dataframe(data, **kwargs)
    
    @staticmethod
    def render_formatted_table(data: pd.DataFrame, format_columns: Dict[str, str], 
                              title: str = "", **kwargs):
        """Render a table with formatted columns"""
        display_data = data.copy()
        
        for col, format_type in format_columns.items():
            if col in display_data.columns:
                if format_type == 'currency':
                    display_data[col] = display_data[col].apply(lambda x: f"{x:,.0f}")
                elif format_type == 'percentage':
                    display_data[col] = display_data[col].apply(lambda x: f"{x:.2f}%")
                elif format_type == 'integer':
                    display_data[col] = display_data[col].apply(lambda x: f"{x:,}")
        
        TableComponents.render_data_table(display_data, title, **kwargs)


class ExportComponents:
    """Reusable export components"""
    
    @staticmethod
    def render_export_buttons(data: pd.DataFrame, base_filename: str, title: str = "Export Options"):
        """Render export buttons for a dataset"""
        if title:
            st.subheader(title)
        
        col1 = st.columns(1)[0]
        

        with col1:
            from modules.utils import export_to_excel
            excel_data = export_to_excel(data, title)
            st.download_button(
                "📊 Download Excel",
                excel_data,
                f"{base_filename}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch"
            )

class FilterComponents:
    """Reusable filter components"""
    
    @staticmethod
    def render_search_filter(label: str, key: str) -> str:
        """Render a search input filter"""
        return st.text_input(label, key=key)
    
    @staticmethod
    def render_multiselect_filter(label: str, options: List[str], default: List[str], key: str) -> List[str]:
        """Render a multiselect filter"""
        return st.multiselect(label, options, default=default, key=key)
    
    @staticmethod
    def render_checkbox_filter(label: str, default: bool, key: str) -> bool:
        """Render a checkbox filter"""
        return st.checkbox(label, value=default, key=key)
    
    @staticmethod
    def render_date_range_filter(start_date: str, end_date: str, key_prefix: str) -> tuple:
        """Render date range filters"""
        col1, col2 = st.columns(2)
        with col1:
            new_start = st.date_input("Start Date", value=pd.to_datetime(start_date), key=f"{key_prefix}_start")
        with col2:
            new_end = st.date_input("End Date", value=pd.to_datetime(end_date), key=f"{key_prefix}_end")
        return str(new_start), str(new_end)
