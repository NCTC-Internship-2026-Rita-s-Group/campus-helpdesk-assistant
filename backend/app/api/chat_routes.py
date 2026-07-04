from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models.schemas import ChatRequest, ChatResponse
from app.models import db_models
from app.rag.rag_pipeline import rag_pipeline

router = APIRouter(prefix="/chat", tags=["AI Copilot Chat Engine"])


@router.post("", response_model=ChatResponse)
async def process_student_assistant_query(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    💬 Live Conversational Retrieval Gateway
    Processes query threads under strict input safety guardrails, compiles context,
    tracks backend analytics telemetry, and updates sidebar conversation log titles chronologically.
    """
    if not payload.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User prompt cannot be an empty statement line vector."
        )

    formatted_history = [
        {"role": node.role, "content": node.content} 
        for node in payload.history
    ]

    # 🚀 Run query through the pipeline, processing guardrails and logging telemetry
    pipeline_result = await rag_pipeline.execute_rag_chat_cycle(
        student_query=payload.question,
        db=db,
        chat_history=formatted_history
    )

    # 🏷️ CHRONOLOGICAL TITLE SYNC INTERCEPTOR
    generated_title = pipeline_result.get("generated_title")
    conversation_id = getattr(payload, "conversation_id", None)

    # Dynamically resolve model variants safely
    model_class = getattr(db_models, "Conversation", getattr(db_models, "ChatSession", None))

    if generated_title and model_class is not None:
        try:
            # 1. If the frontend supplied an explicit conversation ID tracking token, use it directly
            if conversation_id:
                title_update_stmt = (
                    update(model_class)
                    .where(model_class.id == conversation_id)
                    .values(title=generated_title)
                )
                await db.execute(title_update_stmt)
                await db.commit()
                print(f"✅ [TITLE COMPLIED] Explicit Session ID {conversation_id} updated to: '{generated_title}'")
            
            # 2. Chronological Fallback: If no ID was sent, sort by creation timestamp or autoincrement ID 
            # to prevent alphabetical string locking across separate chat tabs.
            else:
                sort_field = getattr(model_class, "created_at", getattr(model_class, "id", None))
                if sort_field is not None:
                    fallback_query = select(model_class).order_by(sort_field.desc()).limit(1)
                    fallback_result = await db.execute(fallback_query)
                    latest_session = fallback_result.scalar_one_or_none()
                    
                    if latest_session:
                        latest_session.title = generated_title
                        db.add(latest_session)
                        await db.commit()
                        print(f"✅ [TITLE COMPLIED] Chronological Fallback Session ID {latest_session.id} updated to: '{generated_title}'")
                
        except Exception as sync_fault:
            await db.rollback()
            print(f"⚠️ Non-blocking database session title sync exception dropped: {sync_fault}")

    # 🔐 ANTIDOTE FOR FRONTEND "undefined" GLITCHES
    return {
        "answer": pipeline_result.get("answer", ""),
        "sources": pipeline_result.get("sources", []),
        "context_verified": pipeline_result.get("context_verified", False),
        "generated_title": generated_title, 
        "supplemental_data": "",              
        "error": None
    }