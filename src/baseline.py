import pandas as pd

def decimal_hour_to_time(decimal_hour):
    """
    Convert a decimal hour such as 9.53 into a readable time such as 09:32.
    """
    total_minutes = round(decimal_hour * 60)

    hours = (total_minutes // 60) % 24
    minutes = total_minutes % 60

    return f"{hours:02d}:{minutes:02d}"

def build_customer_baseline(transactions: pd.DataFrame):
    """
    Build a behavioral baseline from a customer's transaction history.

    Uses robust statistics so that a few unusual transactions do not
    heavily distort the customer's normal behavior.
    """

    if transactions.empty:
        raise ValueError("Cannot build baseline from empty transaction history.")

    
    median_amount = transactions["amount"].median()
    mean_amount = transactions["amount"].mean()

    q1 = transactions["amount"].quantile(0.25)
    q3 = transactions["amount"].quantile(0.75)
    iqr = q3 - q1

    
    transaction_hours = (
        transactions["datetime"].dt.hour
        + transactions["datetime"].dt.minute / 60
    )

   
    typical_start_hour = transaction_hours.quantile(0.10)
    typical_end_hour = transaction_hours.quantile(0.90)

   
    payee_counts = transactions["payee"].value_counts()

    common_payees = payee_counts.head(5).to_dict()

    
    channel_counts = transactions["channel"].value_counts()

    common_channels = channel_counts.to_dict()

    baseline = {
        "transaction_count": len(transactions),

        "amount": {
            "mean": round(float(mean_amount), 2),
            "median": round(float(median_amount), 2),
            "q1": round(float(q1), 2),
            "q3": round(float(q3), 2),
            "iqr": round(float(iqr), 2),
        },

        "time": {
    "typical_start_hour": round(float(typical_start_hour), 2),
    "typical_end_hour": round(float(typical_end_hour), 2),
    "typical_start_time": decimal_hour_to_time(
        float(typical_start_hour)
    ),
    "typical_end_time": decimal_hour_to_time(
        float(typical_end_hour)
    ),
},
        "common_payees": common_payees,

        "channels": common_channels,
    }

    return baseline