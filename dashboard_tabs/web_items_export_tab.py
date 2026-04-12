"""
Web Items Export Tab

Runs a fixed query to export web items (iswebitem=1) into Excel.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.connection_cloud import DatabaseConfig
from modules.database import pool
from modules.utils import export_to_excel


WEB_ITEMS_QUERY = """
select
  pi.Product_item_ID,
  p.Product_code,
  p.item_name,
  p.Product_ID
FROM tblDefProducts p
INNER JOIN tblProductItem pi
  ON p.Product_ID = pi.Product_ID
WHERE p.iswebitem = 1
"""


@st.cache_data(ttl=int(getattr(DatabaseConfig, "CACHE_TTL", 300)))
def _load_web_items_df() -> pd.DataFrame:
    conn = pool.get_connection("candelahns")
    return pd.read_sql(WEB_ITEMS_QUERY, conn)


class WebItemsExportTab:
    def render(self) -> None:
        st.header("Web Items Export")
        st.caption("Exports Product + ProductItem rows where `iswebitem = 1`.")

        with st.expander("SQL", expanded=False):
            st.code(WEB_ITEMS_QUERY.strip(), language="sql")

        run_key = "web_items_export_run"
        if st.button("Run Query", key=run_key):
            try:
                st.session_state["web_items_export_df"] = _load_web_items_df()
            except Exception as e:
                st.error(f"Query failed: {e}")
                st.session_state["web_items_export_df"] = pd.DataFrame()

        df: pd.DataFrame | None = st.session_state.get("web_items_export_df")
        if df is None:
            st.info("Click “Run Query” to load data.")
            return

        if df.empty:
            st.warning("No rows returned.")
            return

        st.dataframe(df, width="stretch", hide_index=True, height=520)

        st.download_button(
            label="Download Excel",
            data=export_to_excel(df, "web_items"),
            file_name="web_items_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="web_items_export_download",
        )

