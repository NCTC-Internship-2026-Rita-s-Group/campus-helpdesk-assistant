import time
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_models import ChatAuditLog

class CampusGuardrailAuditEngine:
    """
    🛡️ LLM Guardrail, Cost Control, and Telemetry Engine
    Detects malicious prompt injection vectors, monitors context token allocations, 
    and handles asynchronous database logging streams.
    """
    def __init__(self):
        # Strict prompt injection signature patterns to intercept before reaching Groq hardware
        self.injection_blocklist = [
            "ignore previous instructions",
            "ignore all instructions",
            "system prompt",
            "you must disregard",
            "bypass safety",
            "act as a malicious",
            "forget your rules"
        ]

    def execute_pre_flight_guardrail(self, incoming_query: str) -> tuple[bool, str]:
        """
        🔍 Pre-Flight Security Check
        Scans student prompts for adversarial text structures.
        Returns (is_safe, triggered_rule).
        """
        normalized_text = incoming_query.lower()
        
        # 1. Block empty or spam text strings
        if len(normalized_text) > 2000:
            return False, "Query length limit exceeded (Max 2000 characters)"

        # 2. Check for known prompt injection attack strings
        for forbidden_phrase in self.injection_blocklist:
            if forbidden_phrase in normalized_text:
                return False, f"Adversarial Prompt Injection Vector: '{forbidden_phrase}'"
                
        return True, "None"

    @staticmethod
    def approximate_token_footprint(input_text: str, output_text: str) -> int:
        """
        🧮 Telemetry Measurement Metric
        Approximates the operational token count using standard linguistic multipliers 
        (1 word ≈ 1.33 tokens) to keep cost metrics clean without heavy runtime overhead.
        """
        total_words = len(input_text.split()) + len(output_text.split())
        return int(total_words * 1.33)

    async def register_interaction_audit(
        self,
        db: AsyncSession,
        query: str,
        response: str,
        latency: float,
        is_safe: bool,
        rule_triggered: str
    ):
        """
        📥 Asynchronous Logging Stream
        Commits performance tracking logs and threat intelligence records into PostgreSQL.
        """
        try:
            tokens_used = self.approximate_token_footprint(query, response)
            
            log_record = ChatAuditLog(
                user_query=query,
                ai_response=response,
                latency_seconds=round(latency, 3),
                estimated_tokens=tokens_used,
                is_safe=is_safe,
                triggered_rules=rule_triggered
            )
            
            db.add(log_record)
            await db.commit()
            print(f"📊 Telemetry logged: {tokens_used} tokens parsed over {round(latency, 2)}s | Threat Block: {not is_safe}")
        except Exception as e:
            print(f"❌ Failed to commit analytics telemetry down to storage lines: {str(e)}")

# Instantiate unified global security auditing instance
audit_engine = CampusGuardrailAuditEngine()