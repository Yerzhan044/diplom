#!/usr/bin/env python3
"""
Генератор диаграмм для дипломного проекта (ИСПРАВЛЕННАЯ ВЕРСИЯ).
Создает диаграммы архитектуры и потоков данных в формате Mermaid.
"""

import os
from pathlib import Path


def create_dataflow():
    return """graph TD
    A["Input Transaction"] --> B["Feature Engineering"]
    B --> B1["Online Features"]
    B --> B2["Temporal Features"]
    B --> B3["Behavioral"]
    B1 --> C["ML Ensemble"]
    B2 --> C
    B3 --> C
    C --> C1["Supervised"]
    C --> C2["Anomaly"]
    C1 --> D["Rules"]
    C2 --> D
    D --> D1["Velocity"]
    D --> D2["Geography"]
    D --> D3["Behavior"]
    D1 --> E["SHAP XAI"]
    D2 --> E
    D3 --> E
    E --> F["Decision"]
    F --> G{"Threshold Check"}
    G -->|Under 0.65| H["Approve"]
    G -->|0.65-0.85| I["Review"]
    G -->|Over 0.85| J["Decline"]
    H --> K["Logging"]
    I --> K
    J --> K
    style A fill:#e1f5ff
    style B fill:#f3e5f5
    style C fill:#fff3e0
    style D fill:#e8f5e9
    style E fill:#fce4ec
    style F fill:#f1f8e9
    style H fill:#c8e6c9
    style I fill:#ffe0b2
    style J fill:#ffccbc"""


def create_architecture():
    return """graph LR
    subgraph API["API Layer"]
        A1["GET health"]
        A2["POST score"]
        A3["POST upload-csv"]
        A4["GET dashboard"]
    end
    subgraph Core["Core Processing"]
        C1["Feature Engineering"]
        C2["ML Models"]
        C3["Rules"]
        C4["XAI"]
    end
    subgraph Models["ML Models"]
        M1["RandomForest"]
        M2["ExtraTrees"]
        M3["GradientBoosting"]
        M4["Isolation Forest"]
    end
    subgraph Storage["Storage"]
        S1["fraud_model.joblib"]
        S2["anomaly_model.joblib"]
        S3["predictions.jsonl"]
    end
    A1 --> C1
    A2 --> C1
    A3 --> C1
    C1 --> C2
    C2 --> C3
    C3 --> C4
    C2 --> M1
    C2 --> M2
    C2 --> M3
    C2 --> M4
    C4 --> S1
    C4 --> S2
    C4 --> S3
    style API fill:#e3f2fd
    style Core fill:#f3e5f5
    style Models fill:#fff3e0
    style Storage fill:#e8f5e9"""


def create_ensemble():
    return """graph TD
    subgraph Input["Input Features"]
        I["17 Features Total"]
    end
    subgraph Supervised["Supervised Models"]
        RF["RandomForest"]
        ET["ExtraTrees"]
        GB["GradientBoosting"]
    end
    subgraph Unsupervised["Unsupervised"]
        IF["Isolation Forest"]
    end
    subgraph Rules["Rules"]
        VR["Velocity"]
        GR["Geographical"]
        BR["Behavioral"]
    end
    I --> RF
    I --> ET
    I --> GB
    I --> IF
    I --> VR
    I --> GR
    I --> BR
    RF --> Voting["Voting Classifier"]
    ET --> Voting
    GB --> Voting
    IF --> Agg["Aggregation"]
    VR --> Agg
    GR --> Agg
    BR --> Agg
    Voting --> Final["Final Score"]
    Agg --> Final
    Final --> D{"Under 0.65"}
    D -->|Yes| APPROVE["Approve"]
    D -->|No| D2{"Under 0.85"}
    D2 -->|Yes| REVIEW["Review"]
    D2 -->|No| DECLINE["Decline"]
    style I fill:#e1f5ff
    style Supervised fill:#fff3e0
    style Unsupervised fill:#e8f5e9
    style Rules fill:#fce4ec
    style Final fill:#f1f8e9
    style APPROVE fill:#c8e6c9
    style REVIEW fill:#ffe0b2
    style DECLINE fill:#ffccbc"""


def create_components():
    return """graph TB
    subgraph API["API Server"]
        HC["Health Check"]
        SC["Score"]
        UL["Upload CSV"]
    end
    subgraph Processing["Processing"]
        FE["Feature Eng"]
        VAL["Validators"]
        MOD["Model Inference"]
    end
    subgraph Decision["Decision Logic"]
        RUL["Rules"]
        XAI["SHAP"]
        DEC["Decision Maker"]
    end
    subgraph Logging["Logging"]
        LOG["Security Logger"]
        MON["Monitoring"]
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
    LOG --> MON"""


def create_decision_tree():
    return """graph TD
    START["Transaction Received"] --> VALIDATE{"Valid Input"}
    VALIDATE -->|No| ERR["Return Error"]
    VALIDATE -->|Yes| EXTRACT["Extract Features"]
    EXTRACT --> ENGINEER["Feature Engineering"]
    ENGINEER --> ML["ML Prediction"]
    ENGINEER --> ANOMALY["Anomaly Detection"]
    ENGINEER --> RULES["Rule Engine"]
    ML --> AGG["Aggregate Scores"]
    ANOMALY --> AGG
    RULES --> AGG
    AGG --> FINAL["Calculate Final Score"]
    FINAL --> CHECK1{"Under 0.65"}
    CHECK1 -->|Yes| APPROVE["APPROVE"]
    CHECK1 -->|No| CHECK2{"Under 0.85"}
    CHECK2 -->|Yes| REVIEW["REVIEW"]
    CHECK2 -->|No| DECLINE["DECLINE"]
    APPROVE --> EXPLAIN["Generate Explanations"]
    REVIEW --> EXPLAIN
    DECLINE --> EXPLAIN
    EXPLAIN --> LOG["Log Decision"]
    LOG --> RESPONSE["Return Response"]
    ERR --> RESPONSE
    style START fill:#e1f5ff
    style ENGINEER fill:#f3e5f5
    style APPROVE fill:#c8e6c9
    style REVIEW fill:#ffe0b2
    style DECLINE fill:#ffccbc
    style LOG fill:#b3e5fc"""


def create_training():
    return """graph TD
    T1["Dataset 280K Transactions"] --> PREPROCESS["Preprocessing"]
    PREPROCESS --> SPLIT["Train/Val/Test Split"]
    SPLIT --> RF["RandomForest 300 trees"]
    SPLIT --> ET["ExtraTrees 400 trees"]
    SPLIT --> GB["GradientBoosting 250"]
    SPLIT --> IF["Isolation Forest"]
    RF --> VC["VotingClassifier"]
    ET --> VC
    GB --> VC
    VC --> METRICS["Calculate Metrics"]
    METRICS --> ROC["ROC-AUC 0.9245"]
    METRICS --> PR["PR-AUC 0.8912"]
    METRICS --> F1["F1 0.8234"]
    ROC --> SAVE1["Save fraud_model"]
    PR --> SAVE1
    IF --> SAVE2["Save anomaly_model"]
    F1 --> SAVE2
    SAVE1 --> DEPLOY["Deploy to Production"]
    SAVE2 --> DEPLOY
    style T1 fill:#e1f5ff
    style METRICS fill:#fff59d
    style ROC fill:#c8e6c9
    style PR fill:#c8e6c9
    style F1 fill:#c8e6c9
    style DEPLOY fill:#e8f5e9"""


def create_logging():
    return """graph LR
    subgraph TX["Transaction Processing"]
        INPUT["Input"]
        SCORE["Score"]
        DECISION["Decision"]
    end
    subgraph LOG_SYS["Logging System"]
        LOG_ALL["Log All"]
        LOG_SUSP["Log Suspicious"]
    end
    subgraph FILES["JSONL Files"]
        PRED["predictions.jsonl"]
        SUSP["suspicious_transactions.jsonl"]
    end
    subgraph AUDIT["Compliance & Audit"]
        QUERY["Query Logs"]
        REPORT["Generate Reports"]
    end
    INPUT --> SCORE
    SCORE --> DECISION
    DECISION --> LOG_ALL
    DECISION --> LOG_SUSP
    LOG_ALL --> PRED
    LOG_SUSP --> SUSP
    PRED --> QUERY
    SUSP --> QUERY
    QUERY --> REPORT
    style TX fill:#e1f5ff
    style LOG_SYS fill:#f3e5f5
    style FILES fill:#fff3e0
    style AUDIT fill:#e8f5e9"""


def main():
    """Создает все диаграммы."""
    diagrams_dir = Path("docs/diagrams")
    diagrams_dir.mkdir(parents=True, exist_ok=True)

    diagrams = {
        "01_dataflow.md": create_dataflow(),
        "02_architecture.md": create_architecture(),
        "03_ensemble_voting.md": create_ensemble(),
        "04_components.md": create_components(),
        "05_decision_tree.md": create_decision_tree(),
        "06_model_ensemble.md": create_training(),
        "07_security_logging.md": create_logging(),
    }

    print("📊 Creating diagrams...\n")

    for filename, code in diagrams.items():
        filepath = diagrams_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"✓ Created: {filename}")

    print("\n✅ All diagrams created successfully!")
    print(f"📁 Location: {diagrams_dir.absolute()}")


if __name__ == "__main__":
    main()
