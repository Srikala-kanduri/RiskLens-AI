from src.data_loader import load_transactions


def main():
    transactions = load_transactions()

    print("Transaction Risk Investigation Assistant")
    print("----------------------------------------")
    print(f"Transactions loaded: {len(transactions)}")

    print("\nFirst 5 transactions:")
    print(transactions.head())

    print("\nLast 5 transactions:")
    print(transactions.tail())


if __name__ == "__main__":
    main()