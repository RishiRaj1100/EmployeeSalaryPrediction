"""
Data processing and feature engineering for salary prediction system.
"""
import pandas as pd
import numpy as np

def load_employee_data(filepath):
    """Load employee data from CSV/Excel."""
    return pd.read_csv(filepath)

def preprocess_employee_data(df):
    """Basic preprocessing and feature engineering."""
    # Example: Convert categorical columns to category dtype
    categorical_cols = ['Education', 'Job Role', 'Department', 'Location', 'Skills', 'Certifications', 'Internal/External', 'Company Size', 'Business Unit']
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype('category')
    # Example: Fill missing values
    df = df.fillna(0)
    return df
