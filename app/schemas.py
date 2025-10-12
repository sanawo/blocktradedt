from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    use_llm: bool = True

class SearchResult(BaseModel):
    score: float
    listing: dict

class SearchResponse(BaseModel):
    results: List[SearchResult]
    summary: Optional[str] = None
    total: int

class SearchHistoryItem(BaseModel):
    id: int
    query: str
    results_count: int
    search_time: str
    use_llm: bool

class TrendsData(BaseModel):
    market_data: dict
    daily_stats: List[dict]

class ChatRequest(BaseModel):
    message: str
    system_prompt: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None

class ChatResponse(BaseModel):
    response: str
    timestamp: str
    success: bool

class MarketAnalysisRequest(BaseModel):
    market_data: Optional[Dict[str, Any]] = None

class MarketAnalysisResponse(BaseModel):
    analysis: str
    market_data: Dict[str, Any]
    timestamp: str
    success: bool

class InvestmentAdviceRequest(BaseModel):
    query: str

class InvestmentAdviceResponse(BaseModel):
    advice: str
    timestamp: str
    success: bool



