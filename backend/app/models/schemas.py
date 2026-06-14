from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, EmailStr

from datetime import datetime

# ==========================================
# ADMINISTRATIVE VALIDATION SCHEMAS
# ==========================================
class AuditLogResponse(BaseModel):
    id: int
    user_message: Optional[str] = None
    detected_intent: Optional[str] = None
    selected_agent: Optional[str] = None
    tool_called: Optional[str] = None
    tool_result: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True  # Allows Pydantic to read raw SQLAlchemy object rows

class EscalationResponse(BaseModel):
    id: int
    escalation_id: str
    student_email: Optional[str] = None
    user_message: str
    reason: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================================
# STEP 2: GLOBAL API RESPONSE ENVELOPE
# ==========================================
T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    error: Optional[Any] = None

    class Config:
        from_attributes = True


# ==========================================
# STEP 4: DATA VALIDATION SCHEMAS
# ==========================================

# Ticket Validation Schemas
class TicketCreate(BaseModel):
    student_name: str
    student_email: EmailStr
    category: str
    description: str

class TicketResponse(BaseModel):
    id: int
    ticket_id: str
    student_name: str
    student_email: str
    category: str
    description: str
    status: str

    class Config:
        from_attributes = True

# Notice Validation Schemas
class NoticeCreate(BaseModel):
    title: str
    description: str
    category: Optional[str] = "General"
    notice_date: str  # YYYY-MM-DD

class NoticeResponse(BaseModel):
    id: int
    title: str
    description: str
    category: Optional[str]
    notice_date: str

    class Config:
        from_attributes = True

# Reminder Validation Schema
class ReminderCreate(BaseModel):
    student_email: EmailStr
    reminder_text: str
    reminder_date: str  # YYYY-MM-DD
    
# Chat Validation Schemas
class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    answer: str
    intent: str
    agent: str
    confidence: float
    sources: Optional[list] = []