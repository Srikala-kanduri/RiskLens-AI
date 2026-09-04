from src.data_loader import load_transactions
from src.risk_engine import (
    detect_large_transfers,
    detect_new_payee_bursts,
    detect_odd_hours,
    detect_behavior_deviation,
)
from src.report_generator import generate_investigation_report
from src.gemini_service import generate_ai_investigation


def main():
    transactions = load_transactions()

    print("Transaction Risk Investigation Assistant")
    print("----------------------------------------")

    # Run all deterministic risk rules once
    large_transfer_findings = detect_large_transfers(transactions)
    new_payee_findings = detect_new_payee_bursts(transactions)
    odd_hour_findings = detect_odd_hours(transactions)
    behavior_findings = detect_behavior_deviation(transactions)

    # --------------------------------------------------
    # RISK-01
    # --------------------------------------------------
    print(
        f"\nRISK-01 Large transfer findings: "
        f"{len(large_transfer_findings)}"
    )

    for finding in large_transfer_findings:
        print("\n----------------------------------------")
        print(f"Transaction: {finding['transaction_id']}")
        print(f"Amount: ₹{finding['amount']:,.2f}")
        print(f"Payee: {finding['payee']}")
        print(f"Reason: {finding['reason']}")

    # --------------------------------------------------
    # RISK-02
    # --------------------------------------------------
    print(
        f"\n\nRISK-02 New payee burst findings: "
        f"{len(new_payee_findings)}"
    )

    for finding in new_payee_findings:
        print("\n----------------------------------------")
        print(f"Payee: {finding['payee']}")
        print(
            "Transactions:",
            ", ".join(finding["transaction_ids"])
        )
        print(
            f"Transaction count: "
            f"{finding['transaction_count']}"
        )
        print(
            f"Total amount: "
            f"₹{finding['total_amount']:,.2f}"
        )
        print(f"Reason: {finding['reason']}")

    # --------------------------------------------------
    # RISK-03
    # --------------------------------------------------
    print(
        f"\n\nRISK-03 Odd-hours findings: "
        f"{len(odd_hour_findings)}"
    )

    for finding in odd_hour_findings:
        print("\n----------------------------------------")
        print(f"Transaction: {finding['transaction_id']}")
        print(
            f"Time: "
            f"{finding['datetime'].strftime('%H:%M')}"
        )
        print(f"Payee: {finding['payee']}")
        print(f"Amount: ₹{finding['amount']:,.2f}")
        print(f"Reason: {finding['reason']}")

    # --------------------------------------------------
    # RISK-04
    # --------------------------------------------------
    print(
        f"\n\nRISK-04 Behaviour deviation findings: "
        f"{len(behavior_findings)}"
    )

    for finding in behavior_findings:
        print("\n----------------------------------------")
        print(f"Transaction: {finding['transaction_id']}")
        print(f"Payee: {finding['payee']}")
        print(f"Amount: ₹{finding['amount']:,.2f}")
        print(
            f"Deviation score: "
            f"{finding['deviation_score']}"
        )

        print("Deviation reasons:")

        for reason in finding["deviation_reasons"]:
            print(f"  - {reason}")

    # --------------------------------------------------
    # Structured investigation report
    # --------------------------------------------------
    report = generate_investigation_report(
        transactions=transactions,
        large_transfer_findings=large_transfer_findings,
        new_payee_findings=new_payee_findings,
        odd_hour_findings=odd_hour_findings,
        behavior_findings=behavior_findings,
    )

    print("\n\n========================================")
    print("INVESTIGATION REPORT")
    print("========================================")

    print(f"Status: {report['status']}")
    print(f"Summary: {report['summary']}")

    print("\nTriggered rules:")

    for rule in report["triggered_rules"]:
        print(
            f"  {rule['rule_id']} - "
            f"{rule['rule_name']}"
        )

    print("\nFlagged transactions:")

    for finding in report["findings"]:
        print("\n----------------------------------------")
        print(f"Transaction: {finding['transaction_id']}")
        print(f"Payee: {finding['payee']}")
        print(f"Amount: ₹{finding['amount']:,.2f}")
        print(
            "Rules:",
            ", ".join(finding["triggered_rules"])
        )

        print("Reasons:")

        for reason in finding["reasons"]:
            print(f"  - {reason}")

    # --------------------------------------------------
    # Gemini explanation — run only once
    # --------------------------------------------------
    ai_report = generate_ai_investigation(report)

    print("\n\n========================================")
    print("AI INVESTIGATION NARRATIVE")
    print("========================================")

    print(ai_report["content"])


if __name__ == "__main__":
    main()