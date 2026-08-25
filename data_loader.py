import os
import glob
import pandas as pd
import streamlit as st
from typing import Optional
from utils.preprocessing import preprocess_home_credit_data
from utils.features import engineer_features

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(WORKSPACE_ROOT, "data")


def get_dataset_path() -> str:
    """Finds application_train.csv in data/ or workspace directory."""
    candidates = [
        os.path.join(DATA_DIR, "application_train.csv"),
        os.path.join(WORKSPACE_ROOT, "application_train.csv"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p

    # Fallback recursive search
    csv_files = glob.glob(os.path.join(WORKSPACE_ROOT, "**", "*.csv"), recursive=True)
    for f in csv_files:
        if any(w in os.path.basename(f).lower() for w in ["train", "application", "credit"]):
            return f
    if csv_files:
        return csv_files[0]

    raise FileNotFoundError("Could not find application_train.csv dataset in workspace.")


def load_raw_data(max_rows: Optional[int] = None) -> pd.DataFrame:
    """Loads raw application_train.csv without transformations."""
    csv_path = get_dataset_path()
    return pd.read_csv(csv_path, nrows=max_rows)


@st.cache_data(show_spinner="Loading and Preprocessing Home Credit Default Risk Dataset...")
def load_home_credit_data(max_rows: Optional[int] = None) -> pd.DataFrame:
    """
    Loads application_train.csv and applies complete preprocessing and feature engineering
    pipelines across all 20 Streamlit analytical perspectives.
    """
    df = load_raw_data(max_rows=max_rows)
    df = preprocess_home_credit_data(df)
    df = engineer_features(df)
    return df
