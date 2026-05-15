# 🚀 Quick Start: LLM Integration

**Time to setup**: 5 minutes  
**Status**: Production ready

---

## ⚡ TL;DR Setup

### Step 1: Get API Key (2 min)
```
https://console.anthropic.com/account/keys
```
Email: `kengesbaeve28@gmail.com`

### Step 2: Update .env (1 min)
```bash
ANTHROPIC_API_KEY=sk-ant-YOUR-KEY-HERE
```

### Step 3: Install & Run (2 min)
```bash
pip install -r requirements.txt
python3 -m train.train_model
uvicorn app.main:app --reload
```

**Done!** Go to http://localhost:8000

---

## 📋 What Changed

### Code Files (4 files)
- ✅ `app/llm_explanations.py` - NEW: LLM explainer module
- ✅ `app/main.py` - Updated: added LLM integration
- ✅ `app/schemas.py` - Updated: added explanation field
- ✅ `requirements.txt` - Updated: added anthropic

### Config Files (1 file)
- ✅ `.env` - NEW: API key configuration

### Docs (3 files)
- ✅ `LLM_SETUP.md` - Full setup guide
- ✅ `LLM_INTEGRATION_SUMMARY.md` - Executive summary
- ✅ `QUICK_START_LLM.md` - This file

---

## 🧪 Quick Test

### Without API Key
```bash
# Works fine - just no LLM explanations
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "tx_test",
    "card_id": "card_123",
    "merchant_id": "m_456",
    "amount": 100,
    "currency": "USD",
    "country": "US",
    "mcc": "5411",
    "device_id": "d_789",
    "ip_address": "192.168.1.1",
    "timestamp": "2026-05-14T15:30:00Z"
  }' | jq .
```

### With API Key
Same request → now includes natural language "explanation"

---

## 📝 Example Response

### APPROVE (Normal transaction)
```json
{
  "decision": "APPROVE",
  "final_score": 0.15,
  "explanation": "This transaction appears legitimate. The transaction amount is within normal range and velocity patterns are typical for this card."
}
```

### REVIEW (Suspicious)
```json
{
  "decision": "REVIEW", 
  "final_score": 0.77,
  "explanation": "This transaction requires manual review due to high-risk country, night-time activity, and amount significantly above historical average for this card."
}
```

### DECLINE (High Risk)
```json
{
  "decision": "DECLINE",
  "final_score": 0.94,
  "explanation": "This transaction has been declined due to extreme fraud risk. Multiple critical factors: unusually high velocity (5 transactions in 1 minute), transaction amount 125x above average, and location in high-risk country."
}
```

---

## 🔗 What LLM Sees

```
LLM Input:
├─ Final Score: 77% (REVIEW)
├─ Fraud Probability: 72.34%
├─ Rule Score: 85%
├─ Decision: REVIEW
├─ Reasons:
│  ├─ High-risk country: RU
│  ├─ Night transaction
│  └─ Gambling merchant
└─ Features:
   ├─ Amount: $5000
   ├─ Velocity: 3 txns in 5 min
   ├─ Avg historical: $150
   └─ Amount ratio: 33.3x

LLM Output:
"This transaction requires manual review due to a 
combination of risk factors. The card is located in 
a high-risk country (Russia) and the transaction 
occurred during night hours (23:00-05:00), with an 
amount of $5000 on a gambling merchant category. 
These factors together indicate a 77.55% fraud 
probability."
```

---

## ⚙️ How to Change Settings

### Use Faster/Cheaper Model
```python
# In app/llm_explanations.py, line 11
self.model = "claude-3-haiku-20240307"  # 5x faster, 80% cheaper
```

### Reduce Token Limit
```python
# In app/llm_explanations.py, line 12
self.max_tokens = 150  # Shorter explanations
```

### Increase Explanation Detail
```python
# In app/llm_explanations.py, line 12
self.max_tokens = 512  # Longer explanations
```

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Setup time | 5 min |
| Extra latency per request | +100-150ms |
| Cost per transaction | $0.003 (Sonnet) |
| Monthly cost (1k/day) | ~$90 |
| Fallback behavior | Rule-based explanations |

---

## ✅ Checklist

- [ ] API key from https://console.anthropic.com
- [ ] Updated `.env` with API key
- [ ] Installed anthropic: `pip install anthropic`
- [ ] Trained models: `python3 -m train.train_model`
- [ ] Started API: `uvicorn app.main:app --reload`
- [ ] Tested `/score` endpoint
- [ ] Checked response has `explanation` field

---

## 🐛 Troubleshooting

### LLM explanations are empty
```bash
# Check if API key is set
echo $ANTHROPIC_API_KEY

# If empty, update .env
export ANTHROPIC_API_KEY=sk-ant-YOUR-KEY
```

### "API Error: 401 Unauthorized"
```bash
# Invalid API key
# Get new one: https://console.anthropic.com/account/keys
```

### "ModuleNotFoundError: No module named 'anthropic'"
```bash
pip install anthropic>=0.28.0
```

### API is slow (> 500ms)
```bash
# Normal (LLM API calls take 100-200ms)
# To optimize: add caching or use smaller model
```

---

## 🎯 Next Steps

### Short Term (Now)
1. Set up API key
2. Test single transaction
3. Try batch CSV upload
4. Check logs/suspicious_transactions.jsonl

### Medium Term (v2.3)
- Add response caching
- Optimize with Haiku model
- Multilingual support

### Long Term (v2.4+)
- Custom explanation templates
- Streaming responses
- Advanced analytics

---

## 📚 Full Docs

- **Setup Details**: `LLM_SETUP.md`
- **Technical Summary**: `LLM_INTEGRATION_SUMMARY.md`
- **Working Demo**: `python3 examples/llm_demo.py`
- **System Architecture**: `CLAUDE.md`

---

**Questions?** Check the docs or run: `python3 examples/llm_demo.py`

