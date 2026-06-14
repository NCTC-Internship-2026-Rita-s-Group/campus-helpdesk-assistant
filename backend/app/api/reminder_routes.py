from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import APIResponse, ReminderCreate
from app.services.database_services import DBService

router = APIRouter()

@router.post("/", response_model=APIResponse[dict], status_code=status.HTTP_201_CREATED)
def record_student_reminder(reminder_in: ReminderCreate, db: Session = Depends(get_db)):
    """
    Store a simulated reminder record in the campus support database.
    """
    try:
        new_reminder = DBService.create_reminder(db, reminder_data=reminder_in)
        return APIResponse(
            success=True,
            message=f"Reminder set successfully for {new_reminder.reminder_date}.",
            data={
                "reminder_id": new_reminder.reminder_id,
                "status": new_reminder.status,
                "reminder_text": new_reminder.reminder_text
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to set reminder record: {str(e)}"
        )