from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.schemas import APIResponse, ReminderCreate
from app.services.database_services import DBService
from typing import List

router = APIRouter(prefix="/reminders", tags=["Student Dashboard Reminders"])

@router.post("/", response_model=APIResponse[dict], status_code=status.HTTP_201_CREATED)
async def record_student_reminder(reminder_in: ReminderCreate, db: AsyncSession = Depends(get_db)):
    """
    Store an active reminder record in the campus support database asynchronously.
    """
    try:
        # 🟢 Refactored to await database commits smoothly
        new_reminder = await DBService.create_reminder(db, reminder_data=reminder_in)
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set reminder record: {str(e)}"
        )

@router.get("/{student_email}", response_model=APIResponse[List[dict]])
async def get_active_student_reminders(student_email: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieve all scheduled dashboard reminders for a specific student email profile.
    """
    try:
        reminders = await DBService.get_reminders_by_student(db, student_email=student_email)
        
        formatted_reminders = [
            {
                "reminder_id": r.reminder_id,
                "reminder_text": r.reminder_text,
                "reminder_date": r.reminder_date,
                "status": r.status
            } for r in reminders
        ]
        
        return APIResponse(
            success=True,
            message=f"Successfully compiled {len(formatted_reminders)} active profile reminders.",
            data=formatted_reminders
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve reminders: {str(e)}"
        )