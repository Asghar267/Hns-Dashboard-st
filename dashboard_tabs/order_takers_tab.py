"""
Order Takers Tab Module
Handles Order Taker performance analysis
"""

import plotly.express as px
from typing import List, Optional
import streamlit as st

# Import from existing modules
from modules.database import (
    get_cached_ot_data,
    get_cached_employee_sales,
    get_cached_cashier_sales
)
from modules.utils import (
    format_currency,
    exclude_employee_names
)


class OrderTakersTab:
    """Order Takers tab functionality"""
    
    def __init__(self, start_date: str, end_date: str, selected_branches: List[int], data_mode: str):
        self.start_date = start_date
        self.end_date = end_date
        self.selected_branches = selected_branches
        self.data_mode = data_mode
        
        # Fetch data
        self.df_ot = get_cached_ot_data(start_date, end_date, selected_branches, data_mode)
        self.df_employee_sales = get_cached_employee_sales(start_date, end_date, selected_branches)
        self.df_cashier_sales = get_cached_cashier_sales(start_date, end_date, selected_branches, data_mode)
        
        # Exclude non-attributed rows
        self.df_ot = exclude_employee_names(self.df_ot, "employee_name")
        self.df_employee_sales = exclude_employee_names(self.df_employee_sales, "employee_name")
        
    def render_order_takers(self):
        """Render the Order Takers dashboard"""
        if self.df_ot.empty:
            st.info("ℹ️ No OT data available")
            return
            
        # Summary metrics
        self._render_summary_metrics()

        st.markdown("---")

        # Cashier/Counter Cashier Sales
        self._render_cashier_sales()

        st.markdown("---")
        
        # Top performers
        st.subheader("🏆 Top 10 Performers")
        self._render_top_performers()
        
        st.markdown("---")
        
        # Detailed table with search
        st.subheader("📋 All Order Takers")
        self._render_detailed_table()
        
        # Export

    def _render_summary_metrics(self):
        """Render summary metrics for Order Takers"""
        total_ot_sales = self.df_ot['total_sale'].sum()
        unique_ots = self.df_ot['employee_id'].nunique()
        avg_sale_per_ot = total_ot_sales / unique_ots if unique_ots > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total OT Sales", format_currency(total_ot_sales))
        col2.metric("Active OTs", f"{unique_ots:,}")
        col3.metric("Avg per OT", format_currency(avg_sale_per_ot))

    def _render_cashier_sales(self):
        """Render cashier and counter cashier sales from Candelahns OT data."""
        df_cashier = self.df_cashier_sales.copy()

        st.subheader("Cashier Sales (Candelahns)")
        if df_cashier.empty:
            st.info("No cashier records found in the selected date range.")
            return

        total_cashier_sales = df_cashier['total_sale'].sum()
        unique_cashiers = df_cashier['employee_id'].nunique()
        col1, col2 = st.columns(2)
        col1.metric("Total Cashier Sales", format_currency(total_cashier_sales))
        col2.metric("Cashiers", f"{unique_cashiers:,}")

        df_cashier_sorted = df_cashier.sort_values('total_sale', ascending=False)
        display_cashier = df_cashier_sorted.copy()
        display_cashier['total_sale'] = display_cashier['total_sale'].apply(lambda x: format_currency(x))
        cols = [c for c in ["shop_name", "employee_id", "employee_code", "employee_name", "total_sale"] if c in display_cashier.columns]
        if cols:
            display_cashier = display_cashier[cols]
        self._render_table(display_cashier, width="stretch", height=320)


    def _render_top_performers(self):
        """Render top 10 performers chart"""
        df_ot_sorted = self.df_ot.sort_values('total_sale', ascending=False).head(10)
        
        fig = px.bar(
            df_ot_sorted,
            x='total_sale',
            y='employee_name',
            orientation='h',
            title="Top 10 Order Takers by Sales",
            labels={'total_sale': 'Sales (PKR)', 'employee_name': 'Order Taker'},
            color='total_sale',
            color_continuous_scale='Blues',
            text='total_sale'
        )
        
        # Add value labels inside bars
        fig.update_traces(
            texttemplate=' %{text:,.0f}',
            textposition='inside',
            textfont_size=11,
            textfont_color='white',
            insidetextanchor='middle'
        )
        
        fig.update_layout(
            showlegend=False, 
            height=500,
            xaxis_title="Sales (PKR)",
            yaxis_title="Order Taker"
        )
        
        st.plotly_chart(fig, width="stretch")

    def _render_detailed_table(self):
        """Render detailed table with search functionality"""
        search = st.text_input("🔍 Search by name", "")
        if search:
            df_ot_filtered = self.df_ot[
                self.df_ot['employee_name'].str.contains(search, case=False, na=False)
            ]
        else:
            df_ot_filtered = self.df_ot
        
        # Format for display
        display_ot = df_ot_filtered.copy()
        display_ot['total_sale'] = display_ot['total_sale'].apply(lambda x: format_currency(x))
        cols = [c for c in ["shop_name", "employee_id", "employee_code", "employee_name", "total_sale"] if c in display_ot.columns]
        if cols:
            display_ot = display_ot[cols]
        
        self._render_table(display_ot, width="stretch")

    def _render_table(self, data, width: str = "stretch", height: Optional[int] = None, hide_index: bool = True):
        """Consistent dataframe rendering for readability across the dashboard."""
        kwargs = {
            "width": width,
            "hide_index": hide_index
        }
        if height is not None:
            kwargs["height"] = height
        st.dataframe(data, **kwargs)
