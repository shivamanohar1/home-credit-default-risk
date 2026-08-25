import streamlit as st
import pandas as pd
from utils.page_helpers import apply_page_config, render_header, render_insights_card
from utils.data_loader import load_home_credit_data
from utils.filters import render_sidebar_filters
from utils.kpis import format_number, format_percent
from utils.charts import create_bar_chart, create_donut_chart

apply_page_config(page_title="Demographic Analysis", page_icon="👥")
df = load_home_credit_data()
filtered_df, _ = render_sidebar_filters(df)

render_header(
    title="Page 3: Customer Demographic Analysis",
    subtitle="Understand demographic profiles, household structures, and credit delinquency across borrower segments.",
    badge="Demographic BI",
)

total_clients = len(filtered_df)
avg_age = filtered_df["Age"].mean() if "Age" in filtered_df.columns and total_clients > 0 else 0.0
male_count = (filtered_df["CODE_GENDER"] == "M").sum() if "CODE_GENDER" in filtered_df.columns else 0
female_count = (filtered_df["CODE_GENDER"] == "F").sum() if "CODE_GENDER" in filtered_df.columns else 0
avg_fam_size = filtered_df["CNT_FAM_MEMBERS"].mean() if "CNT_FAM_MEMBERS" in filtered_df.columns and total_clients > 0 else 0.0

# Exact 5 KPI Cards from Projects.ipynb
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Customers", format_number(total_clients))
c2.metric("Average Age", f"{avg_age:.1f} Yrs")
c3.metric("Male Customers", format_number(male_count), f"{(male_count/total_clients*100):.1f}% Share" if total_clients > 0 else "")
c4.metric("Female Customers", format_number(female_count), f"{(female_count/total_clients*100):.1f}% Share" if total_clients > 0 else "")
c5.metric("Average Family Size", f"{avg_fam_size:.1f} Members")

st.divider()

# Visualizations Row 1: Customers by Gender & Customers by Age Group
st.subheader("👥 Gender & Age Cohort Demographics")
dm1, dm2 = st.columns(2)
with dm1:
    gender_dist = filtered_df[filtered_df["CODE_GENDER"] != "XNA"]["CODE_GENDER"].value_counts().reset_index()
    gender_dist.columns = ["Gender", "Count"]
    fig_g = create_donut_chart(gender_dist, names_col="Gender", values_col="Count", title="Customers by Gender")
    st.plotly_chart(fig_g, use_container_width=True)

with dm2:
    if "Age Group" in filtered_df.columns:
        age_dist = filtered_df["Age Group"].value_counts().sort_index().reset_index()
        age_dist.columns = ["Age Group", "Count"]
        fig_ag = create_bar_chart(age_dist, x_col="Age Group", y_col="Count", title="Customers by Age Group")
        st.plotly_chart(fig_ag, use_container_width=True)

# Visualizations Row 2: Customers by Family Status & Customers by Education
st.subheader("👨‍👩‍👧 Family Status & Education Level")
dm3, dm4 = st.columns(2)
with dm3:
    if "NAME_FAMILY_STATUS" in filtered_df.columns:
        fam_dist = filtered_df["NAME_FAMILY_STATUS"].value_counts().reset_index()
        fam_dist.columns = ["Family Status", "Count"]
        fig_fam = create_bar_chart(fam_dist, x_col="Family Status", y_col="Count", title="Customers by Family Status")
        st.plotly_chart(fig_fam, use_container_width=True)

with dm4:
    if "NAME_EDUCATION_TYPE" in filtered_df.columns:
        edu_dist = filtered_df["NAME_EDUCATION_TYPE"].value_counts().reset_index()
        edu_dist.columns = ["Education", "Count"]
        fig_edu = create_bar_chart(edu_dist, x_col="Education", y_col="Count", title="Customers by Education")
        st.plotly_chart(fig_edu, use_container_width=True)

# Visualizations Row 3: Customers by Housing Type & Interactive Default Rate by Demographic Group
st.subheader("🏠 Housing Type & Default Rate by Demographic Group")
dm5, dm6 = st.columns(2)
with dm5:
    if "NAME_HOUSING_TYPE" in filtered_df.columns:
        house_dist = filtered_df["NAME_HOUSING_TYPE"].value_counts().reset_index()
        house_dist.columns = ["Housing Type", "Count"]
        fig_house = create_bar_chart(house_dist, x_col="Housing Type", y_col="Count", title="Customers by Housing Type")
        st.plotly_chart(fig_house, use_container_width=True)

with dm6:
    demo_opts = {
        "Family Status": "NAME_FAMILY_STATUS",
        "Gender": "CODE_GENDER",
        "Age Group": "Age Group",
        "Education": "NAME_EDUCATION_TYPE",
        "Housing Type": "NAME_HOUSING_TYPE"
    }
    sel_demo = st.selectbox("Select Demographic Dimension for Default Rate Analysis:", list(demo_opts.keys()))
    col_name = demo_opts[sel_demo]
    
    if col_name in filtered_df.columns:
        demo_dr = filtered_df.groupby(col_name)["TARGET"].agg(Customers="count", Default_Rate="mean").reset_index()
        demo_dr["Default Rate %"] = (demo_dr["Default_Rate"] * 100).round(2)
        fig_demo_dr = create_bar_chart(
            demo_dr.sort_values("Default Rate %", ascending=False),
            x_col=col_name,
            y_col="Default Rate %",
            title=f"Default Rate by {sel_demo}"
        )
        st.plotly_chart(fig_demo_dr, use_container_width=True)

if total_clients > 0:
    render_insights_card([
        "**Female Volume Majority**: Female applicants constitute nearly two-thirds (~66%) of the overall applicant pool.",
        "**Family Structure**: Married applicants account for ~64% of volume with an average family size of ~2.2 members.",
        "**Housing Security**: ~88% of clients live in standard house/apartments, while applicants in Rented Apartments or Living with Parents exhibit higher default rates (~10-11%).",
    ])
