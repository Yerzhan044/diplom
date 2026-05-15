#!/usr/bin/env python3
"""
Demo: Free LLM explanations (Ollama, Groq, or Claude)

Shows how the system automatically picks the best LLM:
1. Ollama (local, free)
2. Groq (cloud, free tier)
3. Claude (paid, premium)
"""

import os
from datetime import datetime, timezone

# Try importing free LLM modules
try:
    from app.llm_free import get_free_explainer, get_groq_explainer
    from app.llm_explanations import get_llm_explainer
except ImportError:
    print("Error: Install dependencies: pip install -r requirements.txt")
    exit(1)


def detect_available_llms():
    """Detect which LLM providers are available."""
    print("🔍 Detecting available LLM providers...\n")

    ollama = get_free_explainer()
    groq = get_groq_explainer()
    claude = get_llm_explainer()

    print("Available LLMs:")
    print(f"  ✅ Ollama (local)  → {ollama is not None and ollama.available}")
    print(f"  ✅ Groq (cloud)    → {groq is not None and groq.available}")
    print(f"  ✅ Claude (paid)   → {claude is not None}")

    # Determine which will be used
    print("\nPriority order (first available is used):")
    if ollama and ollama.available:
        print("  🥇 Ollama - LOCAL & FREE (SELECTED)")
        return ollama, "Ollama"
    elif groq and groq.available:
        print("  🥇 Groq - CLOUD & FREE (SELECTED)")
        return groq, "Groq"
    elif claude:
        print("  🥇 Claude - PAID OPTION (SELECTED)")
        return claude, "Claude"
    else:
        print("  ⚠️  No LLM provider available (fallback mode)")
        return None, "None"


def demo_transaction(explainer, provider_name, fraud_prob, rule_score, decision, reasons):
    """Demo a single transaction."""
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

    final_score = 0.5 * fraud_prob + 0.2 * 0.45 + 0.3 * rule_score

    print(f"\n{'=' * 70}")
    print(f"Transaction Demo ({provider_name})")
    print(f"{'=' * 70}")

    print(f"\n📊 Scores:")
    print(f"  Fraud probability: {fraud_prob:.1%}")
    print(f"  Rule score: {rule_score:.1%}")
    print(f"  Final score: {final_score:.1%}")
    print(f"\n🎯 Decision: {decision}")
    print(f"\n📋 Reasons:")
    for reason in reasons:
        print(f"  • {reason}")

    if explainer:
        try:
            print(f"\n🤖 {provider_name} Explanation:")
            explanation = explainer.generate_explanation(
                fraud_probability=fraud_prob,
                rule_score=rule_score,
                final_score=final_score,
                decision=decision,
                reasons=reasons,
                ml_features=ml_features,
            )
            print(f"  {explanation}")
        except Exception as e:
            print(f"  ⚠️ Error: {e}")
    else:
        print(f"\n⚠️ {provider_name} not available (using fallback)")


def main():
    """Run the demo."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  🆓 Free LLM Explanations Demo  ".center(68) + "║")
    print("║" + "  (Ollama, Groq, or Claude)  ".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    # Detect available LLMs
    explainer, provider = detect_available_llms()

    # Demo transaction
    print("\n")
    print("📝 Testing with a suspicious transaction:")
    print("   - Country: Russia (high-risk)")
    print("   - Time: 02:45 UTC (night)")
    print("   - Amount: $5000 (33x above average)")
    print("   - Merchant: Gambling (risky category)")

    if explainer:
        demo_transaction(
            explainer,
            provider,
            fraud_prob=0.72,
            rule_score=0.85,
            decision="REVIEW",
            reasons=[
                "High-risk country detected",
                "Night transaction (02:45 UTC)",
                "Gambling merchant category",
                "Amount significantly above average (33.3x)",
            ],
        )
    else:
        demo_transaction(
            None,
            "Rule-Based (Fallback)",
            fraud_prob=0.72,
            rule_score=0.85,
            decision="REVIEW",
            reasons=[
                "High-risk country detected",
                "Night transaction detected",
                "Gambling merchant detected",
            ],
        )

    # Instructions
    print("\n\n" + "=" * 70)
    print("Setup Instructions")
    print("=" * 70)

    if not explainer or provider == "None":
        print("\n⚠️ No LLM provider is currently available.\n")
        print("To enable free explanations, choose one:\n")

        print("1️⃣  OLLAMA (Recommended for development)")
        print("   • Download: https://ollama.ai")
        print("   • Run: ollama serve")
        print("   • Pull model: ollama pull mistral")
        print("   • No API key needed!")
        print("   • Completely free and local\n")

        print("2️⃣  GROQ (Recommended for production)")
        print("   • Get free API key: https://console.groq.com/keys")
        print("   • Add to .env: GROQ_API_KEY=your-key")
        print("   • Install: pip install groq")
        print("   • Free tier: 14,400 requests/day\n")

        print("3️⃣  CLAUDE (Premium option)")
        print("   • Get API key: https://console.anthropic.com/account/keys")
        print("   • Add to .env: ANTHROPIC_API_KEY=sk-ant-...")
        print("   • Install: pip install anthropic")
        print("   • Cost: ~$90/month for 1k txns/day\n")

        print("Then run this demo again to see explanations!")
    else:
        print(f"\n✅ {provider} is set up and working!")
        print(f"\nYour fraud detection system will now use {provider}")
        print("for natural language explanations.\n")

        if provider == "Ollama":
            print("💡 Tip: Keep 'ollama serve' running in background")
        elif provider == "Groq":
            print("💡 Tip: Groq has generous free tier (14.4k requests/day)")
        elif provider == "Claude":
            print("💡 Tip: Claude is premium but offers best quality")

    print("\n" + "=" * 70)
    print("Start the API to see explanations in real transactions:")
    print("  python3 -m train.train_model")
    print("  uvicorn app.main:app --reload")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
