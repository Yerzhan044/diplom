graph LR
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
    style Storage fill:#e8f5e9