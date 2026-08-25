import pandas as pd
import numpy as np
from typing import Dict, Any, Union


def format_currency(value: Union[int, float]) -> str:
    """Formats numeric value into clean currency notation ($1.23M, $45.6K, $789)."""
    if pd.isna(value):
        return "$0.00"
    sign = "-" if value < 0 else ""
    abs_val = abs(value)
    if abs_val >= 1_000_000:
        return f"{sign}${abs_val / 1_000_000:.2f}M"
    elif abs_val >= 1_000:
        return f"{sign}${abs_val / 1_000:.1f}K"
    return f"{sign}${abs_val:,.2f}"


def format_percent(value: Union[int, float]) -> str:
    """Formats decimal or percentage float into formatted percentage string."""
    if pd.isna(value):
        return "0.0%"
    return f"{value:.2f}%"


def format_number(value: Union[int, float]) -> str:
    """Formats count with comma separators."""
    if pd.isna(value):
        return "0"
    if isinstance(value, float):
        return f"{int(value):,}" if value.is_integer() else f"{value:,.1f}"
    return f"{value:,}"


def format_ratio(value: Union[int, float], suffix: str = "x") -> str:
    """Formats a ratio value."""
    if pd.isna(value):
        return f"0.00{suffix}"
    return f"{value:.2f}{suffix}"


def calculate_home_credit_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Computes all core portfolio KPIs for Home Credit Default Risk."""
    if df.empty:
        return {
            "total_applications": 0,
            "default_customers": 0,
            "non_default_customers": 0,
            "default_rate": 0.0,
            "non_default_rate": 0.0,
            "total_credit": 0.0,
            "avg_credit": 0.0,
            "median_credit": 0.0,
            "max_credit": 0.0,
            "min_credit": 0.0,
            "total_income": 0.0,
            "avg_income": 0.0,
            "median_income": 0.0,
            "max_income": 0.0,
            "avg_annuity": 0.0,
            "median_annuity": 0.0,
            "max_annuity": 0.0,
            "avg_age": 0.0,
            "avg_ext_score": 0.0,
            "avg_credit_income_ratio": 0.0,
            "avg_annuity_burden": 0.0,
        }

    total_apps = len(df)
    defaults = int((df["TARGET"] == 1).sum()) if "TARGET" in df.columns else 0
    non_defaults = int((df["TARGET"] == 0).sum()) if "TARGET" in df.columns else 0
    default_rate = round(defaults / total_apps * 100, 2) if total_apps > 0 else 0.0
    non_default_rate = round(100.0 - default_rate, 2) if total_apps > 0 else 0.0

    tot_credit = float(df["AMT_CREDIT"].sum()) if "AMT_CREDIT" in df.columns else 0.0
    avg_credit = float(df["AMT_CREDIT"].mean()) if "AMT_CREDIT" in df.columns else 0.0
    med_credit = float(df["AMT_CREDIT"].median()) if "AMT_CREDIT" in df.columns else 0.0
    max_credit = float(df["AMT_CREDIT"].max()) if "AMT_CREDIT" in df.columns else 0.0
    min_credit = float(df["AMT_CREDIT"].min()) if "AMT_CREDIT" in df.columns else 0.0

    tot_income = float(df["AMT_INCOME_TOTAL"].sum()) if "AMT_INCOME_TOTAL" in df.columns else 0.0
    avg_income = float(df["AMT_INCOME_TOTAL"].mean()) if "AMT_INCOME_TOTAL" in df.columns else 0.0
    med_income = float(df["AMT_INCOME_TOTAL"].median()) if "AMT_INCOME_TOTAL" in df.columns else 0.0
    max_income = float(df["AMT_INCOME_TOTAL"].max()) if "AMT_INCOME_TOTAL" in df.columns else 0.0

    avg_annuity = float(df["AMT_ANNUITY"].mean()) if "AMT_ANNUITY" in df.columns else 0.0
    med_annuity = float(df["AMT_ANNUITY"].median()) if "AMT_ANNUITY" in df.columns else 0.0
    max_annuity = float(df["AMT_ANNUITY"].max()) if "AMT_ANNUITY" in df.columns else 0.0

    avg_age = float(df["Age"].mean()) if "Age" in df.columns else 0.0
    avg_ext = float(df["Avg External Score"].mean()) if "Avg External Score" in df.columns else 0.0
    avg_cir = float(df["Credit to Income Ratio"].mean()) if "Credit to Income Ratio" in df.columns else 0.0
    avg_burd = float(df["Annuity Burden %"].mean()) if "Annuity Burden %" in df.columns else 0.0

    return {
        "total_applications": total_apps,
        "default_customers": defaults,
        "non_default_customers": non_defaults,
        "default_rate": default_rate,
        "non_default_rate": non_default_rate,
        "total_credit": round(tot_credit, 2),
        "avg_credit": round(avg_credit, 2),
        "median_credit": round(med_credit, 2),
        "max_credit": round(max_credit, 2),
        "min_credit": round(min_credit, 2),
        "total_income": round(tot_income, 2),
        "avg_income": round(avg_income, 2),
        "median_income": round(med_income, 2),
        "max_income": round(max_income, 2),
        "avg_annuity": round(avg_annuity, 2),
        "median_annuity": round(med_annuity, 2),
        "max_annuity": round(max_annuity, 2),
        "avg_age": round(avg_age, 1),
        "avg_ext_score": round(avg_ext, 3),
        "avg_credit_income_ratio": round(avg_cir, 2),
        "avg_annuity_burden": round(avg_burd, 2),
    }
