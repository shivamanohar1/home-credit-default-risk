import streamlit as st
import pandas as pd
from utils.page_helpers import apply_page_config, render_header, render_insights_card
from utils.data_loader import load_home_credit_data
from utils.filters import render_sidebar_filters
from utils.kpis import format_percent, format_number, format_currency
from utils.charts import create_bar_chart, create_donut_chart

apply_page_config(page_title="Contract Type Analysis", page_icon="📄")
df = load_home_credit_data()
filtered_df, _ = render_sidebar_filters(df)

render_header(
    title="Page 15: Contract Type Analysis",
    subtitle="Analyze credit applications according to loan contract structure: Cash Loans vs Revolving Lines of Credit.",
    badge="Contract Structuring",
)

contract_agg = filtered_df.groupby("NAME_CONTRACT_TYPE").agg(
    Applications=("TARGET", "count"),
    Defaults=("TARGET", "sum"),
    Default_Rate=("TARGET", "mean"),
    Avg_Credit=("AMT_CREDIT", "mean"),
    Avg_Income=("AMT_INCOME_TOTAL", "mean"),
    Avg_Annuity=("AMT_ANNUITY", "mean"),
    Avg_Leverage=("Credit to Income Ratio", "mean"),
).reset_index()
contract_agg["Default Rate %"] = (contract_agg["Default_Rate"] * 100).round(2)

cash_row = contract_agg[contract_agg["NAME_CONTRACT_TYPE"] == "Cash loans"]
revolv_row = contract_agg[contract_agg["NAME_CONTRACT_TYPE"] == "Revolving loans"]

cash_apps = cash_row["Applications"].iloc[0] if not cash_row.empty else 0
revolv_apps = revolv_row["Applications"].iloc[0] if not revolv_row.empty else 0
cash_dr = cash_row["Default Rate %"].iloc[0] if not cash_row.empty else 0.0
revolv_dr = revolv_row["Default Rate %"].iloc[0] if not revolv_row.empty else 0.0

# Exact 4 KPI Cards from Projects.ipynb
c1, c2, c3, c4 = st.columns(4)
c1.metric("Cash Loan Applications", format_number(cash_apps), "Term Installment Loans")
c2.metric("Revolving Loan Applications", format_number(revolv_apps), "Credit Line Drawdowns")
c3.metric("Cash Loan Default Rate", format_percent(cash_dr), "Term Loan Risk", delta_color="inverse")
c4.metric("Revolving Loan Default Rate", format_percent(revolv_dr), "Credit Line Risk")

st.divider()

# Visualizations Row 1: Applications by Contract Type & Default Rate by Contract Type
st.subheader("📄 Application Volume & Default Propensity")
ct1, ct2 = st.columns(2)
with ct1:
    fig_cdonut = create_donut_chart(contract_agg, names_col="NAME_CONTRACT_TYPE", values_col="Applications", title="Applications by Contract Type")
    st.plotly_chart(fig_cdonut, use_container_width=True)

with ct2:
    fig_cdr = create_bar_chart(contract_agg, x_col="NAME_CONTRACT_TYPE", y_col="Default Rate %", title="Default Rate by Contract Type", color_col="NAME_CONTRACT_TYPE")
    st.plotly_chart(fig_cdr, use_container_width=True)

# Visualizations Row 2: Average Credit by Contract Type & Average Annuity by Contract Type
st.subheader("💳 Loan Sizing & Installment Terms")
ct3, ct4 = st.columns(2)
with ct3:
    fig_ccrd = create_bar_chart(contract_agg, x_col="NAME_CONTRACT_TYPE", y_col="Avg_Credit", title="Average Credit by Contract Type", color_col="NAME_CONTRACT_TYPE")
    st.plotly_chart(fig_ccrd, use_container_width=True)

with ct4:
    fig_cann = create_bar_chart(contract_agg, x_col="NAME_CONTRACT_TYPE", y_col="Avg_Annuity", title="Average Annuity by Contract Type", color_col="NAME_CONTRACT_TYPE")
    st.plotly_chart(fig_cann, use_container_width=True)

# Visualizations Row 3: Average Income by Contract Type & Credit-to-Income Ratio by Contract Type
st.subheader("💰 Income & Leverage Multiples across Contracts")
ct5, ct6 = st.columns(2)
with ct5:
    fig_cinc = create_bar_chart(contract_agg, x_col="NAME_CONTRACT_TYPE", y_col="Avg_Income", title="Average Income by Contract Type", color_col="NAME_CONTRACT_TYPE")
    st.plotly_chart(fig_cinc, use_container_width=True)

with ct6:
    fig_clev = create_bar_chart(contract_agg, x_col="NAME_CONTRACT_TYPE", y_col="Avg_Leverage", title="Credit-to-Income Ratio by Contract Type", color_col="NAME_CONTRACT_TYPE")
    st.plotly_chart(fig_clev, use_container_width=True)

# Comparison Table from Projects.ipynb
st.subheader("📋 Contract Performance Comparison Matrix")
disp_con = contract_agg.copy()
disp_con["Applications"] = disp_con["Applications"].apply(lambda v: f"{v:,}")
disp_con["Defaults"] = disp_con["Defaults"].apply(lambda v: f"{v:,}")
disp_con["Default Rate"] = disp_con["Default Rate %"].apply(lambda v: f"{v:.2f}%")
disp_con["Avg Credit"] = disp_con["Avg_Credit"].apply(lambda v: format_currency(v))
disp_con["Avg Income"] = disp_con["Avg_Income"].apply(lambda v: format_currency(v))
disp_con["Avg Annuity"] = disp_con["Avg_Annuity"].apply(lambda v: format_currency(v))
disp_con["Avg Leverage"] = disp_con["Avg_Leverage"].apply(lambda v: f"{v:.2f}x")
disp_con = disp_con[["NAME_CONTRACT_TYPE", "Applications", "Defaults", "Default Rate", "Avg Credit", "Avg Income", "Avg Annuity", "Avg Leverage"]]

st.dataframe(disp_con, use_container_width=True, hide_index=True)

if not contract_agg.empty:
    render_insights_card([
        "**Cash Loans Dominance**: Over 90% of requests are Cash Loans, with average ticket size of ~$627K.",
        "**Revolving Credit Safety**: Revolving Loans display lower default rates (~5.4%) due to lower overall ticket sizes and flexible drawdown utility.",
        "**Leverage Disparity**: Cash loan applicants assume nearly 3x the income leverage multiple of revolving clients.",
    ])
