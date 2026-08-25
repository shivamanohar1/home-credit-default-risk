import streamlit as st
import pandas as pd
from utils.page_helpers import apply_page_config, render_header, render_insights_card
from utils.data_loader import load_home_credit_data
from utils.filters import render_sidebar_filters
from utils.kpis import format_currency, format_percent, format_number, calculate_home_credit_kpis

apply_page_config(page_title="Customer Risk Explorer", page_icon="👤")
df = load_home_credit_data()
filtered_df, _ = render_sidebar_filters(df)

render_header(
    title="Page 20: Customer Risk Explorer & Export Engine",
    subtitle="Search individual customer dossiers by SK_ID_CURR, evaluate calculated risk indicators, and export custom segments.",
    badge="Underwriting Dossier",
)

# 1. Search Section by SK_ID_CURR
st.subheader("🔍 Instant Customer Search Engine")
search_id = st.text_input("Enter Customer SK_ID_CURR (e.g. 100002, 100003, 100004):", "")

if search_id:
    matched = df[df["SK_ID_CURR"].astype(str) == search_id.strip()]
    if not matched.empty:
        client = matched.iloc[0]
        st.subheader("📋 Customer Risk Profile Dossier")
        is_default = client.get("TARGET", 0) == 1
        badge_text = "🚨 High Default Risk (TARGET = 1)" if is_default else "✅ Low Default Risk (TARGET = 0)"
        
        with st.container(border=True):
            st.markdown(f"### Customer ID: #{client['SK_ID_CURR']} — **{badge_text}**")
            st.divider()
            
            # Customer Information Profile
            st.markdown("#### 👤 Customer & Loan Information")
            p1, p2, p3, p4 = st.columns(4)
            p1.metric("Age", f"{client.get('Age', 'N/A')} Yrs")
            p2.metric("Gender", f"{client.get('CODE_GENDER', 'N/A')}")
            p3.metric("Annual Income", format_currency(client.get('AMT_INCOME_TOTAL', 0)))
            p4.metric("Credit Amount", format_currency(client.get('AMT_CREDIT', 0)))

            p5, p6, p7, p8 = st.columns(4)
            p5.metric("Scheduled Annuity", format_currency(client.get('AMT_ANNUITY', 0)))
            p6.metric("Education", f"{client.get('NAME_EDUCATION_TYPE', 'N/A')}")
            p7.metric("Occupation", f"{client.get('OCCUPATION_TYPE', 'N/A')}")
            p8.metric("Family Status", f"{client.get('NAME_FAMILY_STATUS', 'N/A')}")

            p9, p10, p11, p12 = st.columns(4)
            p9.metric("Number of Children", f"{client.get('CNT_CHILDREN', 0)}")
            p10.metric("Housing Type", f"{client.get('NAME_HOUSING_TYPE', 'N/A')}")
            p11.metric("Car / Realty", f"{client.get('FLAG_OWN_CAR', 'N')} / {client.get('FLAG_OWN_REALTY', 'N')}")
            p12.metric("Contract Type", f"{client.get('NAME_CONTRACT_TYPE', 'N/A')}")

            st.divider()
            # Calculated Risk Indicators from Projects.ipynb
            st.markdown("#### 📐 Calculated Risk Indicators")
            r1, r2, r3, r4, r5 = st.columns(5)
            r1.metric("Credit-to-Income Ratio", f"{client.get('Credit to Income Ratio', 'N/A')}x")
            r2.metric("Annuity-to-Income Ratio", f"{client.get('Annuity Burden %', 'N/A')}%")
            r3.metric("Credit-to-Goods Ratio", f"{client.get('Credit to Goods Ratio', 'N/A')}x")
            r4.metric("Employment Years", f"{client.get('Employment Years', 'N/A')} Yrs")
            r5.metric("Average External Score", f"{client.get('Avg External Score', 'N/A')}")
    else:
        st.warning(f"Applicant ID #{search_id} not found in database.")

st.divider()

# 2. Filtered Applicant Records Data Table
st.subheader("📊 Filtered Customer Records Explorer")
default_cols = [
    "SK_ID_CURR", "TARGET", "Target Label", "CODE_GENDER", "Age", "NAME_EDUCATION_TYPE",
    "NAME_INCOME_TYPE", "OCCUPATION_TYPE", "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY",
    "Credit to Income Ratio", "Annuity Burden %", "Avg External Score"
]
avail_cols = [c for c in default_cols if c in filtered_df.columns]
sel_cols = st.multiselect("Customize Data Columns to Display:", options=filtered_df.columns.tolist(), default=avail_cols)
st.dataframe(filtered_df[sel_cols].head(1000).copy(), use_container_width=True, hide_index=True)

st.divider()

# 3. Exact 4 Download Options from Projects.ipynb
st.subheader("📥 Download Options")
d1, d2, d3, d4 = st.columns(4)

with d1:
    csv_filtered = filtered_df.head(25000).to_csv(index=False).encode("utf-8")
    st.download_button(
        "📄 Download Filtered CSV",
        data=csv_filtered,
        file_name="home_credit_filtered_customers.csv",
        mime="text/csv",
        use_container_width=True
    )

with d2:
    csv_default = filtered_df[filtered_df["TARGET"] == 1].head(20000).to_csv(index=False).encode("utf-8")
    st.download_button(
        "🚨 Download Default Customers CSV",
        data=csv_default,
        file_name="home_credit_default_customers.csv",
        mime="text/csv",
        use_container_width=True
    )

with d3:
    high_risk = filtered_df[(filtered_df["Credit to Income Ratio"] > 4.0) | (filtered_df["Avg External Score"] < 0.3)].head(20000)
    csv_high_risk = high_risk.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⚠️ Download High-Risk CSV",
        data=csv_high_risk,
        file_name="home_credit_high_risk_customers.csv",
        mime="text/csv",
        use_container_width=True
    )

with d4:
    kpis = calculate_home_credit_kpis(filtered_df)
    summary_df = pd.DataFrame([kpis])
    csv_summary = summary_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📊 Download Summary CSV",
        data=csv_summary,
        file_name="home_credit_portfolio_summary.csv",
        mime="text/csv",
        use_container_width=True
    )

render_insights_card([
    f"**Active Records**: **{format_number(len(filtered_df))}** applicants currently matching all selected sidebar filters.",
    "**Customer Dossier Engine**: Enter any SK_ID_CURR in the search box to view a full risk assessment profile.",
    "**Data Export Center**: Directly download Filtered CSV, Default Customers, High-Risk Watchlist, or Summary CSV for underwriting analysis.",
])
