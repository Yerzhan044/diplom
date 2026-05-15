#!/usr/bin/env python3
"""
Генератор диаграмм для дипломного проекта.
Создает диаграммы архитектуры, потоков данных и компонентов в формате Mermaid.
"""

import os
import json
from pathlib import Path


class DiagramGenerator:
    """Генератор диаграмм для системы детектирования мошенничества."""

    def __init__(self, output_dir="./docs/diagrams"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_dataflow_diagram(self):
        """Генерирует диаграмму потока данных."""
        mermaid_code = """graph TD
    A["Input: Transaction JSON"] --> B["Feature Engineering"]
    
    B --> B1["Online Features<br/>- count_1m, count_5m<br/>- avg_amount_30"]
    B --> B2["Temporal Features<br/>- hour, day"]
    B --> B3["Behavioral Patterns<br/>- risk_country, night, gambling"]
    
    B1 --> C["Ensemble ML Module"]
    B2 --> C
    B3 --> C
    
    C --> C1["Supervised Ensemble<br/>RandomForest + ExtraTrees + GB"]
    C --> C2["Unsupervised Anomaly<br/>Isolation Forest"]
    
    C1 --> D["Rule Engine"]
    C2 --> D
    
    D --> D1["Velocity Rules"]
    D --> D2["Geographical Rules"]
    D --> D3["Behavioral Rules"]
    
    D1 --> E["XAI SHAP Module"]
    D2 --> E
    D3 --> E
    
    E --> F["Ensemble Decision Layer"]
    
    F --> G{Score Threshold Check}
    
    G -->|less than 0.65| H["APPROVE"]
    G -->|0.65 to 0.85| I["REVIEW"]
    G -->|greater than 0.85| J["DECLINE"]
    
    H --> K["Security Logging"]
    I --> K
    J --> K
    
    K --> K1["predictions.jsonl"]
    K --> K2["suspicious_transactions.jsonl"]
    
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
    style K fill:#b3e5fc"""

    def generate_architecture_diagram(self):
        """Генерирует диаграмму архитектуры системы."""
        mermaid_code = """graph LR
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
    style Frontend fill:#fce4ec"""

        return mermaid_code

    def generate_ensemble_voting_diagram(self):
        """Генерирует диаграмму ансамблевого голосования."""
        mermaid_code = """graph TD
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
    style LOG fill:#b3e5fc"""

        return mermaid_code

    def generate_component_diagram(self):
        """Генерирует диаграмму компонентов."""
        mermaid_code = """graph TB
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
    
    style API fill:#e3f2fd
    style Processing fill:#f3e5f5
    style DecisionLogic fill:#fff3e0
    style Logging fill:#e8f5e9
    style Artifacts fill:#fce4ec"""

        return mermaid_code

    def generate_decision_tree_diagram(self):
        """Генерирует диаграмму дерева решений."""
        mermaid_code = """graph TD
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
    
    style START fill:#e1f5ff
    style VALIDATE fill:#fff3e0
    style ENGINEER fill:#f3e5f5
    style ML fill:#fff3e0
    style ANOMALY fill:#e8f5e9
    style RULES fill:#fce4ec
    style AGG fill:#f1f8e9
    style APPROVE fill:#c8e6c9
    style REVIEW fill:#ffe0b2
    style DECLINE fill:#ffccbc
    style LOG fill:#b3e5fc
    style RESPONSE fill:#e1f5ff"""

        return mermaid_code

    def generate_model_ensemble_diagram(self):
        """Генерирует диаграмму ансамбля моделей."""
        mermaid_code = """graph TD
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
    
    style Training fill:#e1f5ff
    style Supervised fill:#fff3e0
    style Unsupervised fill:#e8f5e9
    style Voting fill:#f1f8e9
    style Tuning fill:#fce4ec
    style Evaluation fill:#fff59d
    style Deployment fill:#c8e6c9
    style Production fill:#b3e5fc
    style OUTPUT fill:#c8e6c9"""

        return mermaid_code

    def generate_security_logging_diagram(self):
        """Генерирует диаграмму системы логирования."""
        mermaid_code = """graph LR
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
    
    style Transaction fill:#e1f5ff
    style Logging fill:#f3e5f5
    style Files fill:#fff3e0
    style LogData fill:#e8f5e9
    style Compliance fill:#fce4ec
    style OUTPUT fill:#c8e6c9"""

        return mermaid_code

    def save_diagram(self, filename, mermaid_code):
        """Сохраняет диаграмму в файл."""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(mermaid_code)
        print(f"✓ Saved: {filepath}")
        return filepath

    def generate_all_diagrams(self):
        """Генерирует все диаграммы."""
        print(f"🎨 Генерирование диаграмм в {self.output_dir}/\n")

        diagrams = {
            "01_dataflow.md": self.generate_dataflow_diagram(),
            "02_architecture.md": self.generate_architecture_diagram(),
            "03_ensemble_voting.md": self.generate_ensemble_voting_diagram(),
            "04_components.md": self.generate_component_diagram(),
            "05_decision_tree.md": self.generate_decision_tree_diagram(),
            "06_model_ensemble.md": self.generate_model_ensemble_diagram(),
            "07_security_logging.md": self.generate_security_logging_diagram(),
        }

        for filename, code in diagrams.items():
            self.save_diagram(filename, code)

        print(f"\n✅ Все диаграммы сгенерированы!\n")
        self.print_summary()

    def print_summary(self):
        """Выводит сводку по диаграммам."""
        summary = """
📊 СОЗДАННЫЕ ДИАГРАММЫ:

1. 01_dataflow.md
   └─ Полный поток данных от входа до логирования
   
2. 02_architecture.md
   └─ Архитектура системы (API, Core, Models, Storage)
   
3. 03_ensemble_voting.md
   └─ Ансамблевое голосование моделей и агрегация
   
4. 04_components.md
   └─ Диаграмма компонентов системы
   
5. 05_decision_tree.md
   └─ Дерево решений и логика обработки
   
6. 06_model_ensemble.md
   └─ Обучение, тюнинг и развертывание моделей
   
7. 07_security_logging.md
   └─ Система логирования и аудита

📝 ИСПОЛЬЗОВАНИЕ:
- Копируй содержимое каждого файла в https://mermaid.live/
- Или используй эти диаграммы в markdown документах

🚀 Для интеграции в документ:
```markdown
```mermaid
[содержимое файла]
```
```
"""
        print(summary)


if __name__ == "__main__":
    # Генерируем диаграммы в docs/diagrams/
    generator = DiagramGenerator()
    generator.generate_all_diagrams()

    # Выводим информацию о файлах
    print(f"\n📁 Диаграммы сохранены в: {os.path.abspath(generator.output_dir)}/")
