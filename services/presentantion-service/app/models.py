from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class PresentationStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class SlideType(str, Enum):
    TITLE = "title"
    CONTENT = "content"
    IMAGE = "image"
    VIDEO = "video"
    QUOTE = "quote"

class PresentationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    theme: str = Field(default="default")
    tags: List[str] = Field(default_factory=list)

class SlideCreate(BaseModel):
    title: str
    content: str
    slide_type: SlideType = SlideType.CONTENT
    order: int = Field(ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PresentationResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: PresentationStatus
    theme: str
    slides: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    owner_id: str

class PresentationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[PresentationStatus] = None
    theme: Optional[str] = None