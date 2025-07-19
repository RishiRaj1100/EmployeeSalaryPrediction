def generate_pdf_report(results, filename):
    """Generate a PDF summary report for all employees."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(filename, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Salary Prediction Summary Report")
    c.setFont("Helvetica", 12)
    y = 770
    for i, data in enumerate(results):
        c.drawString(50, y, f"{i+1}. {data.get('Name', 'Employee')} | Predicted: ₹{data.get('Predicted Salary', '')} | Low: ₹{data.get('Low Range', '')} | High: ₹{data.get('High Range', '')} | Parity: {data.get('Parity Score', '')} | Bias: {'Yes' if data.get('Bias Detected', False) else 'No'}")
        y -= 20
        if y < 100:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 800
    c.save()
def generate_excel_report(results, filename):
    """Generate an Excel report for all employees."""
    import pandas as pd
    df = pd.DataFrame(results)
    # Ensure 'ID' column is numeric and Arrow-compatible
    if 'ID' in df.columns:
        df['ID'] = pd.to_numeric(df['ID'], errors='coerce')
        df = df.dropna(subset=['ID'])
        df['ID'] = df['ID'].astype(int)
    df.to_excel(filename, index=False)
"""
Salary slip and report generation for salary prediction system.
"""
from reportlab.pdfgen import canvas
from fpdf import FPDF

# TODO: Implement functions to generate salary slips and parity reports



def generate_salary_slip(data, filename):
    """Generate a PDF salary slip using ReportLab, including parity score."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(filename, pagesize=A4)
    c.setFont("Helvetica", 14)
    c.drawString(50, 800, f"Salary Slip for {data.get('Name', 'Employee')}")
    c.setFont("Helvetica", 12)
    y = 770
    for key, value in data.items():
        c.drawString(50, y, f"{key}: {value}")
        y -= 20
    # Add parity score and bias detection
    parity_score, bias_flag = salary_parity_analysis(data)
    c.drawString(50, y-20, f"Salary Parity Score: {parity_score}")
    c.drawString(50, y-40, f"Bias Detected: {'Yes' if bias_flag else 'No'}")
    c.save()

def salary_parity_analysis(data):
    """Simple parity analysis: compare predicted salary to market and department budget."""
    pred = data.get('Predicted Salary', 0)
    market = data.get('Market CTC', 0)
    dept = data.get('Departmental Budget', 0)
    # Parity score: 1 if within 5% of both, else lower
    score = 1.0 - (abs(pred-market)/market + abs(pred-dept)/dept)/2 if market and dept else 0.5
    bias = score < 0.9
    return round(score,2), bias

# ...existing code...
