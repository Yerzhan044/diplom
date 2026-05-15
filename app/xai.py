import json
import logging
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import shap

logger = logging.getLogger(__name__)


class ExplainabilityEngine:
    """SHAP-based explainability module for fraud detection decisions."""

    def __init__(self, model_path: str, feature_columns: list[str]) -> None:
        self.model = None
        self.explainer = None
        self.feature_columns = feature_columns
        self.shap_values_cache = {}

        model_file = Path(model_path)
        if model_file.exists():
            self.model = joblib.load(model_file)
            self._initialize_explainer()

    def _initialize_explainer(self) -> None:
        """Initialize SHAP explainer with background data."""
        if self.model is None:
            return

        try:
            # Create a minimal background dataset for SHAP
            background = pd.DataFrame(
                {
                    col: [0.5] if col.startswith("is_") else [1.0]
                    for col in self.feature_columns
                }
            )

            # Try TreeExplainer first (works for tree-based models)
            try:
                self.explainer = shap.TreeExplainer(self.model, background)
                logger.info("SHAP TreeExplainer initialized")
            except Exception:
                # Fallback to KernelExplainer for VotingClassifier or other models
                # Use a predict_proba wrapper for classification
                self.explainer = shap.KernelExplainer(
                    lambda x: self.model.predict_proba(x)[:, 1],
                    background
                )
                logger.info("SHAP KernelExplainer initialized as fallback")

        except Exception as e:
            logger.warning(f"Could not initialize SHAP explainer: {e}")

    def explain_prediction(
        self, features_dict: dict[str, float]
    ) -> dict[str, Any]:
        """Generate SHAP-based explanation for a prediction."""
        if self.model is None or self.explainer is None:
            return self._fallback_explanation(features_dict)

        try:
            frame = pd.DataFrame([features_dict])
            shap_values = self.explainer.shap_values(frame)

            # For binary classification, get the fraud class (index 1)
            if isinstance(shap_values, list):
                shap_vals = shap_values[1][0]
            else:
                shap_vals = shap_values[0]

            # Get base value (expected model output)
            if hasattr(self.explainer, "expected_value"):
                base_value = (
                    self.explainer.expected_value[1]
                    if isinstance(self.explainer.expected_value, list)
                    else self.explainer.expected_value
                )
            else:
                base_value = 0.5

            # Create feature importance ranking
            feature_importance = []
            for feature, shap_val in zip(self.feature_columns, shap_vals):
                feature_importance.append(
                    {
                        "feature": feature,
                        "shap_value": float(shap_val),
                        "feature_value": float(features_dict.get(feature, 0)),
                        "impact": "increases_fraud_risk"
                        if shap_val > 0
                        else "decreases_fraud_risk",
                    }
                )

            # Sort by absolute SHAP value
            feature_importance.sort(
                key=lambda x: abs(x["shap_value"]), reverse=True
            )

            return {
                "method": "SHAP (SHapley Additive exPlanations)",
                "base_value": float(base_value),
                "feature_importance": feature_importance[:3],  # Top 3 features
                "all_features": feature_importance,
            }

        except Exception as e:
            logger.warning(f"SHAP explanation failed: {e}")
            return self._fallback_explanation(features_dict)

    def _fallback_explanation(
        self, features_dict: dict[str, float]
    ) -> dict[str, Any]:
        """Provide explanations when SHAP is unavailable."""
        feature_importance = []
        for feature, value in features_dict.items():
            # Heuristic: higher risk if values indicate anomaly
            risk_score = 0.0
            if feature == "amount_to_avg_ratio" and value > 3:
                risk_score = value * 0.2
            elif feature == "count_1m" and value > 5:
                risk_score = value * 0.1
            elif feature == "is_high_risk_country" and value == 1:
                risk_score = 0.3
            elif feature == "is_gambling_mcc" and value == 1:
                risk_score = 0.25
            elif feature == "is_night" and value == 1:
                risk_score = 0.15

            feature_importance.append(
                {
                    "feature": feature,
                    "shap_value": risk_score,
                    "feature_value": float(value),
                    "impact": "increases_fraud_risk"
                    if risk_score > 0
                    else "decreases_fraud_risk",
                }
            )

        feature_importance.sort(
            key=lambda x: abs(x["shap_value"]), reverse=True
        )

        return {
            "method": "Heuristic (SHAP unavailable)",
            "base_value": 0.5,
            "feature_importance": feature_importance[:3],
            "all_features": feature_importance,
        }


def generate_human_readable_explanation(explanation: dict[str, Any]) -> list[str]:
    """Convert SHAP explanation to human-readable reasons."""
    reasons = []

    for feat_info in explanation.get("feature_importance", []):
        feature = feat_info["feature"]
        value = feat_info["feature_value"]
        impact = feat_info["impact"]

        if "increases" in impact:
            if feature == "amount_to_avg_ratio" and value > 2:
                reasons.append(
                    f"Необычно высокая сумма: {value:.1f}x от среднего"
                )
            elif feature == "count_1m" and value > 3:
                reasons.append(f"Большое количество транзакций: {int(value)} за 1 мин")
            elif feature == "is_high_risk_country" and value == 1:
                reasons.append("Транзакция из страны высокого риска")
            elif feature == "is_gambling_mcc" and value == 1:
                reasons.append("MCC код связан с азартными играми")
            elif feature == "is_night" and value == 1:
                reasons.append("Ночной час активности")

    return reasons or ["Нет специфических аномалий по SHAP"]
