"""
dashboard/app.py
-----------------
Streamlit analytics dashboard reading from the dbt-built DuckDB marts.
Displays revenue trends, customer LTV segments, and channel performance.
"""

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="📊",
    layout="wide",
)

DB_PATH = "data/ecommerce.duckdb"

st.markdown("""
<style>
.metric-card { background:#1a1d2e; border-radius:10px; padding:16px; text-align:center; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_data():
    if not Path(DB_PATH).exists():
        return None, None
    conn = duckdb.connect(DB_PATH, read_only=True)
    try:
        revenue = conn.execute("""
            SELECT * FROM mart_revenue_analytics
            ORDER BY order_year, order_month
        """).df()
        ltv = conn.execute("""
            SELECT * FROM mart_customer_ltv
        """).df()
        return revenue, ltv
    except Exception:
        return None, None
    finally:
        conn.close()


revenue_df, ltv_df = load_data()

st.title("📊 E-Commerce Analytics Dashboard")
st.caption("Built on dbt + DuckDB | Staging → Intermediate → Marts")

if revenue_df is None:
    st.warning("Run `python scripts/setup_and_run.py` first to build the data warehouse.")
    st.stop()

# ── KPIs ──────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue",    f"${revenue_df['gross_revenue'].sum():,.0f}")
c2.metric("Total Orders",     f"{revenue_df['total_orders'].sum():,.0f}")
c3.metric("Unique Customers", f"{ltv_df['customer_id'].nunique():,}")
c4.metric("Avg Order Value",  f"${revenue_df['avg_order_value'].mean():.2f}")

st.divider()

# ── Revenue trend ─────────────────────────────────────────────────────────────
st.subheader("Monthly Revenue Trend")
monthly = (
    revenue_df
    .groupby(["order_year", "order_month"])["gross_revenue"]
    .sum().reset_index()
)
monthly["period"] = monthly["order_year"].astype(str) + "-" + monthly["order_month"].astype(str).str.zfill(2)
fig = px.line(monthly, x="period", y="gross_revenue",
              title="Gross Revenue by Month",
              labels={"gross_revenue": "Revenue ($)", "period": "Month"})
fig.update_layout(template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# ── Channel + LTV ─────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue by Sales Channel")
    channel = revenue_df.groupby("sales_channel")["gross_revenue"].sum().reset_index()
    fig2 = px.pie(channel, values="gross_revenue", names="sales_channel",
                  title="Channel Revenue Share")
    fig2.update_layout(template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("Customer LTV Segments")
    seg = ltv_df["ltv_segment"].value_counts().reset_index()
    seg.columns = ["segment", "count"]
    fig3 = px.bar(seg, x="segment", y="count",
                  title="Customers by LTV Segment", color="segment")
    fig3.update_layout(template="plotly_dark", showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

# ── Top customers ─────────────────────────────────────────────────────────────
st.subheader("Top 10 Customers by Revenue")
top = ltv_df.nlargest(10, "total_revenue")[
    ["customer_id", "country", "ltv_segment", "total_orders",
     "total_revenue", "avg_order_value"]
].reset_index(drop=True)
st.dataframe(top, use_container_width=True)
