from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class WebhookProvider(str, Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    MIN = "min"
    CUSTOM = "custom"

class WebhookStatus(str, Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"
    RETRYING = "retrying"

class WebhookEvent(BaseModel):
    id: Optional[str] = None
    provider: WebhookProvider
    event_type: str
    payload: Dict[str, Any]
    signature: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    status: WebhookStatus = WebhookStatus.PENDING
    processed_at: Optional[datetime] = None
    attempts: int = Field(default=0, ge=0)
    max_attempts: int = Field(default=3, ge=1)
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WebhookResponse(BaseModel):
    status: str
    message: str
    processed: bool
    result: Optional[Dict[str, Any]] = None
    webhook_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class WebhookConfig(BaseModel):
    provider: WebhookProvider
    secret_key: str
    webhook_id: Optional[str] = None  # For PayPal
    client_id: Optional[str] = None   # For PayPal
    client_secret: Optional[str] = None  # For PayPal
    enabled: bool = True
    retry_enabled: bool = True
    max_retries: int = 3

class RetryPolicy(BaseModel):
    max_attempts: int = Field(default=3, ge=1)
    backoff_factor: float = Field(default=1.5, ge=1.0)
    max_delay: int = Field(default=300, ge=1)  # 5 minutes
    retryable_errors: List[str] = Field(default_factory=list)

class WebhookStats(BaseModel):
    total_received: int = 0
    total_processed: int = 0
    total_failed: int = 0
    total_retried: int = 0
    by_provider: Dict[WebhookProvider, int] = Field(default_factory=dict)
    by_event_type: Dict[str, int] = Field(default_factory=dict)
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    period_start: datetime
    period_end: datetime

class WebhookFilter(BaseModel):
    providers: Optional[List[WebhookProvider]] = None
    event_types: Optional[List[str]] = None
    statuses: Optional[List[WebhookStatus]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)