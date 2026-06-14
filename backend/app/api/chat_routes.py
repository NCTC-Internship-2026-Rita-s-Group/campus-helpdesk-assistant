from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import APIResponse, ChatRequest, ChatResponse
from app.models.db_models import AuditLogModel
from app.agents.campus_graph import campus_agent_executor

router = APIRouter()

@router.post("/", response_model=APIResponse[ChatResponse], status_code=status.HTTP_200_OK)
def process_campus_query(chat_in: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chat interaction hub. Processes queries through the LangGraph multi-agent network
    and logs tracking details inside the database audit schemas.
    """
    try:
        # 1. Initialize the internal state object matching our LangGraph structure
        initial_state = {
            "user_message": chat_in.message,
            "session_id": chat_in.session_id,
            "detected_intent": "",
            "selected_agent": "",
            "confidence_score": 0.0,
            "final_answer": "",
            "sources": []
        }
        
        # 2. Invoke the compiled multi-agent state graph pipeline synchronously
        graph_output = campus_agent_executor.invoke(initial_state)
        
        # 3. Extract the computed properties resolved across the graph node operations
        final_response = ChatResponse(
            answer=graph_output["final_answer"],
            intent=graph_output["detected_intent"],
            agent=graph_output["selected_agent"],
            confidence=graph_output["confidence_score"],
            sources=graph_output["sources"]
        )
        
        # 4. Record details into the database audit logs for tracking purposes
        audit_entry = AuditLogModel(
            user_message=chat_in.message,
            detected_intent=final_response.intent,
            selected_agent=final_response.agent,
            tool_called="None" if not final_response.sources else "ChromaDB_Retriever",
            tool_result=str(final_response.sources),
            confidence=final_response.confidence
        )
        db.add(audit_entry)
        db.commit()
        
        return APIResponse(
            success=True,
            message="Query successfully processed through the campus multi-agent network.",
            data=final_response
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-agent processing pipeline failure: {str(e)}"
        )