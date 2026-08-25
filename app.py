import streamlit as st
import pandas as pd
from utils.page_helpers import apply_page_config, render_header, render_insights_card
from utils.data_loader import load_home_credit_data
from utils.kpis import calculate_home_credit_kpis, format_currency, format_percent, format_number
from utils.charts import create_bar_chart, create_donut_chart, create_scatter_plot

apply_page_config(page_title="Home Credit Analytics Hub", page_icon="🏦")

try:
    df = load_home_credit_data()
except Exception as e:
    st.error(f"Error loading Home Credit dataset: {e}")
    st.stop()

# Header
render_header(
    title="Home Credit Default Risk Intelligence Platform",
    subtitle="Enterprise Credit Risk Analytics & Default Prediction Platform • 20 Interactive Analytical Perspectives",
    badge="v2.5 Production Portfolio Suite",
)

kpis = calculate_home_credit_kpis(df)

# Pure Streamlit Metric Cards
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Applicants", format_number(kpis["total_applications"]), help="Total Loan Requests Analyzed")
c2.metric("Default Rate", format_percent(kpis["default_rate"]), f"{format_number(kpis['default_customers'])} Defaults", delta_color="inverse")
c3.metric("Total Credit Issued", format_currency(kpis["total_credit"]), "Cumulative Exposure")
c4.metric("Avg Client Income", format_currency(kpis["avg_income"]), "Annual Earnings")
c5.metric("Avg Applicant Age", f"{kpis['avg_age']:.1f} Yrs", f"Bureau Score: {kpis['avg_ext_score']:.2f}")

st.divider()

# Executive Visualizations
st.subheader("📊 Executive Portfolio Snapshot")
r1, r2, r3 = st.columns([1.2, 1.2, 1.6])

with r1:
    target_counts = df["Target Label"].value_counts().reset_index()
    target_counts.columns = ["Status", "Count"]
    fig_target = create_donut_chart(target_counts, names_col="Status", values_col="Count", title="Portfolio Default vs Repaid Share")
    st.plotly_chart(fig_target, use_container_width=True)

with r2:
    if "NAME_INCOME_TYPE" in df.columns:
        inc_agg = df.groupby("NAME_INCOME_TYPE")["TARGET"].agg(Default_Rate="mean", Count="count").reset_index()
        inc_agg["Default Rate %"] = (inc_agg["Default_Rate"] * 100).round(2)
        fig_inc = create_bar_chart(
            inc_agg.sort_values("Count", ascending=False).head(5),
            x_col="NAME_INCOME_TYPE",
            y_col="Default Rate %",
            title="Default Rate % by Top Income Types"
        )
        st.plotly_chart(fig_inc, use_container_width=True)

with r3:
    sample_df = df.sample(min(1500, len(df)), random_state=42)
    fig_scat = create_scatter_plot(
        sample_df,
        x_col="AMT_INCOME_TOTAL",
        y_col="AMT_CREDIT",
        color_col="Target Label",
        title="Credit Requested vs Income (Sample View)"
    )
    st.plotly_chart(fig_scat, use_container_width=True)

st.divider()

# 20 Analytical Perspectives Matrix in pure Streamlit containers
st.subheader("🗂️ 20 Comprehensive Analytical Perspectives")
st.caption("Select any perspective from the **Sidebar Navigation** or browse the summary below:")

pages_info = [
    ("01 Executive Overview", "📈", "Portfolio overview, default rates, volume, income and credit metrics."),
    ("02 Default Analysis", "🎯", "In-depth TARGET variable distribution across contract, income, and education."),
    ("03 Demographic Analysis", "👥", "Gender, age, marital status, and housing demographic risk profiles."),
    ("04 Age Analysis", "🎂", "Age cohorts (18–25 to 61+) and their direct correlation with repayment risk."),
    ("05 Gender Analysis", "👤", "Comparative benchmark between male and female credit applicants."),
    ("06 Income Analysis", "💰", "Income distribution (<50K to >500K) and default rates across salary tiers."),
    ("07 Credit Analysis", "💳", "Loan sizes requested, credit brackets, and default rates by loan size."),
    ("08 Annuity Analysis", "💵", "Annual loan payment obligations, annuity distribution, and repayment risk."),
    ("09 Income vs Credit", "⚖️", "Credit-to-Income leverage scatter plots and risk tiers (<2x to >6x)."),
    ("10 Annuity Burden", "📊", "Debt-to-Income burden ratio and repayment stress indicators."),
    ("11 Education Analysis", "🎓", "Education levels (Academic Degree to Lower Secondary) and default risk."),
    ("12 Employment Analysis", "💼", "Work tenure, high-risk occupations, and organization categories."),
    ("13 Family & Children", "👨‍👩‍👧", "Household size, number of dependents, and family status risk factors."),
    ("14 Housing & Assets", "🏠", "Car and real estate collateral ownership impact on default rates."),
    ("15 Contract Analysis", "📄", "Cash Loans vs Revolving Loans risk profiling and credit terms."),
    ("16 External Scores", "🌟", "EXT_SOURCE_1/2/3 predictive credit bureau score analysis."),
    ("17 Regional Risk", "🌍", "Regional population densities, city risk ratings, and address mismatches."),
    ("18 Missing Values", "🔍", "Data quality auditor, missing data heatmaps, and imputation strategy."),
    ("19 Correlation & Risk", "🔗", "Feature correlation heatmap against TARGET and key default drivers."),
    ("20 Customer Risk Explorer", "👤", "Search applicant by SK_ID_CURR, risk dossier card, and CSV downloads."),
]

cols = st.columns(4)
for idx, (title, icon, desc) in enumerate(pages_info):
    with cols[idx % 4]:
        with st.container(border=True):
            st.markdown(f"**{icon} {title}**")
            st.caption(desc)

st.divider()

# Executive Insights
render_insights_card([
    f"**Portfolio Default Rate**: Overall baseline default rate is **{format_percent(kpis['default_rate'])}** across **{format_number(kpis['total_applications'])}** total applicants.",
    f"**Capital Deployment**: Cumulative credit issued stands at **{format_currency(kpis['total_credit'])}** with average ticket size of **{format_currency(kpis['avg_credit'])}**.",
    f"**External Credit Bureau**: Average composite external score is **{kpis['avg_ext_score']:.3f}**, serving as the prime statistical predictor of default propensity.",
    "Navigate to individual pages from the sidebar to inspect granular breakdowns and download custom applicant cohorts.",
])
