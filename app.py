from src.data_loader import load_transactions
from src.risk_engine import (
    detect_large_transfers,
    detect_new_payee_bursts,
)


def main():
    transactions = load_transactions()

    print("Transaction Risk Investigation Assistant")
    print("----------------------------------------")

    large_transfer_findings = detect_large_transfers(transactions)
    new_payee_findings = detect_new_payee_bursts(transactions)

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


if __name__ == "__main__":
    main()