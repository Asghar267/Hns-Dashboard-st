"""
Chef Sales Tab Module
Handles Chef Sales analysis and product performance
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional
import streamlit as st

# Optional: AgGrid for Chef Sales table only
try:
    from st_aggrid import AgGrid, GridOptionsBuilder
except Exception:
    AgGrid = None
    GridOptionsBuilder = None

# Import from existing modules
from modules.database import (
    get_cached_line_items,
    get_cached_product_monthly_sales_by_product,
    get_cached_branch_summary
)
from modules.utils import (
    format_currency,
    exclude_employee_names
)
from modules.config import SALE_CATEGORIES, QTY_CATEGORIES, HIDDEN_PRODUCTS


class ChefSalesTab:
    """Chef Sales tab functionality"""

    def __init__(self, start_date: str, end_date: str, selected_branches: List[int], data_mode: str):
        self.start_date = start_date
        self.end_date = end_date
        self.selected_branches = selected_branches
        self.data_mode = data_mode

        # Fetch data with cache-forcing version
        self.df_raw = get_cached_line_items(start_date, end_date, selected_branches, data_mode, apply_category_filters=False, cache_version=106)
        
        # Fetch Overview Total for 100% reconciliation
        self.df_overview = get_cached_branch_summary(start_date, end_date, selected_branches, data_mode, apply_category_filters=False)
        self.overview_total = self.df_overview['total_Nt_amount'].sum() if not self.df_overview.empty else 0.0
        
        # Identify Hidden vs Visible categories
        self.hidden_categories = ['Unused']
        
        # Split data
        if not self.df_raw.empty:
            self.df_hidden = self.df_raw[self.df_raw["product"].isin(self.hidden_categories)].copy()
            self.df_line_item = self.df_raw[~self.df_raw["product"].isin(self.hidden_categories)].copy()
        else:
            self.df_hidden = pd.DataFrame()
            self.df_line_item = pd.DataFrame()

    def render_chef_sales(self):
        """Render the Chef Sales dashboard"""
        if self.df_line_item.empty:
            st.info("No chef sales data available")
            return

        # Advanced filters / diagnostics
        with st.expander("Advanced Filters / Diagnostics", expanded=False):
            product_search = st.text_input("Product search", key="chef_sales_product_search")
            include_hidden = st.checkbox("Include hidden products", value=False, key="chef_sales_include_hidden")
            min_sales = st.number_input("Min total sales (PKR)", min_value=0.0, value=0.0, step=100.0)
            st.caption("Filters apply to charts and tables below.")

        # Apply filters to base data
        df_line = self.df_line_item.copy()
        if not include_hidden and HIDDEN_PRODUCTS:
            df_line = df_line[~df_line["product"].isin(HIDDEN_PRODUCTS)].copy()
        if product_search.strip():
            df_line = df_line[
                df_line["product"].astype(str).str.contains(product_search.strip(), case=False, na=False)
            ].copy()

        # Product analysis
        df_product_summary = df_line.groupby('product').agg({
            'total_qty': 'sum',
            'total_line_value_incl_tax': 'sum'
        }).reset_index()
        df_product_summary = df_product_summary.sort_values(
            'total_line_value_incl_tax', ascending=False
        )
        if min_sales > 0:
            df_product_summary = df_product_summary[
                df_product_summary["total_line_value_incl_tax"] >= float(min_sales)
            ].copy()

        # KPI row
        with st.container():
            # Calculate Reconciliation Gap
            current_chef_total = df_product_summary["total_line_value_incl_tax"].sum()
            reconciliation_gap = float(self.overview_total) - float(current_chef_total)
            
            # If gap exists (Service Charges, Taxes, Rounding), add it to summary
            if abs(reconciliation_gap) > 1.0:
                adjustment_row = pd.DataFrame([{
                    'product': 'Reconciliation Adjustment (Taxes/Service Charges)',
                    'total_qty': 0,
                    'total_line_value_incl_tax': reconciliation_gap
                }])
                df_product_summary = pd.concat([df_product_summary, adjustment_row], ignore_index=True)
            
            # Recalculate totals for KPIs
            total_sales = df_product_summary["total_line_value_incl_tax"].sum()
            total_qty = df_product_summary["total_qty"].sum()
            unique_products = df_product_summary["product"].nunique() - (1 if abs(reconciliation_gap) > 1.0 else 0)
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Sales", format_currency(total_sales))
            c2.metric("Total Qty", f"{total_qty:,.0f}")
            c3.metric("Unique Products", f"{unique_products:,}")

        # Top products
        st.subheader("Top 15 Products by Revenue")
        self._render_top_products_chart(df_product_summary)

        st.markdown("---")

        # Category breakdown
        st.subheader("Product Category Distribution")
        self._render_category_pie_chart(df_product_summary)

        st.markdown("---")

        # Detailed table
        st.subheader("All Products")
        self._render_products_table(df_product_summary)

        # Branch-wise table
        st.subheader("All Products by Branch")
        self._render_branch_products_table(df_line)

        # Hidden Categories Review
        if not self.df_hidden.empty:
            st.markdown("---")
            with st.expander("👁️ View Hidden Categories / Items (Unused & Unmapped)", expanded=False):
                st.info("The following categories are hidden from main charts and totals.")
                self._render_hidden_items_table(self.df_hidden)

        # Export
        st.markdown("---")

    def _render_top_products_chart(self, df_product_summary: pd.DataFrame):
        """Render top products bar chart"""
        top_products = df_product_summary.head(15)
        fig = px.bar(
            top_products,
            x='total_line_value_incl_tax',
            y='product',
            orientation='h',
            title="Top 15 Products",
            labels={
                'total_line_value_incl_tax': 'Revenue (PKR)',
                'product': 'Product'
            },
            color='total_line_value_incl_tax',
            color_continuous_scale='Greens',
            text='total_line_value_incl_tax'
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
            height=600,
            xaxis_title="Revenue (PKR)",
            yaxis_title="Product"
        )

        st.plotly_chart(fig, width="stretch")

    def _render_category_pie_chart(self, df_product_summary: pd.DataFrame):
        """Render category distribution pie chart"""
        top_products = df_product_summary.head(10)
        fig_pie = px.pie(
            top_products,
            values='total_line_value_incl_tax',
            names='product',
            title="Revenue Distribution - Top 10 Products"
        )
        st.plotly_chart(fig_pie, width="stretch")

    def _render_products_table(self, df_product_summary: pd.DataFrame):
        """Render products table"""
        # Format for display
        display_products = df_product_summary.copy()
        display_products['total_qty'] = display_products['total_qty'].apply(lambda x: f"{x:,.0f}")
        display_products['total_line_value_incl_tax'] = display_products['total_line_value_incl_tax'].apply(
            lambda x: format_currency(x)
        )

        if AgGrid and GridOptionsBuilder:
            gb = GridOptionsBuilder.from_dataframe(display_products)
            gb.configure_default_column(filter=True, sortable=True, resizable=True)
            gb.configure_grid_options(enableRangeSelection=True)
            grid_options = gb.build()
            AgGrid(
                display_products,
                gridOptions=grid_options,
                height=520,
                width="100%",
                enable_enterprise_modules=True,
                theme="streamlit",
            )
        else:
            self._render_table(display_products, width="stretch")

    def _render_branch_products_table(self, df_line: pd.DataFrame):
        """Render branch-wise products table"""
        display_branch_products = df_line.copy()
        display_branch_products = display_branch_products.rename(
            columns={
                'shop_name': 'Branch',
                'product': 'Product',
                'total_qty': 'Total Qty',
                'total_line_value_incl_tax': 'Total Sales'
            }
        )
        display_branch_products['Total Qty'] = display_branch_products['Total Qty'].apply(lambda x: f"{x:,.0f}")
        display_branch_products['Total Sales'] = display_branch_products['Total Sales'].apply(lambda x: format_currency(x))
        display_branch_products = display_branch_products.sort_values(['Branch', 'Total Sales'], ascending=[True, False])

        self._render_table(
            display_branch_products[['Branch', 'Product', 'Total Qty', 'Total Sales']],
            width="stretch",
            height=800
        )

    def _render_reconciliation_check(self):
        """Render reconciliation check between Chef and Overview tabs"""
        if self.df_raw.empty:
            return

        st.subheader("Branch-wise Reconciliation")
        st.caption("This table shows total collection per branch to match with Sales Overview.")
        
        # Group raw data by branch (including hidden items) to match Overview total
        df_reconcile = self.df_raw.groupby('shop_name').agg({
            'total_line_value_incl_tax': 'sum'
        }).reset_index()
        
        df_reconcile = df_reconcile.rename(columns={
            'shop_name': 'Branch Name',
            'total_line_value_incl_tax': 'Total Sales (Net Incl Tax)'
        })
        
        df_reconcile = df_reconcile.sort_values('Total Sales (Net Incl Tax)', ascending=False)
        
        # Add a total row
        total_sum = df_reconcile['Total Sales (Net Incl Tax)'].sum()
        
        # Format for display
        display_df = df_reconcile.copy()
        display_df['Total Sales (Net Incl Tax)'] = display_df['Total Sales (Net Incl Tax)'].apply(format_currency)
        
        self._render_table(display_df, width="stretch")
        st.success(f"**Combined Branch Total: {format_currency(total_sum)}**")

    def _render_hidden_items_table(self, df_hidden: pd.DataFrame):
        """Render table for hidden items"""
        df_hidden_summary = df_hidden.groupby('product').agg({
            'total_qty': 'sum',
            'total_line_value_incl_tax': 'sum'
        }).sort_values('total_line_value_incl_tax', ascending=False).reset_index()
        
        df_hidden_summary = df_hidden_summary.rename(columns={
            'product': 'Category',
            'total_qty': 'Qty',
            'total_line_value_incl_tax': 'Sales'
        })
        
        df_hidden_summary['Sales'] = df_hidden_summary['Sales'].apply(format_currency)
        st.table(df_hidden_summary)

    def _render_table(self, data, width: str = "stretch", height: Optional[int] = None, hide_index: bool = True):
        """Consistent dataframe rendering for readability across the dashboard."""
        kwargs = {
            "width": width,
            "hide_index": hide_index
        }
        if height is not None:
            kwargs["height"] = height
        st.dataframe(data, **kwargs)
