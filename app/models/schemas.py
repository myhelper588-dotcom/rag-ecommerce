from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class QuestionRequest(BaseModel):
    """Modèle de la requête entrante"""
    question: str
    source_filter: Optional[str] = None

class QuestionResponse(BaseModel):
    """Modèle de la réponse sortante"""
    answer: str
    sources_used: List[str] = []
    execution_time: float
    timestamp: datetime

class HistoryItem(BaseModel):
    """Un élément de l'historique"""
    question: str
    answer: str
    timestamp: datetime

class HealthResponse(BaseModel):
    """Réponse du health check"""
    status: str
    version: str
    tools_available: List[str]