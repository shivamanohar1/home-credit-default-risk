import pandas as pd
import numpy as np


def add_age_features(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates Age in years from DAYS_BIRTH and segments into 9 standard age cohorts."""
    df = df.copy()
    if "DAYS_BIRTH" in df.columns:
        df["Age"] = (df["DAYS_BIRTH"].abs() / 365.0).round(1)
        age_bins = [18, 26, 31, 36, 41, 46, 51, 56, 61, 100]
        age_labels = ["18–25", "26–30", "31–35", "36–40", "41–45", "46–50", "51–55", "56–60", "61+"]
        df["Age Group"] = pd.cut(df["Age"], bins=age_bins, labels=age_labels, right=False)
    return df


def add_employment_features(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates Employment Years from DAYS_EMPLOYED and segments into tenure tiers."""
    df = df.copy()
    if "DAYS_EMPLOYED" in df.columns:
        clean_days_emp = df["DAYS_EMPLOYED"].replace(365243, np.nan)
        df["Employment Years"] = (clean_days_emp.abs() / 365.0).round(1)
        emp_bins = [0, 1, 3, 5, 10, 20, 100]
        emp_labels = ["< 1 Year", "1–3 Years", "3–5 Years", "5–10 Years", "10–20 Years", "20+ Years"]
        df["Employment Tier"] = pd.cut(df["Employment Years"], bins=emp_bins, labels=emp_labels, right=False)
    return df


def add_financial_bins(df: pd.DataFrame) -> pd.DataFrame:
    """Creates discrete demographic and underwriting bins for Income, Credit, and Annuity."""
    df = df.copy()

    # Income Groups
    if "AMT_INCOME_TOTAL" in df.columns:
        inc_bins = [0, 50000, 100000, 150000, 200000, 300000, 500000, np.inf]
        inc_labels = ["Below 50K", "50K–100K", "100K–150K", "150K–200K", "200K–300K", "300K–500K", "Above 500K"]
        df["Income Group"] = pd.cut(df["AMT_INCOME_TOTAL"], bins=inc_bins, labels=inc_labels, right=False)

    # Credit Groups
    if "AMT_CREDIT" in df.columns:
        crd_bins = [0, 100000, 300000, 500000, 700000, 1000000, np.inf]
        crd_labels = ["Below 100K", "100K–300K", "300K–500K", "500K–700K", "700K–1M", "Above 1M"]
        df["Credit Group"] = pd.cut(df["AMT_CREDIT"], bins=crd_bins, labels=crd_labels, right=False)

    # Annuity Groups
    if "AMT_ANNUITY" in df.columns:
        ann_bins = [0, 15000, 30000, 45000, 60000, 100000, np.inf]
        ann_labels = ["< 15K", "15K–30K", "30K–45K", "45K–60K", "60K–100K", "> 100K"]
        df["Annuity Group"] = pd.cut(df["AMT_ANNUITY"], bins=ann_bins, labels=ann_labels, right=False)

    return df


def add_leverage_and_burden_features(df: pd.DataFrame) -> pd.DataFrame:
    """Computes financial leverage multiples, debt burden percentages, and risk tiers."""
    df = df.copy()
    income_valid = df["AMT_INCOME_TOTAL"].replace(0, np.nan) if "AMT_INCOME_TOTAL" in df.columns else None

    # Credit-to-Income Ratio
    if income_valid is not None and "AMT_CREDIT" in df.columns:
        df["Credit to Income Ratio"] = (df["AMT_CREDIT"] / income_valid).round(2)
        lev_bins = [0, 2, 4, 6, np.inf]
        lev_labels = ["Low (< 2x)", "Moderate (2–4x)", "High (4–6x)", "Very High (> 6x)"]
        df["Credit Leverage Group"] = pd.cut(df["Credit to Income Ratio"], bins=lev_bins, labels=lev_labels, right=False)

    # Annuity-to-Income Ratio (Debt-to-Income Repayment Burden)
    if income_valid is not None and "AMT_ANNUITY" in df.columns:
        df["Annuity to Income Ratio"] = (df["AMT_ANNUITY"] / income_valid).round(4)
        df["Annuity Burden %"] = (df["Annuity to Income Ratio"] * 100).round(2)
        burd_bins = [0, 10, 20, 30, 40, np.inf]
        burd_labels = ["Low (< 10%)", "Moderate (10–20%)", "Substantial (20–30%)", "High (30–40%)", "Severe (> 40%)"]
        df["Annuity Burden Tier"] = pd.cut(df["Annuity Burden %"], bins=burd_bins, labels=burd_labels, right=False)

    # Credit-to-Goods Price Ratio
    if "AMT_CREDIT" in df.columns and "AMT_GOODS_PRICE" in df.columns:
        df["Credit to Goods Ratio"] = (df["AMT_CREDIT"] / df["AMT_GOODS_PRICE"].replace(0, np.nan)).round(2)

    return df


def add_external_score_features(df: pd.DataFrame) -> pd.DataFrame:
    """Computes mean composite external credit score and risk ratings."""
    df = df.copy()
    ext_cols = [c for c in ["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"] if c in df.columns]
    if ext_cols:
        df["Avg External Score"] = df[ext_cols].mean(axis=1).round(3)
        ext_bins = [0, 0.25, 0.50, 0.75, 1.01]
        ext_labels = ["Poor (< 0.25)", "Fair (0.25–0.50)", "Good (0.50–0.75)", "Excellent (0.75–1.0)"]
        df["External Score Rating"] = pd.cut(df["Avg External Score"], bins=ext_bins, labels=ext_labels, right=False)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Master feature engineering pipeline for Home Credit Default Risk dataset.
    Executes age derivation, tenure calculation, financial binning, leverage ratios,
    and external bureau score compositing.
    """
    df = add_age_features(df)
    df = add_employment_features(df)
    df = add_financial_bins(df)
    df = add_leverage_and_burden_features(df)
    df = add_external_score_features(df)
    return df
