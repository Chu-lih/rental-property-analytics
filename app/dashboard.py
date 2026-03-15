#!/usr/bin/env python3
"""
dashboard.py — Streamlit dashboard for Rental Property Analytics.

Usage:
    streamlit run app/dashboard.py
"""

import sys
import os

# Add project root to path so we can import db_helpers
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from db_helpers import (
    get_occupancy_kpis,
    get_payment_kpis,
    get_revenue_total,
    get_expense_total,
    get_storefront_monthly_rent,
    get_parking_monthly_revenue,
    get_unit_summary,
    get_avg_rent_by_floor,
    get_monthly_cash_flow,
    get_expense_by_category,
    get_late_payments,
    get_parking_summary,
    get_storefront_summary,
)

# ── Page Config ────────────────────────────────────────────
st.set_page_config(
    page_title="Rental Property Analytics",
    page_icon="🏠",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global font */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* KPI card styling */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    div[data-testid="stMetric"] label {
        color: #a0a0b8 !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.03em;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #e0e0f0 !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }

    /* Section headers */
    h1 { color: #e0e0f0 !important; font-weight: 700 !important; }
    h2 { color: #c8c8e0 !important; font-weight: 600 !important; border-bottom: 2px solid #3d3d5c; padding-bottom: 8px; }
    h3 { color: #b0b0d0 !important; font-weight: 600 !important; }

    /* Divider */
    hr { border-color: #3d3d5c !important; }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ── Color palette ──────────────────────────────────────────
COLORS = {
    "primary": "#6C63FF",
    "success": "#2ECC71",
    "warning": "#F39C12",
    "danger": "#E74C3C",
    "info": "#3498DB",
    "purple": "#9B59B6",
    "teal": "#1ABC9C",
    "dark": "#2C3E50",
}
CHART_COLORS = ["#6C63FF", "#2ECC71", "#F39C12", "#E74C3C", "#3498DB", "#9B59B6", "#1ABC9C"]

# ── Title ──────────────────────────────────────────────────
st.markdown("# 🏠 Rental Property Analytics")
st.markdown("*Townhouse rental · B1–4F · 9 units · 1 storefront · 5 parking spaces*")
st.divider()

# ── KPI Cards ──────────────────────────────────────────────
occ = get_occupancy_kpis()
pay = get_payment_kpis()
total_rev = get_revenue_total()
total_exp = get_expense_total()
noi = total_rev - total_exp
storefront_rent = get_storefront_monthly_rent()
parking_rev = get_parking_monthly_revenue()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Residential Revenue", f"NT${total_rev:,.0f}")
col2.metric("Storefront (Monthly)", f"NT${storefront_rent:,.0f}")
col3.metric("Parking (Monthly)", f"NT${parking_rev:,.0f}")
col4.metric("Total Expenses", f"NT${total_exp:,.0f}")

col5, col6, col7, col8 = st.columns(4)
col5.metric("Net Operating Income", f"NT${noi:,.0f}")
col6.metric("Occupancy Rate", f"{occ['occupancy_rate']}%")
col7.metric("On-Time Payment", f"{pay['on_time_pct']}%")
col8.metric("Overdue Rate", f"{pay['overdue_pct']}%")

st.divider()

# ── Tabs ───────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 Cash Flow", "🏠 Units & Rent", "📋 Payments", "🅿️ Parking & Store"])

# ── Tab 1: Cash Flow ──────────────────────────────────────
with tab1:
    cf = get_monthly_cash_flow()

    # Monthly cash flow chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=cf["month"], y=cf["revenue"], name="Revenue",
        marker_color=COLORS["success"], opacity=0.85
    ))
    fig.add_trace(go.Bar(
        x=cf["month"], y=cf["expenses"], name="Expenses",
        marker_color=COLORS["danger"], opacity=0.85
    ))
    fig.add_trace(go.Scatter(
        x=cf["month"], y=cf["net_cash_flow"], name="Net Cash Flow",
        line=dict(color=COLORS["primary"], width=3),
        mode="lines+markers", marker=dict(size=5)
    ))
    fig.update_layout(
        title="Monthly Cash Flow",
        xaxis_title="Month", yaxis_title="NT$",
        barmode="group",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(30,30,46,0.6)",
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family="Inter", color="#c8c8e0"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Expense breakdown
    exp_cat = get_expense_by_category()
    col_a, col_b = st.columns([1, 1])

    with col_a:
        fig2 = px.pie(
            exp_cat, values="Total", names="Category",
            title="Expenses by Category",
            color_discrete_sequence=CHART_COLORS,
            hole=0.45,
        )
        fig2.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(30,30,46,0.6)",
            height=360,
            font=dict(family="Inter", color="#c8c8e0"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        st.markdown("### Expense Breakdown")
        st.dataframe(exp_cat, use_container_width=True, hide_index=True)

# ── Tab 2: Units & Rent ──────────────────────────────────
with tab2:
    units = get_unit_summary()
    rent_floor = get_avg_rent_by_floor()

    # Floor filter
    floors = sorted(units["Floor"].unique())
    selected_floors = st.multiselect("Filter by Floor", floors, default=floors, key="floor_filter")
    filtered = units[units["Floor"].isin(selected_floors)]

    col_c, col_d = st.columns([1, 1])

    with col_c:
        fig3 = px.bar(
            filtered, x="Unit", y="Base Rent", color="Floor",
            title="Base Rent by Unit",
            color_continuous_scale=["#6C63FF", "#2ECC71", "#F39C12"],
            text="Base Rent",
        )
        fig3.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(30,30,46,0.6)",
            height=380,
            font=dict(family="Inter", color="#c8c8e0"),
        )
        fig3.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        st.markdown("### Avg Rent by Floor")
        st.dataframe(rent_floor, use_container_width=True, hide_index=True)
        st.markdown("### Unit Details")
        st.dataframe(filtered, use_container_width=True, hide_index=True)

# ── Tab 3: Payments ───────────────────────────────────────
with tab3:
    late = get_late_payments()

    # Payment status donut
    labels = ["On-Time", "Late/Overdue"]
    values = [int(pay["on_time"]), int(pay["overdue"])]

    col_e, col_f = st.columns([1, 1])

    with col_e:
        fig4 = go.Figure(data=[go.Pie(
            labels=labels, values=values, hole=0.5,
            marker=dict(colors=[COLORS["success"], COLORS["danger"]]),
            textinfo="label+percent",
        )])
        fig4.update_layout(
            title="Payment Status Distribution",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            height=360,
            font=dict(family="Inter", color="#c8c8e0"),
        )
        st.plotly_chart(fig4, use_container_width=True)

    with col_f:
        st.markdown("### Late / Overdue Payments")
        if late.empty:
            st.success("No late payments!")
        else:
            st.dataframe(late, use_container_width=True, hide_index=True)

# ── Tab 4: Parking & Storefront ───────────────────────────
with tab4:
    col_g, col_h = st.columns([1, 1])

    with col_g:
        st.markdown("### 🅿️ Parking Slots")
        parking = get_parking_summary()
        st.dataframe(parking, use_container_width=True, hide_index=True)

    with col_h:
        st.markdown("### 🏪 Storefront")
        store = get_storefront_summary()
        st.dataframe(store, use_container_width=True, hide_index=True)

# ── Footer ─────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center; color:#666; font-size:0.8rem;'>"
    "Rental Property Analytics · Built with Python, SQLite & Streamlit"
    "</div>",
    unsafe_allow_html=True,
)
