from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from app.database import Base

class TicketModel(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String, unique=True, nullable=False)
    student_name = Column(String, nullable=False)
    student_email = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, default="Open")
    created_at = Column(DateTime, default=datetime.utcnow)

class ReminderModel(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reminder_id = Column(String, unique=True, nullable=False)
    student_email = Column(String, nullable=False)
    reminder_text = Column(Text, nullable=False)
    reminder_date = Column(String, nullable=False)
    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)

class NoticeModel(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    notice_date = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class EscalationModel(Base):
    __tablename__ = "escalations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    escalation_id = Column(String, unique=True, nullable=False)
    student_email = Column(String, nullable=True)
    user_message = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_message = Column(Text, nullable=True)
    detected_intent = Column(String, nullable=True)
    selected_agent = Column(String, nullable=True)
    tool_called = Column(String, nullable=True)
    tool_result = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)