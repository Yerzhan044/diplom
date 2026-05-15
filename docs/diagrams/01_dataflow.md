graph TD
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
    style J fill:#ffccbc