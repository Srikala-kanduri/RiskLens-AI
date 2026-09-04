from flask import Flask, render_template, request

from src.data_loader import load_transactions
from src.analysis_service import analyze_transactions


app = Flask(__name__)


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
    try:
        selected_case = request.form.get("case_type", "difficult")

        if selected_case == "normal":
            file_path = "data/normal_case.csv"
        else:
            file_path = "data/transactions.csv"

        transactions = load_transactions(file_path)

        result = analyze_transactions(
            transactions,
            include_ai=True,
        )

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
            selected_case="difficult",
        )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True,
    )