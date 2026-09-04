from src.data_loader import load_transactions
from src.risk_engine import detect_large_transfers


def main():
    transactions = load_transactions()

    print("Transaction Risk Investigation Assistant")
    print("----------------------------------------")

    findings = detect_large_transfers(transactions)

    print(f"\nLarge transfer findings: {len(findings)}")

    for finding in findings:
        print("\n----------------------------------------")
        print(f"Transaction: {finding['transaction_id']}")
        print(f"Payee: {finding['payee']}")
        print(f"Amount: ₹{finding['amount']:,.2f}")
        print(f"Rule: {finding['rule_id']} - {finding['rule_name']}")
        print(f"Historical median: ₹{finding['historical_median']:,.2f}")
        print(f"Threshold: ₹{finding['large_amount_threshold']:,.2f}")
        print(f"Median ratio: {finding['median_ratio']}x")
        print(f"Reason: {finding['reason']}")


if __name__ == "__main__":
    main()