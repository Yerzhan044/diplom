graph TD
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
    style LOG fill:#b3e5fc