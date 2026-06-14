from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import APIResponse, AuditLogResponse, EscalationResponse
from app.services.audit_service import AuditService
from typing import List

router = APIRouter()

@router.get("/audit-logs", response_model=APIResponse[List[AuditLogResponse]])
def view_system_audit_trail(db: Session = Depends(get_db)):
    """
    Retrieve system execution records tracking agent selections and confidence scores.
    """
    logs = AuditService.get_all_logs(db)
    return APIResponse(
        success=True,
        message="System audit telemetry retrieved successfully.",
        data=logs
    )

@router.get("/escalations", response_model=APIResponse[List[EscalationResponse]])
def view_escalated_student_queries(db: Session = Depends(get_db)):
    """
    Retrieve a list of student queries that the RAG model could not confidently resolve.
    """
    escalations = AuditService.get_all_escalations(db)
    return APIResponse(
        success=True,
        message="Active low-confidence escalations retrieved successfully.",
        data=escalations
    )