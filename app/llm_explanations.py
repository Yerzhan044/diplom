"""LLM-powered natural language explanations using Claude API."""

import os
from typing import Optional

from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class LLMExplainer:
    """Generate natural language fraud explanations using Claude."""

    def __init__(self):
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 256

    def generate_explanation(
        self,
        fraud_probability: float,
        rule_score: float,
        final_score: float,
        decision: str,
        reasons: list[str],
        ml_features: dict,
    ) -> str:
        """
        Generate natural language explanation for fraud decision.

        Args:
            fraud_probability: ML model's fraud probability (0-1)
            rule_score: Rule engine score (0-1)
            final_score: Final ensemble score (0-1)
            decision: APPROVE/REVIEW/DECLINE
            reasons: List of rule-based reasons
            ml_features: ML features dict

        Returns:
            Natural language explanation string
        """
        try:
            prompt = self._build_prompt(
                fraud_probability,
                rule_score,
                final_score,
                decision,
                reasons,
                ml_features,
            )

            message = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )

            return message.content[0].text

        except Exception as e:
            return f"Transaction decision: {decision}. Unable to generate detailed explanation."

    def _build_prompt(
        self,
        fraud_probability: float,
        rule_score: float,
        final_score: float,
        decision: str,
        reasons: list[str],
        ml_features: dict,
    ) -> str:
        """Build the prompt for Claude."""
        reasons_text = "\n".join([f"  • {r}" for r in reasons]) if reasons else "  • No anomalies detected"

        features_text = (
            f"  • Transaction amount: ${ml_features.get('amount', 'N/A')}\n"
            f"  • Transactions in last 1 min: {int(ml_features.get('count_1m', 0))}\n"
            f"  • Transactions in last 5 min: {int(ml_features.get('count_5m', 0))}\n"
            f"  • Amount vs 30-day average: {ml_features.get('amount_to_avg_ratio', 0):.2f}x\n"
            f"  • High-risk country: {'Yes' if ml_features.get('is_high_risk_country', 0) else 'No'}\n"
            f"  • Night transaction: {'Yes' if ml_features.get('is_night', 0) else 'No'}\n"
            f"  • Gambling merchant: {'Yes' if ml_features.get('is_gambling_mcc', 0) else 'No'}"
        )

        return f"""You are a fraud detection analyst. Explain a credit card fraud decision in 1-2 sentences, in plain English, for a customer or regulator.

DECISION: {decision}
Final Fraud Score: {final_score:.2%}
  - ML Model Score: {fraud_probability:.2%}
  - Rule Engine Score: {rule_score:.2%}

DETECTED ISSUES:
{reasons_text}

TRANSACTION DETAILS:
{features_text}

Write a brief, clear explanation (1-2 sentences) of WHY the transaction was {decision}. Be specific about the key factors. Avoid jargon."""

    def generate_batch_summary(
        self, decisions: dict[str, int], total: int, fraud_avg: float
    ) -> str:
        """Generate summary for batch processing."""
        try:
            prompt = f"""Summarize these batch fraud detection results in 1-2 sentences, for a compliance report:
- Total transactions: {total}
- Approved: {decisions.get('APPROVE', 0)}
- Under review: {decisions.get('REVIEW', 0)}
- Declined: {decisions.get('DECLINE', 0)}
- Average fraud probability: {fraud_avg:.2%}

Be concise and professional."""

            message = client.messages.create(
                model=self.model,
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}],
            )

            return message.content[0].text

        except Exception:
            return f"Processed {total} transactions: {decisions.get('APPROVE', 0)} approved, {decisions.get('REVIEW', 0)} for review, {decisions.get('DECLINE', 0)} declined."


# Singleton instance
_llm_explainer: Optional[LLMExplainer] = None


def get_llm_explainer() -> Optional[LLMExplainer]:
    """Get or create LLM explainer instance."""
    global _llm_explainer
    if _llm_explainer is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            _llm_explainer = LLMExplainer()
    return _llm_explainer
