import streamlit as st
import pandas as pd
from utils.page_helpers import apply_page_config, render_header, render_formula_card, render_insights_card
from utils.data_loader import load_home_credit_data
from utils.filters import render_sidebar_filters
from utils.kpis import format_percent, format_ratio
from utils.charts import create_bar_chart, create_histogram, create_scatter_plot

apply_page_config(page_title="Income vs Credit", page_icon="⚖️")
df = load_home_credit_data()
filtered_df, _ = render_sidebar_filters(df)

render_header(
    title="Page 9: Income vs Credit Analysis",
    subtitle="Determine whether borrowers are taking loans proportional to their income capacity and evaluate leverage risk.",
    badge="Leverage Ratios",
)

avg_ratio = filtered_df["Credit to Income Ratio"].mean() if "Credit to Income Ratio" in filtered_df.columns else 0.0
max_ratio = filtered_df["Credit to Income Ratio"].max() if "Credit to Income Ratio" in filtered_df.columns else 0.0

high_ratio_df = filtered_df[filtered_df["Credit to Income Ratio"] > 4.0] if "Credit to Income Ratio" in filtered_df.columns else pd.DataFrame()
high_ratio_dr = high_ratio_df["TARGET"].mean() * 100 if not high_ratio_df.empty else 0.0

# Exact 3 KPI Cards from Projects.ipynb
c1, c2, c3 = st.columns(3)
c1.metric("Average Credit-to-Income Ratio", format_ratio(avg_ratio), "Mean Multiple")
c2.metric("Highest Credit-to-Income Ratio", format_ratio(max_ratio), "Peak Leverage")
c3.metric("Default Rate for High Ratio Customers", format_percent(high_ratio_dr), "For Ratio > 4.0x", delta_color="inverse")

st.divider()

# Formula Card
render_formula_card(
    formula_name="Credit-to-Income Ratio",
    formula_math="Credit Income Ratio = AMT_CREDIT / AMT_INCOME_TOTAL",
    formula_desc="Risk tiers: Low (< 2x), Moderate (2–4x), High (4–6x), Very High (> 6x)."
)

st.divider()

# Risk Groups Aggregation
if "Credit Leverage Group" in filtered_df.columns:
    lev_agg = filtered_df.groupby("Credit Leverage Group", observed=False).agg(
        Customers=("TARGET", "count"),
        Default_Rate=("TARGET", "mean"),
    ).reset_index()
    lev_agg["Default Rate %"] = (lev_agg["Default_Rate"] * 100).round(2)

# Visualizations Row 1: Income vs Credit Scatter Plot & Credit/Income Ratio Distribution
st.subheader("⚖️ Income vs Credit & Ratio Distribution")
lv1, lv2 = st.columns(2)
with lv1:
    sample_ci = filtered_df[(filtered_df["AMT_INCOME_TOTAL"] <= 500000) & (filtered_df["AMT_CREDIT"] <= 1500000)].sample(min(2000, len(filtered_df)), random_state=42)
    fig_ciscat = create_scatter_plot(sample_ci, x_col="AMT_INCOME_TOTAL", y_col="AMT_CREDIT", color_col="Credit Leverage Group", title="Income vs Credit Scatter Plot")
    st.plotly_chart(fig_ciscat, use_container_width=True)

with lv2:
    fig_rhist = create_histogram(filtered_df[filtered_df["Credit to Income Ratio"] <= 12], col="Credit to Income Ratio", nbins=40, title="Credit/Income Ratio Distribution", color_by="Target Label")
    st.plotly_chart(fig_rhist, use_container_width=True)

# Visualizations Row 2: Default Rate vs Credit/Income Ratio & Customers by Leverage Group
st.subheader("📊 Default Rate by Leverage Bracket")
lv3, lv4 = st.columns(2)
with lv3:
    fig_ldr = create_bar_chart(lev_agg, x_col="Credit Leverage Group", y_col="Default Rate %", title="Default Rate vs Credit/Income Ratio")
    st.plotly_chart(fig_ldr, use_container_width=True)

with lv4:
    fig_lg = create_bar_chart(lev_agg, x_col="Credit Leverage Group", y_col="Customers", title="Customers by Credit Leverage Tier")
    st.plotly_chart(fig_lg, use_container_width=True)

# Visualizations Row 3: Gender-wise & Education-wise Credit/Income Ratio
st.subheader("👥 Leverage Multiples across Demographics")
lv5, lv6 = st.columns(2)
with lv5:
    if "CODE_GENDER" in filtered_df.columns:
        g_lev = filtered_df[filtered_df["CODE_GENDER"] != "XNA"].groupby("CODE_GENDER")["Credit to Income Ratio"].mean().reset_index()
        fig_glev = create_bar_chart(g_lev, x_col="CODE_GENDER", y_col="Credit to Income Ratio", title="Gender-wise Credit/Income Ratio", color_col="CODE_GENDER")
        st.plotly_chart(fig_glev, use_container_width=True)

with lv6:
    if "NAME_EDUCATION_TYPE" in filtered_df.columns:
        e_lev = filtered_df.groupby("NAME_EDUCATION_TYPE")["Credit to Income Ratio"].mean().reset_index().sort_values("Credit to Income Ratio", ascending=False)
        fig_elev = create_bar_chart(e_lev, x_col="NAME_EDUCATION_TYPE", y_col="Credit to Income Ratio", title="Education-wise Credit/Income Ratio")
        st.plotly_chart(fig_elev, use_container_width=True)

if not filtered_df.empty:
    render_insights_card([
        "**Prudent Leverage (< 2x)**: Loans under 2x annual earnings sustain lower default probability (~5.8%).",
        "**High Leverage Spike (> 6x)**: When credit requested exceeds 6x annual income, loan default risk escalates significantly.",
        "**Underwriting Policy Rule**: Maintain an internal advisory ceiling of 4.0x income on unsecured consumer loans.",
    ])
