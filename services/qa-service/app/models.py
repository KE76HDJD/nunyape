from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class QuestionType(str, Enum):
    FACTUAL = "factual"
    PROCEDURAL = "procedural"
    CONCEPTUAL = "conceptual"
    COMPARATIVE = "comparative"

class AnswerConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    context: Optional[str] = None
    question_type: Optional[QuestionType] = QuestionType.FACTUAL
    max_results: int = Field(default=5, ge=1, le=20)

class AnswerResponse(BaseModel):
    answer: str
    confidence: float = Field(..., ge=0, le=1)
    confidence_level: AnswerConfidence
    source_documents: List[Dict[str, Any]] = Field(default_factory=list)
    related_questions: List[str] = Field(default_factory=list)
    processing_time: float

class DocumentUpload(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class QAPair(BaseModel):
    question: str
    answer: str
    confidence_score: float = Field(default=1.0, ge=0, le=1)
    document_id: Optional[int] = None

class SearchResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    total_count: int
    processing_time: float

class KnowledgeBaseStats(BaseModel):
    total_documents: int
    total_qa_pairs: int
    categories: Dict[str, int]
    last_updated: datetime