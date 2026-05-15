graph TB
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
    LOG --> MON