import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from app.schemas import ScoreResponse, TransactionIn

logger = logging.getLogger(__name__)


class SecurityLogger:
    """Centralized security and audit logging for fraud detection system."""

    def __init__(self, log_dir: str = "logs") -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Setup file handlers for different log types
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Setup logging handlers for different event types."""
        # Suspicious transactions log
        suspicious_handler = logging.FileHandler(
            self.log_dir / "suspicious_transactions.jsonl"
        )
        suspicious_handler.setFormatter(
            logging.Formatter("%(message)s")
        )

        # Model predictions log
        predictions_handler = logging.FileHandler(
            self.log_dir / "predictions.jsonl"
        )
        predictions_handler.setFormatter(
            logging.Formatter("%(message)s")
        )

        # Setup loggers
        self.suspicious_logger = logging.getLogger("security.suspicious")
        self.suspicious_logger.addHandler(suspicious_handler)
        self.suspicious_logger.setLevel(logging.INFO)

        self.predictions_logger = logging.getLogger("security.predictions")
        self.predictions_logger.addHandler(predictions_handler)
        self.predictions_logger.setLevel(logging.INFO)

    def log_suspicious_transaction(
        self,
        tx: TransactionIn,
        result: ScoreResponse,
        explanation: dict[str, Any],
    ) -> None:
        """Log a suspicious transaction (REVIEW or DECLINE)."""
        if result.decision not in {"REVIEW", "DECLINE"}:
            return

        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "transaction_id": result.transaction_id,
            "card_id": tx.card_id,
            "merchant_id": tx.merchant_id,
            "amount": float(tx.amount),
            "country": tx.country,
            "fraud_probability": result.fraud_probability,
            "rule_score": result.rule_score,
            "final_score": result.final_score,
            "decision": result.decision,
            "reasons": result.reasons,
            "xai_method": explanation.get("method", "unknown"),
            "top_contributing_features": [
                {
                    "feature": feat["feature"],
                    "value": feat["feature_value"],
                    "shap_value": feat["shap_value"],
                }
                for feat in explanation.get("feature_importance", [])
            ],
        }

        self.suspicious_logger.info(json.dumps(event))

    def log_prediction(
        self,
        tx: TransactionIn,
        result: ScoreResponse,
    ) -> None:
        """Log all predictions for monitoring and analysis."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "transaction_id": result.transaction_id,
            "card_id": tx.card_id,
            "amount": float(tx.amount),
            "country": tx.country,
            "fraud_probability": result.fraud_probability,
            "rule_score": result.rule_score,
            "final_score": result.final_score,
            "decision": result.decision,
        }

        self.predictions_logger.info(json.dumps(event))

    def get_suspicious_summary(self, limit: int = 100) -> dict[str, Any]:
        """Get summary of suspicious transactions."""
        try:
            log_file = self.log_dir / "suspicious_transactions.jsonl"
            if not log_file.exists():
                return {
                    "total": 0,
                    "by_decision": {},
                    "by_country": {},
                    "recent": [],
                }

            events = []
            with open(log_file, "r") as f:
                for line in f:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

            summary = {
                "total": len(events),
                "by_decision": {},
                "by_country": {},
                "by_reason": {},
                "recent": events[-limit:],
            }

            for event in events:
                decision = event.get("decision", "unknown")
                summary["by_decision"][decision] = (
                    summary["by_decision"].get(decision, 0) + 1
                )

                country = event.get("country", "unknown")
                summary["by_country"][country] = (
                    summary["by_country"].get(country, 0) + 1
                )

                for reason in event.get("reasons", []):
                    summary["by_reason"][reason] = (
                        summary["by_reason"].get(reason, 0) + 1
                    )

            return summary

        except Exception as e:
            logger.error(f"Error reading suspicious transaction logs: {e}")
            return {
                "total": 0,
                "by_decision": {},
                "by_country": {},
                "recent": [],
            }
