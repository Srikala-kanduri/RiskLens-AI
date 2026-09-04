from flask import Flask, render_template, request
import markdown
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
        uploaded_file = request.files.get("transaction_file")

        # Use uploaded CSV if provided
        if uploaded_file and uploaded_file.filename:
            transactions = load_transactions(uploaded_file)
            selected_case = "uploaded"

        # Otherwise use selected sample
        elif selected_case == "normal":
            transactions = load_transactions("data/normal_case.csv")

        else:
            transactions = load_transactions("data/transaction.csv")

        result = analyze_transactions(
            transactions,
            include_ai=True,
        )

        result["ai_investigation"]["html"] = markdown.markdown(
            result["ai_investigation"]["content"],
            extensions=["nl2br"],
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
            selected_case=request.form.get(
                "case_type",
                "difficult",
            ),
        )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True,
    )