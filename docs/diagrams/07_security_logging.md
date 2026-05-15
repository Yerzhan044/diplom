graph LR
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
    style AUDIT fill:#e8f5e9