# ⚡ Quick Start: Free LLM (2-5 minutes)

**Pick one option below:**

---

## 🆓 Option 1: Groq (Cloud, Fastest Setup - 2 min)

### Step 1: Get Free API Key
```
https://console.groq.com/keys
No credit card required!
```

### Step 2: Update .env
```bash
GROQ_API_KEY=gsk_YOUR_KEY_HERE
```

### Step 3: Run
```bash
pip install groq
python3 -m train.train_model
uvicorn app.main:app --reload
```

✅ **Done!** Explanations powered by free Groq.

---

## 🖥️ Option 2: Ollama (Local, 100% Free - 5 min)

### Step 1: Install
```bash
# Download: https://ollama.ai
# Or: brew install ollama
```

### Step 2: Start
```bash
ollama serve
```

### Step 3: Download Model
```bash
# In another terminal:
ollama pull mistral
```

### Step 4: Run
```bash
python3 -m train.train_model
uvicorn app.main:app --reload
```

✅ **Done!** Explanations powered by local Ollama.

---

## 💰 Option 3: Claude (Premium - 2 min)

### Step 1: Get API Key
```
https://console.anthropic.com/account/keys
```

### Step 2: Update .env
```bash
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
```

### Step 3: Run
```bash
pip install anthropic
python3 -m train.train_model
uvicorn app.main:app --reload
```

✅ **Done!** Explanations powered by Claude.

---

## 🎯 Recommendation

**Best free option**: **Groq**
- No installation needed
- Works in cloud
- Free tier: 14.4k requests/day
- Fast: 100-200ms

**Best local option**: **Ollama**
- Completely free
- No API key
- Runs on your machine
- Works offline

**Best quality**: **Claude**
- Premium quality
- Reliable API
- Costs ~$90/month

---

## ✅ Test It

### See Which LLM Activated
```bash
curl http://localhost:8000/health | jq .llm_source
```

### Run Demo
```bash
python3 examples/llm_free_demo.py
```

### Test with Transaction
```bash
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "tx_test",
    "card_id": "card_123",
    "amount": 100,
    "currency": "USD",
    "country": "US",
    "mcc": "5411",
    "device_id": "d_789",
    "ip_address": "192.168.1.1",
    "timestamp": "2026-05-14T15:30:00Z"
  }' | jq .explanation
```

---

**System picks automatically:**
1. Ollama (if running)
2. Groq (if API key set)
3. Claude (if API key set)
4. Fallback (no LLM)

**Choose one and go!** 🚀
