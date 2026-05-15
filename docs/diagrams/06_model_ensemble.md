graph TD
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
    style DEPLOY fill:#e8f5e9