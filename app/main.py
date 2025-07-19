"""
Streamlit app entry point for AI Employee-Based Salary Prediction System.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st

st.title("AI Employee-Based Salary Prediction System")
st.write("A smart HR tool for salary decisioning, parity auditing & market alignment.")


import pandas as pd
from scripts.data_processing import load_employee_data, preprocess_employee_data
from scripts.model_engine import train_model, save_model, load_model, predict_salary
from scripts.report_generator import generate_salary_slip
import os

from scripts.market_scraper import fetch_market_salary

st.header("Upload Employee Data")
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    # Ensure 'ID' column is numeric and Arrow-compatible
    if 'ID' in df.columns:
        df['ID'] = pd.to_numeric(df['ID'], errors='coerce')
        df = df.dropna(subset=['ID'])
        df['ID'] = df['ID'].astype(int)
    st.write("Preview of uploaded data:", df.head())
    df_processed = preprocess_employee_data(df)

    if st.button("Train Model & Predict Salary"):
        # For demo, use Experience and Previous Salary as features, Market CTC as target
        # Fetch market salary for each employee
        market_ctc_list = []
        scrape_status = []
        for i, row in df_processed.iterrows():
            job_role = row.get("Job Role", "")
            location = row.get("Location", "")
            market_ctc = fetch_market_salary(job_role, location)
            if market_ctc is None:
                market_ctc = row.get("Market CTC", 0)
                # Do not append fallback info message
            else:
                scrape_status.append(f"{row.get('Name','Employee')}: Market data fetched successfully (₹{market_ctc})")
            market_ctc_list.append(market_ctc)
        df_processed["Market CTC"] = market_ctc_list
        # Show only successful scraping status to user
        for msg in scrape_status:
            st.info(msg)
        # Dynamically select numeric features for model training
        numeric_cols = df_processed.select_dtypes(include=["number"]).columns.tolist()
        feature_cols = [col for col in ["Experience", "Previous Salary"] if col in numeric_cols]
        if not feature_cols:
            # If neither column is present, use all numeric columns except target
            feature_cols = [col for col in numeric_cols if col != "Market CTC"]
        if not feature_cols:
            # If still no features, create a dummy column of zeros
            df_processed["DummyFeature"] = 0
            feature_cols = ["DummyFeature"]
        X = df_processed[feature_cols]
        y = df_processed["Market CTC"]
        model = train_model(X, y)
        save_model(model, "../models/salary_model.pkl")
        adjusted_preds = predict_salary(model, X, df_processed)
        # Show results for each employee
        results = []
        expected_cols = ["ID","Name","Predicted Salary","Low Range","High Range","Department Budget","Market CTC","Parity Score","Bias Detected"]
        for i, row in df.iterrows():
            pred = adjusted_preds[i]
            slip_data = row.to_dict()
            # Fill missing input columns with defaults
            slip_data.setdefault("ID", i+1)
            slip_data.setdefault("Name", f"Employee {i+1}")
            slip_data["Predicted Salary"] = pred.get('optimal', 0)
            slip_data["Low Range"] = pred.get('low', 0)
            slip_data["High Range"] = pred.get('high', 0)
            slip_data["Department Budget"] = pred.get('dept_budget', 0)
            slip_data["Market CTC"] = pred.get('market_ctc', 0)
            from scripts.report_generator import salary_parity_analysis
            parity_score, bias_flag = salary_parity_analysis(slip_data)
            slip_data["Parity Score"] = parity_score
            slip_data["Bias Detected"] = bias_flag
            results.append(slip_data)
        # Ensure all expected columns are present in results
        results_df = pd.DataFrame(results)
        for col in expected_cols:
            if col not in results_df.columns:
                results_df[col] = "N/A"
        st.write("Salary Prediction Results:", results_df[expected_cols])

        # Generate salary slip for first employee as example
        slip_path = f"reports/salary_slip_{results[0].get('ID','1')}.pdf"
        generate_salary_slip(results[0], slip_path)
        with open(slip_path, "rb") as f:
            st.download_button("Download Salary Slip (PDF)", f, file_name=os.path.basename(slip_path))

        # Generate and offer download for full Excel report
        from scripts.report_generator import generate_excel_report, generate_pdf_report
        excel_path = "reports/salary_report.xlsx"
        generate_excel_report(results, excel_path)
        with open(excel_path, "rb") as f:
            st.download_button("Download Full Salary Report (Excel)", f, file_name="salary_report.xlsx")

        # Generate and offer download for full PDF report
        pdf_path = "reports/salary_report.pdf"
        generate_pdf_report(results, pdf_path)
        with open(pdf_path, "rb") as f:
            st.download_button("Download Full Salary Report (PDF)", f, file_name="salary_report.pdf")
