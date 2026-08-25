import streamlit as st
import pandas as pd
from typing import Tuple, Dict, Any


def render_sidebar_filters(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Renders enterprise sidebar filter controls for Home Credit Default Risk dataset
    matching all common filters defined in Projects.ipynb.
    """
    st.sidebar.markdown("### 🎛️ Underwriting Filters")
    filtered_df = df.copy()
    filters_applied = {}

    # 1. Target Status Filter
    if "TARGET" in df.columns:
        target_opt = st.sidebar.radio(
            "🎯 Loan Status (TARGET)",
            options=["All Applicants", "Repaid (TARGET = 0)", "Default (TARGET = 1)"],
            index=0,
            help="Filter by loan repayment status."
        )
        if target_opt == "Repaid (TARGET = 0)":
            filtered_df = filtered_df[filtered_df["TARGET"] == 0]
            filters_applied["target"] = 0
        elif target_opt == "Default (TARGET = 1)":
            filtered_df = filtered_df[filtered_df["TARGET"] == 1]
            filters_applied["target"] = 1

    st.sidebar.markdown("---")

    # 2. Gender Filter
    if "CODE_GENDER" in df.columns:
        gender_options = [g for g in sorted(df["CODE_GENDER"].dropna().unique().tolist()) if g != "XNA"]
        sel_gender = st.sidebar.multiselect("👤 Gender", options=gender_options, default=[], help="Filter by applicant gender.")
        if sel_gender:
            filtered_df = filtered_df[filtered_df["CODE_GENDER"].isin(sel_gender)]
            filters_applied["gender"] = sel_gender

    # 3. Age Range Filter
    if "Age" in df.columns and not df.empty:
        min_age = int(df["Age"].min())
        max_age = int(df["Age"].max())
        sel_age = st.sidebar.slider("🎂 Age Range (Years)", min_value=min_age, max_value=max_age, value=(min_age, max_age))
        if sel_age != (min_age, max_age):
            filtered_df = filtered_df[(filtered_df["Age"] >= sel_age[0]) & (filtered_df["Age"] <= sel_age[1])]
            filters_applied["age_range"] = sel_age

    # 4. Income Range Filter
    if "AMT_INCOME_TOTAL" in df.columns and not df.empty:
        max_inc_val = float(df["AMT_INCOME_TOTAL"].quantile(0.99))
        min_inc_val = float(df["AMT_INCOME_TOTAL"].min())
        sel_inc = st.sidebar.slider(
            "💰 Annual Income Range ($)",
            min_value=int(min_inc_val),
            max_value=int(max_inc_val),
            value=(int(min_inc_val), int(max_inc_val)),
            step=5000,
            format="$%d"
        )
        if sel_inc != (int(min_inc_val), int(max_inc_val)):
            filtered_df = filtered_df[(filtered_df["AMT_INCOME_TOTAL"] >= sel_inc[0]) & (filtered_df["AMT_INCOME_TOTAL"] <= sel_inc[1])]
            filters_applied["income_range"] = sel_inc

    # 5. Credit Range Filter
    if "AMT_CREDIT" in df.columns and not df.empty:
        max_crd_val = float(df["AMT_CREDIT"].quantile(0.99))
        min_crd_val = float(df["AMT_CREDIT"].min())
        sel_crd = st.sidebar.slider(
            "💳 Credit Amount Range ($)",
            min_value=int(min_crd_val),
            max_value=int(max_crd_val),
            value=(int(min_crd_val), int(max_crd_val)),
            step=25000,
            format="$%d"
        )
        if sel_crd != (int(min_crd_val), int(max_crd_val)):
            filtered_df = filtered_df[(filtered_df["AMT_CREDIT"] >= sel_crd[0]) & (filtered_df["AMT_CREDIT"] <= sel_crd[1])]
            filters_applied["credit_range"] = sel_crd

    # 6. Advanced Demographic & Product Filters in an Expander
    with st.sidebar.expander("🔍 Additional Dimension Filters", expanded=False):
        # Contract Type
        if "NAME_CONTRACT_TYPE" in df.columns:
            contracts = sorted(df["NAME_CONTRACT_TYPE"].dropna().unique().tolist())
            sel_contract = st.multiselect("📄 Contract Type", options=contracts)
            if sel_contract:
                filtered_df = filtered_df[filtered_df["NAME_CONTRACT_TYPE"].isin(sel_contract)]
                filters_applied["contract_type"] = sel_contract

        # Income Type
        if "NAME_INCOME_TYPE" in df.columns:
            incomes = sorted(df["NAME_INCOME_TYPE"].dropna().unique().tolist())
            sel_inc_type = st.multiselect("💼 Income Type", options=incomes)
            if sel_inc_type:
                filtered_df = filtered_df[filtered_df["NAME_INCOME_TYPE"].isin(sel_inc_type)]
                filters_applied["income_type"] = sel_inc_type

        # Education Type
        if "NAME_EDUCATION_TYPE" in df.columns:
            edus = sorted(df["NAME_EDUCATION_TYPE"].dropna().unique().tolist())
            sel_edu = st.multiselect("🎓 Education Level", options=edus)
            if sel_edu:
                filtered_df = filtered_df[filtered_df["NAME_EDUCATION_TYPE"].isin(sel_edu)]
                filters_applied["education"] = sel_edu

        # Family Status
        if "NAME_FAMILY_STATUS" in df.columns:
            fam_status = sorted(df["NAME_FAMILY_STATUS"].dropna().unique().tolist())
            sel_fam = st.multiselect("👨‍👩‍👧 Family Status", options=fam_status)
            if sel_fam:
                filtered_df = filtered_df[filtered_df["NAME_FAMILY_STATUS"].isin(sel_fam)]
                filters_applied["family_status"] = sel_fam

        # Housing Type
        if "NAME_HOUSING_TYPE" in df.columns:
            houses = sorted(df["NAME_HOUSING_TYPE"].dropna().unique().tolist())
            sel_house = st.multiselect("🏠 Housing Type", options=houses)
            if sel_house:
                filtered_df = filtered_df[filtered_df["NAME_HOUSING_TYPE"].isin(sel_house)]
                filters_applied["housing_type"] = sel_house

        # Car Ownership
        if "FLAG_OWN_CAR" in df.columns:
            car_opts = sorted(df["FLAG_OWN_CAR"].dropna().unique().tolist())
            sel_car = st.multiselect("🚗 Car Ownership", options=car_opts, format_func=lambda x: "Yes (Car Owner)" if x == "Y" else "No Car")
            if sel_car:
                filtered_df = filtered_df[filtered_df["FLAG_OWN_CAR"].isin(sel_car)]
                filters_applied["own_car"] = sel_car

        # Property Ownership
        if "FLAG_OWN_REALTY" in df.columns:
            realty_opts = sorted(df["FLAG_OWN_REALTY"].dropna().unique().tolist())
            sel_realty = st.multiselect("🏢 Realty Ownership", options=realty_opts, format_func=lambda x: "Yes (Property Owner)" if x == "Y" else "No Property")
            if sel_realty:
                filtered_df = filtered_df[filtered_df["FLAG_OWN_REALTY"].isin(sel_realty)]
                filters_applied["own_realty"] = sel_realty

        # Occupation Type
        if "OCCUPATION_TYPE" in df.columns:
            occs = [o for o in sorted(df["OCCUPATION_TYPE"].dropna().unique().tolist()) if o != "Unknown"]
            sel_occ = st.multiselect("🛠️ Occupation", options=occs)
            if sel_occ:
                filtered_df = filtered_df[filtered_df["OCCUPATION_TYPE"].isin(sel_occ)]
                filters_applied["occupation"] = sel_occ

    st.sidebar.markdown("---")
    total_recs = len(df)
    filtered_recs = len(filtered_df)
    pct = (filtered_recs / total_recs * 100) if total_recs > 0 else 0.0

    st.sidebar.metric("Filtered Portfolio", f"{filtered_recs:,}", f"{pct:.1f}% of total")

    return filtered_df, filters_applied
