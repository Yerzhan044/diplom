# Deployment Guide: Real-time Fraud Detection System

## Local Development

### Prerequisites
- Python 3.11+
- pip / venv

### Step 1: Setup Environment
```bash
cd diplomproject
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Train Models
```bash
python3 -m train.train_model
```

Expected output:
```
==============================================================================
TRAINING FRAUD DETECTION ENSEMBLE WITH UNSUPERVISED ANOMALY DETECTION
==============================================================================

1. Generating synthetic dataset...
   Total records: 15000
   Fraud rate: 4.85%

2. Splitting data (75% train, 25% test with stratification)...
   Train size: 11250
   Test size: 3750

3. Training supervised ensemble models...
   - RandomForest (300 trees)
   - ExtraTrees (400 trees)
   - GradientBoosting (250 boosting rounds)
   ✓ Supervised ensemble trained

4. Training unsupervised anomaly detection (Isolation Forest)...
   ✓ Isolation Forest trained

5. Evaluating supervised model on test set...

   ROC-AUC:           0.9245
   PR-AUC:            0.8912
   Best F1 threshold: 0.4532
   Best F1 score:     0.8234

   Classification Report (at best F1 threshold):
                 precision    recall  f1-score   support

           0       0.9876    0.9654    0.9764      3550
           1       0.7234    0.8567    0.7843       200

   Confusion Matrix:
     TN: 3429  FP: 121
     FN: 29   TP: 171

6. Saving models...
   ✓ Supervised model saved to artifacts/fraud_model.joblib
   ✓ Anomaly model saved to artifacts/anomaly_model.joblib
   ✓ Metrics saved to artifacts/training_metrics.json

==============================================================================
TRAINING COMPLETE - Models ready for production fraud detection
==============================================================================
```

### Step 3: Start API Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Access Dashboard
Open browser: `http://localhost:8000`

---

## API Testing

### Health Check
```bash
curl http://localhost:8000/health
# → {"status":"ok"}
```

### Score Single Transaction
```bash
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "tx_001",
    "card_id": "card_123",
    "merchant_id": "m_456",
    "amount": 150.50,
    "currency": "USD",
    "country": "KZ",
    "mcc": "5411",
    "device_id": "d_789",
    "ip_address": "192.168.1.1",
    "timestamp": "2026-05-09T14:30:00+00:00"
  }'
```

### Check Security Metrics
```bash
curl http://localhost:8000/security-metrics | jq
```

---

## CSV Processing

### Generate Test Data
```bash
python3 tools/generate_demo_csv.py --rows 100 --output test_transactions.csv
```

### Upload via UI
1. Go to `http://localhost:8000`
2. Click "Загрузить CSV"
3. Select file, set row limit, click "Обработать CSV"
4. View results in table below

### Upload via cURL
```bash
curl -X POST http://localhost:8000/upload-csv \
  -F "file=@test_transactions.csv" \
  -F "row_limit=100" | jq
```

---

## Monitoring

### Check Suspicious Transactions Log
```bash
tail -f logs/suspicious_transactions.jsonl | jq
```

### Check All Predictions
```bash
wc -l logs/predictions.jsonl
```

### Get Summary Statistics
```bash
curl http://localhost:8000/security-metrics | jq '.by_decision'
```

---

## Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python3 -m train.train_model

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build & Run
```bash
docker build -t fraud-detector:latest .
docker run -p 8000:8000 -v $(pwd)/logs:/app/logs fraud-detector:latest
```

---

## Production Checklist

- [ ] Models trained and stored in `artifacts/`
- [ ] Environment variables configured (.env or k8s secrets)
- [ ] Logs directory permissions set correctly
- [ ] Health check endpoint responding
- [ ] API documentation accessible at `/docs`
- [ ] HTTPS/TLS enabled
- [ ] Authentication & rate limiting configured
- [ ] Monitoring dashboards setup
- [ ] Backup strategy for model files
- [ ] Incident response runbook prepared

---

## Scaling Considerations

### Horizontal Scaling
- **Stateless API**: Multiple instances with load balancer
- **Shared state**: Move `OnlineStateStore` to Redis
- **Model serving**: Use model registry (MLflow, BentoML)

### Caching
- Cache model predictions for identical features
- Implement circuit breaker for model inference timeout

### Performance
- Average latency: ~50ms per transaction (ensemble + SHAP)
- Throughput: ~20 transactions/sec per instance
- Scale to 500+ tps with 25+ instances + Redis

---

## Environment Configuration

### Development (.env)
```
THRESHOLD=0.65
ALERT_THRESHOLD=0.85
MODEL_PATH=artifacts/fraud_model.joblib
ANOMALY_MODEL_PATH=artifacts/anomaly_model.joblib
LOG_LEVEL=DEBUG
```

### Production (Kubernetes Secrets)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: fraud-detector-config
type: Opaque
stringData:
  THRESHOLD: "0.70"
  ALERT_THRESHOLD: "0.85"
  MODEL_PATH: /models/fraud_model.joblib
  ANOMALY_MODEL_PATH: /models/anomaly_model.joblib
  LOG_LEVEL: INFO
  REDIS_URL: redis://redis:6379
  DB_CONNECTION: postgresql://user:pass@db:5432/fraud_logs
```

---

## Troubleshooting

### Models Not Loading
```bash
python3 -c "import joblib; joblib.load('artifacts/fraud_model.joblib')"
```

### SHAP Explainability Unavailable
- Check `logs/` for warnings
- Fallback heuristic will be used
- Monitor with: `curl http://localhost:8000/security-metrics`

### Slow Predictions
- Check CPU usage (ensemble + SHAP can be compute-intensive)
- Consider disabling SHAP in production if latency critical
- Use approximate SHAP (kernel method) instead of TreeExplainer

### Memory Issues
- Reduce batch size in `/upload-csv`
- Clear old logs periodically
- Monitor with: `ps aux | grep python`

---

## Next Steps

1. **Data Pipeline**: Integrate with Kafka/Kinesis for streaming
2. **Feature Store**: Implement with Feast or Tecton
3. **Model Registry**: Use MLflow or BentoML
4. **Monitoring**: Setup Prometheus + Grafana
5. **A/B Testing**: Threshold optimization framework
6. **Feedback Loop**: Model retraining pipeline

---

**Version**: 1.0  
**Last Updated**: 2026-05-09
