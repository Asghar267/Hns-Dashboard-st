"""
Shift Analysis Tab Module
Handles shift-wise sales performance analysis
"""

import pandas as pd
from typing import List, Optional
import streamlit as st
import plotly.express as px

from modules.database import get_cached_shift_sales
from modules.utils import format_currency
from modules.responsive import clamp_dataframe_height, get_responsive_context

class ShiftAnalysisTab:
    """Shift Analysis tab functionality"""
    
    def __init__(self, start_date: str, end_date: str, selected_branches: List[int], data_mode: str):
        self.start_date = start_date
        self.end_date = end_date
        self.selected_branches = selected_branches
        self.data_mode = data_mode
        self.responsive = get_responsive_context()

    def render(self):
        st.header("Shift-wise Sales Analysis")
        
        # Timezone documentation note
        st.info(
            "â° **Timezone Note**: Database time is adjusted by **+6 hours** to align with Pakistani Time (PKT). "
            "The database uses Greenland Standard Time (UTC-1), while Pakistan is UTC+5."
        )
        
        st.caption(f"Analysis Period: {self.start_date} to {self.end_date} | Mode: {self.data_mode}")
        
        df_shifts = get_cached_shift_sales(
            self.start_date, self.end_date, self.selected_branches, self.data_mode
        )
        
        if df_shifts.empty:
            st.warning("No shift data found for the selected filters.")
            return

        # Summary Metrics
        self._render_summary_metrics(df_shifts)
        
        st.markdown("---")
        
        # Create columns for charts
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_shift_distribution_chart(df_shifts)
            
        with col2:
            self._render_shift_heatmap(df_shifts)
            
        st.markdown("---")
        
        # Branch-wise Matrix
        self._render_branch_wise_summary(df_shifts)
        
        st.markdown("---")
        
        # Detailed Table
        self._render_detailed_table(df_shifts)

    def _render_summary_metrics(self, df_shifts: pd.DataFrame):
        """Render grand totals by shift"""
        summary = df_shifts.groupby('shift_name')['total_sales'].sum().reset_index()
        
        # Ensure we show all shifts even if empty
        shifts_order = ['Morning', 'Lunch', 'Dinner']
        
        cols = st.columns(3)
        for idx, shift in enumerate(shifts_order):
            shift_data = summary[summary['shift_name'] == shift]
            val = shift_data['total_sales'].iloc[0] if not shift_data.empty else 0
            
            with cols[idx]:
                st.markdown(f"""
                    <div style="padding: 1rem; border-radius: 0.5rem; background-color: #f8f9fa; border-left: 5px solid #1E88E5;">
                        <div style="color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;">Total {shift} Sales</div>
                        <div style="font-size: 1.5rem; font-weight: bold; color: #1E88E5;">{format_currency(val)}</div>
                    </div>
                """, unsafe_allow_html=True)

    def _render_shift_distribution_chart(self, df_shifts: pd.DataFrame):
        """Bar chart of shifts by branch"""
        st.subheader("Shift Distribution by Branch")
        fig = px.bar(
            df_shifts,
            x="shop_name",
            y="total_sales",
            color="shift_name",
            title="Sales by Shift and Branch",
            barmode="group",
            category_orders={"shift_name": ["Morning", "Lunch", "Dinner"]},
            color_discrete_map={
                "Morning": "#FF9800",  # Orange/Sun
                "Lunch": "#4CAF50",    # Green
                "Dinner": "#3F51B5"    # Indigo/Night
            },
            template="plotly_white"
        )
        fig.update_layout(xaxis_title="Branch", yaxis_title="Sales (PKR)")
        st.plotly_chart(fig, use_container_width=True)

    def _render_shift_heatmap(self, df_shifts: pd.DataFrame):
        """Heatmap of shifts vs branches"""
        st.subheader("Sales Heatmap (Shift vs Branch)")
        
        try:
            pivot_df = df_shifts.pivot(index="shift_name", columns="shop_name", values="total_sales").fillna(0)
            # Reorder index to logical time sequence
            available_shifts = [s for s in ['Morning', 'Lunch', 'Dinner'] if s in pivot_df.index]
            pivot_df = pivot_df.reindex(available_shifts)
            
            fig = px.imshow(
                pivot_df,
                labels=dict(x="Branch", y="Shift", color="Sales"),
                color_continuous_scale="Blues",
                aspect="auto",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("Not enough data to generate heatmap.")

    def _render_detailed_table(self, df_shifts: pd.DataFrame):
        """Detailed raw data table"""
        st.subheader("Shift Performance Details")
        
        display_df = df_shifts.copy()
        
        # Calculate percentage of branch total
        branch_totals = display_df.groupby('shop_name')['total_sales'].transform('sum')
        display_df['Branch Share %'] = (display_df['total_sales'] / branch_totals * 100).round(1).astype(str) + '%'
        
        # Format sales
        display_df['total_sales'] = display_df['total_sales'].apply(format_currency)
        
        display_df = display_df.rename(columns={
            'shop_name': 'Branch',
            'shift_name': 'Shift',
            'total_orders': 'Orders',
            'total_sales': 'Revenue'
        })
        
        height = clamp_dataframe_height(self.responsive, desktop=400, tablet=300, phone=250)
        st.dataframe(
            display_df[['Branch', 'Shift', 'Orders', 'Revenue', 'Branch Share %']], 
            height=height, 
            use_container_width=True, 
            hide_index=True
        )

    def _render_branch_wise_summary(self, df_shifts: pd.DataFrame):
        """Render a pivoted matrix of Branches vs Shifts"""
        st.subheader("Branch-wise Shift Comparison")
        
        try:
            # Pivot the data
            matrix = df_shifts.pivot(index="shop_name", columns="shift_name", values="total_sales").fillna(0)
            
            # Ensure order
            shifts_order = [s for s in ['Morning', 'Lunch', 'Dinner'] if s in matrix.columns]
            matrix = matrix[shifts_order]
            
            # Add total column
            matrix['Total'] = matrix.sum(axis=1)
            
            # Add grand total row
            total_row = matrix.sum(axis=0)
            total_row.name = "GRAND TOTAL"
            matrix = pd.concat([matrix, total_row.to_frame().T])
            
            # Formatting
            formatted_matrix = matrix.copy()
            for col in formatted_matrix.columns:
                formatted_matrix[col] = formatted_matrix[col].apply(format_currency)
                
            formatted_matrix.index.name = "Branch"
            
            st.dataframe(
                formatted_matrix,
                use_container_width=True,
                height=clamp_dataframe_height(self.responsive, desktop=450, tablet=350, phone=300)
            )
        except Exception as e:
            st.error(f"Could not generate branch-wise matrix: {e}")
