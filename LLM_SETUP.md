# 🤖 LLM Integration Guide

## Quick Start

The system now includes **Claude API integration** for natural language fraud explanations. Every transaction decision includes an AI-generated explanation.

### Step 1: Get Your API Key

```bash
# Your API key is at: https://console.anthropic.com/account/keys
# Email: kengesbaeve28@gmail.com
```

### Step 2: Add API Key to .env

```bash
# Edit .env file
ANTHROPIC_API_KEY=sk-ant-YOUR-KEY-HERE
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
# or just: pip install anthropic>=0.28.0
```

### Step 4: Run the System

```bash
python3 -m train.train_model  # Generate models
uvicorn app.main:app --reload  # Start API
```

---

## How It Works

### Single Transaction Example

**Request:**
```bash
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "tx_001",
    "card_id": "card_123",
    "merchant_id": "m_456",
    "amount": 5000.0,
    "currency": "USD",
    "country": "RU",
    "mcc": "7995",
    "device_id": "d_789",
    "ip_address": "192.168.1.1",
    "timestamp": "2026-05-14T15:30:00+00:00"
  }'
```

**Response:**
```json
{
  "transaction_id": "tx_001",
  "fraud_probability": 0.7234,
  "rule_score": 0.8500,
  "final_score": 0.7755,
  "decision": "REVIEW",
  "reasons": [
    "High-risk country: RU",
    "Night transaction detected",
    "Gambling merchant detected"
  ],
  "explanation": "This transaction requires manual review due to a combination of risk factors. The card is located in a high-risk country (Russia) and the transaction occurred during night hours (23:00-05:00), with an amount of $5000 on a gambling merchant category. These factors together indicate a 77.55% fraud probability."
}
```

---

## Features

### 🎯 What LLM Does

1. **Natural Language Explanations**: Converts technical scores into human-readable text
2. **Context-Aware**: Explains specific factors that triggered the decision
3. **Compliance-Ready**: Suitable for customer service and regulatory reports
4. **Non-Technical Language**: Accessible to non-experts

### 📊 Explanation Components

The LLM considers:
- **Final fraud score** and decision rationale
- **ML model confidence** (fraud probability)
- **Rule violations** (velocity, geography, behavior)
- **Transaction details** (amount, country, merchant type, time)
- **Feature analysis** (transaction velocity, average amounts)

---

## Architecture

```
POST /score
    ↓
[Validation] → [Feature Engineering]
    ↓
[Ensemble ML Scoring]
    ├─ Supervised: fraud_probability
    ├─ Unsupervised: anomaly_score
    └─ Rules: rule_score
    ↓
[Decision Layer] → APPROVE/REVIEW/DECLINE
    ↓
[XAI Layer] → SHAP explanations (technical)
    ↓
[LLM Layer] ← NEW! ← Claude API
    │  ├─ Scores, reasons, features
    │  └─ Generate natural language
    ↓
[Response] → ScoreResponse with "explanation" field
    ↓
[Logging] → JSONL audit trail
```

---

## Performance Impact

- **Latency**: +100-200ms per request (LLM API call)
  - Can be reduced with caching strategy
  - Consider batch processing for high-throughput scenarios

- **Cost**: ~$0.003 per transaction (Sonnet 3.5 pricing)
  - Can be reduced by using smaller model or caching

---

## Configuration

### Model Selection

Currently using `claude-3-5-sonnet-20241022` (best balance of speed/cost).

To change:
```python
# In app/llm_explanations.py
self.model = "claude-opus-4-1"  # More powerful, slower
self.model = "claude-3-haiku-20240307"  # Faster, cheaper
```

### Token Limits

```python
self.max_tokens = 256  # Max response length
```

---

## Error Handling

If Claude API is unavailable:
- System falls back to basic rule-based explanations
- No transaction scoring is blocked
- Graceful degradation

**Example fallback:**
```json
{
  "explanation": "Transaction decision: REVIEW. Unable to generate detailed explanation."
}
```

---

## Testing

### Test with Valid API Key

```bash
# 1. Update .env with your real API key
ANTHROPIC_API_KEY=sk-ant-...

# 2. Start the API
uvicorn app.main:app --reload

# 3. Test single transaction
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{...transaction data...}'

# 4. Check explanation field in response
```

### Test with Mock (no API key needed)

Replace `get_llm_explainer()` in `app/main.py`:
```python
# Mock for testing
if not os.getenv("ANTHROPIC_API_KEY"):
    llm_explainer = None  # Falls back to rule-based
```

---

## Batch Processing

For CSV uploads, the LLM also generates **batch summaries**:

```python
# In app/llm_explanations.py
summary = llm_explainer.generate_batch_summary(
    decisions={"APPROVE": 45, "REVIEW": 4, "DECLINE": 1},
    total=50,
    fraud_avg=0.1234
)
```

---

## Monitoring & Logging

All LLM explanations are saved in the security logs:

```bash
# View suspicious transactions with LLM explanations
tail -f logs/suspicious_transactions.jsonl | jq '.explanation'
```

---

## Limitations & Future Work

### Current Limitations
- ✅ English explanations only (multilingual in v2.3)
- ✅ +100-200ms latency per transaction
- ✅ Requires API key (no local fallback)

### Future Enhancements
- [ ] Caching layer for similar transactions
- [ ] Multilingual support (Russian, Chinese, etc.)
- [ ] Faster models (Haiku) with cost optimization
- [ ] Batch explanation generation
- [ ] Custom explanation templates per use case

---

## Cost Estimation

**Assumption**: 1,000 transactions/day

| Model | Cost/1K | Daily Cost | Monthly |
|-------|---------|-----------|---------|
| Sonnet 3.5 | $3 | $3 | $90 |
| Haiku | $0.80 | $0.80 | $24 |
| Opus | $15 | $15 | $450 |

---

## Support

**Anthropic API Issues**:
- Dashboard: https://console.anthropic.com
- Docs: https://docs.anthropic.com
- Email: support@anthropic.com

**Project Issues**:
- Check: `logs/predictions.jsonl`
- Test: `curl http://localhost:8000/health`

---

## Version Info

- **System Version**: 2.2
- **LLM Integration**: Claude API (Sonnet 3.5)
- **Added**: 2026-05-14
- **Status**: ✅ Production Ready

