import streamlit as st
import pandas as pd
from utils.page_helpers import apply_page_config, render_header, render_formula_card, render_insights_card
from utils.data_loader import load_home_credit_data
from utils.filters import render_sidebar_filters
from utils.kpis import format_number, format_percent
from utils.charts import create_bar_chart, create_histogram, create_scatter_plot

apply_page_config(page_title="External Score Analysis", page_icon="🌟")
df = load_home_credit_data()
filtered_df, _ = render_sidebar_filters(df)

render_header(
    title="Page 16: External Credit Score Analysis",
    subtitle="Analyze external credit bureau score distributions (EXT_SOURCE_1/2/3) and their predictive discrimination of default risk.",
    badge="Bureau Scores",
)

avg_ext1 = filtered_df["EXT_SOURCE_1"].mean() if "EXT_SOURCE_1" in filtered_df.columns else 0.0
avg_ext2 = filtered_df["EXT_SOURCE_2"].mean() if "EXT_SOURCE_2" in filtered_df.columns else 0.0
avg_ext3 = filtered_df["EXT_SOURCE_3"].mean() if "EXT_SOURCE_3" in filtered_df.columns else 0.0

missing_ext = filtered_df[["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]].isna().all(axis=1).sum() if set(["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]).issubset(filtered_df.columns) else 0

# Exact 4 KPI Cards from Projects.ipynb
c1, c2, c3, c4 = st.columns(4)
c1.metric("Average EXT_SOURCE_1", f"{avg_ext1:.3f}", "External Bureau 1")
c2.metric("Average EXT_SOURCE_2", f"{avg_ext2:.3f}", "External Bureau 2")
c3.metric("Average EXT_SOURCE_3", f"{avg_ext3:.3f}", "External Bureau 3")
c4.metric("Missing External Score Records", format_number(missing_ext), "Missing All 3 Scores", delta_color="inverse")

st.divider()

render_formula_card(
    formula_name="Average External Score",
    formula_math="Average External Score = (EXT_SOURCE_1 + EXT_SOURCE_2 + EXT_SOURCE_3) / 3",
    formula_desc="Aggregates normalized third-party credit bureau ratings into a unified 0.00–1.00 creditworthiness score."
)

st.divider()

# Visualizations Row 1: EXT_SOURCE_1, EXT_SOURCE_2, and EXT_SOURCE_3 Distributions
st.subheader("🌟 External Bureau Score Distributions")
ex1, ex2, ex3 = st.columns(3)
with ex1:
    fig_ext1_hist = create_histogram(filtered_df.dropna(subset=["EXT_SOURCE_1"]), col="EXT_SOURCE_1", nbins=30, title="EXT_SOURCE_1 Distribution", color_by="Target Label")
    st.plotly_chart(fig_ext1_hist, use_container_width=True)

with ex2:
    fig_ext2_hist = create_histogram(filtered_df.dropna(subset=["EXT_SOURCE_2"]), col="EXT_SOURCE_2", nbins=30, title="EXT_SOURCE_2 Distribution", color_by="Target Label")
    st.plotly_chart(fig_ext2_hist, use_container_width=True)

with ex3:
    fig_ext3_hist = create_histogram(filtered_df.dropna(subset=["EXT_SOURCE_3"]), col="EXT_SOURCE_3", nbins=30, title="EXT_SOURCE_3 Distribution", color_by="Target Label")
    st.plotly_chart(fig_ext3_hist, use_container_width=True)

# Visualizations Row 2: External Scores by TARGET & External Score vs Default Rate
st.subheader("📊 External Scores by TARGET & Default Propensity")
ex4, ex5 = st.columns(2)
with ex4:
    ext_target_comp = filtered_df.groupby("Target Label")[["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3", "Avg External Score"]].mean().reset_index()
    ext_melt = pd.melt(ext_target_comp, id_vars=["Target Label"], value_vars=["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3", "Avg External Score"], var_name="Score Type", value_name="Average Score")
    fig_ext_comp = create_bar_chart(ext_melt, x_col="Score Type", y_col="Average Score", color_col="Target Label", title="External Scores by TARGET")
    st.plotly_chart(fig_ext_comp, use_container_width=True)

with ex5:
    if "External Score Rating" in filtered_df.columns:
        ext_rating_order = ["Poor (< 0.25)", "Fair (0.25–0.50)", "Good (0.50–0.75)", "Excellent (0.75–1.0)"]
        ext_agg = filtered_df.groupby("External Score Rating", observed=False)["TARGET"].agg(Customers="count", Default_Rate="mean").reindex(ext_rating_order).dropna().reset_index()
        ext_agg["Default Rate %"] = (ext_agg["Default_Rate"] * 100).round(2)
        fig_ext_dr = create_bar_chart(ext_agg, x_col="External Score Rating", y_col="Default Rate %", title="External Score vs Default Rate")
        st.plotly_chart(fig_ext_dr, use_container_width=True)

# Visualizations Row 3: EXT_SOURCE_1 vs EXT_SOURCE_2 & EXT_SOURCE_2 vs EXT_SOURCE_3
st.subheader("🔍 Inter-Bureau Correlation & Separation")
ex6, ex7 = st.columns(2)
with ex6:
    sample_ext12 = filtered_df.dropna(subset=["EXT_SOURCE_1", "EXT_SOURCE_2"]).sample(min(2000, len(filtered_df)), random_state=42)
    fig_ext12 = create_scatter_plot(sample_ext12, x_col="EXT_SOURCE_1", y_col="EXT_SOURCE_2", color_col="Target Label", title="EXT_SOURCE_1 vs EXT_SOURCE_2")
    st.plotly_chart(fig_ext12, use_container_width=True)

with ex7:
    sample_ext23 = filtered_df.dropna(subset=["EXT_SOURCE_2", "EXT_SOURCE_3"]).sample(min(2000, len(filtered_df)), random_state=42)
    fig_ext23 = create_scatter_plot(sample_ext23, x_col="EXT_SOURCE_2", y_col="EXT_SOURCE_3", color_col="Target Label", title="EXT_SOURCE_2 vs EXT_SOURCE_3")
    st.plotly_chart(fig_ext23, use_container_width=True)

if not filtered_df.empty:
    render_insights_card([
        "**#1 Statistical Discriminator**: External credit bureau scores (particularly EXT_SOURCE_2 & 3) exhibit the strongest negative correlation with default propensity.",
        "**High External Score Safety**: Borrowers scoring Above 0.75 maintain default rates below 2.5%.",
        "**Low External Score Hazard**: Applicants with scores Below 0.25 exhibit default rates exceeding 22.0% (nearly 3x portfolio average).",
    ])
