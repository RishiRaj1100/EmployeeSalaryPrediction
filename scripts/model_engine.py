"""
Model training and prediction logic for salary prediction system.
"""



import os
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
os.makedirs(log_dir, exist_ok=True)
import logging
log_file = os.path.join(log_dir, 'model_engine.log')
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')

# Add missing imports
from sklearn.ensemble import RandomForestRegressor
import joblib
import pandas as pd

def train_model(X, y):
    """Train a Random Forest model."""
    logging.info("Training Random Forest model.")
    model = RandomForestRegressor()
    model.fit(X, y)
    logging.info("Model training complete.")
    return model

def save_model(model, filepath):
    """Save trained model to disk."""
    # Ensure the directory exists before saving
    model_dir = os.path.dirname(os.path.abspath(filepath))
    os.makedirs(model_dir, exist_ok=True)
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
        # Ensure 'ID' column is numeric and Arrow-compatible
        if 'ID' in df.columns:
            df['ID'] = pd.to_numeric(df['ID'], errors='coerce')
            df = df.dropna(subset=['ID'])
            df['ID'] = df['ID'].astype(int)
        adjusted_preds = []
        for i, pred in enumerate(preds):
            row = df.iloc[i]
            dept_budget = row['Departmental Budget'] if 'Departmental Budget' in df.columns else pred
            market_ctc = row['Market CTC'] if 'Market CTC' in df.columns else pred
            previous_salary = row['Previous Salary'] if 'Previous Salary' in df.columns else pred
            experience = row['Experience'] if 'Experience' in df.columns else 0
            promotion = row.get('Promotion', False)
            current_ctc = row['Current CTC'] if 'Current CTC' in df.columns else previous_salary
            perf_rating = row['Performance Rating'] if 'Performance Rating' in df.columns else 3
            team_size = row['Team Size'] if 'Team Size' in df.columns else 1
            # Enhanced business logic:
            # - Freshers: If experience <= 1, salary is close to dept_budget or market_ctc, whichever is lower
            # - Experienced: Use model prediction, but ensure not below previous/current salary
            # - Promotion: If promoted, increase salary by 10-20%
            # - Performance Rating: Higher rating increases salary by up to 10%
            # - Team Size: Larger teams may get a small bump
            # - Always respect department budget and market CTC as bounds
            base_salary = pred
            if experience <= 1:
                base_salary = min(dept_budget, market_ctc)
            else:
                base_salary = max(pred, previous_salary, current_ctc)
            if promotion:
                base_salary *= 1.15  # 15% increase for promotion
            base_salary *= 1 + (perf_rating - 3) * 0.025  # 2.5% per rating above 3
            if team_size > 5:
                base_salary *= 1.05  # 5% bump for managing larger teams
            # Final adjustment
            low = max(dept_budget, base_salary * 0.95)
            high = min(market_ctc, base_salary * 1.10)
            optimal = min(max(base_salary, dept_budget), market_ctc)
            adjusted_preds.append({
                'low': low,
                'optimal': optimal,
                'high': high,
                'raw': pred,
                'dept_budget': dept_budget,
                'market_ctc': market_ctc,
                'previous_salary': previous_salary,
                'experience': experience,
                'promotion': promotion,
                'current_ctc': current_ctc,
                'perf_rating': perf_rating,
                'team_size': team_size
            })
        logging.info("Salary prediction and adjustment complete.")
        return adjusted_preds
    return preds
