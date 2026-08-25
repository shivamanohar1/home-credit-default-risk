import streamlit as st
import pandas as pd
from utils.page_helpers import apply_page_config, render_header, render_formula_card, render_insights_card
from utils.data_loader import load_home_credit_data
from utils.filters import render_sidebar_filters
from utils.charts import create_bar_chart, create_histogram

apply_page_config(page_title="Employment Analysis", page_icon="💼")
df = load_home_credit_data()
filtered_df, _ = render_sidebar_filters(df)

render_header(
    title="Page 12: Employment Analysis",
    subtitle="Understand how employment status, work history tenure, and occupational categories influence credit risk.",
    badge="Employment Risk",
)

avg_emp_yrs = filtered_df["Employment Years"].mean() if "Employment Years" in filtered_df.columns else 0.0
common_occ = filtered_df[filtered_df["OCCUPATION_TYPE"] != "Unknown"]["OCCUPATION_TYPE"].mode().iloc[0] if not filtered_df.empty else "N/A"
common_inc = filtered_df["NAME_INCOME_TYPE"].mode().iloc[0] if "NAME_INCOME_TYPE" in filtered_df.columns else "N/A"

occ_dr = filtered_df[filtered_df["OCCUPATION_TYPE"] != "Unknown"].groupby("OCCUPATION_TYPE")["TARGET"].agg(Default_Rate="mean", Count="count").reset_index()
occ_dr = occ_dr[occ_dr["Count"] > 50].sort_values("Default_Rate", ascending=False)
highest_risk_occ = occ_dr.iloc[0]["OCCUPATION_TYPE"] if not occ_dr.empty else "N/A"
highest_risk_occ_dr = occ_dr.iloc[0]["Default_Rate"] * 100 if not occ_dr.empty else 0.0

# Exact 4 KPI Cards from Projects.ipynb
c1, c2, c3, c4 = st.columns(4)
c1.metric("Average Employment Years", f"{avg_emp_yrs:.1f} Yrs")
c2.metric("Most Common Occupation", str(common_occ)[:20])
c3.metric("Most Common Income Type", str(common_inc)[:20])
c4.metric("Highest Risk Occupation", str(highest_risk_occ)[:20], f"{highest_risk_occ_dr:.2f}% Default", delta_color="inverse")

st.divider()

render_formula_card(
    formula_name="Derived Employment Years",
    formula_math="Employment Years = abs(DAYS_EMPLOYED) / 365",
    formula_desc="Special code 365,243 is treated as NaN/Pensioner to prevent outlier skewness in tenure calculations."
)

st.divider()

# Visualizations Row 1: Employment Years Distribution & Default Rate by Employment Years
st.subheader("💼 Work Tenure & Delinquency Curve")
em1, em2 = st.columns(2)
with em1:
    fig_emhist = create_histogram(filtered_df[filtered_df["Employment Years"] <= 30], col="Employment Years", nbins=30, title="Employment Years Distribution", color_by="Target Label")
    st.plotly_chart(fig_emhist, use_container_width=True)

with em2:
    if "Employment Tier" in filtered_df.columns:
        emp_tier_agg = filtered_df.groupby("Employment Tier", observed=False)["TARGET"].agg(Total="count", Default_Rate="mean").reset_index()
        emp_tier_agg["Default Rate %"] = (emp_tier_agg["Default_Rate"] * 100).round(2)
        fig_et_dr = create_bar_chart(emp_tier_agg, x_col="Employment Tier", y_col="Default Rate %", title="Default Rate by Employment Years")
        st.plotly_chart(fig_et_dr, use_container_width=True)

# Visualizations Row 2: Applications by Income Type & Default Rate by Income Type
st.subheader("🏢 Income Streams & Default Propensity")
em3, em4 = st.columns(2)
with em3:
    inc_counts = filtered_df["NAME_INCOME_TYPE"].value_counts().reset_index()
    inc_counts.columns = ["Income Type", "Applications"]
    fig_icount = create_bar_chart(inc_counts, x_col="Income Type", y_col="Applications", title="Applications by Income Type")
    st.plotly_chart(fig_icount, use_container_width=True)

with em4:
    inc_dr_all = filtered_df.groupby("NAME_INCOME_TYPE")["TARGET"].agg(Default_Rate="mean", Count="count").reset_index()
    inc_dr_all["Default Rate %"] = (inc_dr_all["Default_Rate"] * 100).round(2)
    fig_idr = create_bar_chart(inc_dr_all.sort_values("Default Rate %", ascending=False), x_col="NAME_INCOME_TYPE", y_col="Default Rate %", title="Default Rate by Income Type")
    st.plotly_chart(fig_idr, use_container_width=True)

# Visualizations Row 3: Applications by Occupation & Default Rate by Occupation
st.subheader("🛠️ Occupation Analysis")
em5, em6 = st.columns(2)
with em5:
    if "OCCUPATION_TYPE" in filtered_df.columns:
        occ_counts = filtered_df[filtered_df["OCCUPATION_TYPE"] != "Unknown"]["OCCUPATION_TYPE"].value_counts().reset_index().head(10)
        occ_counts.columns = ["Occupation", "Applications"]
        fig_ocount = create_bar_chart(occ_counts, x_col="Occupation", y_col="Applications", orientation="h", title="Applications by Occupation (Top 10)")
        st.plotly_chart(fig_ocount, use_container_width=True)

with em6:
    occ_dr_top = occ_dr.sort_values("Default_Rate", ascending=True).tail(10)
    occ_dr_top["Default Rate %"] = (occ_dr_top["Default_Rate"] * 100).round(2)
    fig_odr = create_bar_chart(occ_dr_top, x_col="OCCUPATION_TYPE", y_col="Default Rate %", orientation="h", title="Default Rate by Occupation (Top 10 High Risk)")
    st.plotly_chart(fig_odr, use_container_width=True)

# Visualizations Row 4: Default Rate by Organization Type
st.subheader("🏭 Default Rate by Organization Type")
if "ORGANIZATION_TYPE" in filtered_df.columns:
    org_agg = filtered_df[filtered_df["ORGANIZATION_TYPE"] != "XNA"].groupby("ORGANIZATION_TYPE")["TARGET"].agg(Default_Rate="mean", Count="count").reset_index()
    org_agg = org_agg[org_agg["Count"] > 100].sort_values("Default_Rate", ascending=True).tail(15)
    org_agg["Default Rate %"] = (org_agg["Default_Rate"] * 100).round(2)
    fig_org = create_bar_chart(org_agg, x_col="ORGANIZATION_TYPE", y_col="Default Rate %", orientation="h", title="Default Rate by Organization Type (Top 15 Sectors, Min 100 Applicants)")
    st.plotly_chart(fig_org, use_container_width=True)

if not filtered_df.empty:
    render_insights_card([
        "**Job Tenure Protective Effect**: Applicants with >5 years at their current position have a 40% lower default rate than workers with <1 year tenure.",
        "**High Risk Roles**: Low-skill Laborers, Drivers, and Security guards experience default rates between ~10.5% and 12.5%.",
        "**Low Risk Roles**: Accountants, Core High-tech staff, and Executives maintain default rates below 5.5%.",
    ])
