import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr, Field

# --- 📢 NOTICE / ANNOUNCEMENT VALIDATION CROSSROADS ---
class NoticeBase(BaseModel):
    title: str = Field(..., max_length=255, description="The structural subject of the announcement")
    category: str = Field(..., max_length=100, description="Category filter e.g., Academics, Placements")
    date: str = Field(..., max_length=50, description="String date display tag for frontend parity")
    excerpt: str = Field(..., description="Short line summary snippet")
    content: str = Field(..., description="Full markdown textual payload body")

class NoticeCreate(NoticeBase):
    pass

class NoticeResponse(NoticeBase):
    id: int
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


# --- 🎫 TICKET / GRIEVANCE VALIDATION CROSSROADS ---
class TicketTimelineElement(BaseModel):
    date: str
    message: str

class TicketBase(BaseModel):
    subject: str = Field(..., max_length=255)
    category: str = Field(..., max_length=100)
    priority: str = Field("Medium", max_length=50) # Low, Medium, High, Critical
    description: str

class TicketCreate(TicketBase):
    pass

class TicketStatusUpdate(BaseModel):
    status: str = Field(..., max_length=50) # Open, In Review, Resolved

class TicketResponse(BaseModel):
    id: str
    subject: str
    category: str
    priority: str
    status: str
    description: str
    timeline: List[Dict[str, Any]]
    created_date: str
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


# --- 👤 USER MAPPING ACCESS CONTROL SCHEMAS ---
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str = "student"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime.datetime

    model_config = {"from_attributes": True}
    

# --- 💬 CHAT CONVERSATIONAL RAG SCHEMAS ---
class ChatHistoryNode(BaseModel):
    role: str # 'user' or 'assistant'
    content: str

# Change this specific schema block inside backend/app/models/schemas.py:

class ChatRequest(BaseModel):
    question: str = Field(..., description="The live query string submitted by the student")
    history: List[ChatHistoryNode] = Field(default=[], description="The sliding window turn-history list")
    conversation_id: Optional[str] = Field(default=None, description="The tracking session ID mapping back to relational SQL models")

# 🟢 Update this specific schema block inside backend/app/models/schemas.py

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    context_verified: bool   
    generated_title: Optional[str] = Field(default=None, description="The auto-generated clean topic summary for first-turn sidebar sync")
    supplemental_data: Optional[str] = Field(default="", description="Safe fallback string tracker neutralizing frontend string bugs")
    error: Optional[str] = Field(default=None, description="Error payload transmission string hook")

    model_config = {"from_attributes": True}

# --- 🔒 AUTHENTICATION & ACCESS SCHEMAS ---
class UserLoginPayload(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse