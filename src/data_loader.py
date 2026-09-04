import pandas as pd


def load_transactions(file_path="data/transaction.csv"):
    """
    Load transaction history from CSV.
    """

    try:
        df = pd.read_csv(file_path)

        required_columns = {
            "transaction_id",
            "date",
            "time",
            "description",
            "payee",
            "amount",
            "channel",
        }

        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {', '.join(missing_columns)}"
            )

        df["datetime"] = pd.to_datetime(
            df["date"].astype(str) + " " + df["time"].astype(str)
        )

        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

        if df["amount"].isna().any():
            raise ValueError("Invalid transaction amount found.")

        df = df.sort_values("datetime").reset_index(drop=True)

        return df

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Transaction file not found: {file_path}"
        )