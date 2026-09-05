from flask import Flask, render_template, request, send_file

import io

from src.data_loader import load_transactions
from src.analysis_service import analyze_transactions
from src.pdf_report import generate_pdf_report


app = Flask(__name__)

# Stores the latest completed investigation result.
# Fine for this local hackathon application.
latest_investigation = None


@app.route("/")
def home():
    return render_template(
        "index.html",
        result=None,
        error=None,
        selected_case="difficult",
    )


@app.route("/analyze", methods=["POST"])
def analyze():
    global latest_investigation

    try:
        selected_case = request.form.get(
            "case_type",
            "difficult",
        )

        uploaded_file = request.files.get(
            "transaction_file"
        )

        # Use uploaded CSV if provided
        if uploaded_file and uploaded_file.filename:
            transactions = load_transactions(
                uploaded_file
            )

            selected_case = "uploaded"

        # Otherwise use selected sample
        elif selected_case == "normal":
            transactions = load_transactions(
                "data/normal_case.csv"
            )

        else:
            transactions = load_transactions(
                "data/transaction.csv"
            )

        result = analyze_transactions(
            transactions,
            include_ai=True,
        )

        # Save latest completed investigation
        # for PDF download.
        latest_investigation = result

        return render_template(
            "index.html",
            result=result,
            error=None,
            selected_case=selected_case,
        )

    except Exception as error:
        return render_template(
            "index.html",
            result=None,
            error=str(error),
            selected_case=request.form.get(
                "case_type",
                "difficult",
            ),
        )


@app.route("/download-report")
def download_report():
    if latest_investigation is None:
        return (
            "No investigation report is available. "
            "Run an investigation first.",
            400,
        )

    pdf_buffer = generate_pdf_report(
        latest_investigation
    )

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="RiskLens_Investigation_Report.pdf",
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False,
    )