import streamlit as st
import pandas as pd
from utils.page_helpers import apply_page_config, render_header, render_insights_card
from utils.data_loader import load_home_credit_data
from utils.filters import render_sidebar_filters
from utils.kpis import format_currency
from utils.charts import create_bar_chart, create_histogram, create_box_plot

apply_page_config(page_title="Credit Amount Analysis", page_icon="💳")
df = load_home_credit_data()
filtered_df, _ = render_sidebar_filters(df)

render_header(
    title="Page 7: Credit Amount Analysis",
    subtitle="Analyze requested loan sizing, exposure brackets, and the relationship between credit amount and default propensity.",
    badge="Credit Sizing",
)

tot_credit = filtered_df["AMT_CREDIT"].sum() if "AMT_CREDIT" in filtered_df.columns else 0.0
avg_credit = filtered_df["AMT_CREDIT"].mean() if "AMT_CREDIT" in filtered_df.columns else 0.0
med_credit = filtered_df["AMT_CREDIT"].median() if "AMT_CREDIT" in filtered_df.columns else 0.0
max_credit = filtered_df["AMT_CREDIT"].max() if "AMT_CREDIT" in filtered_df.columns else 0.0
min_credit = filtered_df["AMT_CREDIT"].min() if "AMT_CREDIT" in filtered_df.columns else 0.0

# Exact 5 KPI Cards from Projects.ipynb
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Credit", format_currency(tot_credit))
c2.metric("Average Credit", format_currency(avg_credit))
c3.metric("Median Credit", format_currency(med_credit))
c4.metric("Maximum Credit", format_currency(max_credit))
c5.metric("Minimum Credit", format_currency(min_credit))

st.divider()

# Credit Groups Aggregation
c_group_order = ["Below 100K", "100K–300K", "300K–500K", "500K–700K", "700K–1M", "Above 1M"]
if "Credit Group" in filtered_df.columns:
    crd_agg = filtered_df.groupby("Credit Group", observed=False).agg(
        Customers=("TARGET", "count"),
        Defaults=("TARGET", "sum"),
        Default_Rate=("TARGET", "mean"),
    ).reindex(c_group_order).dropna().reset_index()
    crd_agg["Default Rate %"] = (crd_agg["Default_Rate"] * 100).round(2)

# Visualizations Row 1: Credit Amount Distribution & Credit Amount by TARGET
st.subheader("💳 Credit Distribution & Target Comparison")
cr1, cr2 = st.columns(2)
with cr1:
    fig_chist = create_histogram(filtered_df[filtered_df["AMT_CREDIT"] <= 2000000], col="AMT_CREDIT", nbins=40, title="Credit Amount Distribution (Under $2M)", color_by="Target Label")
    st.plotly_chart(fig_chist, use_container_width=True)

with cr2:
    fig_cbox = create_box_plot(filtered_df[filtered_df["AMT_CREDIT"] <= 2000000], x_col="Target Label", y_col="AMT_CREDIT", title="Credit Amount by TARGET")
    st.plotly_chart(fig_cbox, use_container_width=True)

# Visualizations Row 2: Default Rate by Credit Range & Average Credit by Gender
st.subheader("📊 Default Rates by Loan Size & Gender")
cr3, cr4 = st.columns(2)
with cr3:
    fig_cdr = create_bar_chart(crd_agg, x_col="Credit Group", y_col="Default Rate %", title="Default Rate by Credit Range")
    st.plotly_chart(fig_cdr, use_container_width=True)

with cr4:
    if "CODE_GENDER" in filtered_df.columns:
        gender_crd = filtered_df[filtered_df["CODE_GENDER"] != "XNA"].groupby("CODE_GENDER")["AMT_CREDIT"].mean().reset_index()
        fig_gc = create_bar_chart(gender_crd, x_col="CODE_GENDER", y_col="AMT_CREDIT", title="Average Credit by Gender", color_col="CODE_GENDER")
        st.plotly_chart(fig_gc, use_container_width=True)

# Visualizations Row 3: Credit by Income Type & Credit by Education
st.subheader("💼 Credit by Income Stream & Education Level")
cr5, cr6 = st.columns(2)
with cr5:
    if "NAME_INCOME_TYPE" in filtered_df.columns:
        inc_crd = filtered_df.groupby("NAME_INCOME_TYPE")["AMT_CREDIT"].mean().reset_index().sort_values("AMT_CREDIT", ascending=False).head(5)
        fig_ic = create_bar_chart(inc_crd, x_col="NAME_INCOME_TYPE", y_col="AMT_CREDIT", title="Credit by Income Type")
        st.plotly_chart(fig_ic, use_container_width=True)

with cr6:
    if "NAME_EDUCATION_TYPE" in filtered_df.columns:
        edu_crd = filtered_df.groupby("NAME_EDUCATION_TYPE")["AMT_CREDIT"].mean().reset_index().sort_values("AMT_CREDIT", ascending=False)
        fig_ec = create_bar_chart(edu_crd, x_col="NAME_EDUCATION_TYPE", y_col="AMT_CREDIT", title="Credit by Education")
        st.plotly_chart(fig_ec, use_container_width=True)

# Visualizations Row 4: Credit by Contract Type
st.subheader("📄 Credit by Contract Type")
if "NAME_CONTRACT_TYPE" in filtered_df.columns:
    con_crd = filtered_df.groupby("NAME_CONTRACT_TYPE")["AMT_CREDIT"].mean().reset_index()
    fig_con_crd = create_bar_chart(con_crd, x_col="NAME_CONTRACT_TYPE", y_col="AMT_CREDIT", title="Credit by Contract Type", color_col="NAME_CONTRACT_TYPE")
    st.plotly_chart(fig_con_crd, use_container_width=True)

if not filtered_df.empty:
    render_insights_card([
        f"**Core Ticket Size**: Median credit issued is **{format_currency(med_credit)}**, with 300K–700K representing the primary volume segment.",
        "**Small Loan Hazard**: Micro-loans (Below 100K) exhibit higher default rates (~11%), frequently representing emergency distress borrowing.",
        "**Commercial Stability**: Large loans (Above $1M) display lower default rates (~5.5%), primarily secured by established commercial borrowers.",
    ])
