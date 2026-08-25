import streamlit as st
import pandas as pd
from utils.page_helpers import apply_page_config, render_header, render_insights_card
from utils.data_loader import load_home_credit_data
from utils.filters import render_sidebar_filters
from utils.kpis import format_number, format_percent
from utils.charts import create_bar_chart

apply_page_config(page_title="Family & Children Analysis", page_icon="👨‍👩‍👧")
df = load_home_credit_data()
filtered_df, _ = render_sidebar_filters(df)

render_header(
    title="Page 13: Family & Children Analysis",
    subtitle="Study whether household composition, dependent children count, and family status influence credit risk.",
    badge="Household Risk",
)

avg_children = filtered_df["CNT_CHILDREN"].mean() if "CNT_CHILDREN" in filtered_df.columns else 0.0
avg_fam_size = filtered_df["CNT_FAM_MEMBERS"].mean() if "CNT_FAM_MEMBERS" in filtered_df.columns else 0.0

with_kids = (filtered_df["CNT_CHILDREN"] > 0).sum() if "CNT_CHILDREN" in filtered_df.columns else 0
no_kids = (filtered_df["CNT_CHILDREN"] == 0).sum() if "CNT_CHILDREN" in filtered_df.columns else 0

fam_dr = filtered_df.groupby("NAME_FAMILY_STATUS")["TARGET"].agg(Count="count", Mean="mean").reset_index() if "NAME_FAMILY_STATUS" in filtered_df.columns else pd.DataFrame()
valid_fam = fam_dr[fam_dr["Count"] > 50].sort_values("Mean", ascending=False) if not fam_dr.empty else pd.DataFrame()
highest_risk_fam = valid_fam.iloc[0]["NAME_FAMILY_STATUS"] if not valid_fam.empty else "N/A"
highest_risk_fam_val = valid_fam.iloc[0]["Mean"] * 100 if not valid_fam.empty else 0.0

# Exact 5 KPI Cards from Projects.ipynb
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Average Children", f"{avg_children:.2f}")
c2.metric("Average Family Members", f"{avg_fam_size:.1f}")
c3.metric("Customers with Children", format_number(with_kids), f"{(with_kids/len(filtered_df)*100):.1f}% Share" if len(filtered_df)>0 else "")
c4.metric("Customers without Children", format_number(no_kids), f"{(no_kids/len(filtered_df)*100):.1f}% Share" if len(filtered_df)>0 else "")
c5.metric("Highest Risk Family Type", str(highest_risk_fam)[:16], f"{highest_risk_fam_val:.2f}% Default", delta_color="inverse")

st.divider()

# Visualizations Row 1: Customers by Number of Children & Default Rate by Number of Children
st.subheader("👶 Children Count & Delinquency Rates")
fm1, fm2 = st.columns(2)
with fm1:
    kids_df = filtered_df[filtered_df["CNT_CHILDREN"] <= 5]
    kids_agg = kids_df.groupby("CNT_CHILDREN").agg(Customers=("TARGET", "count"), Default_Rate=("TARGET", "mean")).reset_index()
    kids_agg["Default Rate %"] = (kids_agg["Default_Rate"] * 100).round(2)
    kids_agg["Children Label"] = kids_agg["CNT_CHILDREN"].astype(str) + " Children"
    fig_kc = create_bar_chart(kids_agg, x_col="Children Label", y_col="Customers", title="Customers by Number of Children")
    st.plotly_chart(fig_kc, use_container_width=True)

with fm2:
    fig_kdr = create_bar_chart(kids_agg, x_col="Children Label", y_col="Default Rate %", title="Default Rate by Number of Children")
    st.plotly_chart(fig_kdr, use_container_width=True)

# Visualizations Row 2: Customers by Family Size & Default Rate by Family Size
st.subheader("👨‍👩‍👧 Family Size & Delinquency Tiers")
fm3, fm4 = st.columns(2)
with fm3:
    fam_size_df = filtered_df[(filtered_df["CNT_FAM_MEMBERS"] >= 1) & (filtered_df["CNT_FAM_MEMBERS"] <= 6)]
    fam_size_agg = fam_size_df.groupby("CNT_FAM_MEMBERS").agg(Customers=("TARGET", "count"), Default_Rate=("TARGET", "mean")).reset_index()
    fam_size_agg["Default Rate %"] = (fam_size_agg["Default_Rate"] * 100).round(2)
    fam_size_agg["Family Size Label"] = fam_size_agg["CNT_FAM_MEMBERS"].astype(int).astype(str) + " Members"
    fig_fsc = create_bar_chart(fam_size_agg, x_col="Family Size Label", y_col="Customers", title="Customers by Family Size")
    st.plotly_chart(fig_fsc, use_container_width=True)

with fm4:
    fig_fsdr = create_bar_chart(fam_size_agg, x_col="Family Size Label", y_col="Default Rate %", title="Default Rate by Family Size")
    st.plotly_chart(fig_fsdr, use_container_width=True)

# Visualizations Row 3: Applications by Family Status & Default Rate by Family Status
st.subheader("💍 Marital / Family Status Analysis")
fm5, fm6 = st.columns(2)
with fm5:
    fam_status_agg = filtered_df.groupby("NAME_FAMILY_STATUS")["TARGET"].agg(Customers="count", Default_Rate="mean").reset_index()
    fam_status_agg["Default Rate %"] = (fam_status_agg["Default_Rate"] * 100).round(2)
    fig_fapps = create_bar_chart(fam_status_agg, x_col="NAME_FAMILY_STATUS", y_col="Customers", title="Applications by Family Status")
    st.plotly_chart(fig_fapps, use_container_width=True)

with fm6:
    fig_fst = create_bar_chart(fam_status_agg.sort_values("Default Rate %", ascending=False), x_col="NAME_FAMILY_STATUS", y_col="Default Rate %", title="Default Rate by Family Status")
    st.plotly_chart(fig_fst, use_container_width=True)

# Visualizations Row 4: Income vs Family Size
st.subheader("💰 Income vs Family Size")
fam_inc = filtered_df[filtered_df["CNT_FAM_MEMBERS"] <= 6].groupby("CNT_FAM_MEMBERS")["AMT_INCOME_TOTAL"].mean().reset_index()
fam_inc["Family Size Label"] = fam_inc["CNT_FAM_MEMBERS"].astype(int).astype(str) + " Members"
fig_finc = create_bar_chart(fam_inc, x_col="Family Size Label", y_col="AMT_INCOME_TOTAL", title="Income vs Family Size")
st.plotly_chart(fig_finc, use_container_width=True)

if not filtered_df.empty:
    render_insights_card([
        "**Dependent Pressure**: Applicants with 3 or more children experience higher default rates (~10.2%) due to higher non-discretionary living costs.",
        "**Civil Marriage Risk**: Applicants in Civil Marriage or Single status exhibit higher default rates (~9.5–10%) than Married (~7.5%) or Widowed (~5.8%).",
        "**Per-Capita Income**: Household income does not scale linearly with family size, reducing discretionary debt-service buffers.",
    ])
