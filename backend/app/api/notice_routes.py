from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import APIResponse, NoticeResponse
from app.services.database_services import DBService
from typing import List

router = APIRouter()

@router.get("/latest", response_model=APIResponse[List[NoticeResponse]])
def get_latest_campus_notices(
    limit: int = Query(default=5, ge=1, le=20), 
    db: Session = Depends(get_db)
):
    """
    Fetch the latest live notices from the Amity University Ranchi notice board database.
    """
    notices = DBService.get_latest_notices(db, limit=limit)
    return APIResponse(
        success=True,
        message=f"Successfully retrieved the latest {len(notices)} campus notices.",
        data=notices
    )