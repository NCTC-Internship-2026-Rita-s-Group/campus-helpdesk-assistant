from sqlalchemy.orm import Session
from app.models.db_models import AuditLogModel, EscalationModel

class AuditService:
    @staticmethod
    def get_all_logs(db: Session, limit: int = 100):
        """
        Fetch system routing logs for administrative performance audits.
        """
        return db.query(AuditLogModel).order_by(AuditLogModel.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_all_escalations(db: Session):
        """
        Fetch all queries flagged as low-confidence for manual review.
        """
        return db.query(EscalationModel).order_by(EscalationModel.created_at.desc()).all()