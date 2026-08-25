import streamlit as st
import pandas as pd
from utils.page_helpers import apply_page_config, render_header, render_insights_card
from utils.data_loader import load_home_credit_data
from utils.filters import render_sidebar_filters
from utils.charts import create_bar_chart

apply_page_config(page_title="Regional Risk Analysis", page_icon="🌍")
df = load_home_credit_data()
filtered_df, _ = render_sidebar_filters(df)

render_header(
    title="Page 17: Regional Risk Analysis",
    subtitle="Analyze whether applicant location, regional credit rating indices, and address mismatches influence loan default rates.",
    badge="Geographic Risk",
)

common_rating = filtered_df["REGION_RATING_CLIENT"].mode().iloc[0] if "REGION_RATING_CLIENT" in filtered_df.columns else 2
avg_pop = filtered_df["REGION_POPULATION_RELATIVE"].mean() if "REGION_POPULATION_RELATIVE" in filtered_df.columns else 0.0

reg_dr = filtered_df.groupby("REGION_RATING_CLIENT")["TARGET"].mean().reset_index() if "REGION_RATING_CLIENT" in filtered_df.columns else pd.DataFrame()
highest_risk_rating = reg_dr.loc[reg_dr["TARGET"].idxmax(), "REGION_RATING_CLIENT"] if not reg_dr.empty else 3
highest_risk_val = reg_dr["TARGET"].max() * 100 if not reg_dr.empty else 0.0

# Exact 3 KPI Cards from Projects.ipynb
c1, c2, c3 = st.columns(3)
c1.metric("Most Common Region Rating", f"Rating {common_rating}", "Modal Score")
c2.metric("Highest Risk Region Rating", f"Rating {highest_risk_rating}", f"{highest_risk_val:.2f}% Default Rate", delta_color="inverse")
c3.metric("Average Regional Population Indicator", f"{avg_pop:.4f}", "Density Ratio")

st.divider()

# Visualizations Row 1: Customers by Region Rating & Default Rate by Region Rating
st.subheader("🌍 Regional Rating Volume & Risk")
rg1, rg2 = st.columns(2)
with rg1:
    if "REGION_RATING_CLIENT" in filtered_df.columns:
        rating_counts = filtered_df["REGION_RATING_CLIENT"].value_counts().sort_index().reset_index()
        rating_counts.columns = ["Region Rating", "Applicants"]
        rating_counts["Region Rating Label"] = "Rating " + rating_counts["Region Rating"].astype(str)
        fig_rc = create_bar_chart(rating_counts, x_col="Region Rating Label", y_col="Applicants", title="Customers by Region Rating")
        st.plotly_chart(fig_rc, use_container_width=True)

with rg2:
    if not reg_dr.empty:
        reg_dr_plot = reg_dr.copy()
        reg_dr_plot["Region Rating Label"] = "Rating " + reg_dr_plot["REGION_RATING_CLIENT"].astype(str)
        reg_dr_plot["Default Rate %"] = (reg_dr_plot["TARGET"] * 100).round(2)
        fig_rdr = create_bar_chart(reg_dr_plot, x_col="Region Rating Label", y_col="Default Rate %", title="Default Rate by Region Rating")
        st.plotly_chart(fig_rdr, use_container_width=True)

# Visualizations Row 2: Credit by Region Rating & Income by Region Rating
st.subheader("💳 Credit & Income by Regional Rating")
rg3, rg4 = st.columns(2)
with rg3:
    if "REGION_RATING_CLIENT" in filtered_df.columns:
        crd_rating = filtered_df.groupby("REGION_RATING_CLIENT")["AMT_CREDIT"].mean().reset_index()
        crd_rating["Region Rating Label"] = "Rating " + crd_rating["REGION_RATING_CLIENT"].astype(str)
        fig_crd_r = create_bar_chart(crd_rating, x_col="Region Rating Label", y_col="AMT_CREDIT", title="Credit by Region Rating")
        st.plotly_chart(fig_crd_r, use_container_width=True)

with rg4:
    if "REGION_RATING_CLIENT" in filtered_df.columns:
        inc_rating = filtered_df.groupby("REGION_RATING_CLIENT")["AMT_INCOME_TOTAL"].mean().reset_index()
        inc_rating["Region Rating Label"] = "Rating " + inc_rating["REGION_RATING_CLIENT"].astype(str)
        fig_inc_r = create_bar_chart(inc_rating, x_col="Region Rating Label", y_col="AMT_INCOME_TOTAL", title="Income by Region Rating")
        st.plotly_chart(fig_inc_r, use_container_width=True)

# Visualizations Row 3: Region Mismatch vs Default & City Mismatch vs Default
st.subheader("📍 Location Mismatch vs Default Risk")
rg5, rg6 = st.columns(2)
with rg5:
    if "REG_REGION_NOT_LIVE_REGION" in filtered_df.columns:
        reg_mm = filtered_df.groupby("REG_REGION_NOT_LIVE_REGION")["TARGET"].agg(Customers="count", Default_Rate="mean").reset_index()
        reg_mm["Default Rate %"] = (reg_mm["Default_Rate"] * 100).round(2)
        reg_mm["Mismatch Label"] = reg_mm["REG_REGION_NOT_LIVE_REGION"].map({0: "Address Matches Live Region", 1: "Address Mismatches Live Region"})
        fig_reg_mm = create_bar_chart(reg_mm, x_col="Mismatch Label", y_col="Default Rate %", title="Region Mismatch vs Default", color_col="Mismatch Label")
        st.plotly_chart(fig_reg_mm, use_container_width=True)

with rg6:
    if "REG_CITY_NOT_WORK_CITY" in filtered_df.columns:
        city_mm = filtered_df.groupby("REG_CITY_NOT_WORK_CITY")["TARGET"].agg(Customers="count", Default_Rate="mean").reset_index()
        city_mm["Default Rate %"] = (city_mm["Default_Rate"] * 100).round(2)
        city_mm["Mismatch Label"] = city_mm["REG_CITY_NOT_WORK_CITY"].map({0: "Address Matches Work City", 1: "Address Mismatches Work City"})
        fig_city_mm = create_bar_chart(city_mm, x_col="Mismatch Label", y_col="Default Rate %", title="City Mismatch vs Default", color_col="Mismatch Label")
        st.plotly_chart(fig_city_mm, use_container_width=True)

if not filtered_df.empty:
    render_insights_card([
        "**Regional Risk Rating Hierarchy**: Rating 1 regions exhibit ~5.1% default, while Rating 3 regions rise to ~11.8%.",
        "**Workplace Mismatch Indicator**: Applicants whose registration address differs from their workplace city exhibit ~30% higher delinquency.",
        "**Economic Urbanization**: Higher population density areas display stronger income stability and credit capacity.",
    ])
