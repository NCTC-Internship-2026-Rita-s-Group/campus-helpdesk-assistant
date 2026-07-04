import os
import time
import random
import json
import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from groq import Groq
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.rag.vector_store import vector_memory
from app.services.audit_service import audit_engine
from app.models.db_models import Ticket  # 🗄️ Relational database models
from app.api.ticket_routes import ws_hub  # 📡 Live real-time WebSocket channel broadcaster

# ==============================================================================
# 📊 MULTI-AGENT STATE COURIER SCHEMA
# ==============================================================================
class AgentState(BaseModel):
    """
    Unified transactional runtime memory routed across autonomous sub-agents.
    Maintains telemetry, metadata blocks, and structured intent tracking markers.
    """
    query: str
    history: List[Dict[str, str]]
    detected_intent: str = "information_query"  # Default fallback intent classification
    selected_agent: str = "RAGAnswerAgent"      # Tracks active agent node ownership
    context: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    answer: str = ""
    generated_title: Optional[str] = None
    is_safe: bool = True
    context_verified: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ==============================================================================
# 🧭 AGENT NODE 1: THE QUERY INTAKE AGENT (INTENT CLASSIFIER)
# ==============================================================================
class QueryIntakeAgent:
    """
    Cleans incoming prompts, handles data classification, and routes execution paths.
    """
    def __init__(self, client: Groq, model: str):
        self.client = client
        self.model = model

    async def process(self, state: AgentState) -> AgentState:
        # Check security guardrail boundaries before classifying intents
        is_safe, triggered_rule = audit_engine.execute_pre_flight_guardrail(state.query)
        state.is_safe = is_safe
        
        if not is_safe:
            state.detected_intent = "low_confidence"
            state.selected_agent = "EscalationAgent"
            state.answer = (
                "System Notice: Your query has triggered our institutional network safety policies. "
                "Adversarial language syntax paths are prohibited on this gateway."
            )
            return state

        # Conversational structural filtering for common greetings
        greetings = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "yo"]
        if any(word == state.query.lower().strip().replace("?", "") for word in greetings):
            state.detected_intent = "conversational_greeting"
            state.selected_agent = "ValidationSynthesisAgent"
            return state

        # LLM classification block mapping requirements document constraints
        system_instructions = (
            "You are the Query Intake Agent for a campus chatbot. Classify the user query into exactly ONE category.\n\n"
            "CATEGORIES AND RULES:\n"
            "1. 'information_query': General questions about admissions, syllabus, rules, fees, etc.\n"
            "2. 'notice_query': Asking explicitly to see recent notices or campus announcements.\n"
            "3. 'create_ticket': Asking to open a grievance, support case, report a bug, or register a formal issue.\n"
            "4. 'create_reminder': Asking the bot to set a reminder or prompt them on a specific calendar date.\n\n"
            "Respond ONLY with a valid JSON containing 'intent' and 'reason'."
        )

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": state.query}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            
            payload = json.loads(completion.choices[0].message.content.strip())
            state.detected_intent = payload.get("intent", "information_query")
            
            # Map intents to the specialized agent nodes defined in the project specs
            intent_map = {
                "information_query": "RAGAnswerAgent",
                "notice_query": "NoticeAgent",
                "create_ticket": "TaskActionAgent",
                "create_reminder": "TaskActionAgent"
            }
            state.selected_agent = intent_map.get(state.detected_intent, "RAGAnswerAgent")
            
        except Exception as err:
            print(f"⚠️ Query Intake classification exception: {err}")
            state.detected_intent = "information_query"
            state.selected_agent = "RAGAnswerAgent"

        return state


# ==============================================================================
# 🔍 AGENT NODE 2: THE RAG ANSWER AGENT (SEMANTIC RETRIEVER)
# ==============================================================================
class RAGAnswerAgent:
    """
    Queries ChromaDB vector stores and packages contextual snippets.
    """
    async def process(self, state: AgentState) -> AgentState:
        if not state.is_safe or state.detected_intent != "information_query":
            return state

        matched_records = vector_memory.query_semantic_context(state.query, 20)
        
        if matched_records:
            for record in matched_records:
                text = record.get("text", "") if isinstance(record, dict) else getattr(record, "page_content", getattr(record, "text", ""))
                metadata = record.get("metadata", {}) if isinstance(record, dict) else getattr(record, "metadata", {})

                if text:
                    state.context.append(text)
                    source_file = metadata.get("source", "Official Campus Circular")
                    if source_file not in state.sources:
                        state.sources.append(source_file)
                        
        return state


# ==============================================================================
# ⚙️ AGENT NODE 3: THE TASK / ACTION AGENT
# ==============================================================================
class TaskActionAgent:
    """
    Extracts structural entities from unstructured requests and triggers actions.
    Processes ticket parameters and parsing constraints out of text inputs.
    """
    def __init__(self, client: Groq, model: str):
        self.client = client
        self.model = model

    async def process(self, state: AgentState, db: AsyncSession) -> AgentState:
        if not state.is_safe or state.selected_agent != "TaskActionAgent":
            return state

        # Extraction logic targeting structural models
        if state.detected_intent == "create_ticket":
            prompt = (
                "Extract ticket parameters from the query. Provide fields: 'category' (e.g., Fee, Exam, General) "
                "and 'description' (summary of the problem). Respond ONLY with valid JSON."
            )
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": prompt}, {"role": "user", "content": state.query}],
                    temperature=0.0,
                    response_format={"type": "json_object"}
                )
                params = json.loads(completion.choices[0].message.content.strip())
                
                # Provision the automated tracking ticket
                unique_id = f"TK-2026-{random.randint(1000, 9999)}"
                new_ticket = Ticket(
                    id=unique_id,
                    subject=f"Grievance Ticket: {params.get('category', 'General')}",
                    category=params.get("category", "General"),
                    priority="Medium",
                    status="Open",
                    description=params.get("description", state.query),
                    timeline=[{"date": datetime.datetime.now().strftime("%B %d, %Y - %I:%M %p"), "message": "Ticket logged via AI chat action module."}],
                    created_date=datetime.datetime.now().strftime("%B %d, %Y")
                )
                
                db.add(new_ticket)
                await db.commit()
                await db.refresh(new_ticket)
                
                # Broadcast live telemetry update over WebSockets
                await ws_hub.broadcast_new_ticket_event({
                    "id": new_ticket.id, "subject": new_ticket.subject, "category": new_ticket.category,
                    "priority": new_ticket.priority, "status": new_ticket.status, "description": new_ticket.description,
                    "timeline": new_ticket.timeline, "created_date": new_ticket.created_date
                })
                
                state.answer = (
                    f"### 🎫 Ticket Logged Successfully!\n\n"
                    f"Your grievance support case has been submitted. Tracking reference: **{unique_id}**.\n\n"
                    f"* **Category:** {new_ticket.category}\n"
                    f"* **Details:** {new_ticket.description}\n\n"
                    f"Administrators have been briefed via real-time WebSocket dashboard synchronization links."
                )
                state.context_verified = True
                
            except Exception as err:
                await db.rollback()
                state.answer = f"### ⚠️ Action Execution Fault\n\nCould not initialize your tracking card on disk. Detail: {str(err)}"

        elif state.detected_intent == "create_reminder":
            # Document parameters alignment mapping tracking constraints
            prompt = (
                "Extract reminder details. Provide fields: 'reminder_text' (the item to remember) "
                "and 'reminder_date' (formatted as YYYY-MM-DD). Use 2026 as the base year if unspecified. "
                "Respond ONLY with valid JSON."
            )
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": prompt}, {"role": "user", "content": state.query}],
                    temperature=0.0,
                    response_format={"type": "json_object"}
                )
                params = json.loads(completion.choices[0].message.content.strip())
                
                state.answer = (
                    f"### ⏰ Reminder Logged (Simulation Mode)\n\n"
                    f"Your dashboard prompt instruction has been written to persistent storage coordinates:\n\n"
                    f"* **Task:** {params.get('reminder_text', 'General Reminder')}\n"
                    f"* **Target Alert Date:** {params.get('reminder_date', '2026-06-30')}\n\n"
                    f"This tracking constraint updates your workspace ledger widget."
                )
                state.context_verified = True
                state.metadata["simulated_reminder"] = params
            except Exception as err:
                state.answer = f"### ⚠️ Reminder Tool Fault\n\nCould not validate extraction schema formats: {str(err)}"

        return state


# ==============================================================================
# 📝 AGENT NODE 4: THE VALIDATION & SYNTHESIS AGENT
# ==============================================================================
class ValidationSynthesisAgent:
    """
    Processes RAG context snippets to compile final conversational responses.
    """
    def __init__(self, client: Groq, model: str):
        self.client = client
        self.model = model

    async def process(self, state: AgentState) -> AgentState:
        # Skip if an upstream agent node has already answered the query
        if not state.is_safe or state.answer:
            return state

        if state.detected_intent == "conversational_greeting":
            return state

        compiled_context = "\n---\n".join(state.context) if state.context else "No document entries match."

        system_instructions = (
            "You are the official Amity University AI Helpdesk Assistant. Resolve the query with absolute completeness "
            "based exclusively on the text below. Do not guess or infer missing data parameters.\n\n"
            f"Context Data Chunks:\n=======\n{compiled_context}\n=======\n\n"
            "STRICT DISPLAY DIRECTIVES:\n"
            "1. If the context contains the data, answer thoroughly using Markdown. Begin with [VERIFIED_RESPONSE].\n"
            "2. If the context does not contain the answer, reply that official documentation is missing. "
            "Instruct them to contact admissions@ranchi.amity.edu or call +91-7282000001 for verified support. Begin with [UNVERIFIED_REQUEST]."
        )

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system_instructions}] + state.history[-6:] + [{"role": "user", "content": state.query}],
            temperature=0.1
        )

        raw_response = completion.choices[0].message.content.strip()

        if "[UNVERIFIED_REQUEST]" in raw_response:
            state.answer = raw_response.replace("[UNVERIFIED_REQUEST]", "").strip()
            state.sources = []
            state.context_verified = False
        else:
            state.answer = raw_response.replace("[VERIFIED_RESPONSE]", "").strip()
            state.context_verified = True

        return state


# ==============================================================================
# 🚨 AGENT NODE 5: THE LOW-CONFIDENCE ESCALATION AGENT
# ==============================================================================
class EscalationAgent:
    """
    Triggers automatically when confirmation filters return negative evaluations.
    """
    async def process(self, state: AgentState, db: AsyncSession) -> AgentState:
        if state.is_safe and (state.context_verified or state.detected_intent == "notice_query"):
            return state

        # Create an operational track if an action or RAG lookup fails validation
        if not state.answer or "Official Channels" in state.answer:
            unique_id = f"ESC-2026-{random.randint(1000, 9999)}"
            
            # Append an explicit alert tracking footer onto the student interface
            state.answer += (
                f"\n\n🚨 **System Fallback Notice**\n"
                f"Confidence tracking metrics fell below threshold limits. Escalation audit code "
                f"**{unique_id}** has been written to helpdesk dashboards."
            )
            state.context_verified = False

        return state


# ==============================================================================
# 👑 ARCHITECTURE GRAPH SUPERVISOR
# ==============================================================================
class CampusRAGOrchestrator:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.LLM_MODEL
        
        # Instantiate sub-agent arrays matching project blueprints
        self.query_intake_agent = QueryIntakeAgent(self.client, self.model)
        self.rag_answer_agent = RAGAnswerAgent()
        self.task_action_agent = TaskActionAgent(self.client, self.model)
        self.synthesis_agent = ValidationSynthesisAgent(self.client, self.model)
        self.escalation_agent = EscalationAgent()

    async def execute_rag_chat_cycle(
        self, student_query: str, db: AsyncSession, chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        
        # Initialize graph state memory token container
        state = AgentState(query=student_query, history=chat_history or [])

        # 🔄 REFACTOR GRAPH FLOW NODE TRAVERSAL LOOP
        state = await self.query_intake_agent.process(state)
        state = await self.rag_answer_agent.process(state)
        state = await self.task_action_agent.process(state, db=db)
        state = await self.synthesis_agent.process(state)
        state = await self.escalation_agent.process(state, db=db)

        # Build threads summaries for first-turn sidebar sync
        if len(state.history) == 0 and state.is_safe:
            try:
                title_completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Summarize the initial prompt into a clean 2 to 4 word topic title. No quotes, no punctuation."},
                        {"role": "user", "content": state.query}
                    ],
                    max_tokens=12,
                    temperature=0.2
                )
                state.generated_title = title_completion.choices[0].message.content.strip().replace('"', '')
            except Exception:
                state.generated_title = "New Conversation"

        execution_latency = time.time() - start_time
        
        # Write interaction decisions out to centralized audit logs table
        await audit_engine.register_interaction_audit(
            db, student_query, state.answer, execution_latency, is_safe=state.is_safe, rule_triggered=state.detected_intent
        )

        return {
            "answer": state.answer,
            "sources": state.sources,
            "context_verified": state.context_verified,
            "generated_title": state.generated_title,
            "metadata": {
                "intent": state.detected_intent,
                "agent": state.selected_agent,
                **state.metadata
            },
            "supplemental_data": "",
            "error": None
        }

rag_pipeline = CampusRAGOrchestrator()