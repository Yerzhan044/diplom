import os
from datetime import timezone
from io import StringIO
from typing import Any, Dict

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse

from app.cache import ExplanationCache, PredictionCache
from app.llm_explanations import get_llm_explainer
from app.llm_free import get_free_explainer, get_groq_explainer
from app.model import FraudModel, FEATURE_COLUMNS
from app.monitoring import ModelMonitor
from app.rules import GAMBLING_MCC, HIGH_RISK_COUNTRIES, evaluate_rules
from app.schemas import ScoreResponse, TransactionIn
from app.security_logger import SecurityLogger
from app.state import OnlineStateStore
from app.validators import TransactionValidator
from app.xai import ExplainabilityEngine, generate_human_readable_explanation

load_dotenv()

THRESHOLD = float(os.getenv("THRESHOLD", "0.65"))
ALERT_THRESHOLD = float(os.getenv("ALERT_THRESHOLD", "0.85"))
MODEL_PATH = os.getenv("MODEL_PATH", "artifacts/fraud_model.joblib")
ANOMALY_MODEL_PATH = os.getenv("ANOMALY_MODEL_PATH", "artifacts/anomaly_model.joblib")

app = FastAPI(
    title="Real-time Credit Card Fraud Prevention System (Production)",
    version="2.2",
    description="Enterprise-grade fraud detection with SHAP + Free LLM explanations (Ollama/Groq/Claude)"
)

# Initialize components
state_store = OnlineStateStore()
fraud_model = FraudModel(MODEL_PATH, ANOMALY_MODEL_PATH)
xai_engine = None
security_logger = SecurityLogger()
explanation_cache = ExplanationCache(max_size=1000)
prediction_cache = PredictionCache(max_size=5000)
model_monitor = ModelMonitor(window_size=100)
validator = TransactionValidator()

# Initialize LLM explainer (try free options first, then Claude API)
llm_explainer = None
llm_source = "none"

# Try free Ollama first (local, no API key)
free_explainer = get_free_explainer()
if free_explainer:
    llm_explainer = free_explainer
    llm_source = "ollama (local, free)"
else:
    # Try Groq (free tier)
    groq_explainer = get_groq_explainer()
    if groq_explainer:
        llm_explainer = groq_explainer
        llm_source = "groq (free tier)"
    else:
        # Fall back to Claude API (paid)
        claude_explainer = get_llm_explainer()
        if claude_explainer:
            llm_explainer = claude_explainer
            llm_source = "claude (paid)"

try:
    xai_engine = ExplainabilityEngine(MODEL_PATH, FEATURE_COLUMNS)
except Exception:
    pass


def build_ml_features(tx: TransactionIn, online: dict[str, float]) -> dict[str, float]:
    ts_utc = tx.timestamp.astimezone(timezone.utc)
    hour = ts_utc.hour

    return {
        "amount": float(tx.amount),
        "count_1m": online["count_1m"],
        "count_5m": online["count_5m"],
        "avg_amount_30": online["avg_amount_30"],
        "amount_to_avg_ratio": online["amount_to_avg_ratio"],
        "is_high_risk_country": float(tx.country in HIGH_RISK_COUNTRIES),
        "is_night": float(hour <= 5 or hour >= 23),
        "is_gambling_mcc": float(tx.mcc in GAMBLING_MCC),
    }


def score_transaction_core(tx: TransactionIn) -> ScoreResponse:
    online = state_store.update_and_get_features(tx.card_id, tx.amount, tx.timestamp)
    ml_features = build_ml_features(tx, online)

    rule_score, reasons = evaluate_rules(tx, online)

    # Supervised model prediction
    fraud_probability = fraud_model.predict_proba(ml_features)

    # Unsupervised anomaly detection
    anomaly_score = fraud_model.anomaly_score(ml_features)

    # XAI explanation (SHAP or fallback heuristic)
    explanation = {}
    if xai_engine:
        explanation = xai_engine.explain_prediction(ml_features)
        xai_reasons = generate_human_readable_explanation(explanation)
        if xai_reasons and xai_reasons[0] != "Нет специфических аномалий по SHAP":
            reasons.extend(xai_reasons)

    # Ensemble score: combine supervised, anomaly, and rules
    # Supervised: 50%, Anomaly: 20%, Rules: 30%
    final_score = 0.5 * fraud_probability + 0.2 * anomaly_score + 0.3 * rule_score

    if final_score >= ALERT_THRESHOLD:
        decision = "DECLINE"
    elif final_score >= THRESHOLD:
        decision = "REVIEW"
    else:
        decision = "APPROVE"

    if not reasons:
        reasons.append("Аномалий по правилам и XAI не найдено")

    # Generate LLM-powered natural language explanation
    llm_explanation = ""
    if llm_explainer:
        llm_explanation = llm_explainer.generate_explanation(
            fraud_probability=fraud_probability,
            rule_score=rule_score,
            final_score=final_score,
            decision=decision,
            reasons=reasons,
            ml_features=ml_features,
        )

    result = ScoreResponse(
        transaction_id=tx.transaction_id,
        fraud_probability=round(fraud_probability, 4),
        rule_score=round(rule_score, 4),
        final_score=round(final_score, 4),
        decision=decision,
        reasons=reasons,
        explanation=llm_explanation,
    )

    # Log all predictions
    security_logger.log_prediction(tx, result)

    # Log suspicious transactions with detailed explanation
    if decision in {"REVIEW", "DECLINE"}:
        security_logger.log_suspicious_transaction(tx, result, explanation)

    return result


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    return """
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Fraud Prevention Dashboard</title>
    <style>
        :root {
            --bg: #08111f;
            --panel: rgba(12, 21, 38, 0.9);
            --panel-2: rgba(17, 30, 53, 0.95);
            --text: #e8eefc;
            --muted: #94a3b8;
            --accent: #57d39d;
            --accent-2: #66a3ff;
            --danger: #ff6b6b;
            --warning: #ffca66;
            --border: rgba(148, 163, 184, 0.18);
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            min-height: 100vh;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: var(--text);
            background:
                radial-gradient(circle at top left, rgba(87, 211, 157, 0.18), transparent 28%),
                radial-gradient(circle at top right, rgba(102, 163, 255, 0.18), transparent 24%),
                linear-gradient(135deg, #07101d 0%, #0b1628 46%, #050a14 100%);
        }
        .wrap { max-width: 1200px; margin: 0 auto; padding: 32px 20px 44px; }
        .hero {
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 20px;
            align-items: stretch;
            margin-bottom: 20px;
        }
        .card {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 22px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.28);
            backdrop-filter: blur(14px);
        }
        .hero-main { padding: 28px; }
        .eyebrow {
            display: inline-flex;
            padding: 6px 12px;
            border-radius: 999px;
            background: rgba(87, 211, 157, 0.12);
            color: var(--accent);
            font-size: 12px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 16px;
        }
        h1 { margin: 0 0 12px; font-size: clamp(30px, 4vw, 48px); line-height: 1.05; }
        .lead { margin: 0; color: var(--muted); max-width: 70ch; line-height: 1.6; }
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-top: 20px;
        }
        .stat {
            background: var(--panel-2);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 16px;
        }
        .stat strong { display: block; font-size: 20px; margin-bottom: 4px; }
        .stat span { color: var(--muted); font-size: 13px; }
        .side { padding: 24px; display: flex; flex-direction: column; gap: 14px; justify-content: center; }
        .side h2 { margin: 0; font-size: 20px; }
        .side p { margin: 0; color: var(--muted); line-height: 1.6; }
        .actions {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 12px;
        }
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 12px 18px;
            border-radius: 14px;
            border: 1px solid transparent;
            font-weight: 700;
            cursor: pointer;
            transition: transform .16s ease, opacity .16s ease, border-color .16s ease;
            text-decoration: none;
        }
        .btn:hover { transform: translateY(-1px); }
        .btn-primary { background: linear-gradient(135deg, var(--accent), #42b883); color: #042012; }
        .btn-secondary { background: transparent; color: var(--text); border-color: var(--border); }
        .panel { padding: 22px; margin-top: 20px; }
        .upload-box {
            border: 1.5px dashed rgba(148, 163, 184, 0.35);
            border-radius: 20px;
            padding: 22px;
            background: rgba(255, 255, 255, 0.02);
        }
        .upload-box input[type=file] {
            width: 100%;
            padding: 14px;
            border-radius: 14px;
            color: var(--muted);
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--border);
            margin: 14px 0;
        }
        .limit-row {
            display: flex;
            flex-direction: column;
            gap: 8px;
            max-width: 300px;
            margin-bottom: 10px;
        }
        .limit-row label { color: var(--muted); font-size: 13px; }
        .limit-row input {
            width: 100%;
            padding: 10px 12px;
            border-radius: 12px;
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.03);
            color: var(--text);
        }
        .grid-two {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-top: 14px;
        }
        .summary-item {
            background: var(--panel-2);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 14px;
        }
        .summary-item small { color: var(--muted); display: block; margin-bottom: 6px; }
        .summary-item strong { font-size: 22px; }
        .summary-item em {
            display: block;
            margin-top: 6px;
            color: var(--muted);
            font-style: normal;
            font-size: 12px;
            line-height: 1.4;
        }
        .table-wrap { overflow-x: auto; margin-top: 14px; }
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        th, td { padding: 12px 10px; border-bottom: 1px solid rgba(148,163,184,0.15); text-align: left; vertical-align: top; }
        th { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .06em; }
        .pill {
            display: inline-flex;
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
        }
        .approve { background: rgba(87, 211, 157, 0.15); color: var(--accent); }
        .review { background: rgba(255, 202, 102, 0.15); color: var(--warning); }
        .decline { background: rgba(255, 107, 107, 0.16); color: var(--danger); }
        .hint { color: var(--muted); font-size: 13px; margin-top: 10px; }
        .footer-note { margin-top: 16px; color: var(--muted); font-size: 13px; }
        @media (max-width: 900px) {
            .hero, .grid-two, .summary-grid, .stats { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="wrap">
        <section class="hero">
            <div class="card hero-main">
                <div class="eyebrow">Real-time Fraud Prevention</div>
                <h1>Загрузка CSV и потоковый скоринг в одном интерфейсе</h1>
                <p class="lead">
                    Загрузи CSV-файл с транзакциями, и система автоматически прогонит их через
                    ensemble-модель и rule engine, чтобы показать подозрительные операции,
                    вероятности fraud и итоговые решения.
                </p>
                <div class="stats">
                    <div class="stat"><strong>Ensemble</strong><span>RandomForest + ExtraTrees + GradientBoosting</span></div>
                    <div class="stat"><strong>Realtime</strong><span>Скоринг каждой транзакции на лету</span></div>
                    <div class="stat"><strong>Explainable</strong><span>Человекочитаемые причины срабатывания</span></div>
                </div>
            </div>
            <div class="card side">
                <h2>Как это работает</h2>
                <p>1. Загрузите CSV с транзакциями.</p>
                <p>2. Нажмите кнопку обработки.</p>
                <p>3. Получите summary, таблицу результатов и тревожные записи.</p>
                <div class="actions">
                    <a class="btn btn-primary" href="#upload">Загрузить CSV</a>
                    <a class="btn btn-secondary" href="/docs">Открыть API docs</a>
                </div>
            </div>
        </section>

        <section class="card panel" id="upload">
            <h2 style="margin-top:0">CSV upload</h2>
            <div class="upload-box">
                <div class="limit-row">
                    <label for="row-limit">Сколько строк обработать</label>
                    <input id="row-limit" type="number" min="1" max="50000" value="50" />
                </div>
                <input id="csv-file" type="file" accept=".csv" />
                <div class="actions">
                    <button class="btn btn-primary" type="button" onclick="uploadCsv()">Обработать CSV</button>
                    <button class="btn btn-secondary" type="button" onclick="clearResults()">Очистить</button>
                </div>
                <div class="hint">Файл должен содержать колонки: transaction_id, card_id, amount, country, mcc, timestamp. Лимит строк выбирается вручную.</div>
            </div>
            <div id="message" class="footer-note"></div>
        </section>

        <section class="grid-two">
            <div class="card panel">
                <h3 style="margin-top:0">Сводка</h3>
                <div id="summary" class="summary-grid">
                    <div class="summary-item"><small>Всего</small><strong>0</strong><em>строк обработано</em></div>
                    <div class="summary-item"><small>Approve</small><strong>0</strong><em>без ручной проверки</em></div>
                    <div class="summary-item"><small>Review</small><strong>0</strong><em>на ручную проверку</em></div>
                    <div class="summary-item"><small>Decline</small><strong>0</strong><em>отклонено системой</em></div>
                </div>
            </div>
            <div class="card panel">
                <h3 style="margin-top:0">Рекомендации для защиты</h3>
                <p class="lead">Этот интерфейс уже делает проект заметно лучше: он выглядит как полноценный аналитический инструмент, а не просто API. Для защиты можно показать CSV-файл, автоматическую обработку и список подозрительных транзакций.</p>
            </div>
        </section>

        <section class="card panel">
            <h3 style="margin-top:0">Результаты</h3>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Amount</th>
                            <th>Country</th>
                            <th>Score</th>
                            <th>Decision</th>
                            <th>Reasons</th>
                        </tr>
                    </thead>
                    <tbody id="results-body">
                        <tr><td colspan="6" style="color:#94a3b8">Пока нет загруженного файла.</td></tr>
                    </tbody>
                </table>
            </div>
        </section>
    </div>

    <script>
        async function uploadCsv() {
            const input = document.getElementById('csv-file');
            const rowLimitInput = document.getElementById('row-limit');
            const message = document.getElementById('message');
            const file = input.files[0];
            const rowLimit = Number(rowLimitInput.value || 50);
            if (!file) {
                message.textContent = 'Выберите CSV-файл сначала.';
                return;
            }
            if (!Number.isFinite(rowLimit) || rowLimit < 1) {
                message.textContent = 'Введите корректный лимит строк (минимум 1).';
                return;
            }

            const formData = new FormData();
            formData.append('file', file);
            formData.append('row_limit', String(Math.floor(rowLimit)));

            message.textContent = 'Обработка файла...';
            const response = await fetch('/upload-csv', { method: 'POST', body: formData });
            const data = await response.json();

            if (!response.ok) {
                message.textContent = data.detail || 'Ошибка обработки CSV';
                return;
            }

            renderSummary(data.summary);
            renderRows(data.rows);
            message.textContent = `Обработано ${data.summary.total} строк (первые ${data.summary.limit_used} из загруженного файла).`;
        }

        function clearResults() {
            document.getElementById('csv-file').value = '';
            document.getElementById('message').textContent = '';
            document.getElementById('results-body').innerHTML = '<tr><td colspan="6" style="color:#94a3b8">Пока нет загруженного файла.</td></tr>';
            renderSummary({ total: 0, approve: 0, review: 0, decline: 0, fraud_avg: 0, limit_used: 50, top_score: 0, top_transaction_id: '-', suspicious_count: 0 });
        }

        function renderSummary(summary) {
            document.getElementById('summary').innerHTML = `
                <div class="summary-item"><small>Всего</small><strong>${summary.total}</strong><em>строк обработано</em></div>
                <div class="summary-item"><small>Approve</small><strong>${summary.approve}</strong><em>без ручной проверки</em></div>
                <div class="summary-item"><small>Review</small><strong>${summary.review}</strong><em>на ручную проверку</em></div>
                <div class="summary-item"><small>Decline</small><strong>${summary.decline}</strong><em>отклонено системой</em></div>
                <div class="summary-item"><small>Avg fraud</small><strong>${Number(summary.fraud_avg || 0).toFixed(4)}</strong><em>средняя вероятность fraud</em></div>
                <div class="summary-item"><small>Top risk</small><strong>${Number(summary.top_score || 0).toFixed(4)}</strong><em>${summary.top_transaction_id || '-'}</em></div>
                <div class="summary-item"><small>Suspicious</small><strong>${summary.suspicious_count || 0}</strong><em>REVIEW + DECLINE</em></div>
                <div class="summary-item"><small>Limit</small><strong>${summary.limit_used || 0}</strong><em>строк взято из CSV</em></div>
            `;
        }

        function renderRows(rows) {
            const tbody = document.getElementById('results-body');
            tbody.innerHTML = rows.map(row => {
                const cls = row.decision === 'DECLINE' ? 'decline' : row.decision === 'REVIEW' ? 'review' : 'approve';
                return `
                    <tr>
                        <td>${row.transaction_id}</td>
                        <td>${row.amount.toFixed(2)}</td>
                        <td>${row.country}</td>
                        <td>${row.final_score.toFixed(4)}</td>
                        <td><span class="pill ${cls}">${row.decision}</span></td>
                        <td>${row.reasons.join('; ')}</td>
                    </tr>
                `;
            }).join('');
        }
    </script>
</body>
</html>
"""


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "models_loaded": fraud_model.supervised_model is not None,
        "xai_enabled": xai_engine is not None,
        "llm_source": llm_source,
    }


@app.post("/score", response_model=ScoreResponse)
def score_transaction(tx: TransactionIn) -> ScoreResponse:
    """Score a single transaction with validation and error handling."""
    # Validate input
    validation_result = validator.validate_transaction(tx.dict())
    if not validation_result["valid"]:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid transaction data",
                "errors": validation_result["errors"]
            }
        )

    try:
        result = score_transaction_core(tx)
        # Record for monitoring
        online_features = state_store.get_features(tx.card_id, tx.amount, tx.timestamp)
        ml_features = build_ml_features(tx, online_features)
        model_monitor.record_prediction(
            features=ml_features,
            fraud_probability=result.fraud_probability,
            decision=result.decision,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scoring error: {str(e)}"
        )


@app.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...), row_limit: int = Form(50)
) -> dict[str, Any]:
    if not file.filename.lower().endswith(".csv"):
        return {"detail": "Загрузите CSV-файл."}

    row_limit = max(1, min(int(row_limit), 50000))

    content = await file.read()
    dataframe = pd.read_csv(StringIO(content.decode("utf-8-sig"))).head(row_limit)

    required_columns = [
        "transaction_id",
        "card_id",
        "amount",
        "country",
        "mcc",
        "timestamp",
    ]
    missing = [column for column in required_columns if column not in dataframe.columns]
    if missing:
        return {"detail": f"В CSV не хватает колонок: {', '.join(missing)}"}

    rows = []
    summary = {
        "total": 0,
        "approve": 0,
        "review": 0,
        "decline": 0,
        "fraud_avg": 0.0,
        "limit_used": row_limit,
        "top_score": 0.0,
        "top_transaction_id": "-",
        "suspicious_count": 0,
    }

    for record in dataframe.to_dict(orient="records"):
        tx = TransactionIn(
            transaction_id=str(record.get("transaction_id")),
            card_id=str(record.get("card_id")),
            merchant_id=str(record.get("merchant_id", "unknown")),
            amount=float(record.get("amount")),
            currency=str(record.get("currency", "USD")),
            country=str(record.get("country")),
            mcc=str(record.get("mcc")),
            device_id=str(record.get("device_id", "unknown")),
            ip_address=str(record.get("ip_address", "0.0.0.0")),
            timestamp=record.get("timestamp"),
        )

        result = score_transaction_core(tx)
        summary["total"] += 1
        summary["fraud_avg"] += result.fraud_probability
        summary[result.decision.lower()] += 1
        if result.decision in {"REVIEW", "DECLINE"}:
            summary["suspicious_count"] += 1
        if result.final_score >= summary["top_score"]:
            summary["top_score"] = result.final_score
            summary["top_transaction_id"] = result.transaction_id
        rows.append(
            {
                "transaction_id": result.transaction_id,
                "amount": float(tx.amount),
                "country": tx.country,
                "final_score": result.final_score,
                "decision": result.decision,
                "reasons": result.reasons,
            }
        )

    if summary["total"]:
        summary["fraud_avg"] = round(summary["fraud_avg"] / summary["total"], 4)

    return {"summary": summary, "rows": rows}


@app.get("/security-metrics")
def get_security_metrics() -> dict[str, Any]:
    """Get security audit logs and suspicious activity summary."""
    return security_logger.get_suspicious_summary()


@app.get("/monitoring/performance")
def get_performance_monitoring() -> dict[str, Any]:
    """Get model performance statistics and alerts."""
    stats = model_monitor.get_performance_stats()
    drift = model_monitor.get_feature_drift()
    alerts = model_monitor.get_alerts()

    return {
        "performance": stats,
        "feature_drift": drift,
        "alerts": alerts,
        "alert_count": len(alerts),
    }


@app.get("/monitoring/cache")
def get_cache_stats() -> dict[str, Any]:
    """Get caching statistics."""
    return {
        "explanation_cache": explanation_cache.get_stats(),
        "prediction_cache": {
            "size": len(prediction_cache.cache),
            "max_size": prediction_cache.max_size,
        },
    }


@app.post("/monitoring/reset")
def reset_monitoring() -> dict[str, str]:
    """Reset monitoring data and caches."""
    model_monitor.predictions.clear()
    model_monitor.feature_stats.clear()
    explanation_cache.clear()
    prediction_cache.clear()
    return {"status": "Monitoring data and caches cleared"}
