from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from app.rag.rag_pipeline import RAGPipeline
from app.services.database_services import DBService
from app.models.schemas import TicketCreate, ReminderCreate
from app.database import SessionLocal
import re

# 1. Unified State layout tracking properties across agent operations
class AgentState(TypedDict):
    user_message: str
    session_id: str
    detected_intent: str   # Options: information_query, notice_query, create_ticket, create_reminder, low_confidence
    selected_agent: str    # Options: rag_answer_agent, notice_agent, task_action_agent, escalation_agent
    confidence_score: float
    final_answer: str
    sources: List[Dict[str, Any]]

# =========================================================================
# NODE 1: THE QUERY INTAKE AGENT (Intent Classifier)
# =========================================================================
def query_intake_node(state: AgentState) -> Dict[str, Any]:
    print(f"[LANGGRAPH] Node 1: Query Intake analyzing message: '{state['user_message']}'")
    msg = state['user_message'].lower()
    
    intent = "information_query"
    agent = "rag_answer_agent"
    
    if any(word in msg for word in ["notice", "announcement", "circular", "update"]):
        intent = "notice_query"
        agent = "notice_agent"
    elif any(word in msg for word in ["ticket", "complain", "grievance", "issue", "lodge", "problem"]):
        intent = "create_ticket"
        agent = "task_action_agent"
    elif any(word in msg for word in ["remind", "reminder", "schedule", "alert"]):
        intent = "create_reminder"
        agent = "task_action_agent"
        
    return {
        "detected_intent": intent,
        "selected_agent": agent,
        "confidence_score": 0.95
    }

# =========================================================================
# NODE 2: THE RAG ANSWER AGENT (Academic & Policy Expert)
# =========================================================================
def rag_answer_agent_node(state: AgentState) -> Dict[str, Any]:
    print("[LANGGRAPH] Node 2: Routing to RAG Answer Agent for Document Semantic Search...")
    
    # 1. Trigger the vector search and AI synthesis pipeline
    rag_result = RAGPipeline.query_knowledge_base(state["user_message"])
    
    # 2. DYNAMIC ROUTING CHECK: If the pipeline returned an error or low confidence score
    if rag_result.get("confidence_score", 1.0) == 0.0:
        print("[LANGGRAPH RAG NODE] Low confidence or API failure detected. Preparing route to Escalation Agent...")
        return {
            "confidence_score": 0.0,
            "selected_agent": "escalation_agent"
        }
            
    # 3. Standard path if the AI generation worked perfectly
    return {
        "final_answer": rag_result["answer"],
        "sources": rag_result["sources"],
        "confidence_score": rag_result.get("confidence_score", 0.95)
    }

# =========================================================================
# NODE 3: THE NOTICE BOARD AGENT (Live Database Lookups)
# =========================================================================
def notice_agent_node(state: AgentState) -> Dict[str, Any]:
    print("[LANGGRAPH] Node 3: Routing to Notice Board Agent for Live Database Lookups...")
    db = SessionLocal()
    try:
        notices = DBService.get_latest_notices(db, limit=3)
        if notices:
            lines = [f"• {n.title} ({n.notice_date}): {n.description}" for n in notices]
            answer = "Here are the latest official announcements from the Amity University Ranchi Notice Board:\n\n" + "\n\n".join(lines)
        else:
            answer = "There are currently no active notices published on the campus announcement board."
        return {"final_answer": answer, "sources": [{"database": "sqlite_notice_table"}]}
    finally:
        db.close()

# =========================================================================
# NODE 4: THE TASK & ACTION AGENT (Transactional DB Writer)
# =========================================================================
def task_action_agent_node(state: AgentState) -> Dict[str, Any]:
    print(f"[LANGGRAPH] Node 4: Task Action Agent intercepting transaction for: {state['detected_intent']}")
    db = SessionLocal()
    sources = []
    
    try:
        if state["detected_intent"] == "create_ticket":
            ticket_payload = TicketCreate(
                student_name="Prakash Kumar Prajapati", 
                student_email="student.helpdesk@amity.ranchi.edu",
                category="General Grievance",
                description=state["user_message"]
            )
            
            new_ticket = DBService.create_ticket(db, ticket_payload)
            
            answer = (
                f"Your formal grievance ticket has been successfully compiled and registered into the database!\n\n"
                f"• Tracking ID: {new_ticket.ticket_id}\n"
                f"• Status: {new_ticket.status}\n"
                f"• Filed Description: '{new_ticket.description}'\n\n"
                f"Our Amity Ranchi administration team has been notified and will review your file shortly."
            )
            sources.append({"database": "sqlite_tickets_table", "inserted_id": new_ticket.ticket_id})

        elif state["detected_intent"] == "create_reminder":
            reminder_payload = ReminderCreate(
                student_email="student.helpdesk@amity.ranchi.edu",
                reminder_text=state["user_message"],
                reminder_date="2026-06-19" 
            )
            
            new_reminder = DBService.create_reminder(db, reminder_payload)
            
            answer = (
                f"Automated alert successfully scheduled in your student profile dashboard!\n\n"
                f"• Reminder ID: {new_reminder.reminder_id}\n"
                f"• Alert Date: {new_reminder.reminder_date}\n"
                f"• Context: {new_reminder.reminder_text}\n\n"
                f"You will receive a notification alert on your system dashboard on the scheduled date."
            )
            sources.append({"database": "sqlite_reminders_table", "inserted_id": new_reminder.reminder_id})
            
        return {"final_answer": answer, "sources": sources}
        
    except Exception as e:
        print(f"[LANGGRAPH TRANSACTION CRASH] Database write failure: {str(e)}")
        return {"final_answer": "Failed to automatically process form request due to an internal transaction mismatch.", "sources": []}
    finally:
        db.close()

# =========================================================================
# NODE 5: THE ESCALATION AGENT (The Safety Fallback)
# =========================================================================
def escalation_agent_node(state: AgentState) -> Dict[str, Any]:
    print("[LANGGRAPH] Node 5: Query flagged as low confidence or system error. Committing row to Escalations Table...")
    
    db = SessionLocal()
    try:
        new_esc = DBService.create_escalation(
            db=db,
            student_email="student.helpdesk@amity.ranchi.edu",
            user_message=state["user_message"],
            reason="Low similarity confidence score or operational exception inside the core AI model engines."
        )
        
        answer = (
            f"I was unable to locate a definitive answer in our official university documents.\n\n"
            f"• Escalation ID: {new_esc.escalation_id}\n"
            f"• Status: {new_esc.status}\n\n"
            f"Don't worry! Your query has been successfully logged and escalated directly to the Amity Ranchi student helpdesk supervisors for manual review."
        )
        return {
            "final_answer": answer, 
            "sources": [{"database": "sqlite_escalations_table", "inserted_id": new_esc.escalation_id}],
            "detected_intent": "low_confidence"
        }
    finally:
        db.close()

# =========================================================================
# THE STATE CHART GRAPH ORCHESTRATION TOPOLOGY
# =========================================================================
workflow = StateGraph(AgentState)

workflow.add_node("query_intake", query_intake_node)
workflow.add_node("rag_answer_agent", rag_answer_agent_node)
workflow.add_node("notice_agent", notice_agent_node)
workflow.add_node("task_action_agent", task_action_agent_node)
workflow.add_node("escalation_agent", escalation_agent_node)

workflow.set_entry_point("query_intake")

# Reusable Router Logic that assesses state boundaries dynamically
def router_decision_edge(state: AgentState) -> str:
    if state["confidence_score"] < 0.60 or state["selected_agent"] == "escalation_agent":
        return "escalation_agent"
    return state["selected_agent"]

# Router Edge 1: Routes traffic from the initial Intake block
workflow.add_conditional_edges(
    "query_intake",
    router_decision_edge,
    {
        "rag_answer_agent": "rag_answer_agent",
        "notice_agent": "notice_agent",
        "task_action_agent": "task_action_agent",
        "escalation_agent": "escalation_agent"
    }
)

# Router Edge 2: Evaluates the output of the RAG block before finishing
workflow.add_conditional_edges(
    "rag_answer_agent",
    router_decision_edge,
    {
        "rag_answer_agent": END, # If confidence remains high, exit safely with the answer
        "escalation_agent": "escalation_agent" # If confidence dropped to 0.0, divert straight to Node 5!
    }
)

workflow.add_edge("notice_agent", END)
workflow.add_edge("task_action_agent", END)
workflow.add_edge("escalation_agent", END)

campus_agent_executor = workflow.compile()