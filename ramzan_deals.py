import streamlit as st
import pandas as pd
import pyodbc
from datetime import date

st.set_page_config(layout="wide")

# ==============================
# CONFIG
# ==============================

FIXED_PRODUCT_IDS = [701,703,704,705,706,707,708,709]

SELECTED_BRANCH_IDS = [2, 3, 4, 6, 8, 10, 14]

BRANCH_NAMES = {
    2: "Khadda Main Branch",
    3: "FESTIVAL",
    4: "Rahat Commercial",
    6: "TOWER",
    8: "North Nazimabad",
    10: "MALIR",
    14: "FESTIVAL 2"
}

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=103.86.55.183,2001;"
    "DATABASE=Candelahns;"
    "UID=ReadOnlyUser;"
    "PWD=902729@Rafy;"
)

# ==============================
# DB CONNECTION
# ==============================

def get_connection():
    return pyodbc.connect(CONNECTION_STRING)

# ==============================
# LOAD PRODUCT MASTER
# ==============================

@st.cache_data
def load_product_master():
    fixed_codes = ",".join([f"'{code}'" for code in FIXED_PRODUCT_IDS])
    query = f"""
        SELECT 
            pi.Product_Item_ID,
            p.Product_code,
            p.item_name
        FROM tblDefProducts p
        INNER JOIN tblProductItem pi
            ON p.Product_ID = pi.Product_ID
        WHERE p.Product_code IN ({fixed_codes})
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ==============================
# LOAD SALES DATA
# ==============================

def get_sales_data(start_date, end_date, branch_ids):
    fixed_codes = ",".join([f"'{code}'" for code in FIXED_PRODUCT_IDS])
    branch_id_csv = ",".join(map(str, branch_ids))
    query = f"""
        SELECT  
            sh.shop_id,
            sh.shop_name,
            pi.Product_Item_ID,
            p.Product_code,
            p.item_name,
            ISNULL(SUM(sales_data.qty),0) AS total_qty,
            ISNULL(SUM(sales_data.qty * sales_data.Unit_price),0) AS total_sales
        FROM tblDefShops sh
        CROSS JOIN tblProductItem pi
        INNER JOIN tblDefProducts p 
            ON p.Product_ID = pi.Product_ID
        LEFT JOIN (
            SELECT 
                s.shop_id,
                li.Product_Item_ID,
                li.qty,
                li.Unit_price
            FROM tblSales s
            INNER JOIN tblSalesLineItems li 
                ON s.sale_id = li.sale_id
            WHERE CAST(s.sale_date AS date) BETWEEN '{start_date}' AND '{end_date}'
        ) sales_data
            ON sales_data.shop_id = sh.shop_id
            AND sales_data.Product_Item_ID = pi.Product_Item_ID
        WHERE 
            sh.shop_id IN ({branch_id_csv})
            AND p.Product_code IN ({fixed_codes})
        GROUP BY 
            sh.shop_id,
            sh.shop_name,
            pi.Product_Item_ID,  
            p.Product_code,  
            p.item_name
        ORDER BY 
            sh.shop_id,
            p.Product_code
    """

    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ==============================
# UI
# ==============================

st.title("📊 Branch & Product Sales Dashboard")

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input("Start Date", date.today().replace(day=1))

with col2:
    end_date = st.date_input("End Date", date.today())

selected_branch_ids = st.multiselect(
    "Select Branch(es)",
    options=SELECTED_BRANCH_IDS,
    default=SELECTED_BRANCH_IDS,
    format_func=lambda x: f"{x} - {BRANCH_NAMES.get(x, str(x))}"
)

if not selected_branch_ids:
    st.warning("Please select at least one branch.")
    st.stop()

product_master = load_product_master()

product_master["display"] = (
    product_master["Product_code"].astype(str)
    + " - "
    + product_master["item_name"]
)

selected_products = st.multiselect(
    "📦 Product Multi-select (by Product_code)",
    options=product_master["display"],
    default=product_master["display"]
)

selected_product_df = product_master[
    product_master["display"].isin(selected_products)
]

selected_product_ids = selected_product_df["Product_Item_ID"].tolist()

# ==============================
# GET SALES
# ==============================

sales_df = get_sales_data(start_date, end_date, selected_branch_ids)

sales_df = sales_df[
    sales_df["Product_Item_ID"].isin(selected_product_ids)
]

# ==============================
# BRANCH WISE DISPLAY (QUERY COLUMNS ONLY)
# ==============================

branch_wise_display = sales_df[
    ["shop_id", "shop_name", "Product_Item_ID", "Product_code", "item_name", "total_qty", "total_sales"]
]

# ==============================
# PRODUCT OVERALL
# ==============================

product_overall = branch_wise_display.groupby(
    ["Product_Item_ID","Product_code","item_name"],
    as_index=False
).agg({
    "total_qty":"sum",
    "total_sales":"sum"
})

# ==============================
# DISPLAY
# ==============================

st.subheader("🏬 Branch Wise Sales")

st.dataframe(
    branch_wise_display.sort_values(["shop_id","Product_code"]),
    width="stretch"
)

st.subheader("📦 Product Wise Overall Sales")

st.dataframe(
    product_overall.sort_values("Product_code"),
    width="stretch"
)

# ==============================
# SUMMARY
# ==============================

st.markdown("---")

total_sales = product_overall["total_sales"].sum()
total_qty = product_overall["total_qty"].sum()

col1, col2 = st.columns(2)

col1.metric("💰 Total Sales (PKR)", f"{total_sales:,.0f}")
col2.metric("📦 Total Quantity", f"{total_qty:,.0f}")
