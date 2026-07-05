import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from typing import List

from app.database import get_db
from app.models.db_models import Notice, User
from app.models.schemas import NoticeResponse
from app.services.security import verify_admin_clearance  # 🔒 Secured Administrative Gateway Guard

router = APIRouter(prefix="/notices", tags=["Campus Bulletin Broadcasts"])


@router.get("", response_model=List[NoticeResponse])
async def fetch_all_bulletin_notices(db: AsyncSession = Depends(get_db)):
    """
    📥 Read Operation: Pulls all campus circulars from the database.
    Feeds your frontend Bulletin Board stream dynamically.
    """
    try:
        # Execute non-blocking selection query ordered by latest entry id descending
        result = await db.execute(select(Notice).order_by(Notice.id.desc()))
        notices_list = result.scalars().all()
        return notices_list
    except Exception as e:
        print(f"❌ [BULLETIN READ FAULT] Unable to parse notice database entries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System was unable to scan relational notice registries."
        )


@router.post("", response_model=NoticeResponse, status_code=status.HTTP_201_CREATED)
async def broadcast_new_campus_notice(
    payload: dict, # 👑 FLEXIBLE DICTIONARY: Bypasses rigid structural signature locks to eliminate 422 errors!
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(verify_admin_clearance)  # 🛡️ Enforce Security Clearance Barrier
):
    """
    📤 Write Operation: Commits a fresh administrative announcement down to the database ledger.
    Secured so only cleared admin operators can deploy official university announcements.
    """
    # Safe fallback parameter unpacking directly out of the dictionary block
    title_text = payload.get("title", "").strip() if payload.get("title") else ""
    content_text = payload.get("content", "").strip() if payload.get("content") else ""
    category_text = payload.get("category", "Admin").strip() if payload.get("category") else "Admin"

    # Input validation guard statement
    if not title_text or not content_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Validation Failed: Announcement Title and Detailed Content are required statement fields."
        )

    # 👑 DEFENSIVE DATE POPULATION: Auto-generates standard date stamps if missing from payload
    notice_date = payload.get("date", "").strip() if payload.get("date") else datetime.datetime.now().strftime("%B %d, %Y")
    
    # 👑 AUTO-EXCERPT FALLBACK: Slices summary text dynamically if omitted by the admin operator panel
    provided_excerpt = payload.get("excerpt", "").strip() if payload.get("excerpt") else ""
    if not provided_excerpt:
        computed_excerpt = content_text[:90] + "..." if len(content_text) > 90 else content_text
    else:
        computed_excerpt = provided_excerpt

    try:
        # Map parameters cleanly into your database row instances
        new_notice = Notice(
            title=title_text,
            category=category_text,
            date=notice_date,
            excerpt=computed_excerpt,
            content=content_text
        )
        
        db.add(new_notice)
        
        # 👑 COMPLIANCE LOG INTEGRATION: Commits audit records directly into your chat_audit_logs schema table
        try:
            audit_query = text("""
                INSERT INTO chat_audit_logs (user_query, ai_response, latency_seconds, estimated_tokens, is_safe, triggered_rules)
                VALUES (:user_query, :ai_response, :latency_seconds, :estimated_tokens, :is_safe, :triggered_rules)
            """)
            await db.execute(audit_query, {
                "user_query": "ADMIN_BROADCAST_NOTICE",
                "ai_response": f"Circular title '{title_text[:50]}' deployed successfully by {current_admin.email}.",
                "latency_seconds": 0.0,
                "estimated_tokens": 0,
                "is_safe": True,
                "triggered_rules": "None"
            })
        except Exception as audit_err:
            print(f"⚠️ Notice telemetry log tracking skipped: {str(audit_err)}")

        await db.commit()
        await db.refresh(new_notice)  # Hydrates instance with its auto-generated database row ID
        print(f"📢 [BULLETIN BROADCAST] Official notice deployed completely: '{new_notice.title}'")
        return new_notice

    except Exception as db_fault:
        await db.rollback()
        print(f"❌ [DATABASE BROADCAST FAULT] Transaction rolled back cleanly: {str(db_fault)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Grievance circular lifecycle state change failed to commit to storage."
        )