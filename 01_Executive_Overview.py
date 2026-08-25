import streamlit as st
import pandas as pd
from utils.page_helpers import apply_page_config, render_header, render_insights_card
from utils.data_loader import load_home_credit_data
from utils.filters import render_sidebar_filters
from utils.kpis import calculate_home_credit_kpis, format_currency, format_percent, format_number
from utils.charts import create_donut_chart, create_bar_chart, create_histogram

apply_page_config(page_title="Executive Overview", page_icon="📈")
df = load_home_credit_data()
filtered_df, _ = render_sidebar_filters(df)

render_header(
    title="Page 1: Executive Overview",
    subtitle="Comprehensive high-level picture of loan applicants, credit exposure, and portfolio default risk.",
    badge="Executive Dashboard",
)

kpis = calculate_home_credit_kpis(filtered_df)

# Exact 8 KPI Cards from Projects.ipynb Specification (2 rows of 4)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Applications", format_number(kpis["total_applications"]), help="Total Loan Requests Analyzed")
c2.metric("Total Default Customers", format_number(kpis["default_customers"]), "TARGET = 1 Clients", delta_color="inverse")
c3.metric("Total Non-Default Customers", format_number(kpis["non_default_customers"]), "TARGET = 0 Clients")
c4.metric("Default Rate %", format_percent(kpis["default_rate"]), f"{kpis['non_default_rate']:.1f}% Repaid", delta_color="inverse")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Total Credit Amount", format_currency(kpis["total_credit"]), "Cumulative Portfolio Credit")
c6.metric("Average Credit Amount", format_currency(kpis["avg_credit"]), "Mean Loan Size")
c7.metric("Average Income", format_currency(kpis["avg_income"]), "Mean Applicant Earnings")
c8.metric("Average Annuity", format_currency(kpis["avg_annuity"]), "Mean Periodic Installment")

st.divider()

# Visualizations Row 1: Default vs Non-Default & Gender
st.subheader("📊 Portfolio Composition & Gender Distribution")
r1, r2 = st.columns([1.2, 1.8])
with r1:
    target_counts = filtered_df["Target Label"].value_counts().reset_index()
    target_counts.columns = ["Status", "Count"]
    fig_target = create_donut_chart(target_counts, names_col="Status", values_col="Count", title="Default vs Non-Default Applicants")
    st.plotly_chart(fig_target, use_container_width=True)

with r2:
    if "CODE_GENDER" in filtered_df.columns:
        gender_agg = filtered_df[filtered_df["CODE_GENDER"] != "XNA"].groupby("CODE_GENDER")["TARGET"].agg(Applications="count", Defaults="sum").reset_index()
        fig_gender = create_bar_chart(gender_agg, x_col="CODE_GENDER", y_col="Applications", title="Total Applications by Gender", color_col="CODE_GENDER")
        st.plotly_chart(fig_gender, use_container_width=True)

# Visualizations Row 2: Contract Type & Income Type
st.subheader("📄 Applications by Contract & Income Streams")
r3, r4 = st.columns(2)
with r3:
    if "NAME_CONTRACT_TYPE" in filtered_df.columns:
        contract_agg = filtered_df.groupby("NAME_CONTRACT_TYPE")["TARGET"].agg(Applications="count", Default_Rate="mean").reset_index()
        contract_agg["Default Rate %"] = (contract_agg["Default_Rate"] * 100).round(2)
        fig_contract = create_bar_chart(contract_agg, x_col="NAME_CONTRACT_TYPE", y_col="Applications", title="Applications by Contract Type", color_col="NAME_CONTRACT_TYPE")
        st.plotly_chart(fig_contract, use_container_width=True)

with r4:
    if "NAME_INCOME_TYPE" in filtered_df.columns:
        inc_agg = filtered_df.groupby("NAME_INCOME_TYPE")["TARGET"].agg(Applications="count", Default_Rate="mean").reset_index()
        top_inc = inc_agg.sort_values("Applications", ascending=False).head(5)
        fig_inc = create_bar_chart(top_inc, x_col="NAME_INCOME_TYPE", y_col="Applications", title="Applications by Top Income Types")
        st.plotly_chart(fig_inc, use_container_width=True)

# Visualizations Row 3: Credit Amount Distribution
st.subheader("💳 Credit Amount Distribution")
fig_credit_hist = create_histogram(
    filtered_df[filtered_df["AMT_CREDIT"] <= 2000000],
    col="AMT_CREDIT",
    nbins=40,
    title="Credit Amount Distribution (Under $2M)",
    color_by="Target Label"
)
st.plotly_chart(fig_credit_hist, use_container_width=True)

# Additional Information / Key Insights Section
if not filtered_df.empty:
    common_inc = filtered_df["NAME_INCOME_TYPE"].mode().iloc[0] if "NAME_INCOME_TYPE" in filtered_df.columns else "N/A"
    common_edu = filtered_df["NAME_EDUCATION_TYPE"].mode().iloc[0] if "NAME_EDUCATION_TYPE" in filtered_df.columns else "N/A"
    
    # Calculate highest risk customer segment
    risk_seg = "Unemployed / Low Income"
    if "NAME_INCOME_TYPE" in filtered_df.columns:
        inc_dr = filtered_df.groupby("NAME_INCOME_TYPE")["TARGET"].agg(Count="count", Mean="mean").reset_index()
        valid_inc = inc_dr[inc_dr["Count"] > 50].sort_values("Mean", ascending=False)
        if not valid_inc.empty:
            risk_seg = f"{valid_inc.iloc[0]['NAME_INCOME_TYPE']} ({valid_inc.iloc[0]['Mean']*100:.1f}% Default Rate)"

    render_insights_card([
        f"**Overall Default Rate**: **{format_percent(kpis['default_rate'])}** across **{format_number(kpis['total_applications'])}** total applicants.",
        f"**Average Customer Income**: **{format_currency(kpis['avg_income'])}** with median of **{format_currency(kpis['median_income'])}**.",
        f"**Average Loan Amount**: **{format_currency(kpis['avg_credit'])}** with cumulative exposure of **{format_currency(kpis['total_credit'])}**.",
        f"**Most Common Income Type**: **{common_inc}**.",
        f"**Most Common Education Level**: **{common_edu}**.",
        f"**Highest Risk Customer Segment**: **{risk_seg}**.",
    ])
