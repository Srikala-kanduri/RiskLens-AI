from src.data_loader import load_transactions
from src.baseline import build_customer_baseline


def format_hour(decimal_hour):
    """
    Convert decimal hour such as 9.5 into 09:30.
    """

    hour = int(decimal_hour)
    minute = int(round((decimal_hour - hour) * 60))

    if minute == 60:
        hour += 1
        minute = 0

    return f"{hour:02d}:{minute:02d}"


def main():
    transactions = load_transactions()

    print("Transaction Risk Investigation Assistant")
    print("----------------------------------------")

    print(f"Transactions loaded: {len(transactions)}")

    baseline = build_customer_baseline(transactions)

    print("\nCUSTOMER BEHAVIOURAL BASELINE")
    print("----------------------------------------")

    print(f"Median transaction: ₹{baseline['amount']['median']:,.2f}")
    print(f"Average transaction: ₹{baseline['amount']['mean']:,.2f}")

    print(
        "Typical transaction hours:",
        format_hour(baseline["time"]["typical_start_hour"]),
        "-",
        format_hour(baseline["time"]["typical_end_hour"]),
    )

    print("\nMost common payees:")
    for payee, count in baseline["common_payees"].items():
        print(f"  {payee}: {count} transactions")

    print("\nChannels:")
    for channel, count in baseline["channels"].items():
        print(f"  {channel}: {count} transactions")


if __name__ == "__main__":
    main()