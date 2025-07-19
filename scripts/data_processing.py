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
    # Define required columns and their default values
    required_cols = {
        'Name': 'Employee',
        'ID': '0',
        'Experience': 0,
        'Education': 'Unknown',
        'Job Role': 'Unknown',
        'Department': 'Unknown',
        'Location': 'Unknown',
        'Skills': 'Unknown',
        'Certifications': 'Unknown',
        'Previous Salary': 0,
        'Departmental Budget': 0,
        'Current CTC': 0,
        'Performance Rating': 3,
        'Internal/External': 'Unknown',
        'Market CTC': 0,
        'Company Size': 'Unknown',
        'Business Unit': 'Unknown',
        'Team Size': 1,
        'Age': 0
    }

    # Add missing required columns with default values
    for col, default in required_cols.items():
        if col not in df.columns:
            df[col] = default

    # Convert categorical columns to category dtype
    for col in required_cols:
        if col in df.columns and isinstance(required_cols[col], str):
            df[col] = df[col].astype('category')

    # Fill missing values for all columns
    for col in df.columns:
        if df[col].dtype.name == 'category':
            if 'Unknown' not in df[col].cat.categories:
                df[col] = df[col].cat.add_categories(['Unknown'])
            df[col] = df[col].fillna('Unknown')
        elif df[col].dtype == object:
            df[col] = df[col].fillna('Unknown')
        else:
            df[col] = df[col].fillna(0)

    # Ensure 'ID' column is numeric and Arrow-compatible
    if 'ID' in df.columns:
        df['ID'] = pd.to_numeric(df['ID'], errors='coerce')
        df = df.dropna(subset=['ID'])
        df['ID'] = df['ID'].astype(int)

    # Optionally, drop columns not used by the model (if needed)
    # model_features = list(required_cols.keys())
    # df = df[model_features]

    return df
