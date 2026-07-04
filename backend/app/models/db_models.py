import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import String, DateTime, JSON, Text, Boolean, func, Date
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class User(Base):
    """
    👤 Users & Role Clearance Access Control Table
    Maps institutional profiles, unique cloud provider tracking matrices,
    alphanumeric usernames for admins, and systemic routing clearance privilege tags.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    
    # 🕵️ Unified Role Mapping Strategy (FR-09)
    # Dictates user access paths: 'student', 'faculty', 'helpdesk', or 'admin'
    role: Mapped[str] = mapped_column(String(50), default="student", nullable=False) 
    
    # 👑 Secure Alphanumeric Username Matrix (Enforced for Admin accounts)
    # Stored as unique and index-optimized to guarantee rapid backend lookups
    username: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True, nullable=True)
    
    # 🔗 Firebase Identity Provider Anchor Token
    # Allows fast login verification and automatic role discovery
    firebase_uid: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Ticket(Base):
    """
    🎫 Campus Grievance Matrix Incident Logging Table
    Retains student problem statement profiles, priority layers, and history event matrices.
    """
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)  # Format: 'TK-2026-XXXX'
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)         # Department classification string
    priority: Mapped[str] = mapped_column(String(50), default="Medium", nullable=False)  # 'Low', 'Medium', 'High', 'Critical'
    status: Mapped[str] = mapped_column(String(50), default="Open", nullable=False)      # 'Open', 'In Review', 'Resolved'
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 🗃️ Utilizing PostgreSQL native JSON columns for rapid parsing of historical lifecycle loops
    timeline: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    
    created_date: Mapped[str] = mapped_column(String(50), nullable=False)     # String formatted date for UI synchronization
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Notice(Base):
    """
    📢 Campus Information Bulletin Board Broadcast Table
    Retains verified administrative notices, publishing logs, and rich-text contents.
    """
    __tablename__ = "notices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)         # Filtering categorization index
    date: Mapped[str] = mapped_column(String(50), nullable=False)             # Presentation layer string timestamp
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Reminder(Base):
    """
    ⏰ Simulated Calendar Reminder Table (FR-06)
    Stores institutional timeline tracking reminders and dashboard notification alerts for users.
    """
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    reminder_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)  # Format: 'REM-2026-XXXX'
    student_email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    reminder_text: Mapped[str] = mapped_column(Text, nullable=False)
    reminder_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)  # Calendar trigger mark
    status: Mapped[str] = mapped_column(String(50), default="Pending", nullable=False)  # 'Pending', 'Triggered', 'Dismissed'
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ChatAuditLog(Base):
    """
    📊 LLM Telemetry & Conversational Audit Ledger Table (FR-10)
    Tracks system safety flags, token usage, execution latency, and response metrics.
    """
    __tablename__ = "chat_audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_query: Mapped[str] = mapped_column(Text, nullable=False)
    ai_response: Mapped[str] = mapped_column(Text, nullable=False)
    latency_seconds: Mapped[float] = mapped_column(nullable=False)
    estimated_tokens: Mapped[int] = mapped_column(nullable=False)
    is_safe: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    triggered_rules: Mapped[str] = mapped_column(String(255), default="None", nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())