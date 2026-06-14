import uuid
from sqlalchemy.orm import Session
from app.models.db_models import TicketModel, NoticeModel, ReminderModel
from app.models.schemas import TicketCreate, NoticeCreate, ReminderCreate

class DBService:
    @staticmethod
    def create_ticket(db: Session, ticket_data: TicketCreate) -> TicketModel:
        # Generate a unique, recognizable campus tracking token
        unique_ticket_id = f"TCK-{uuid.uuid4().hex[:6].upper()}"
        
        db_ticket = TicketModel(
            ticket_id=unique_ticket_id,
            student_name=ticket_data.student_name,
            student_email=ticket_data.student_email,
            category=ticket_data.category,
            description=ticket_data.description
        )
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        return db_ticket

    @staticmethod
    def get_all_tickets(db: Session):
        return db.query(TicketModel).order_by(TicketModel.created_at.desc()).all()

    @staticmethod
    def create_notice(db: Session, notice_data: NoticeCreate) -> NoticeModel:
        db_notice = NoticeModel(
            title=notice_data.title,
            description=notice_data.description,
            category=notice_data.category,
            notice_date=notice_data.notice_date
        )
        db.add(db_notice)
        db.commit()
        db.refresh(db_notice)
        return db_notice

    @staticmethod
    def get_latest_notices(db: Session, limit: int = 5):
        return db.query(NoticeModel).order_by(NoticeModel.notice_date.desc()).limit(limit).all()

    @staticmethod
    def create_reminder(db: Session, reminder_data: ReminderCreate) -> ReminderModel:
        unique_reminder_id = f"REM-{uuid.uuid4().hex[:6].upper()}"
        
        db_reminder = ReminderModel(
            reminder_id=unique_reminder_id,
            student_email=reminder_data.student_email,
            reminder_text=reminder_data.reminder_text,
            reminder_date=reminder_data.reminder_date
        )
        db.add(db_reminder)
        db.commit()
        db.refresh(db_reminder)
        return db_reminder