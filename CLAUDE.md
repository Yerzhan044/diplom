# Real-time Credit Card Fraud Prevention System

**Diploma Project - Network Security (6806303)**  
**IITU 2026**

## Executive Summary

A production-grade real-time fraud detection system combining:
- **Ensemble Machine Learning** (RandomForest + ExtraTrees + GradientBoosting)
- **Unsupervised Anomaly Detection** (Isolation Forest)
- **Explainable AI** (SHAP - SHapley Additive exPlanations)
- **Rule-based Detection** (velocity, geographical, behavioral)
- **Security Audit Logging** (JSONL format for compliance)

---

## Architecture Overview

### Data Flow

```
Transaction Input
    ↓
[Feature Engineering Module]
    ├─ Online features (velocity, ratios)
    ├─ Temporal features (hour of day)
    └─ Behavioral patterns
    ↓
[Ensemble ML Module]
    ├─ Supervised: Fraud probability (RandomForest + ExtraTrees + GradientBoosting)
    ├─ Unsupervised: Anomaly score (Isolation Forest)
    └─ Soft voting aggregation
    ↓
[Rule Engine]
    ├─ Velocity rules (transactions per minute)
    ├─ Geographical rules (high-risk countries)
    ├─ Behavioral rules (gambling, night activity)
    └─ Output: rule_score + human-readable reasons
    ↓
[XAI / SHAP Module]
    ├─ Feature importance analysis
    ├─ SHAP values for interpretability
    └─ Convert to human-readable explanations
    ↓
[Ensemble Decision Layer]
    └─ final_score = 0.5*supervised + 0.2*anomaly + 0.3*rules
    ↓
[Decision & Output Layer]
    ├─ APPROVE (score < 0.65)
    ├─ REVIEW (0.65 ≤ score < 0.85)
    └─ DECLINE (score ≥ 0.85)
    ↓
[Security Logging Module]
    ├─ Log all predictions (predictions.jsonl)
    ├─ Log suspicious transactions (suspicious_transactions.jsonl)
    └─ Audit trail for compliance
```

---

## Key Components

### 1. Feature Engineering (`app/state.py`)
- **Online velocity features**:
  - `count_1m`: transactions in last 1 minute
  - `count_5m`: transactions in last 5 minutes
  - `avg_amount_30`: rolling average of last 30 transactions
  - `amount_to_avg_ratio`: transaction amount vs. historical average

- **Behavioral features**:
  - `is_high_risk_country`: geographical risk
  - `is_night`: transaction at night (23:00-05:00)
  - `is_gambling_mcc`: gambling merchant category code

### 2. Supervised Ensemble (`train/train_model.py`)
Three complementary classifiers with soft voting:
- **RandomForest** (300 trees, depth=10): robust, high accuracy
- **ExtraTrees** (400 trees, depth=12): extra randomness, variance reduction
- **GradientBoosting** (250 rounds, depth=3): captures non-linear patterns

**Weights**: [3, 3, 2] → optimized for imbalanced fraud detection

### 3. Unsupervised Anomaly Detection (`app/model.py`)
- **Isolation Forest** (contamination=0.1): detects behavioral outliers
- Complements supervised model for previously unseen fraud patterns
- Returns anomaly_score ∈ [0, 1]

### 4. XAI/SHAP Module (`app/xai.py`)
- **SHAP TreeExplainer**: explains predictions for each transaction
- **Feature importance**: ranks features by SHAP values
- **Human-readable explanations**: converts technical SHAP to business language
- **Fallback heuristic**: works even if SHAP unavailable

### 5. Rule Engine (`app/rules.py`)
Transparent decision rules with human-readable outputs:
- Velocity anomalies (3+ transactions per minute)
- Geographical risks (high-risk country codes)
- Behavioral patterns (gambling, night time)
- Returns both `rule_score` and `reasons` list

### 6. Security Logger (`app/security_logger.py`)
**JSONL format for production compliance**:
- `logs/predictions.jsonl`: all transaction decisions
- `logs/suspicious_transactions.jsonl`: detailed logs for REVIEW/DECLINE
- Includes: SHAP values, feature importance, decision rationale
- Queryable for audit, analytics, and model monitoring

---

## Deployment & API

### Endpoints

**Health Check**
```
GET /health
→ {"status": "ok"}
```

**Single Transaction Scoring**
```
POST /score
{
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
}
→ {
  "transaction_id": "tx_001",
  "fraud_probability": 0.2345,
  "rule_score": 0.1500,
  "final_score": 0.2020,
  "decision": "APPROVE",
  "reasons": ["Аномалий по правилам и XAI не найдено"]
}
```

**Batch CSV Upload**
```
POST /upload-csv
multipart/form-data:
  - file: CSV with transactions
  - row_limit: max rows to process (default 50)
→ {
  "summary": {
    "total": 50,
    "approve": 45,
    "review": 4,
    "decline": 1,
    "fraud_avg": 0.1234,
    "suspicious_count": 5
  },
  "rows": [...]
}
```

**Web Dashboard**
```
GET /
→ Interactive HTML dashboard for:
  - CSV upload and batch scoring
  - Real-time results table
  - Summary statistics
  - Decision breakdown (APPROVE/REVIEW/DECLINE)
```

**Security Metrics**
```
GET /security-metrics
→ {
  "total": 150,
  "by_decision": {"APPROVE": 140, "REVIEW": 8, "DECLINE": 2},
  "by_country": {"KZ": 120, "US": 20, ...},
  "by_reason": {"Velocity anomaly": 5, ...},
  "recent": [list of last 100 suspicious transactions with SHAP values]
}
```

---

## Training Pipeline

### Generate & Train
```bash
python3 -m train.train_model
```

**Output**:
- `artifacts/fraud_model.joblib`: VotingClassifier (supervised ensemble)
- `artifacts/anomaly_model.joblib`: IsolationForest (unsupervised)
- `artifacts/training_metrics.json`: ROC-AUC, PR-AUC, F1, thresholds

**Sample Metrics** (on synthetic imbalanced dataset):
```
ROC-AUC:           0.9245
PR-AUC:            0.8912
Best F1 threshold: 0.4532
Best F1 score:     0.8234
Test fraud rate:   ~5%
```

---

## Configuration

### Environment Variables
```bash
THRESHOLD=0.65          # REVIEW threshold
ALERT_THRESHOLD=0.85    # DECLINE threshold
MODEL_PATH=artifacts/fraud_model.joblib
ANOMALY_MODEL_PATH=artifacts/anomaly_model.joblib
```

### Thresholds
- `final_score < 0.65` → **APPROVE** (auto-accept)
- `0.65 ≤ final_score < 0.85` → **REVIEW** (manual investigation)
- `final_score ≥ 0.85` → **DECLINE** (block transaction)

---

## Production Readiness

### ✅ Implemented
- [x] Ensemble ML with soft voting
- [x] Unsupervised anomaly detection (Isolation Forest)
- [x] SHAP explainability (TreeExplainer)
- [x] Rule-based decisions with reasons
- [x] Security audit logging (JSONL)
- [x] Real-time API (FastAPI)
- [x] Batch CSV processing
- [x] Web dashboard
- [x] Health checks

### 🚀 Production Enhancements
- [ ] Connect to Kafka for real-time streams
- [ ] Redis for online feature state (horizontal scaling)
- [ ] Model drift monitoring + auto-retrain
- [ ] A/B testing framework for thresholds
- [ ] Feature store (offline/online parity)
- [ ] Advanced monitoring: Prometheus, Grafana
- [ ] Rate limiting & authentication
- [ ] Database logging instead of JSONL

---

## Thesis Alignment

### Chapter 1: Analytical Aspects
- ✅ Cyber fraud threats taxonomy
- ✅ Evolution and automation of attacks
- ✅ Limitations of rule-based systems
- ✅ Justification for ensemble ML + XAI

### Chapter 2: System Design
- ✅ Architecture with 7 components
- ✅ Ensemble decision-making (soft voting)
- ✅ SHAP explainability integration
- ✅ Decision output layer with confidence

### Chapter 3: Implementation & Evaluation
- ✅ Synthetic dataset generation
- ✅ Model training (supervised + unsupervised)
- ✅ Metrics: ROC-AUC, PR-AUC, F1, confusion matrix
- ✅ Explainability examples (SHAP values)

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train models
python3 -m train.train_model

# 3. Start API
uvicorn app.main:app --reload

# 4. Open dashboard
# → http://localhost:8000/

# 5. Test with CSV upload or curl
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "tx_test",
    "card_id": "card_123",
    "merchant_id": "m_456",
    "amount": 500.0,
    "currency": "USD",
    "country": "KZ",
    "mcc": "5411",
    "device_id": "d_789",
    "ip_address": "192.168.1.1",
    "timestamp": "2026-05-09T14:30:00+00:00"
  }'
```

---

## Monitoring & Compliance

### Audit Trails
```
logs/predictions.jsonl
→ All decisions with: timestamp, score, decision

logs/suspicious_transactions.jsonl
→ REVIEW/DECLINE with: SHAP values, feature importance, reasons
```

### Interpretability Requirements
- ✅ Every DECLINE/REVIEW includes top-3 SHAP feature contributions
- ✅ Human-readable explanation for each rule trigger
- ✅ Compliance-ready: can explain decision to regulator/customer

---

## References

**Diploma Documentation Alignment**:
- Section 2.1: System architecture with 7 layers ✅
- Section 2.2: ML algorithm selection (RandomForest, GradientBoosting, ExtraTrees) ✅
- Section 2.3: Ensemble soft voting approach ✅
- Section 2.4: SHAP-based XAI integration ✅
- Section 3.1: Dataset handling and preprocessing ✅
- Section 3.2: Model training and modular design ✅
- Section 3.3: Evaluation metrics (ROC-AUC, PR-AUC, F1) ✅
- Section 3.4: SHAP explainability and security analysis ✅

**Key Papers Referenced**:
- Lundberg & Lee (2017): "A Unified Approach to Interpreting Model Predictions" (SHAP)
- Liu et al. (2008): "Isolation Forest" (anomaly detection)
- Dal Pozzolo et al. (2015): "Calibrating Probability with Undersampling"

---

## Support

For defense presentation:
1. **Demo**: Upload a CSV, show scoring in real-time
2. **Explain**: Walk through SHAP feature importance
3. **Metrics**: Show ROC-AUC, confusion matrix, thresholds
4. **Logs**: Display suspicious_transactions.jsonl audit trail
5. **Architecture**: Present the 7-layer pipeline diagram

---

**Status**: Production-ready MVP for real-time fraud detection  
**Last Updated**: 2026-05-09  
**Next Phase**: Kafka integration + Redis online feature store
