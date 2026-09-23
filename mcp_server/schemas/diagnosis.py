from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class AnomalyDetectionResponse(BaseModel):
    service: str
    is_anomalous: bool
    severity: str
    summary: str

class RCAResponse(BaseModel):
    root_cause: str
    confidence: float
    evidence: List[str]
    contributing_factors: List[str]
