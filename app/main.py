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
                scrape_status.append(f"{row.get('Name','Employee')}: Market data not found, using fallback value ₹{market_ctc}")
            else:
                scrape_status.append(f"{row.get('Name','Employee')}: Market data fetched successfully (₹{market_ctc})")
            market_ctc_list.append(market_ctc)
        df_processed["Market CTC"] = market_ctc_list
        # Show scraping status to user
        for msg in scrape_status:
            st.info(msg)
        X = df_processed[["Experience", "Previous Salary"]]
        y = df_processed["Market CTC"]
        model = train_model(X, y)
        save_model(model, "../models/salary_model.pkl")
        adjusted_preds = predict_salary(model, X, df_processed)
        # Show results for each employee
        results = []
        for i, row in df.iterrows():
            pred = adjusted_preds[i]
            slip_data = row.to_dict()
            slip_data.update({
                "Predicted Salary": pred['optimal'],
                "Low Range": pred['low'],
                "High Range": pred['high'],
                "Department Budget": pred['dept_budget'],
                "Market CTC": pred['market_ctc']
            })
            from scripts.report_generator import salary_parity_analysis
            parity_score, bias_flag = salary_parity_analysis(slip_data)
            slip_data["Parity Score"] = parity_score
            slip_data["Bias Detected"] = bias_flag
            results.append(slip_data)
        st.write("Salary Prediction Results:", pd.DataFrame(results)[["Name","Predicted Salary","Low Range","High Range","Department Budget","Market CTC","Parity Score","Bias Detected"]])

        # Generate salary slip for first employee as example
        slip_path = f"../reports/salary_slip_{results[0]['ID']}.pdf"
        generate_salary_slip(results[0], slip_path)
        with open(slip_path, "rb") as f:
            st.download_button("Download Salary Slip (PDF)", f, file_name=os.path.basename(slip_path))


        # Generate and offer download for full Excel report
        from scripts.report_generator import generate_excel_report, generate_pdf_report
        excel_path = "../reports/salary_report.xlsx"
        generate_excel_report(results, excel_path)
        with open(excel_path, "rb") as f:
            st.download_button("Download Full Salary Report (Excel)", f, file_name="salary_report.xlsx")

        # Generate and offer download for full PDF report
        pdf_path = "../reports/salary_report.pdf"
        generate_pdf_report(results, pdf_path)
        with open(pdf_path, "rb") as f:
            st.download_button("Download Full Salary Report (PDF)", f, file_name="salary_report.pdf")
