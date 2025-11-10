from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"

class PaymentCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Payment amount must be positive")
    currency: str = Field(default="USD", max_length=3)
    payment_method: PaymentMethod
    customer_id: str
    order_id: str
    description: Optional[str] = None

class PaymentResponse(BaseModel):
    id: str
    status: PaymentStatus
    amount: float
    currency: str
    payment_method: PaymentMethod
    transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class RefundRequest(BaseModel):
    payment_id: str
    amount: Optional[float] = None
    reason: str

class WebhookEvent(BaseModel):
    event_type: str
    payment_id: str
    data: dict
    signature: str