"""Free LLM explanations using Ollama (local) or Groq API."""

import os
from typing import Optional

try:
    import requests
except ImportError:
    requests = None


class OllamaExplainer:
    """Free local LLM using Ollama (no API key needed)."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "mistral"  # Fast, free, good quality
        self.available = self._check_connection()

    def _check_connection(self) -> bool:
        """Check if Ollama is running."""
        try:
            if not requests:
                return False
            resp = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return resp.status_code == 200
        except Exception:
            return False

    def generate_explanation(
        self,
        fraud_probability: float,
        rule_score: float,
        final_score: float,
        decision: str,
        reasons: list[str],
        ml_features: dict,
    ) -> str:
        """Generate explanation using local Ollama."""
        if not self.available:
            return self._fallback_explanation(decision, reasons)

        try:
            prompt = self._build_prompt(
                fraud_probability,
                rule_score,
                final_score,
                decision,
                reasons,
                ml_features,
            )

            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=15,
            )

            if resp.status_code == 200:
                return resp.json().get("response", "")
            return self._fallback_explanation(decision, reasons)

        except Exception:
            return self._fallback_explanation(decision, reasons)

    def _build_prompt(
        self,
        fraud_probability: float,
        rule_score: float,
        final_score: float,
        decision: str,
        reasons: list[str],
        ml_features: dict,
    ) -> str:
        """Build prompt for Ollama."""
        reasons_text = "\n".join([f"  • {r}" for r in reasons]) if reasons else "  • No anomalies detected"

        features_text = (
            f"  • Amount: ${ml_features.get('amount', 'N/A')}\n"
            f"  • Txns (1 min): {int(ml_features.get('count_1m', 0))}\n"
            f"  • Txns (5 min): {int(ml_features.get('count_5m', 0))}\n"
            f"  • Amount ratio: {ml_features.get('amount_to_avg_ratio', 0):.2f}x\n"
            f"  • High-risk country: {'Yes' if ml_features.get('is_high_risk_country', 0) else 'No'}\n"
            f"  • Night txn: {'Yes' if ml_features.get('is_night', 0) else 'No'}"
        )

        return f"""Explain a fraud decision in 1-2 sentences, plain English:

DECISION: {decision}
Score: {final_score:.1%} (ML: {fraud_probability:.1%}, Rules: {rule_score:.1%})

ISSUES:
{reasons_text}

DETAILS:
{features_text}

Explain WHY {decision}. Be specific, avoid jargon."""

    def _fallback_explanation(self, decision: str, reasons: list[str]) -> str:
        """Fallback if Ollama unavailable."""
        if not reasons:
            return f"Transaction: {decision}"

        reason_text = "; ".join(reasons[:2])
        return f"Transaction {decision}: {reason_text}"

    def generate_batch_summary(
        self, decisions: dict[str, int], total: int, fraud_avg: float
    ) -> str:
        """Generate batch summary."""
        if not self.available:
            return f"Processed {total} transactions: {decisions.get('APPROVE', 0)} approved, {decisions.get('REVIEW', 0)} review, {decisions.get('DECLINE', 0)} declined."

        try:
            prompt = f"""Summarize in 1-2 sentences:
{total} transactions: {decisions.get('APPROVE', 0)} approved, {decisions.get('REVIEW', 0)} review, {decisions.get('DECLINE', 0)} declined.
Average fraud risk: {fraud_avg:.1%}"""

            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=10,
            )

            if resp.status_code == 200:
                return resp.json().get("response", "")
            return f"Processed {total} transactions."

        except Exception:
            return f"Processed {total} transactions."


class GroqExplainer:
    """Free Groq API (fast inference, generous free tier)."""

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = "mixtral-8x7b-32768"
        self.available = bool(self.api_key)

        if self.available:
            try:
                from groq import Groq as GroqClient

                self.client = GroqClient(api_key=self.api_key)
            except ImportError:
                self.available = False

    def generate_explanation(
        self,
        fraud_probability: float,
        rule_score: float,
        final_score: float,
        decision: str,
        reasons: list[str],
        ml_features: dict,
    ) -> str:
        """Generate explanation using Groq API."""
        if not self.available:
            return self._fallback_explanation(decision, reasons)

        try:
            prompt = self._build_prompt(
                fraud_probability,
                rule_score,
                final_score,
                decision,
                reasons,
                ml_features,
            )

            message = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                max_tokens=200,
                temperature=0.3,
            )

            return message.choices[0].message.content

        except Exception:
            return self._fallback_explanation(decision, reasons)

    def _build_prompt(
        self,
        fraud_probability: float,
        rule_score: float,
        final_score: float,
        decision: str,
        reasons: list[str],
        ml_features: dict,
    ) -> str:
        """Build prompt for Groq."""
        reasons_text = "\n".join([f"  • {r}" for r in reasons]) if reasons else "  • No anomalies"

        return f"""Explain fraud decision in 1-2 sentences:

DECISION: {decision}
SCORE: {final_score:.1%}
REASONS:
{reasons_text}

Be brief, specific, non-technical."""

    def _fallback_explanation(self, decision: str, reasons: list[str]) -> str:
        """Fallback explanation."""
        if not reasons:
            return f"Transaction: {decision}"
        return f"Transaction {decision}: {reasons[0]}"

    def generate_batch_summary(
        self, decisions: dict[str, int], total: int, fraud_avg: float
    ) -> str:
        """Generate batch summary."""
        if not self.available:
            return f"Processed {total} transactions."

        try:
            prompt = f"Summarize in 1 sentence: {total} transactions processed, {fraud_avg:.1%} avg risk."

            message = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                max_tokens=100,
            )

            return message.choices[0].message.content

        except Exception:
            return f"Processed {total} transactions."


def get_free_explainer() -> Optional[OllamaExplainer]:
    """Get free Ollama explainer (local)."""
    explainer = OllamaExplainer()
    if explainer.available:
        return explainer
    return None


def get_groq_explainer() -> Optional[GroqExplainer]:
    """Get free Groq explainer (if API key set)."""
    explainer = GroqExplainer()
    if explainer.available:
        return explainer
    return None
