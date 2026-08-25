import streamlit as st
import pandas as pd
import numpy as np
from utils.page_helpers import apply_page_config, render_header, render_insights_card
from utils.data_loader import load_home_credit_data
from utils.filters import render_sidebar_filters
from utils.kpis import format_currency
from utils.charts import create_bar_chart, create_histogram, create_scatter_plot, create_box_plot

apply_page_config(page_title="Annuity Analysis", page_icon="💵")
df = load_home_credit_data()
filtered_df, _ = render_sidebar_filters(df)

render_header(
    title="Page 8: Annuity Analysis",
    subtitle="Study applicants' annual and periodic loan payment obligations and repayment capacity.",
    badge="Payment Schedules",
)

avg_annuity = filtered_df["AMT_ANNUITY"].mean() if "AMT_ANNUITY" in filtered_df.columns else 0.0
med_annuity = filtered_df["AMT_ANNUITY"].median() if "AMT_ANNUITY" in filtered_df.columns else 0.0
max_annuity = filtered_df["AMT_ANNUITY"].max() if "AMT_ANNUITY" in filtered_df.columns else 0.0

defaulters = filtered_df[filtered_df["TARGET"] == 1]
avg_ann_def = defaulters["AMT_ANNUITY"].mean() if not defaulters.empty else 0.0

# Exact 4 KPI Cards from Projects.ipynb
c1, c2, c3, c4 = st.columns(4)
c1.metric("Average Annuity", format_currency(avg_annuity))
c2.metric("Median Annuity", format_currency(med_annuity))
c3.metric("Maximum Annuity", format_currency(max_annuity))
c4.metric("Average Annuity for Defaulters", format_currency(avg_ann_def), "Target = 1", delta_color="inverse")

st.divider()

# Annuity Groups Aggregation
ann_bins = [0, 15000, 30000, 45000, 60000, 100000, np.inf]
ann_labels = ["< 15K", "15K–30K", "30K–45K", "45K–60K", "60K–100K", "> 100K"]
ann_df = filtered_df.copy()
ann_df["Annuity Group"] = pd.cut(ann_df["AMT_ANNUITY"], bins=ann_bins, labels=ann_labels, right=False)

ann_agg = ann_df.groupby("Annuity Group", observed=False).agg(
    Customers=("TARGET", "count"),
    Default_Rate=("TARGET", "mean"),
).reindex(ann_labels).dropna().reset_index()
ann_agg["Default Rate %"] = (ann_agg["Default_Rate"] * 100).round(2)

# Visualizations Row 1: Annuity Distribution & Annuity by TARGET
st.subheader("💵 Annuity Distribution & Target Breakdown")
an1, an2 = st.columns(2)
with an1:
    fig_ahist = create_histogram(filtered_df[filtered_df["AMT_ANNUITY"] <= 80000], col="AMT_ANNUITY", nbins=40, title="Annuity Distribution", color_by="Target Label")
    st.plotly_chart(fig_ahist, use_container_width=True)

with an2:
    fig_abox = create_box_plot(filtered_df[filtered_df["AMT_ANNUITY"] <= 80000], x_col="Target Label", y_col="AMT_ANNUITY", title="Annuity by TARGET")
    st.plotly_chart(fig_abox, use_container_width=True)

# Visualizations Row 2: Annuity vs Income & Annuity vs Credit
st.subheader("📊 Annuity vs Financial Capacity")
an3, an4 = st.columns(2)
with an3:
    sample_ann = filtered_df[(filtered_df["AMT_INCOME_TOTAL"] <= 400000) & (filtered_df["AMT_ANNUITY"] <= 75000)].sample(min(2000, len(filtered_df)), random_state=42)
    fig_ai = create_scatter_plot(sample_ann, x_col="AMT_INCOME_TOTAL", y_col="AMT_ANNUITY", color_col="Target Label", title="Annuity vs Income")
    st.plotly_chart(fig_ai, use_container_width=True)

with an4:
    sample_crd = filtered_df[(filtered_df["AMT_CREDIT"] <= 1500000) & (filtered_df["AMT_ANNUITY"] <= 75000)].sample(min(2000, len(filtered_df)), random_state=42)
    fig_ac = create_scatter_plot(sample_crd, x_col="AMT_CREDIT", y_col="AMT_ANNUITY", color_col="Target Label", title="Annuity vs Credit")
    st.plotly_chart(fig_ac, use_container_width=True)

# Visualizations Row 3: Average Annuity by Income Type & Default Rate by Annuity Group
st.subheader("💼 Annuity by Income Stream & Delinquency Tiers")
an5, an6 = st.columns(2)
with an5:
    if "NAME_INCOME_TYPE" in filtered_df.columns:
        inc_ann = filtered_df.groupby("NAME_INCOME_TYPE")["AMT_ANNUITY"].mean().reset_index().sort_values("AMT_ANNUITY", ascending=False).head(5)
        fig_ia = create_bar_chart(inc_ann, x_col="NAME_INCOME_TYPE", y_col="AMT_ANNUITY", title="Average Annuity by Income Type")
        st.plotly_chart(fig_ia, use_container_width=True)

with an6:
    fig_adr = create_bar_chart(ann_agg, x_col="Annuity Group", y_col="Default Rate %", title="Default Rate by Annuity Group")
    st.plotly_chart(fig_adr, use_container_width=True)

if not filtered_df.empty:
    render_insights_card([
        f"**Standard Installment Range**: Over 55% of applicants have scheduled annuities between $15K and $30K (median **{format_currency(med_annuity)}**).",
        "**Credit-Annuity Co-movement**: Direct positive linear relationship between credit requested and annual installment requirement.",
        "**Annuity Shock Risk**: Scheduled annuities above $60K without verified commensurate income result in an elevated default probability.",
    ])
