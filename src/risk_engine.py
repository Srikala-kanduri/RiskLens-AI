import pandas as pd


MIN_HISTORY = 10


def calculate_historical_amount_baseline(history: pd.DataFrame):
    """
    Build amount-related statistics only from prior transactions.
    """

    median_amount = history["amount"].median()
    q1 = history["amount"].quantile(0.25)
    q3 = history["amount"].quantile(0.75)
    iqr = q3 - q1

    threshold = q3 + (3 * iqr)

    return {
        "median": float(median_amount),
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(iqr),
        "large_amount_threshold": float(threshold),
    }


def detect_large_transfers(transactions: pd.DataFrame):
    """
    Detect unusually large transactions by comparing each transaction
    only with transactions that occurred before it.

    This avoids data leakage.
    """

    findings = []

    transactions = transactions.sort_values("datetime").reset_index(drop=True)

    for index, transaction in transactions.iterrows():

        # Only previous transactions are used as history
        history = transactions.iloc[:index]

        # We need enough history to establish normal behaviour
        if len(history) < MIN_HISTORY:
            continue

        baseline = calculate_historical_amount_baseline(history)

        amount = float(transaction["amount"])
        median_amount = baseline["median"]
        threshold = baseline["large_amount_threshold"]

        # Additional ratio helps avoid weak statistical flags
        median_ratio = (
            amount / median_amount
            if median_amount > 0
            else 0
        )

        if amount > threshold and median_ratio >= 3:

            findings.append({
                "transaction_id": transaction["transaction_id"],
                "datetime": transaction["datetime"],
                "payee": transaction["payee"],
                "amount": amount,
                "channel": transaction["channel"],

                "rule_id": "RISK-01",
                "rule_name": "Unusually Large Transfer",

                "historical_median": round(median_amount, 2),
                "large_amount_threshold": round(threshold, 2),
                "median_ratio": round(median_ratio, 2),

                "reason": (
                    f"Transaction amount ₹{amount:,.2f} is "
                    f"{median_ratio:.1f}× the historical median "
                    f"of ₹{median_amount:,.2f}."
                ),
            })

    return findings