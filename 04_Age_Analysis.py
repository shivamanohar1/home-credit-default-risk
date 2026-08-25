import streamlit as st
import pandas as pd
from utils.page_helpers import apply_page_config, render_header, render_formula_card, render_insights_card
from utils.data_loader import load_home_credit_data
from utils.filters import render_sidebar_filters
from utils.charts import create_bar_chart, create_histogram, create_line_trend

apply_page_config(page_title="Age Analysis", page_icon="🎂")
df = load_home_credit_data()
filtered_df, _ = render_sidebar_filters(df)

render_header(
    title="Page 4: Age Cohorts & Credit Risk",
    subtitle="Analyze the relationship between applicant age brackets, credit demand, and loan repayment risk.",
    badge="Age Demographics",
)

avg_age = filtered_df["Age"].mean() if "Age" in filtered_df.columns and len(filtered_df) > 0 else 0.0
min_age = filtered_df["Age"].min() if "Age" in filtered_df.columns and len(filtered_df) > 0 else 0.0
max_age = filtered_df["Age"].max() if "Age" in filtered_df.columns and len(filtered_df) > 0 else 0.0

age_group_agg = filtered_df.groupby("Age Group", observed=False).agg(
    Total=("TARGET", "count"),
    Defaults=("TARGET", "sum"),
    Default_Rate=("TARGET", "mean"),
    Avg_Credit=("AMT_CREDIT", "mean"),
    Avg_Income=("AMT_INCOME_TOTAL", "mean"),
).reset_index()
age_group_agg["Default Rate %"] = (age_group_agg["Default_Rate"] * 100).round(2)

highest_risk_group = age_group_agg.loc[age_group_agg["Default Rate %"].idxmax(), "Age Group"] if not age_group_agg.empty else "N/A"
highest_risk_val = age_group_agg["Default Rate %"].max() if not age_group_agg.empty else 0.0

# Exact 4 KPI Cards from Projects.ipynb
c1, c2, c3, c4 = st.columns(4)
c1.metric("Average Age", f"{avg_age:.1f} Yrs")
c2.metric("Youngest Customer", f"{min_age:.0f} Yrs")
c3.metric("Oldest Customer", f"{max_age:.0f} Yrs")
c4.metric("Highest Risk Age Group", str(highest_risk_group), f"{highest_risk_val:.2f}% Default Rate", delta_color="inverse")

st.divider()

render_formula_card(
    formula_name="Derived Age",
    formula_math="Age = abs(DAYS_BIRTH) / 365",
    formula_desc="Converts negative registration days into positive chronological applicant age in years."
)

st.divider()

# Visualizations Row 1: Age Distribution Histogram & Applications by Age Group
st.subheader("🎂 Age Distribution & Application Cohorts")
a1, a2 = st.columns(2)
with a1:
    fig_ahist = create_histogram(filtered_df, col="Age", nbins=35, title="Age Distribution Histogram", color_by="Target Label")
    st.plotly_chart(fig_ahist, use_container_width=True)

with a2:
    fig_ag = create_bar_chart(age_group_agg, x_col="Age Group", y_col="Total", title="Applications by Age Group")
    st.plotly_chart(fig_ag, use_container_width=True)

# Visualizations Row 2: Default Rate by Age & Default Rate by Age Group
st.subheader("📈 Age Default Propensity & Curve")
a3, a4 = st.columns(2)
with a3:
    age_int_agg = filtered_df.groupby(filtered_df["Age"].round().astype(int))["TARGET"].mean().reset_index()
    age_int_agg["Default Rate %"] = (age_int_agg["TARGET"] * 100).round(2)
    fig_acurve = create_line_trend(age_int_agg, x_col="Age", y_cols="Default Rate %", title="Default Rate by Age (Continuous Curve)", show_markers=True)
    st.plotly_chart(fig_acurve, use_container_width=True)

with a4:
    fig_adr = create_bar_chart(age_group_agg, x_col="Age Group", y_col="Default Rate %", title="Default Rate by Age Group")
    st.plotly_chart(fig_adr, use_container_width=True)

# Visualizations Row 3: Credit Amount by Age & Income by Age
st.subheader("💳 Credit Amount & Income by Age Group")
a5, a6 = st.columns(2)
with a5:
    fig_acredit = create_bar_chart(age_group_agg, x_col="Age Group", y_col="Avg_Credit", title="Credit Amount by Age")
    st.plotly_chart(fig_acredit, use_container_width=True)

with a6:
    fig_ainc = create_bar_chart(age_group_agg, x_col="Age Group", y_col="Avg_Income", title="Income by Age")
    st.plotly_chart(fig_ainc, use_container_width=True)

if not age_group_agg.empty:
    render_insights_card([
        "**Inverse Age-Risk Law**: Younger applicants (18–25) experience the highest default rate (>12%), which monotonically declines to under 5% for borrowers aged 60+.",
        "**Peak Credit Demand**: Borrowers aged 36–50 command the largest credit lines as major household and asset expenditures peak.",
        "**Underwriting Policy**: Recommend lower initial credit limits or co-signers for applicants in the 18–25 age bracket.",
    ])
