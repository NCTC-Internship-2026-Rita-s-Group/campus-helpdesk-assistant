from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.database import get_db
from app.models.db_models import Notice
from app.models.schemas import NoticeCreate, NoticeResponse

router = APIRouter(prefix="/notices", tags=["Campus Bulletin Broadcasts"])


@router.get("", response_model=List[NoticeResponse])
async def fetch_all_bulletin_notices(db: AsyncSession = Depends(get_db)):
    """
    📥 Read Operation: Pulls all campus circulars from PostgreSQL.
    Feeds your frontend Bulletin Board stream dynamically.
    """
    # Execute non-blocking selection query order by latest entry
    result = await db.execute(select(Notice).order_by(Notice.id.desc()))
    notices_list = result.scalars().all()
    return notices_list


@router.post("", response_model=NoticeResponse, status_code=status.HTTP_201_CREATED)
async def broadcast_new_campus_notice(
    payload: NoticeCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    📤 Write Operation: Commits a fresh administrative announcement down to the database ledger.
    """
    # Map incoming validation properties cleanly to the table layer instance
    new_notice = Notice(
        title=payload.title,
        category=payload.category,
        date=payload.date,
        excerpt=payload.excerpt,
        content=payload.content
    )
    
    db.add(new_notice)
    await db.commit()
    await db.refresh(new_notice) # Hydrates the instance with its auto-generated database integer ID
    return new_notice

# Add this import to backend/app/api/notice_routes.py
from app.services.security import verify_admin_clearance

@router.post("", response_model=NoticeResponse, status_code=status.HTTP_201_CREATED)
async def broadcast_new_campus_notice(
    payload: NoticeCreate, 
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(verify_admin_clearance) # 🔒 This route now requires a valid Admin JWT!
):
    ...