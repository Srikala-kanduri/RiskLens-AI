def generate_investigation_report(
    transactions,
    large_transfer_findings,
    new_payee_findings,
    odd_hour_findings,
    behavior_findings,
):
    """
    Combine all deterministic risk findings into one structured
    investigation report.

    This report becomes the verified input for Gemini later.
    """

    report = {
        "status": "NO ATTENTION REQUIRED",
         "summary": (
        "No significant activity requiring investigation was identified. "
        "The transaction history appears consistent with the customer's "
        "established behaviour."
    ),
        "triggered_rules": [],
        "flagged_transaction_ids": [],
        "findings": [],
        "total_flagged_amount": 0.0,
    }

    
    rule_map = {}

    for finding in large_transfer_findings:
        rule_map["RISK-01"] = "Unusually Large Transfer"

    for finding in new_payee_findings:
        rule_map["RISK-02"] = "Burst of Payments to New Payee"

    for finding in odd_hour_findings:
        rule_map["RISK-03"] = "Odd-Hours Activity"

    for finding in behavior_findings:
        rule_map["RISK-04"] = "Behaviour Deviation"

    report["triggered_rules"] = [
        {
            "rule_id": rule_id,
            "rule_name": rule_name,
        }
        for rule_id, rule_name in rule_map.items()
    ]

   
    flagged_ids = set()

    for finding in large_transfer_findings:
        flagged_ids.add(finding["transaction_id"])

    for finding in new_payee_findings:
        for transaction_id in finding["transaction_ids"]:
            flagged_ids.add(transaction_id)

    for finding in odd_hour_findings:
        flagged_ids.add(finding["transaction_id"])

    for finding in behavior_findings:
        flagged_ids.add(finding["transaction_id"])

    report["flagged_transaction_ids"] = sorted(flagged_ids)

   
    if not flagged_ids:
        report["summary"] = (
            "No significant activity requiring review was identified. "
            "The supplied transaction history appears consistent with "
            "the customer's established behaviour."
        )

        return report

    
    report["status"] = "ATTENTION RECOMMENDED"

   
    for transaction_id in sorted(flagged_ids):

        transaction_row = transactions[
            transactions["transaction_id"] == transaction_id
        ]

        if transaction_row.empty:
            continue

        transaction = transaction_row.iloc[0]

        triggered_rules = []
        reasons = []

        # RISK-01
        for finding in large_transfer_findings:
            if finding["transaction_id"] == transaction_id:
                triggered_rules.append("RISK-01")
                reasons.append(finding["reason"])

        # RISK-02
        for finding in new_payee_findings:
            if transaction_id in finding["transaction_ids"]:
                triggered_rules.append("RISK-02")
                reasons.append(finding["reason"])

        # RISK-03
        for finding in odd_hour_findings:
            if finding["transaction_id"] == transaction_id:
                triggered_rules.append("RISK-03")
                reasons.append(finding["reason"])

        # RISK-04
                # RISK-04
        for finding in behavior_findings:
            if finding["transaction_id"] == transaction_id:
                triggered_rules.append("RISK-04")

                reasons.append(
                    f"Multi-factor behaviour deviation score: "
                    f"{finding['deviation_score']}."
                )

        report["findings"].append({
            "transaction_id": transaction_id,
            "datetime": transaction["datetime"].isoformat(),
            "description": transaction["description"],
            "payee": transaction["payee"],
            "amount": float(transaction["amount"]),
            "channel": transaction["channel"],
            "triggered_rules": sorted(set(triggered_rules)),
            "reasons": list(dict.fromkeys(reasons)),
        })

    
    total_flagged_amount = sum(
        finding["amount"]
        for finding in report["findings"]
    )

    report["total_flagged_amount"] = total_flagged_amount

    report["summary"] = (
        f"{len(report['findings'])} transactions require review, "
        f"representing ₹{total_flagged_amount:,.2f} in flagged activity. "
        f"{len(report['triggered_rules'])} independent risk rules "
        f"were triggered."
    )

    return report