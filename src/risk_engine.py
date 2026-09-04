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

def detect_new_payee_bursts(
    transactions: pd.DataFrame,
    burst_count=3,
    window_minutes=60
):
    """
    Detect multiple payments to a newly observed payee
    within a short time window.

    A payee is considered 'new' if it has not appeared
    before the first transaction in the burst.
    """

    findings = []

    transactions = transactions.sort_values("datetime").reset_index(drop=True)

    for index, transaction in transactions.iterrows():
        current_payee = transaction["payee"]

        # History before the current transaction
        history = transactions.iloc[:index]

        # If payee already appeared before, it is not new
        if current_payee in set(history["payee"]):
            continue

        current_time = transaction["datetime"]

        window_end = current_time + pd.Timedelta(minutes=window_minutes)

        # Look forward within the burst window
        burst_transactions = transactions[
            (transactions["datetime"] >= current_time)
            & (transactions["datetime"] <= window_end)
            & (transactions["payee"] == current_payee)
        ]

        if len(burst_transactions) >= burst_count:

            transaction_ids = burst_transactions[
                "transaction_id"
            ].tolist()

            total_amount = float(
                burst_transactions["amount"].sum()
            )

            findings.append({
                "rule_id": "RISK-02",
                "rule_name": "Burst of Payments to New Payee",

                "payee": current_payee,
                "transaction_ids": transaction_ids,
                "transaction_count": len(burst_transactions),
                "total_amount": total_amount,

                "start_time": burst_transactions[
                    "datetime"
                ].min(),

                "end_time": burst_transactions[
                    "datetime"
                ].max(),

                "window_minutes": window_minutes,

                "reason": (
                    f"{len(burst_transactions)} payments totaling "
                    f"₹{total_amount:,.2f} were sent to new payee "
                    f"'{current_payee}' within {window_minutes} minutes."
                ),
            })

    return findings

def detect_odd_hours(
    transactions: pd.DataFrame,
    tolerance_hours=2
):
    """
    Detect transactions that occur significantly outside
    the customer's established activity hours.

    Uses prior transaction history only to avoid data leakage.
    A tolerance margin prevents minor variations from being
    incorrectly flagged.
    """

    findings = []

    transactions = transactions.sort_values(
        "datetime"
    ).reset_index(drop=True)

    for index, transaction in transactions.iterrows():

        history = transactions.iloc[:index]

        if len(history) < MIN_HISTORY:
            continue

        historical_hours = (
            history["datetime"].dt.hour
            + history["datetime"].dt.minute / 60
        )

        typical_start = historical_hours.quantile(0.10)
        typical_end = historical_hours.quantile(0.90)

        # Allow reasonable variation around normal hours
        allowed_start = typical_start - tolerance_hours
        allowed_end = typical_end + tolerance_hours

        current_hour = (
            transaction["datetime"].hour
            + transaction["datetime"].minute / 60
        )

        if current_hour < allowed_start or current_hour > allowed_end:

            findings.append({
                "transaction_id": transaction["transaction_id"],
                "datetime": transaction["datetime"],
                "payee": transaction["payee"],
                "amount": float(transaction["amount"]),
                "channel": transaction["channel"],

                "rule_id": "RISK-03",
                "rule_name": "Odd-Hours Activity",

                "transaction_hour": round(current_hour, 2),
                "typical_start_hour": round(
                    float(typical_start), 2
                ),
                "typical_end_hour": round(
                    float(typical_end), 2
                ),
                "allowed_start_hour": round(
                    float(allowed_start), 2
                ),
                "allowed_end_hour": round(
                    float(allowed_end), 2
                ),

                "reason": (
                    f"Transaction occurred at "
                    f"{transaction['datetime'].strftime('%H:%M')}, "
                    f"significantly outside the customer's "
                    f"historical activity pattern."
                ),
            })

    return findings

def detect_behavior_deviation(
    transactions: pd.DataFrame,
    min_deviation_score=2
):
    """
    Detect transactions that materially deviate from the customer's
    established behaviour across multiple dimensions.

    Each transaction is compared only with prior history.
    """

    findings = []

    transactions = transactions.sort_values(
        "datetime"
    ).reset_index(drop=True)

    for index, transaction in transactions.iterrows():

        history = transactions.iloc[:index]

        if len(history) < MIN_HISTORY:
            continue

        deviation_reasons = []
        deviation_score = 0

        
        median_amount = float(history["amount"].median())

        if median_amount > 0:
            amount_ratio = (
                float(transaction["amount"]) / median_amount
            )
        else:
            amount_ratio = 0

        if amount_ratio >= 3:
            deviation_score += 1
            deviation_reasons.append(
                f"Amount is {amount_ratio:.1f}× the historical median"
            )

        
        historical_payees = set(history["payee"])

        if transaction["payee"] not in historical_payees:
            deviation_score += 1
            deviation_reasons.append(
                "Payee has not appeared previously"
            )

        
        channel_counts = history["channel"].value_counts()

        current_channel = transaction["channel"]

        if current_channel not in channel_counts:
            deviation_score += 1
            deviation_reasons.append(
                "Transaction channel has not been used previously"
            )

        
        historical_hours = (
            history["datetime"].dt.hour
            + history["datetime"].dt.minute / 60
        )

        typical_start = historical_hours.quantile(0.10)
        typical_end = historical_hours.quantile(0.90)

        tolerance_hours = 2

        allowed_start = typical_start - tolerance_hours
        allowed_end = typical_end + tolerance_hours

        current_hour = (
            transaction["datetime"].hour
            + transaction["datetime"].minute / 60
        )

        if current_hour < allowed_start or current_hour > allowed_end:
            deviation_score += 1
            deviation_reasons.append(
                "Transaction occurred significantly outside normal hours"
            )

       
        if deviation_score >= min_deviation_score:

            findings.append({
                "transaction_id": transaction["transaction_id"],
                "datetime": transaction["datetime"],
                "payee": transaction["payee"],
                "amount": float(transaction["amount"]),
                "channel": transaction["channel"],

                "rule_id": "RISK-04",
                "rule_name": "Behaviour Deviation",

                "deviation_score": deviation_score,
                "deviation_reasons": deviation_reasons,

                "reason": (
                    f"Transaction differs from the customer's "
                    f"historical behaviour across "
                    f"{deviation_score} dimensions."
                ),
            })

    return findings