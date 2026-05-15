# 🆓 Free LLM Integration Guide

**Status**: ✅ Added  
**Options**: 3 (Ollama, Groq, Claude)  
**Date**: 2026-05-14

---

## 📊 LLM Options Comparison

| Option | Cost | Setup | Speed | Quality | Best For |
|--------|------|-------|-------|---------|----------|
| **Ollama** | 🆓 FREE | 5 min | ⚡ Fast | ⭐⭐⭐⭐ | Local development |
| **Groq** | 🆓 FREE | 2 min | ⚡⚡ Very fast | ⭐⭐⭐⭐ | Production (free tier) |
| **Claude** | 💰 $90/mo | 2 min | ⚡⚡ Very fast | ⭐⭐⭐⭐⭐ | Premium/production |

---

## 🚀 Quick Start (Choose One)

### Option 1: Ollama (Local, Completely Free) ✅

**Step 1**: Install Ollama
```bash
# Download from: https://ollama.ai
# Or install via package manager:
brew install ollama          # macOS
sudo apt install ollama      # Linux (Debian/Ubuntu)
winget install Ollama        # Windows
```

**Step 2**: Start Ollama
```bash
ollama serve
# Ollama now running on: http://localhost:11434
```

**Step 3**: Pull a model (one-time)
```bash
# In another terminal:
ollama pull mistral
# Downloads: ~4.1GB (mistral model)
# Or: ollama pull neural-chat (smaller, faster)
```

**Step 4**: Run fraud detection system
```bash
python3 -m train.train_model
uvicorn app.main:app --reload
```

**Done!** System auto-detects Ollama and uses it. No API key needed.

**Check status**:
```bash
curl http://localhost:8000/health | jq .llm_source
# Response: "ollama (local, free)"
```

---

### Option 2: Groq (Cloud-Based Free Tier) ✅

**Step 1**: Get Free API Key
```
https://console.groq.com/keys
# No credit card required!
```

**Step 2**: Add to .env
```bash
GROQ_API_KEY=your-key-here
```

**Step 3**: Install Groq SDK
```bash
pip install groq
```

**Step 4**: Run system
```bash
python3 -m train.train_model
uvicorn app.main:app --reload
```

**Done!** System auto-detects Groq and uses it.

**Check status**:
```bash
curl http://localhost:8000/health | jq .llm_source
# Response: "groq (free tier)"
```

**Limits** (Free Tier):
- 14,400 requests/day
- 120 requests/minute
- ✅ Enough for ~500 transactions/day

---

### Option 3: Claude API (Premium)

**Step 1**: Get API Key
```
https://console.anthropic.com/account/keys
```

**Step 2**: Add to .env
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

**Step 3**: Install SDK
```bash
pip install anthropic
```

**Step 4**: Run system
```bash
python3 -m train.train_model
uvicorn app.main:app --reload
```

**Cost**: ~$90/month for 1,000 transactions/day

---

## 🎯 Recommendation

**For Development**: Use **Ollama** (local, free, no internet needed)  
**For Production (Free)**: Use **Groq** (fast, reliable, generous free tier)  
**For Premium**: Use **Claude** (best quality, more throughput)

---

## 🔄 How Priority Works

System automatically tries (in order):

```
1. Ollama (if running locally) ← Try this first
2. Groq (if GROQ_API_KEY set)
3. Claude API (if ANTHROPIC_API_KEY set)
4. Fallback (rule-based, no LLM)
```

**Example**:
```
If you have Ollama running → uses Ollama (free)
If Ollama not found → tries Groq (free)
If no Groq key → tries Claude (paid)
If nothing → works fine, just no LLM explanations
```

---

## 📝 Configuration

### .env File
```bash
# Claude API (optional, paid)
ANTHROPIC_API_KEY=sk-ant-...

# Groq (optional, free tier)
GROQ_API_KEY=gsk_...

# Ollama (none needed, just run locally)

# Fraud thresholds (required)
THRESHOLD=0.65
ALERT_THRESHOLD=0.85
```

### Ollama Model Selection

Edit `app/llm_free.py`, line 12:
```python
self.model = "mistral"       # Fast, 7B, high quality
# OR
self.model = "neural-chat"   # Faster, smaller, good quality
# OR  
self.model = "llama2"        # Slower, larger, best quality
# OR
self.model = "zephyr"        # Specialized for instructions
```

Available models: `ollama list`

---

## 🧪 Testing

### Test with Ollama
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Run demo
python3 examples/llm_free_demo.py
```

### Test with Groq
```bash
# Set API key
export GROQ_API_KEY=your-key

# Run demo
python3 examples/llm_free_demo.py
```

### Test with Claude
```bash
# Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# Run demo
python3 examples/llm_free_demo.py
```

---

## 📊 Performance Comparison

### Latency (per transaction)

| Provider | Latency | Cost/1K | Notes |
|----------|---------|---------|-------|
| Ollama | 200-500ms | Free | Depends on hardware |
| Groq | 100-200ms | Free | Very consistent |
| Claude | 100-150ms | $3 | Fastest, premium |

### Quality

All three produce natural language explanations:

**Same Input**: REVIEW decision, high-risk country, night transaction

**Ollama Output**:
```
"This transaction requires review due to high-risk 
country and night-time activity. Amount is within 
normal range but timing suggests caution."
```

**Groq Output**:
```
"Transaction requires review: detected high-risk 
country and night-time purchase. Consider additional 
verification."
```

**Claude Output**:
```
"This transaction requires manual review due to 
high-risk country (Russia) and night-time activity 
(02:45 UTC). However, the amount is within typical 
range and velocity patterns are normal."
```

---

## ⚡ Optimization Tips

### Use Ollama Efficiently
```bash
# Keep model in memory to avoid reload
# Ollama does this automatically

# Or use smaller model for faster inference
ollama pull neural-chat  # Smaller than Mistral
```

### Use Groq Efficiently
```bash
# Groq has great rate limits
# Current: 120 requests/minute
# That's ~2 requests/second
# Perfect for production

# Example: 1000 txns/day = ~0.012 requests/second
# Well under limit!
```

### Use Claude Efficiently
```bash
# Add caching if you have many repeat transactions
# Reduces cost by 50-70%
# See: examples/llm_demo.py
```

---

## 🔧 Troubleshooting

### Ollama Not Detected
```bash
# Check if running
curl http://localhost:11434/api/tags

# If error: Start Ollama
ollama serve

# Then restart FastAPI server
```

### Groq "401 Unauthorized"
```bash
# Invalid API key
# Get new: https://console.groq.com/keys
# Verify in .env: GROQ_API_KEY=gsk_...
```

### Claude "401 Unauthorized"
```bash
# Invalid API key
# Get new: https://console.anthropic.com/account/keys
```

### Slow Responses with Ollama
```bash
# Ollama is CPU-intensive
# Solutions:
# 1. Use smaller model: ollama pull neural-chat
# 2. Run on GPU machine
# 3. Switch to Groq (cloud-based)
# 4. Switch to Claude (premium)
```

---

## 📈 Scaling Strategy

**Development**: Ollama (local, free, no limits)

**Testing/Demo**: Groq (free tier, fast, reliable)

**Production (low volume)**: Groq free tier
- ✅ 14,400 requests/day
- ✅ $0 cost
- ✅ Very fast (100-200ms)

**Production (high volume)**: Claude API
- ✅ Unlimited requests
- ✅ ~$90/month (1k txns/day)
- ✅ Very fast (100-150ms)

---

## 🎯 Migration Path

```
START
  ↓
Use Ollama (develop locally)
  ↓
Test with Groq (no API cost)
  ↓
Deploy to prod with Groq (free tier)
  ↓
Scale to Claude if needed (pay for reliability)
```

---

## 💡 Advanced: Custom LLM

Want to use a different provider? Add to `app/llm_free.py`:

```python
class CustomLLMExplainer:
    def __init__(self):
        self.api_key = os.getenv("CUSTOM_API_KEY")
        
    def generate_explanation(self, ...):
        # Your custom implementation
        pass
```

Then update initialization in `app/main.py`:
```python
custom = CustomLLMExplainer()
if custom.available:
    llm_explainer = custom
```

---

## 📚 Resources

**Ollama**:
- Website: https://ollama.ai
- Models: https://ollama.ai/library

**Groq**:
- Console: https://console.groq.com
- Docs: https://console.groq.com/docs

**Claude**:
- Console: https://console.anthropic.com
- Docs: https://docs.anthropic.com

---

## ✅ Checklist

### Ollama (Free, Local)
- [ ] Download Ollama from https://ollama.ai
- [ ] Run: `ollama serve`
- [ ] Pull model: `ollama pull mistral`
- [ ] Start fraud system
- [ ] Test: `curl http://localhost:8000/health`

### Groq (Free, Cloud)
- [ ] Get key from https://console.groq.com/keys
- [ ] Add to .env: `GROQ_API_KEY=...`
- [ ] Install SDK: `pip install groq`
- [ ] Start fraud system
- [ ] Test: `curl http://localhost:8000/health`

### Claude (Paid, Premium)
- [ ] Get key from https://console.anthropic.com/account/keys
- [ ] Add to .env: `ANTHROPIC_API_KEY=...`
- [ ] Install SDK: `pip install anthropic`
- [ ] Start fraud system
- [ ] Test: `curl http://localhost:8000/health`

---

## 🎉 Summary

Your system now has **3 LLM options**:

1. **Ollama** - Free, local, no internet (recommended for dev)
2. **Groq** - Free cloud tier, fast (recommended for production)
3. **Claude** - Premium, best quality (recommended if budget allows)

**System automatically picks the best available option!**

---

**Version**: 2.2  
**Status**: ✅ Production Ready  
**Free Options**: 🆓 Yes!
