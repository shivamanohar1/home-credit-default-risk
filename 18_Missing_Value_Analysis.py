import streamlit as st
import pandas as pd
from utils.page_helpers import apply_page_config, render_header, render_insights_card
from utils.data_loader import load_home_credit_data
from utils.kpis import format_number
from utils.charts import create_bar_chart, create_histogram, create_heatmap_matrix

apply_page_config(page_title="Missing Value Analysis", page_icon="🔍")
df = load_home_credit_data()

render_header(
    title="Page 18: Missing Value Analysis",
    subtitle="Audit missing data patterns, null distributions, column completeness, and recommended ML imputation strategies.",
    badge="Data Quality BI",
)

total_rows, total_cols = df.shape
missing_counts = df.isnull().sum()
total_missing = missing_counts.sum()
cols_with_missing = (missing_counts > 0).sum()
cols_over_50pct = (missing_counts / total_rows > 0.50).sum()

# Exact 5 KPI Cards from Projects.ipynb
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Rows", format_number(total_rows))
c2.metric("Total Columns", format_number(total_cols))
c3.metric("Total Missing Values", format_number(total_missing))
c4.metric("Columns with Missing Values", format_number(cols_with_missing), "Incomplete Features", delta_color="inverse")
c5.metric("Columns with >50% Missing Data", format_number(cols_over_50pct), "High Null Rate", delta_color="inverse")

st.divider()

# Missing DataFrame Table
missing_df = pd.DataFrame({
    "Column": df.columns,
    "Missing Count": missing_counts.values,
    "Missing %": ((missing_counts.values / total_rows) * 100).round(2),
    "Data Type": df.dtypes.astype(str).values,
})
missing_df = missing_df[missing_df["Missing Count"] > 0].sort_values("Missing %", ascending=False)

def get_impute_action(row):
    pct = row["Missing %"]
    dtype = row["Data Type"]
    if pct > 60:
        return "Drop Column or Create Missing Indicator"
    elif "float" in dtype or "int" in dtype:
        return "Fill with Median"
    elif "object" in dtype or "category" in dtype:
        return "Fill with 'Unknown' / Mode"
    else:
        return "Fill with Mean / Indicator"

missing_df["Recommended Imputation Action"] = missing_df.apply(get_impute_action, axis=1)

# Visualizations Row 1: Top 20 Columns with Missing Values & Missing Percentage by Column
st.subheader("🔍 Top Missing Features & Distribution")
ms1, ms2 = st.columns([3, 2])
with ms1:
    top20_miss = missing_df.head(20).sort_values("Missing %", ascending=True)
    fig_top_miss = create_bar_chart(top20_miss, x_col="Column", y_col="Missing %", orientation="h", title="Top 20 Columns with Missing Values")
    st.plotly_chart(fig_top_miss, use_container_width=True)

with ms2:
    fig_miss_hist = create_histogram(missing_df, col="Missing %", nbins=20, title="Missing Percentage by Column")
    st.plotly_chart(fig_miss_hist, use_container_width=True)

# Visualizations Row 2: Missing Values by Data Type & Missing Values Heatmap
st.subheader("📊 Missing Values by Data Type & Feature Null Sample")
ms3, ms4 = st.columns([2, 3])
with ms3:
    miss_by_type = missing_df.groupby("Data Type")["Column"].count().reset_index()
    miss_by_type.columns = ["Data Type", "Incomplete Features Count"]
    fig_type = create_bar_chart(miss_by_type, x_col="Data Type", y_col="Incomplete Features Count", title="Missing Values by Data Type")
    st.plotly_chart(fig_type, use_container_width=True)

with ms4:
    top_miss_cols = missing_df.head(15)["Column"].tolist()
    sample_null_matrix = df[top_miss_cols].sample(min(50, len(df)), random_state=42).isnull().astype(int)
    fig_null_heat = create_heatmap_matrix(sample_null_matrix.T, title="Missing Values Heatmap (Top 15 Features, 50 Sample Applicants)", colorscale="Reds")
    st.plotly_chart(fig_null_heat, use_container_width=True)

# Full Missing Values Audit Table
st.subheader("📋 Complete Missing Values Audit & Action Table")
disp_miss = missing_df.copy()
disp_miss["Missing Count"] = disp_miss["Missing Count"].apply(lambda v: f"{v:,}")
disp_miss["Missing %"] = disp_miss["Missing %"].apply(lambda v: f"{v:.2f}%")

st.dataframe(disp_miss, use_container_width=True, hide_index=True)

if not missing_df.empty:
    render_insights_card([
        "**Normalized Building Scores**: Real estate features (COMMONAREA, LIVINGAPARTMENTS, etc.) have 50–70% missing values.",
        "**External Scores**: EXT_SOURCE_1 is missing for ~56% of applicants, while EXT_SOURCE_2/3 are largely populated (>99%).",
        "**Recommended ML Action**: Columns with >60% missing data should either be dropped or converted into binary 'Flag_Was_Missing' features before model training.",
    ])
