import pandas as pd
import numpy as np
from typing import List, Optional


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Strips leading/trailing whitespaces from DataFrame column names."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def clean_target_variable(df: pd.DataFrame) -> pd.DataFrame:
    """Maps binary TARGET variable to human-readable labels."""
    df = df.copy()
    if "TARGET" in df.columns:
        df["TARGET"] = pd.to_numeric(df["TARGET"], errors="coerce").fillna(0).astype(int)
        df["Target Label"] = df["TARGET"].map({
            0: "Repaid (TARGET = 0)",
            1: "Default (TARGET = 1)"
        })
        df["Target Name"] = df["TARGET"].map({
            0: "Repaid",
            1: "Default"
        })
    return df


def clean_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans known dataset anomalies:
    - Replaces DAYS_EMPLOYED anomaly code (365243) with NaN
    - Handles invalid or negative days
    """
    df = df.copy()
    if "DAYS_EMPLOYED" in df.columns:
        df["DAYS_EMPLOYED"] = df["DAYS_EMPLOYED"].replace(365243, np.nan)
    return df


def clean_categorical_features(df: pd.DataFrame, categorical_cols: Optional[List[str]] = None) -> pd.DataFrame:
    """Fills missing values in key categorical columns with 'Unknown' and ensures string type."""
    df = df.copy()
    if categorical_cols is None:
        categorical_cols = [
            "NAME_CONTRACT_TYPE", "CODE_GENDER", "FLAG_OWN_CAR", "FLAG_OWN_REALTY",
            "NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE", "NAME_FAMILY_STATUS",
            "NAME_HOUSING_TYPE", "OCCUPATION_TYPE", "ORGANIZATION_TYPE"
        ]
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str)
    return df


def preprocess_home_credit_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Master preprocessing pipeline for Home Credit Default Risk dataset.
    Executes column cleaning, target standardization, anomaly treatment,
    and categorical value handling.
    """
    df = clean_column_names(df)
    df = clean_target_variable(df)
    df = clean_anomalies(df)
    df = clean_categorical_features(df)
    return df
