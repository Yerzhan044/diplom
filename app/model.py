from pathlib import Path

import joblib
import pandas as pd

FEATURE_COLUMNS = [
    "amount",
    "count_1m",
    "count_5m",
    "avg_amount_30",
    "amount_to_avg_ratio",
    "is_high_risk_country",
    "is_night",
    "is_gambling_mcc",
]


class FraudModel:
    """Ensemble fraud detection model with supervised and unsupervised components."""

    def __init__(self, model_path: str, anomaly_model_path: str = None) -> None:
        self.supervised_model = None
        self.anomaly_model = None

        model_file = Path(model_path)
        if model_file.exists():
            self.supervised_model = joblib.load(model_file)

        if anomaly_model_path:
            anomaly_file = Path(anomaly_model_path)
            if anomaly_file.exists():
                self.anomaly_model = joblib.load(anomaly_file)

    def predict_proba(self, feature_dict: dict[str, float]) -> float:
        """Get supervised model fraud probability."""
        if self.supervised_model is None:
            return self._fallback_prediction(feature_dict)

        frame = pd.DataFrame([{k: feature_dict[k] for k in FEATURE_COLUMNS}])
        return float(self.supervised_model.predict_proba(frame)[:, 1][0])

    def anomaly_score(self, feature_dict: dict[str, float]) -> float:
        """Get unsupervised anomaly score (0-1, higher = more anomalous)."""
        if self.anomaly_model is None:
            return 0.0

        try:
            frame = pd.DataFrame([{k: feature_dict[k] for k in FEATURE_COLUMNS}])
            # Isolation Forest returns -1 for anomalies, 1 for normal
            prediction = self.anomaly_model.predict(frame)[0]
            # Convert to [0, 1] where 1 is anomaly
            return 0.9 if prediction == -1 else 0.1
        except Exception:
            return 0.0

    def _fallback_prediction(self, feature_dict: dict[str, float]) -> float:
        """Fallback prediction for cold start."""
        raw = (
            0.00025 * feature_dict["amount"]
            + 0.08 * feature_dict["count_1m"]
            + 0.04 * feature_dict["count_5m"]
            + 0.2 * feature_dict["amount_to_avg_ratio"]
            + 0.3 * feature_dict["is_high_risk_country"]
            + 0.2 * feature_dict["is_night"]
            + 0.2 * feature_dict["is_gambling_mcc"]
        )
        return max(0.0, min(1.0, raw / 3.0))
