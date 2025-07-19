"""
Model training and prediction logic for salary prediction system.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib

import logging
logging.basicConfig(filename='../logs/model_engine.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')

def train_model(X, y):
    """Train a Random Forest model."""
    logging.info("Training Random Forest model.")
    model = RandomForestRegressor()
    model.fit(X, y)
    logging.info("Model training complete.")
    return model

def save_model(model, filepath):
    """Save trained model to disk."""
    joblib.dump(model, filepath)
    logging.info(f"Model saved to {filepath}.")

def load_model(filepath):
    """Load model from disk."""
    logging.info(f"Loading model from {filepath}.")
    return joblib.load(filepath)


def predict_salary(model, X, df=None):
    """Predict salary and adjust based on department budget and market benchmark."""
    logging.info("Running salary prediction.")
    preds = model.predict(X)
    if df is not None:
        adjusted_preds = []
        for i, pred in enumerate(preds):
            dept_budget = df.iloc[i].get('Departmental Budget', pred)
            market_ctc = df.iloc[i].get('Market CTC', pred)
            low = max(dept_budget, pred * 0.95)
            high = min(market_ctc, pred * 1.05)
            optimal = min(max(pred, dept_budget), market_ctc)
            adjusted_preds.append({'low': low, 'optimal': optimal, 'high': high, 'raw': pred, 'dept_budget': dept_budget, 'market_ctc': market_ctc})
        logging.info("Salary prediction and adjustment complete.")
        return adjusted_preds
    return preds
