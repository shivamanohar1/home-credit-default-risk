import streamlit as st
import pandas as pd
from utils.page_helpers import apply_page_config, render_header, render_insights_card
from utils.data_loader import load_home_credit_data
from utils.filters import render_sidebar_filters
from utils.charts import create_heatmap_matrix, create_bar_chart, create_scatter_plot, create_box_plot

apply_page_config(page_title="Correlation & Risk Factors", page_icon="🔗")
df = load_home_credit_data()
filtered_df, _ = render_sidebar_filters(df)

render_header(
    title="Page 19: Correlation & Risk Factor Analysis",
    subtitle="Identify important numerical relationships, feature collinearity, and prime statistical drivers of loan default.",
    badge="Risk Factors BI",
)

corr_features = [
    "TARGET", "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE",
    "Age", "Employment Years", "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3",
    "Avg External Score", "Credit to Income Ratio", "Annuity to Income Ratio", "CNT_CHILDREN", "CNT_FAM_MEMBERS"
]
avail_features = [f for f in corr_features if f in filtered_df.columns]

corr_matrix = filtered_df[avail_features].corr().round(3)
target_corr = corr_matrix["TARGET"].drop("TARGET").sort_values()

top_negative = target_corr.head(4)
top_positive = target_corr.tail(4).iloc[::-1]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Analyzed Numerical Features", str(len(avail_features)))
top_pos_name = top_positive.index[0]
top_pos_val = top_positive.iloc[0]
c2.metric("Top Positive Risk Driver", top_pos_name[:16], f"+{top_pos_val:.3f} Correlation", delta_color="inverse")
top_neg_name = top_negative.index[0]
top_neg_val = top_negative.iloc[0]
c3.metric("Top Protective Factor", top_neg_name[:16], f"{top_neg_val:.3f} Correlation")
c4.metric("Credit Bureau Power", "Extremely High", "EXT_SOURCE 1/2/3")

st.divider()

# Visualizations Row 1: Correlation Heatmap
st.subheader("🗺️ Pearson Correlation Heatmap")
fig_heat = create_heatmap_matrix(corr_matrix, title="Correlation Matrix (Selected Numerical Features)", height=520, colorscale="RdBu_r")
st.plotly_chart(fig_heat, use_container_width=True)

# Visualizations Row 2: Correlation with TARGET & Top Positive/Negative Correlations
st.subheader("📊 Linear Correlation with Default (TARGET)")
cr1, cr2 = st.columns(2)
with cr1:
    t_corr_df = target_corr.reset_index()
    t_corr_df.columns = ["Feature", "Correlation with TARGET"]
    fig_tcorr = create_bar_chart(t_corr_df, x_col="Feature", y_col="Correlation with TARGET", orientation="h", title="Correlation with TARGET (All Features)")
    st.plotly_chart(fig_tcorr, use_container_width=True)

with cr2:
    top_pos_df = top_positive.reset_index()
    top_pos_df.columns = ["Feature", "Correlation"]
    fig_top_pos = create_bar_chart(top_pos_df, x_col="Feature", y_col="Correlation", title="Top Positive Correlations (+ Risk)")
    st.plotly_chart(fig_top_pos, use_container_width=True)

# Visualizations Row 3: Credit vs Income Scatter Plot & External Score vs TARGET
st.subheader("🔍 Credit vs Income & Bureau Score Discrimination")
cr3, cr4 = st.columns(2)
with cr3:
    sample_ci = filtered_df[(filtered_df["AMT_INCOME_TOTAL"] <= 500000) & (filtered_df["AMT_CREDIT"] <= 1500000)].sample(min(2000, len(filtered_df)), random_state=42)
    fig_scat_ci = create_scatter_plot(sample_ci, x_col="AMT_INCOME_TOTAL", y_col="AMT_CREDIT", color_col="Target Label", title="Credit vs Income Scatter Plot")
    st.plotly_chart(fig_scat_ci, use_container_width=True)

with cr4:
    fig_ext_target = create_box_plot(filtered_df.dropna(subset=["Avg External Score"]), x_col="Target Label", y_col="Avg External Score", title="External Score vs TARGET")
    st.plotly_chart(fig_ext_target, use_container_width=True)

# Important Risk Factors Section from Projects.ipynb
st.subheader("🚨 Important Risk Factors Summary")
rc1, rc2, rc3, rc4 = st.columns(4)
with rc1:
    with st.container(border=True):
        st.markdown("**📉 Low External Credit Score**")
        st.caption("Strong negative correlation (-0.18 to -0.22). Scores below 0.30 indicate a 4x risk multiplier.")

with rc2:
    with st.container(border=True):
        st.markdown("**⚖️ High Credit & Annuity Burden**")
        st.caption("Positive correlation (+0.045). Leverage ratios exceeding 4x income significantly spike delinquency.")

with rc3:
    with st.container(border=True):
        st.markdown("**🎂 Younger Age Cohorts**")
        st.caption("Negative correlation (-0.078). Borrowers under 25 have lower asset reserves and volatile cashflow.")

with rc4:
    with st.container(border=True):
        st.markdown("**💼 Short Employment Tenure**")
        st.caption("Negative correlation with default (-0.045). Tenures under 1 year carry significantly higher risk.")

if not filtered_df.empty:
    render_insights_card([
        "**Credit Bureau Scores (EXT_SOURCE)**: Single most potent linear and non-linear risk predictor in the dataset.",
        "**Age & Job Tenure**: Strongest natural protective factors against credit default.",
        "**Multicollinearity Warning**: AMT_CREDIT and AMT_GOODS_PRICE exhibit near-perfect collinearity (r = 0.987).",
    ])
