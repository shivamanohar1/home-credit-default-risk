import streamlit as st
from typing import List, Optional


def apply_page_config(page_title: str = "Home Credit Default Risk", page_icon: str = "🏦"):
    """Configures Streamlit page layout and metadata."""
    st.set_page_config(
        page_title=f"{page_title} | Home Credit Risk Intelligence",
        page_icon=page_icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )


def render_header(title: str, subtitle: str, badge: Optional[str] = None):
    """Renders clean page header with category badge, title, and descriptive subtitle."""
    if badge:
        st.caption(f"🛡️ **Enterprise Risk Analytics** • {badge}")
    st.title(title)
    st.caption(subtitle)
    st.divider()


def render_formula_card(formula_name: str, formula_math: str, formula_desc: str):
    """Renders mathematical calculation formula callout."""
    with st.container(border=True):
        st.markdown(f"**📐 Metric Formula: {formula_name}**")
        st.code(formula_math, language="text")
        st.caption(formula_desc)


def render_insights_card(insights: List[str], title: str = "Key Underwriting & Risk Insights"):
    """Renders structured key business insights using native Streamlit container."""
    with st.container(border=True):
        st.subheader(f"💡 {title}")
        for insight in insights:
            st.markdown(f"• {insight}")
