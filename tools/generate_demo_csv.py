from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


COUNTRIES = ["US", "DE", "KZ", "TR", "VN", "ID", "BR", "GB"]
MCC_CODES = ["5411", "5812", "5732", "5999", "7995"]


def build_row(index: int) -> dict[str, str]:
    fraud_like = random.random() < 0.22

    amount = round(random.uniform(5, 180), 2)
    country = random.choice(COUNTRIES[:4])
    mcc = random.choice(MCC_CODES[:4])

    if fraud_like:
        amount = round(random.uniform(900, 4200), 2)
        country = random.choice(["VN", "ID", "BR"])
        if random.random() < 0.4:
            mcc = "7995"

    timestamp = datetime.now(timezone.utc) + timedelta(seconds=index * 10)

    return {
        "transaction_id": f"tx_{index + 1}",
        "card_id": f"card_{random.randint(1, 30)}",
        "merchant_id": f"m_{random.randint(1, 300)}",
        "amount": f"{amount:.2f}",
        "currency": "USD",
        "country": country,
        "mcc": mcc,
        "device_id": f"d_{random.randint(1, 500)}",
        "ip_address": f"10.0.{random.randint(0, 255)}.{random.randint(1, 254)}",
        "timestamp": timestamp.isoformat(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate demo CSV for fraud dashboard"
    )
    parser.add_argument(
        "--rows", type=int, default=50, help="Number of rows to generate"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="demo_transactions.csv",
        help="Output CSV path",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "transaction_id",
        "card_id",
        "merchant_id",
        "amount",
        "currency",
        "country",
        "mcc",
        "device_id",
        "ip_address",
        "timestamp",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=fieldnames)
        writer.writeheader()
        for index in range(args.rows):
            writer.writerow(build_row(index))

    print(f"Generated {args.rows} rows to {output_path}")


if __name__ == "__main__":
    main()
