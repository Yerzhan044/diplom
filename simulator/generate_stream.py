import argparse
import random
import time
from datetime import datetime, timedelta, timezone

import requests


COUNTRIES = ["US", "DE", "KZ", "TR", "VN", "ID", "BR", "GB"]
MCC_POOL = ["5411", "5812", "5732", "5999", "7995"]


def generate_tx(i: int, fraud_bias: float) -> dict:
    card_id = f"card_{random.randint(1, 30)}"
    is_fraud_like = random.random() < fraud_bias

    amount = round(random.uniform(2, 160), 2)
    country = random.choice(COUNTRIES[:4])
    mcc = random.choice(MCC_POOL[:4])

    if is_fraud_like:
        amount = round(random.uniform(900, 4200), 2)
        country = random.choice(["VN", "ID", "BR"])
        if random.random() < 0.4:
            mcc = "7995"

    return {
        "transaction_id": f"tx_{i}",
        "card_id": card_id,
        "merchant_id": f"m_{random.randint(1, 300)}",
        "amount": amount,
        "currency": "USD",
        "country": country,
        "mcc": mcc,
        "device_id": f"d_{random.randint(1, 500)}",
        "ip_address": f"10.0.{random.randint(0, 255)}.{random.randint(1, 254)}",
        "timestamp": (
            datetime.now(timezone.utc) + timedelta(milliseconds=i)
        ).isoformat(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Transaction stream simulator")
    parser.add_argument("--api", default="http://127.0.0.1:8000/score")
    parser.add_argument(
        "--rate", type=float, default=4.0, help="transactions per second"
    )
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--fraud-bias", type=float, default=0.22)
    args = parser.parse_args()

    delay = 1.0 / max(0.1, args.rate)

    for i in range(1, args.count + 1):
        tx = generate_tx(i=i, fraud_bias=args.fraud_bias)
        try:
            resp = requests.post(args.api, json=tx, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            print(
                f"{tx['transaction_id']} amount={tx['amount']:<8} country={tx['country']} "
                f"decision={data['decision']:<7} score={data['final_score']}"
            )
        except Exception as exc:
            print(f"{tx['transaction_id']} ERROR: {exc}")

        time.sleep(delay)


if __name__ == "__main__":
    main()
