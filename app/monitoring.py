"""Model monitoring and drift detection."""

import json
import logging
from collections import deque
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class ModelMonitor:
    """Monitor model performance and detect data drift."""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.predictions = deque(maxlen=window_size)
        self.feature_stats = {}

    def record_prediction(
        self,
        features: dict[str, float],
        fraud_probability: float,
        decision: str,
    ) -> None:
        """Record a prediction for monitoring."""
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "features": features,
            "fraud_probability": fraud_probability,
            "decision": decision,
        }
        self.predictions.append(record)
        self._update_feature_stats(features)

    def _update_feature_stats(self, features: dict[str, float]) -> None:
        """Update rolling statistics for features."""
        for feature_name, value in features.items():
            if feature_name not in self.feature_stats:
                self.feature_stats[feature_name] = {
                    "min": value,
                    "max": value,
                    "sum": value,
                    "count": 1,
                    "values": deque(maxlen=100),
                }
            stats = self.feature_stats[feature_name]
            stats["min"] = min(stats["min"], value)
            stats["max"] = max(stats["max"], value)
            stats["sum"] += value
            stats["count"] += 1
            stats["values"].append(value)

    def get_performance_stats(self) -> dict[str, Any]:
        """Get current performance statistics."""
        if not self.predictions:
            return {
                "total_predictions": 0,
                "decision_distribution": {},
                "fraud_probability_stats": {},
                "warning": "No predictions recorded yet",
            }

        decisions = [p["decision"] for p in self.predictions]
        fraud_probs = [p["fraud_probability"] for p in self.predictions]

        decision_dist = {}
        for decision in decisions:
            decision_dist[decision] = decision_dist.get(decision, 0) + 1

        avg_fraud_prob = sum(fraud_probs) / len(fraud_probs)
        min_fraud_prob = min(fraud_probs)
        max_fraud_prob = max(fraud_probs)

        return {
            "total_predictions": len(self.predictions),
            "decision_distribution": decision_dist,
            "fraud_probability_stats": {
                "mean": round(avg_fraud_prob, 4),
                "min": round(min_fraud_prob, 4),
                "max": round(max_fraud_prob, 4),
                "stdev": self._calculate_stdev(fraud_probs),
            },
            "approval_rate": round(
                decision_dist.get("APPROVE", 0) / len(self.predictions), 4
            ),
        }

    def _calculate_stdev(self, values: list[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return round(variance ** 0.5, 4)

    def get_feature_drift(self) -> dict[str, Any]:
        """Detect drift in feature distributions."""
        drift_report = {}

        for feature_name, stats in self.feature_stats.items():
            if stats["count"] < 10:
                continue

            values = list(stats["values"])
            avg = sum(values) / len(values)
            range_val = stats["max"] - stats["min"]

            # Simple drift detection: if range is extreme or mean is unusual
            drift_detected = False
            reason = None

            if range_val > 100:
                drift_detected = True
                reason = f"Large range: {stats['min']:.2f} to {stats['max']:.2f}"
            elif avg > stats["max"] * 0.8 or avg < stats["min"] * 0.2:
                drift_detected = True
                reason = f"Mean {avg:.2f} is outlier in range"

            drift_report[feature_name] = {
                "drift_detected": drift_detected,
                "mean": round(avg, 4),
                "min": round(stats["min"], 4),
                "max": round(stats["max"], 4),
                "reason": reason,
            }

        return drift_report

    def get_alerts(self) -> list[str]:
        """Get model health alerts."""
        alerts = []

        stats = self.get_performance_stats()

        # Alert if too many REVIEW/DECLINE
        suspicious_count = (
            stats["decision_distribution"].get("REVIEW", 0)
            + stats["decision_distribution"].get("DECLINE", 0)
        )
        if suspicious_count / max(stats["total_predictions"], 1) > 0.5:
            alerts.append(
                f"⚠️ High fraud rate: {suspicious_count}/{stats['total_predictions']} transactions suspicious"
            )

        # Alert if fraud probability is too high on average
        if stats["fraud_probability_stats"]["mean"] > 0.7:
            alerts.append(
                f"⚠️ High average fraud probability: {stats['fraud_probability_stats']['mean']:.4f}"
            )

        # Alert on feature drift
        drift = self.get_feature_drift()
        for feature, drift_info in drift.items():
            if drift_info["drift_detected"]:
                alerts.append(
                    f"⚠️ Data drift detected in {feature}: {drift_info['reason']}"
                )

        return alerts
