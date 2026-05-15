# Руководство по диаграммам системы

## 📋 Содержание

Этот документ содержит все диаграммы архитектуры, потоков данных и компонентов системы детектирования мошенничества в реальном времени.

---

## 🔄 1. Диаграмма потока данных (Data Flow)

**Файл**: `01_dataflow.md`

Полный путь от получения транзакции до логирования решения:

```mermaid
graph TD
    A["📥 Transaction Input<br/>(JSON)"] --> B["⚙️ Feature Engineering<br/>app/state.py"]

    B --> B1["🔄 Online Features<br/>- count_1m<br/>- count_5m<br/>- avg_amount_30<br/>- amount_to_avg_ratio"]
    B --> B2["📅 Temporal Features<br/>- hour of day<br/>- day of week"]
    B --> B3["👤 Behavioral Patterns<br/>- high_risk_country<br/>- is_night<br/>- is_gambling_mcc"]

    B1 --> C["🤖 Ensemble ML Module<br/>app/model.py"]
    B2 --> C
    B3 --> C

    C --> C1["📊 Supervised Ensemble<br/>RandomForest + ExtraTrees<br/>+ GradientBoosting<br/>→ fraud_probability"]
    C --> C2["🔍 Unsupervised Anomaly<br/>Isolation Forest<br/>→ anomaly_score"]
    C --> C3["⚖️ Soft Voting Aggregation<br/>weighted_ensemble_score"]

    C1 --> D["📋 Rule Engine<br/>app/rules.py"]
    C2 --> D

    D --> D1["⚡ Velocity Rules<br/>3+ tx/min"]
    D --> D2["🌍 Geographical Rules<br/>high-risk countries"]
    D --> D3["🎰 Behavioral Rules<br/>gambling, night activity"]

    D1 --> E["💡 XAI / SHAP Module<br/>app/xai.py"]
    D2 --> E
    D3 --> E

    E --> E1["📊 SHAP Values<br/>Feature contributions"]
    E --> E2["🎯 Feature Importance<br/>Ranked by impact"]
    E --> E3["📝 Human-Readable<br/>Explanations"]

    E1 --> F["🎲 Ensemble Decision Layer<br/>final_score = 0.5*supervised<br/>+ 0.2*anomaly<br/>+ 0.3*rules"]
    E2 --> F
    E3 --> F

    F --> G{final_score<br/>threshold?}

    G -->|score < 0.65| H["✅ APPROVE<br/>Auto-accept"]
    G -->|0.65 ≤ score < 0.85| I["🔍 REVIEW<br/>Manual investigation"]
    G -->|score ≥ 0.85| J["❌ DECLINE<br/>Block transaction"]

    H --> K["🔐 Security Logging<br/>app/security_logger.py"]
    I --> K
    J --> K

    K --> K1["📄 logs/predictions.jsonl<br/>All decisions"]
    K --> K2["⚠️ logs/suspicious_transactions.jsonl<br/>REVIEW/DECLINE with details"]

    style A fill:#e1f5ff
    style B fill:#f3e5f5
    style C fill:#fff3e0
    style D fill:#e8f5e9
    style E fill:#fce4ec
    style F fill:#f1f8e9
    style G fill:#fff59d
    style H fill:#c8e6c9
    style I fill:#ffe0b2
    style J fill:#ffccbc
    style K fill:#b3e5fc
    style K1 fill:#b3e5fc
    style K2 fill:#b3e5fc
```

**Ключевые этапы**:

1. Получение входных данных транзакции в JSON формате
2. Извлечение и инженерия признаков (17 признаков)
3. Предсказание через ансамбль ML моделей
4. Обнаружение аномалий (Isolation Forest)
5. Применение правил (velocity, geographical, behavioral)
6. Генерация SHAP объяснений
7. Агрегация оценок (0.5*supervised + 0.2*anomaly + 0.3\*rules)
8. Финальное решение (APPROVE/REVIEW/DECLINE)
9. Логирование в JSONL файлы

---

## 🏗️ 2. Архитектура системы

**Файл**: `02_architecture.md`

Высокоуровневая архитектура компонентов:

```mermaid
graph LR
    subgraph API["🌐 API Layer (FastAPI)"]
        A1["GET /health"]
        A2["POST /score"]
        A3["POST /upload-csv"]
        A4["GET /"]
        A5["GET /security-metrics"]
    end

    subgraph Core["⚙️ Core Processing"]
        C1["Feature Engineering<br/>state.py"]
        C2["ML Models<br/>model.py"]
        C3["Rule Engine<br/>rules.py"]
        C4["XAI Module<br/>xai.py"]
        C5["Decision Logic"]
    end

    subgraph Models["🤖 ML Models"]
        M1["RandomForest<br/>300 trees"]
        M2["ExtraTrees<br/>400 trees"]
        M3["GradientBoosting<br/>250 rounds"]
        M4["Isolation Forest<br/>Anomaly"]
    end

    subgraph Storage["💾 Storage"]
        S1["artifacts/<br/>fraud_model.joblib"]
        S2["artifacts/<br/>anomaly_model.joblib"]
        S3["logs/<br/>predictions.jsonl"]
        S4["logs/<br/>suspicious_transactions.jsonl"]
    end

    subgraph Frontend["🎨 Frontend"]
        F1["Dashboard<br/>index.html"]
        F2["CSV Upload"]
        F3["Results Table"]
    end

    A1 --> C1
    A2 --> C1
    A3 --> C1
    A4 --> F1
    A5 --> S3

    C1 --> C2
    C2 --> C3
    C3 --> C4
    C4 --> C5

    C2 --> M1
    C2 --> M2
    C2 --> M3
    C2 --> M4

    C5 --> S3
    C5 --> S4

    F1 --> A3
    F2 --> A3
    F3 --> A2

    M1 --> S1
    M2 --> S1
    M3 --> S1
    M4 --> S2

    style API fill:#e3f2fd
    style Core fill:#f3e5f5
    style Models fill:#fff3e0
    style Storage fill:#e8f5e9
    style Frontend fill:#fce4ec
```

**Компоненты**:

- **API Layer**: FastAPI endpoints для взаимодействия
- **Core Processing**: Основные модули обработки
- **ML Models**: Четыре модели (RandomForest, ExtraTrees, GradientBoosting, Isolation Forest)
- **Storage**: Хранение моделей и логов
- **Frontend**: Web интерфейс для пользователей

---

## ⚖️ 3. Ансамблевое голосование

**Файл**: `03_ensemble_voting.md`

Механизм soft voting и агрегации оценок:

```mermaid
graph TD
    subgraph Input["📥 Input Features"]
        I["Engineered Features<br/>17 features total"]
    end

    subgraph Supervised["📊 Supervised Models<br/>Weight: [3, 3, 2]"]
        RF["RandomForest<br/>P_rf = 0.0-1.0"]
        ET["ExtraTrees<br/>P_et = 0.0-1.0"]
        GB["GradientBoosting<br/>P_gb = 0.0-1.0"]
    end

    subgraph Unsupervised["🔍 Unsupervised Model"]
        IF["Isolation Forest<br/>anomaly = 0.0-1.0"]
    end

    subgraph Rules["📋 Rule Engine"]
        VR["Velocity Rules<br/>score: 0.0-1.0"]
        GR["Geographical Rules<br/>score: 0.0-1.0"]
        BR["Behavioral Rules<br/>score: 0.0-1.0"]
    end

    subgraph Aggregation["⚖️ Soft Voting Aggregation"]
        SV["supervised_score =<br/>(3*P_rf + 3*P_et + 2*P_gb) / 8"]
        AS["anomaly_score =<br/>anomaly"]
        RS["rule_score =<br/>max(VR, GR, BR)"]
        FS["final_score =<br/>0.5*supervised +<br/>0.2*anomaly +<br/>0.3*rules"]
    end

    subgraph Decision["🎯 Decision Layer"]
        D["score < 0.65?"] -->|YES| APPROVE["✅ APPROVE"]
        D -->|NO| D2["score < 0.85?"]
        D2 -->|YES| REVIEW["🔍 REVIEW"]
        D2 -->|NO| DECLINE["❌ DECLINE"]
    end

    I --> RF
    I --> ET
    I --> GB
    I --> IF
    I --> VR
    I --> GR
    I --> BR

    RF --> SV
    ET --> SV
    GB --> SV

    IF --> AS

    VR --> RS
    GR --> RS
    BR --> RS

    SV --> FS
    AS --> FS
    RS --> FS

    FS --> D

    APPROVE --> LOG["🔐 Log Decision"]
    REVIEW --> LOG
    DECLINE --> LOG

    style Input fill:#e1f5ff
    style Supervised fill:#fff3e0
    style Unsupervised fill:#e8f5e9
    style Rules fill:#fce4ec
    style Aggregation fill:#f1f8e9
    style Decision fill:#fff59d
    style APPROVE fill:#c8e6c9
    style REVIEW fill:#ffe0b2
    style DECLINE fill:#ffccbc
    style LOG fill:#b3e5fc
```

**Формулы**:

- Supervised score = (3*P_rf + 3*P_et + 2\*P_gb) / 8
- Anomaly score = Isolation Forest output ∈ [0, 1]
- Rule score = max(velocity_score, geo_score, behavioral_score)
- **Final score = 0.5 × supervised + 0.2 × anomaly + 0.3 × rules**

---

## 🔧 4. Диаграмма компонентов

**Файл**: `04_components.md`

Детальное распределение компонентов по модулям:

```mermaid
graph TB
    subgraph API["API Server (main.py)"]
        HC["Health Check"]
        SC["Score Endpoint"]
        UL["CSV Upload"]
        DB["Dashboard"]
        SM["Security Metrics"]
    end

    subgraph Processing["Processing Pipeline"]
        FE["Feature Engineering<br/>state.py"]
        VAL["Validators<br/>validators.py"]
        MOD["Model Inference<br/>model.py"]
    end

    subgraph DecisionLogic["Decision Logic"]
        RUL["Rule Engine<br/>rules.py"]
        XAI["SHAP Explainer<br/>xai.py"]
        DEC["Decision Maker"]
    end

    subgraph Logging["Logging & Monitoring"]
        LOG["Security Logger<br/>security_logger.py"]
        MON["Monitoring<br/>monitoring.py"]
        CACHE["Cache<br/>cache.py"]
    end

    subgraph Artifacts["Models & Data"]
        FM["fraud_model.joblib<br/>Ensemble"]
        AM["anomaly_model.joblib<br/>Isolation Forest"]
        TM["training_metrics.json"]
    end

    HC --> VAL
    SC --> VAL
    UL --> VAL

    VAL --> FE
    FE --> MOD
    FE --> RUL

    MOD --> XAI
    RUL --> XAI

    XAI --> DEC

    DEC --> LOG
    LOG --> MON

    MOD --> FM
    MOD --> AM
    MON --> CACHE

    DB --> SM
    SM --> LOG

    FM --> TM
    AM --> TM
```

---

## 📊 5. Дерево решений

**Файл**: `05_decision_tree.md`

Полный процесс принятия решения для одной транзакции:

```mermaid
graph TD
    START["📊 Transaction Received"] --> VALIDATE{Valid<br/>Input?}

    VALIDATE -->|NO| ERR["❌ Return Error<br/>400 Bad Request"]
    VALIDATE -->|YES| EXTRACT["⚙️ Extract Features"]

    EXTRACT --> ENGINEER["🔧 Feature Engineering<br/>- Velocity (1m, 5m)<br/>- Temporal (hour, day)<br/>- Behavioral patterns"]

    ENGINEER --> ML["🤖 ML Prediction<br/>Supervised Ensemble"]
    ML --> P_FRAUD["P_fraud = 0.0-1.0"]

    ENGINEER --> ANOMALY["🔍 Anomaly Detection<br/>Isolation Forest"]
    ANOMALY --> A_SCORE["anomaly_score = 0.0-1.0"]

    ENGINEER --> RULES["📋 Rule Engine"]
    RULES --> RULE_CHECK{Any Rules<br/>Triggered?}
    RULE_CHECK -->|YES| R_SCORE["rule_score = max(scores)"]
    RULE_CHECK -->|NO| R_SCORE_ZERO["rule_score = 0.0"]

    P_FRAUD --> AGG["⚖️ Aggregate Scores<br/>final = 0.5*P + 0.2*A + 0.3*R"]
    A_SCORE --> AGG
    R_SCORE --> AGG
    R_SCORE_ZERO --> AGG

    AGG --> FINAL["final_score = 0.0-1.0"]

    FINAL --> CHECK1{"final_score<br/>0.65?"}
    CHECK1 -->|YES| APPROVE["✅ APPROVE<br/>Auto-accept"]
    CHECK1 -->|NO| CHECK2{"final_score<br/>0.85?"}

    CHECK2 -->|YES| REVIEW["🔍 REVIEW<br/>Manual check needed"]
    CHECK2 -->|NO| DECLINE["❌ DECLINE<br/>Block transaction"]

    APPROVE --> EXPLAIN["🎯 Generate SHAP<br/>Explanations"]
    REVIEW --> EXPLAIN
    DECLINE --> EXPLAIN

    EXPLAIN --> REASONS["📝 Create Reasons List<br/>Top-3 features"]

    REASONS --> LOG["🔐 Log Decision"]
    LOG --> RESPONSE["📤 Return Response<br/>JSON"]

    ERR --> RESPONSE
```

---

## 🎓 6. Обучение и развертывание моделей

**Файл**: `06_model_ensemble.md`

Процесс обучения, тюнинга и развертывания моделей:

```mermaid
graph TD
    subgraph Training["🎓 Training Phase"]
        T1["Dataset: ~280K transactions<br/>Imbalanced: ~5% fraud"]
        T1 --> PREPROCESS["Preprocessing"]
        PREPROCESS --> SPLIT["Train/Val/Test Split<br/>70% / 15% / 15%"]
    end

    subgraph Supervised["📊 Supervised Models"]
        SPLIT --> RF["RandomForest<br/>- Trees: 300<br/>- Max Depth: 10<br/>- Weights: 3"]
        SPLIT --> ET["ExtraTrees<br/>- Trees: 400<br/>- Max Depth: 12<br/>- Weights: 3"]
        SPLIT --> GB["GradientBoosting<br/>- Estimators: 250<br/>- Depth: 3<br/>- Weights: 2"]
    end

    subgraph Unsupervised["🔍 Unsupervised Model"]
        SPLIT --> IF["Isolation Forest<br/>- Contamination: 0.1<br/>- Samples: 256"]
    end

    subgraph Voting["⚖️ Voting Classifier"]
        RF --> VC["VotingClassifier<br/>soft voting"]
        ET --> VC
        GB --> VC
        VC --> P_PRED["Predictions on Val Set"]
    end

    subgraph Tuning["🎯 Hyperparameter Tuning"]
        P_PRED --> THRESHOLD["Find Best Threshold"]
        THRESHOLD --> CV["Cross-Validation"]
        CV --> METRICS["Calculate Metrics"]
    end

    subgraph Evaluation["📊 Evaluation Metrics"]
        METRICS --> ROC["ROC-AUC: ~0.9245"]
        METRICS --> PR["PR-AUC: ~0.8912"]
        METRICS --> F1["Best F1: ~0.8234<br/>Threshold: 0.4532"]
        METRICS --> CONF["Confusion Matrix"]
    end

    subgraph Deployment["🚀 Deployment"]
        ROC --> SAVE1["Save fraud_model.joblib<br/>VotingClassifier"]
        CONF --> SAVE1
        IF --> SAVE2["Save anomaly_model.joblib<br/>IsolationForest"]
        F1 --> SAVE2
    end

    subgraph Production["🔧 Production Inference"]
        SAVE1 --> INF1["ensemble_pred =<br/>fraud_model.predict_proba"]
        SAVE2 --> INF2["anomaly_score =<br/>anomaly_model.score_samples"]
        INF1 --> FINAL["Combine with Rules"]
        INF2 --> FINAL
    end

    FINAL --> OUTPUT["Output: Decision<br/>(APPROVE/REVIEW/DECLINE)"]
```

---

## 🔐 7. Система логирования и аудита

**Файл**: `07_security_logging.md`

Полная система логирования для соответствия требованиям compliance:

```mermaid
graph LR
    subgraph Transaction["Transaction Processing"]
        TX["Transaction<br/>Input"]
        SCORE["Score Generated"]
        DECISION["Decision Made<br/>APPROVE/REVIEW/DECLINE"]
    end

    subgraph Logging["Logging System (security_logger.py)"]
        LOG_ALL["Log ALL Predictions"]
        LOG_SUSP["Log Suspicious Only<br/>REVIEW + DECLINE"]
    end

    subgraph Files["JSONL Files"]
        PRED["predictions.jsonl<br/>All decisions"]
        SUSP["suspicious_transactions.jsonl<br/>Detailed records"]
    end

    subgraph LogData["Log Data Structure"]
        LD1["transaction_id"]
        LD2["fraud_probability"]
        LD3["rule_score"]
        LD4["final_score"]
        LD5["decision"]
        LD6["reasons[]"]
        LD7["top_features"]
        LD8["shap_values"]
        LD9["timestamp"]
    end

    subgraph Compliance["Compliance & Audit"]
        QUERY["Query Logs"]
        FILTER["Filter by Period/Country"]
        STATS["Generate Reports"]
        EXPLAIN["Explainability Records"]
    end

    TX --> SCORE
    SCORE --> DECISION

    DECISION --> LOG_ALL
    DECISION --> LOG_SUSP

    LOG_ALL --> PRED
    LOG_SUSP --> SUSP

    PRED --> LD1
    PRED --> LD2
    PRED --> LD3
    PRED --> LD4
    PRED --> LD5
    PRED --> LD6

    SUSP --> LD7
    SUSP --> LD8
    SUSP --> LD9

    PRED --> QUERY
    SUSP --> QUERY

    QUERY --> FILTER
    FILTER --> STATS
    QUERY --> EXPLAIN

    STATS --> OUTPUT["Audit Reports<br/>Compliance Ready"]
    EXPLAIN --> OUTPUT
```

---

## 📊 Итоговая таблица метрик

| Метрика                 | Значение |
| ----------------------- | -------- |
| ROC-AUC                 | ~0.9245  |
| PR-AUC                  | ~0.8912  |
| Best F1 Score           | ~0.8234  |
| F1 Threshold            | 0.4532   |
| APPROVE Threshold       | 0.65     |
| REVIEW Threshold        | 0.85     |
| Supervised Score Weight | 50%      |
| Anomaly Score Weight    | 20%      |
| Rule Score Weight       | 30%      |

---

## 🚀 Использование диаграмм

### Для Mermaid Live Editor

1. Открыть https://mermaid.live/
2. Скопировать содержимое любого файла из `docs/diagrams/`
3. Вставить в левую панель
4. Диаграмма отобразится в реальном времени

### Для интеграции в документы

````markdown
```mermaid
[содержимое файла]
```
````

```

### Для экспорта
- PNG: Use "Export as PNG"
- SVG: Use "Export as SVG"
- URL: Copy "Permanent link"

---

## 📝 Версия диаграмм

- **Дата создания**: 2026-05-15
- **Версия кода**: 3.0
- **Состояние**: Production Ready ✅
- **Последнее обновление**: Отражает текущую архитектуру системы

---

## 🔗 Связанные документы

- [Architecture Details](architecture.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Thesis Alignment](thesis_alignment.md)
- [System README](../README.md)

```
