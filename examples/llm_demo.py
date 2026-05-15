#!/usr/bin/env python3
"""
Demo: LLM-powered fraud explanations

Shows how the system generates natural language explanations
using Claude API for fraud detection decisions.
"""

import json
import os
from datetime import datetime, timezone

# Set your API key before running
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY", "sk-ant-...")

from app.llm_explanations import LLMExplainer


def demo_approve_transaction():
    """Demo: Normal transaction gets APPROVE."""
    print("=" * 70)
    print("DEMO 1: Normal Transaction (APPROVE)")
    print("=" * 70)

    explainer = LLMExplainer()

    fraud_prob = 0.15
    rule_score = 0.10
    final_score = 0.12
    ml_features = {
        "amount": 45.50,
        "count_1m": 1,
        "count_5m": 2,
        "avg_amount_30": 42.0,
        "amount_to_avg_ratio": 1.08,
        "is_high_risk_country": 0.0,
        "is_night": 0.0,
        "is_gambling_mcc": 0.0,
    }

    explanation = explainer.generate_explanation(
        fraud_probability=fraud_prob,
        rule_score=rule_score,
        final_score=final_score,
        decision="APPROVE",
        reasons=["Normal transaction velocity", "Amount within historical range"],
        ml_features=ml_features,
    )

    print(f"\n💚 Decision: APPROVE")
    print(f"📊 Final Score: {final_score:.2%}")
    print(f"📝 LLM Explanation:\n   {explanation}\n")


def demo_review_transaction():
    """Demo: Suspicious transaction gets REVIEW."""
    print("=" * 70)
    print("DEMO 2: Suspicious Transaction (REVIEW)")
    print("=" * 70)

    explainer = LLMExplainer()

    fraud_prob = 0.72
    rule_score = 0.85
    final_score = 0.77
    ml_features = {
        "amount": 5000.0,
        "count_1m": 0,
        "count_5m": 3,
        "avg_amount_30": 150.0,
        "amount_to_avg_ratio": 33.33,
        "is_high_risk_country": 1.0,
        "is_night": 1.0,
        "is_gambling_mcc": 1.0,
    }

    explanation = explainer.generate_explanation(
        fraud_probability=fraud_prob,
        rule_score=rule_score,
        final_score=final_score,
        decision="REVIEW",
        reasons=[
            "High-risk country detected (RU)",
            "Night transaction (02:45 UTC)",
            "Gambling merchant category",
            "Amount 33x above average",
        ],
        ml_features=ml_features,
    )

    print(f"\n🟡 Decision: REVIEW")
    print(f"📊 Final Score: {final_score:.2%}")
    print(f"📝 LLM Explanation:\n   {explanation}\n")


def demo_decline_transaction():
    """Demo: Clearly fraudulent transaction gets DECLINE."""
    print("=" * 70)
    print("DEMO 3: High-Risk Transaction (DECLINE)")
    print("=" * 70)

    explainer = LLMExplainer()

    fraud_prob = 0.95
    rule_score = 0.92
    final_score = 0.94
    ml_features = {
        "amount": 25000.0,
        "count_1m": 5,
        "count_5m": 8,
        "avg_amount_30": 200.0,
        "amount_to_avg_ratio": 125.0,
        "is_high_risk_country": 1.0,
        "is_night": 1.0,
        "is_gambling_mcc": 1.0,
    }

    explanation = explainer.generate_explanation(
        fraud_probability=fraud_prob,
        rule_score=rule_score,
        final_score=final_score,
        decision="DECLINE",
        reasons=[
            "CRITICAL: Extreme velocity anomaly (5 txns in 1 min)",
            "CRITICAL: High-risk country with card velocity spike",
            "CRITICAL: Amount 125x above average",
            "Multiple rule violations in 60 seconds",
        ],
        ml_features=ml_features,
    )

    print(f"\n🔴 Decision: DECLINE")
    print(f"📊 Final Score: {final_score:.2%}")
    print(f"📝 LLM Explanation:\n   {explanation}\n")


def demo_batch_summary():
    """Demo: Batch processing summary."""
    print("=" * 70)
    print("DEMO 4: Batch Processing Summary")
    print("=" * 70)

    explainer = LLMExplainer()

    summary = explainer.generate_batch_summary(
        decisions={"APPROVE": 485, "REVIEW": 14, "DECLINE": 1},
        total=500,
        fraud_avg=0.0832,
    )

    print(f"\n📦 Batch Results (500 transactions):")
    print(f"   - Approved: 485 (97.0%)")
    print(f"   - Review: 14 (2.8%)")
    print(f"   - Declined: 1 (0.2%)")
    print(f"   - Average fraud score: 8.32%")
    print(f"\n📝 LLM Summary:\n   {summary}\n")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  🤖 LLM-Powered Fraud Detection - Demo  ".center(68) + "║")
    print("║" + "  (Claude API for Natural Language Explanations)  ".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or api_key.startswith("sk-ant-YOUR"):
            print(
                "⚠️  No valid API key found!\n"
                "Set ANTHROPIC_API_KEY in .env to run this demo.\n"
                "Get your free key at: https://console.anthropic.com/account/keys\n"
            )
            return

        demo_approve_transaction()
        demo_review_transaction()
        demo_decline_transaction()
        demo_batch_summary()

        print("✅ All demos completed successfully!")
        print("ℹ️  For more info, see: LLM_SETUP.md\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"\nMake sure ANTHROPIC_API_KEY is set correctly in .env")


if __name__ == "__main__":
    main()
