from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class CardState:
    timestamps: deque = field(default_factory=lambda: deque(maxlen=200))
    amounts: deque = field(default_factory=lambda: deque(maxlen=200))


class OnlineStateStore:
    def __init__(self) -> None:
        self._store: dict[str, CardState] = defaultdict(CardState)

    def get_features(self, card_id: str, amount: float, ts: datetime) -> dict[str, float]:
        """Get features WITHOUT updating state."""
        state = self._store[card_id]

        one_min_ago = ts - timedelta(minutes=1)
        five_min_ago = ts - timedelta(minutes=5)

        count_1m = 0
        count_5m = 0
        for prev_ts in state.timestamps:
            if prev_ts >= one_min_ago:
                count_1m += 1
            if prev_ts >= five_min_ago:
                count_5m += 1

        avg_amount_30 = (
            (sum(list(state.amounts)[-30:]) / max(1, min(len(state.amounts), 30)))
            if state.amounts
            else amount
        )
        amount_to_avg_ratio = amount / max(1e-6, avg_amount_30)

        return {
            "count_1m": float(count_1m),
            "count_5m": float(count_5m),
            "avg_amount_30": float(avg_amount_30),
            "amount_to_avg_ratio": float(amount_to_avg_ratio),
        }

    def update_and_get_features(
        self, card_id: str, amount: float, ts: datetime
    ) -> dict[str, float]:
        """Get features AND update state."""
        features = self.get_features(card_id, amount, ts)
        state = self._store[card_id]
        state.timestamps.append(ts)
        state.amounts.append(amount)
        return features
