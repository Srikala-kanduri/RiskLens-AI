from src.baseline import build_customer_baseline
from src.risk_engine import (
    detect_large_transfers,
    detect_new_payee_bursts,
    detect_odd_hours,
    detect_behavior_deviation,
)
from src.report_generator import generate_investigation_report
from src.gemini_service import generate_ai_investigation


def analyze_transactions(transactions, include_ai=True):
    """
    Run the complete transaction investigation pipeline.

    Deterministic risk rules identify activity that requires review.
    Gemini is used only to explain the verified findings.
    """

    if transactions.empty:
        raise ValueError("Transaction history is empty.")

    # Build descriptive customer baseline
    baseline = build_customer_baseline(transactions)

    # Run deterministic risk rules
    large_transfer_findings = detect_large_transfers(transactions)

    new_payee_findings = detect_new_payee_bursts(transactions)

    odd_hour_findings = detect_odd_hours(transactions)

    behavior_findings = detect_behavior_deviation(transactions)

    # Generate evidence-grounded deterministic report
    report = generate_investigation_report(
        transactions=transactions,
        large_transfer_findings=large_transfer_findings,
        new_payee_findings=new_payee_findings,
        odd_hour_findings=odd_hour_findings,
        behavior_findings=behavior_findings,
    )

    # Gemini explains only the verified report.
    if include_ai:
        ai_investigation = generate_ai_investigation(report)
    else:
        ai_investigation = {
            "available": False,
            "content": "AI investigation was not requested.",
        }

    return {
        "baseline": baseline,
        "report": report,
        "ai_investigation": ai_investigation,
        "rule_findings": {
            "large_transfers": large_transfer_findings,
            "new_payee_bursts": new_payee_findings,
            "odd_hours": odd_hour_findings,
            "behavior_deviation": behavior_findings,
        },
    }