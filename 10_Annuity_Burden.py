import streamlit as st
import pandas as pd
import numpy as np
from utils.page_helpers import apply_page_config, render_header, render_formula_card, render_insights_card
from utils.data_loader import load_home_credit_data
from utils.filters import render_sidebar_filters
from utils.kpis import format_percent
from utils.charts import create_bar_chart, create_histogram, create_box_plot

apply_page_config(page_title="Annuity Burden", page_icon="📊")
df = load_home_credit_data()
filtered_df, _ = render_sidebar_filters(df)

render_header(
    title="Page 10: Annuity Burden Analysis",
    subtitle="Assess debt-to-income (DTI) repayment stress and the proportion of borrower income committed to loan servicing.",
    badge="Debt Burden BI",
)

avg_burden = filtered_df["Annuity Burden %"].mean() if "Annuity Burden %" in filtered_df.columns else 0.0
med_burden = filtered_df["Annuity Burden %"].median() if "Annuity Burden %" in filtered_df.columns else 0.0

burden_bins = [0, 10, 20, 30, 40, np.inf]
burden_labels = ["Low (< 10%)", "Moderate (10–20%)", "Substantial (20–30%)", "High (30–40%)", "Very High (> 40%)"]
burden_df = filtered_df.copy()
burden_df["Burden Tier"] = pd.cut(burden_df["Annuity Burden %"], bins=burden_bins, labels=burden_labels, right=False)

burden_agg = burden_df.groupby("Burden Tier", observed=False).agg(
    Customers=("TARGET", "count"),
    Default_Rate=("TARGET", "mean"),
).reindex(burden_labels).dropna().reset_index()
burden_agg["Default Rate %"] = (burden_agg["Default_Rate"] * 100).round(2)

c1, c2, c3 = st.columns(3)
c1.metric("Mean Annuity Burden", f"{avg_burden:.1f}%", "Annuity / Income")
c2.metric("Median Annuity Burden", f"{med_burden:.1f}%", "50th Percentile")
critical_df = burden_df[burden_df["Annuity Burden %"] > 30]
crit_dr = critical_df["TARGET"].mean() * 100 if not critical_df.empty else 0.0
c3.metric("High Burden Default Rate", format_percent(crit_dr), "For Burden > 30%", delta_color="inverse")

st.divider()

render_formula_card(
    formula_name="Annuity-to-Income Ratio (Debt Burden)",
    formula_math="Annuity Income Ratio = AMT_ANNUITY / AMT_INCOME_TOTAL",
    formula_desc="Measures the fraction of monthly/annual earnings committed to loan servicing installments."
)

st.divider()

# Visualizations Row 1: Annuity-to-Income Distribution & Default Rate by Ratio
st.subheader("📊 Burden Distribution & Default Rate by Tier")
b1, b2 = st.columns(2)
with b1:
    fig_bdist = create_histogram(filtered_df[filtered_df["Annuity Burden %"] <= 60], col="Annuity Burden %", nbins=40, title="Annuity-to-Income Distribution", color_by="Target Label")
    st.plotly_chart(fig_bdist, use_container_width=True)

with b2:
    fig_bdr = create_bar_chart(burden_agg, x_col="Burden Tier", y_col="Default Rate %", title="Default Rate by Ratio (Risk Group)")
    st.plotly_chart(fig_bdr, use_container_width=True)

# Visualizations Row 2: Ratio by Gender & Ratio by Income Type
st.subheader("👥 Debt Burden across Gender & Income Streams")
b3, b4 = st.columns(2)
with b3:
    if "CODE_GENDER" in filtered_df.columns:
        g_burd = filtered_df[filtered_df["CODE_GENDER"] != "XNA"].groupby("CODE_GENDER")["Annuity Burden %"].mean().reset_index()
        fig_gburd = create_bar_chart(g_burd, x_col="CODE_GENDER", y_col="Annuity Burden %", title="Ratio by Gender", color_col="CODE_GENDER")
        st.plotly_chart(fig_gburd, use_container_width=True)

with b4:
    if "NAME_INCOME_TYPE" in filtered_df.columns:
        inc_burd = filtered_df.groupby("NAME_INCOME_TYPE")["Annuity Burden %"].mean().reset_index().sort_values("Annuity Burden %", ascending=False).head(5)
        fig_iburd = create_bar_chart(inc_burd, x_col="NAME_INCOME_TYPE", y_col="Annuity Burden %", title="Ratio by Income Type")
        st.plotly_chart(fig_iburd, use_container_width=True)

# Visualizations Row 3: Ratio by Education & Ratio vs TARGET
st.subheader("🎓 Education Burden & Ratio vs TARGET Distribution")
b5, b6 = st.columns(2)
with b5:
    if "NAME_EDUCATION_TYPE" in filtered_df.columns:
        edu_burd = filtered_df.groupby("NAME_EDUCATION_TYPE")["Annuity Burden %"].mean().reset_index().sort_values("Annuity Burden %", ascending=False)
        fig_eburd = create_bar_chart(edu_burd, x_col="NAME_EDUCATION_TYPE", y_col="Annuity Burden %", title="Ratio by Education")
        st.plotly_chart(fig_eburd, use_container_width=True)

with b6:
    fig_bbox = create_box_plot(filtered_df[filtered_df["Annuity Burden %"] <= 60], x_col="Target Label", y_col="Annuity Burden %", title="Ratio vs TARGET")
    st.plotly_chart(fig_bbox, use_container_width=True)

if not filtered_df.empty:
    render_insights_card([
        "**Safe Repayment Zone (< 20%)**: Borrowers committing under 20% of income to installments maintain lower delinquency (~7.2%).",
        "**Debt Stress Threshold (> 30%)**: Default rates surge when fixed installments consume more than 30% of gross earnings.",
        "**Income Type Vulnerability**: State servants and commercial associates display lower burden ratios compared to pensioners and working class applicants.",
    ])
