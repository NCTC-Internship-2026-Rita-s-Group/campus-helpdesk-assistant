from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

# Define the shared state structure that travels between nodes in our graph
class AgentState(TypedDict):
    user_message: str
    session_id: str
    detected_intent: str
    selected_agent: str
    confidence_score: float
    final_answer: str
    sources: List[Dict[str, Any]]

# Mock node functions so the graph is fully executable before Hemant codes the nodes
def query_intake_node(state: AgentState) -> Dict[str, Any]:
    print(f"[LANGGRAPH] Node 1: Query Intake analyzing message: '{state['user_message']}'")
    
    # Simulating intent classification routing logic
    msg = state['user_message'].lower()
    if "notice" in msg or "announcement" in msg:
        intent, agent = "notice_query", "notice_agent"
    elif "ticket" in msg or "grievance" in msg or "complain" in msg:
        intent, agent = "create_ticket", "task_action_agent"
    elif "remind" in msg:
        intent, agent = "create_reminder", "task_action_agent"
    else:
        intent, agent = "information_query", "rag_answer_agent"
        
    return {
        "detected_intent": intent,
        "selected_agent": agent,
        "confidence_score": 0.95
    }

def execution_router_node(state: AgentState) -> Dict[str, Any]:
    print(f"[LANGGRAPH] Node 2: Router directing flow to {state['selected_agent']}")
    
    # Default fallback messaging simulating downstream responses
    answer = f"The {state['selected_agent']} recognized your request categorized under '{state['detected_intent']}'."
    sources = []
    
    if state['detected_intent'] == "information_query":
        answer = "The MCA course fee at Amity University Ranchi is structured semester-wise. Please check the official brochure for total amounts."
        sources = [{"document": "fee_structure.pdf", "page": 1}]
        
    return {
        "final_answer": answer,
        "sources": sources
    }

# Build and compile the state chart graph topology workflow
workflow = StateGraph(AgentState)

# Define the positional nodes in our graph network
workflow.add_node("query_intake", query_intake_node)
workflow.add_node("execution_router", execution_router_node)

# Set the operational pathway boundaries
workflow.set_entry_point("query_intake")
workflow.add_edge("query_intake", "execution_router")
workflow.add_edge("execution_router", END)

# Compile the graph into an executable asset
campus_agent_executor = workflow.compile()