from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field


class TransactionIn(BaseModel):
    transaction_id: str
    card_id: str
    merchant_id: str = "unknown"
    amount: float = Field(gt=0)
    currency: str = "USD"
    country: str
    mcc: str
    device_id: str = "unknown"
    ip_address: str = "0.0.0.0"
    timestamp: datetime


class ScoreResponse(BaseModel):
    transaction_id: str
    fraud_probability: float
    rule_score: float
    final_score: float
    decision: Literal["APPROVE", "REVIEW", "DECLINE"]
    reasons: List[str]
    explanation: str = ""
