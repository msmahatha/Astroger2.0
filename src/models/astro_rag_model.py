from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Literal

class AIRequests(BaseModel):
    question: str
    context: Optional[str] = None
    rag_with_context: Optional[bool] = False  # default to False
    religion: Optional[Literal["hindu", "christian", "muslim", "buddhist", "jain", "sikh", "secular"]] = "hindu"  # default to hindu for backward compatibility
    use_history: Optional[bool] = False
    session_id: Optional[str] = None


class AIResponses(BaseModel):
    question: str
    category: str
    answer: str
    remedy: str
    retrieved_sources: List[Dict[str, Any]] = []
