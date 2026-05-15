graph TD
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
    style DECLINE fill:#ffccbc