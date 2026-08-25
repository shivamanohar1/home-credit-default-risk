import streamlit as st
import pandas as pd
from utils.page_helpers import apply_page_config, render_header, render_formula_card, render_insights_card
from utils.data_loader import load_home_credit_data
from utils.filters import render_sidebar_filters
from utils.kpis import calculate_home_credit_kpis, format_percent, format_number
from utils.charts import create_bar_chart, create_donut_chart

apply_page_config(page_title="Default Analysis", page_icon="🎯")
df = load_home_credit_data()
filtered_df, _ = render_sidebar_filters(df)

render_header(
    title="Page 2: Target / Default Analysis",
    subtitle="In-depth analysis of the binary TARGET variable and default propensity across core borrower dimensions.",
    badge="Target Analytics",
)

kpis = calculate_home_credit_kpis(filtered_df)

# Exact 4 KPI Cards from Projects.ipynb
c1, c2, c3, c4 = st.columns(4)
c1.metric("TARGET = 0 Customers", format_number(kpis["non_default_customers"]), "Repaid / No Difficulty")
c2.metric("TARGET = 1 Customers", format_number(kpis["default_customers"]), "Payment Difficulties", delta_color="inverse")
c3.metric("Default Rate %", format_percent(kpis["default_rate"]), "Portfolio Delinquency", delta_color="inverse")
c4.metric("Non-Default Rate %", format_percent(kpis["non_default_rate"]), "Clearance Rate")

st.divider()

# Mathematical Formula Card
render_formula_card(
    formula_name="Default Rate %",
    formula_math="Default Rate % = (Number of TARGET = 1 Customers / Total Customers) × 100",
    formula_desc="Measures the baseline probability of an applicant encountering severe repayment difficulties or defaulting on loan obligations."
)

st.divider()

# Visualizations Row 1: Target Count Bar Chart & Target Percentage Pie/Donut Chart
st.subheader("🎯 TARGET Distribution Breakdown")
d1, d2 = st.columns(2)
with d1:
    target_counts = filtered_df["Target Label"].value_counts().reset_index()
    target_counts.columns = ["Status", "Count"]
    fig_tbar = create_bar_chart(target_counts, x_col="Status", y_col="Count", title="TARGET Count Bar Chart", color_col="Status")
    st.plotly_chart(fig_tbar, use_container_width=True)

with d2:
    fig_tdonut = create_donut_chart(target_counts, names_col="Status", values_col="Count", title="TARGET Percentage Donut Chart")
    st.plotly_chart(fig_tdonut, use_container_width=True)

# Visualizations Row 2: Default Rate by Gender & Income Type
st.subheader("👤 Default Rate by Gender & Income Streams")
d3, d4 = st.columns(2)
with d3:
    if "CODE_GENDER" in filtered_df.columns:
        gender_dr = filtered_df[filtered_df["CODE_GENDER"] != "XNA"].groupby("CODE_GENDER")["TARGET"].mean().reset_index()
        gender_dr["Default Rate %"] = (gender_dr["TARGET"] * 100).round(2)
        fig_gdr = create_bar_chart(gender_dr, x_col="CODE_GENDER", y_col="Default Rate %", title="Default Rate by Gender", color_col="CODE_GENDER")
        st.plotly_chart(fig_gdr, use_container_width=True)

with d4:
    if "NAME_INCOME_TYPE" in filtered_df.columns:
        inc_dr = filtered_df.groupby("NAME_INCOME_TYPE")["TARGET"].agg(Default_Rate="mean", Count="count").reset_index()
        inc_dr = inc_dr[inc_dr["Count"] > 50].sort_values("Default_Rate", ascending=False)
        inc_dr["Default Rate %"] = (inc_dr["Default_Rate"] * 100).round(2)
        fig_idr = create_bar_chart(inc_dr, x_col="NAME_INCOME_TYPE", y_col="Default Rate %", title="Default Rate by Income Type")
        st.plotly_chart(fig_idr, use_container_width=True)

# Visualizations Row 3: Default Rate by Education & Contract Type
st.subheader("🎓 Default Rate by Education Level & Contract Type")
d5, d6 = st.columns(2)
with d5:
    if "NAME_EDUCATION_TYPE" in filtered_df.columns:
        edu_dr = filtered_df.groupby("NAME_EDUCATION_TYPE")["TARGET"].agg(Default_Rate="mean", Count="count").reset_index()
        edu_dr["Default Rate %"] = (edu_dr["Default_Rate"] * 100).round(2)
        fig_edr = create_bar_chart(edu_dr.sort_values("Default Rate %", ascending=False), x_col="NAME_EDUCATION_TYPE", y_col="Default Rate %", title="Default Rate by Education")
        st.plotly_chart(fig_edr, use_container_width=True)

with d6:
    if "NAME_CONTRACT_TYPE" in filtered_df.columns:
        con_dr = filtered_df.groupby("NAME_CONTRACT_TYPE")["TARGET"].mean().reset_index()
        con_dr["Default Rate %"] = (con_dr["TARGET"] * 100).round(2)
        fig_cdr = create_bar_chart(con_dr, x_col="NAME_CONTRACT_TYPE", y_col="Default Rate %", title="Default Rate by Contract Type", color_col="NAME_CONTRACT_TYPE")
        st.plotly_chart(fig_cdr, use_container_width=True)

if not filtered_df.empty:
    render_insights_card([
        f"**Target Imbalance**: Default applicants (TARGET = 1) represent **{format_percent(kpis['default_rate'])}** of the customer portfolio.",
        "**Education Discrimination**: Higher Education holders default at half the rate (~5.3%) of Lower Secondary applicants (~10.9%).",
        "**Gender Risk Spread**: Male applicants exhibit a ~3.1 percentage point higher default rate than female applicants.",
        "**Contract Structure**: Cash loans have a higher default rate (~8.3%) than revolving credit facilities (~5.4%).",
    ])
