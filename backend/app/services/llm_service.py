import httpx
from groq import Groq
from app.config import settings

class LLMService:
    @staticmethod
    def synthesize_answer(student_query: str, retrieved_context: str) -> str:
        """
        Sends the compiled context blocks along with the student's question 
        to Groq using the ultra-powerful Llama 3.3 70B engine.
        """
        if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "mock-key":
            print("[LLM SERVICE WARNING] GROQ_API_KEY is not set or using placeholder defaults. Returning fallback simulation.")
            return (
                "Thank you for contacting the Amity University Ranchi support desk! "
                "I processed your query regarding your request. (Note: Please update your .env with a live Groq API key to view real-time AI responses)."
            )

        try:
            # Initialize the authentic Groq client using your configuration settings
            client = Groq(api_key=settings.GROQ_API_KEY)
            
            system_prompt = (
                "You are the official, elite AI Helpdesk Assistant for Amity University Ranchi.\n"
                "Your objective is to provide professional, precise, welcoming, and accurate assistance to students.\n\n"
                "CRITICAL INSTRUCTIONS:\n"
                "1. Answer the student's question using ONLY the facts provided within the <context> tags below.\n"
                "2. If the context is empty or does not contain the answer, state honestly and politely that you do "
                "not possess that specific information in your current records and offer to lodge a helpdesk ticket.\n"
                "3. Never invent dates, fees, or policy criteria.\n"
                "4. Maintain an encouraging academic tone fitting for a top-tier university representative."
            )
            
            user_content = f"Here is the verified university documentation:\n<context>\n{retrieved_context}\n</context>\n\nStudent Question: {student_query}"
            
            # Execute the query using Groq's high-intelligence tier 70B model
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_content,
                    }
                ],
                model="llama-3.3-70b-versatile",  # 🚀 Swapped to the elite Llama 3.3 70B model
                temperature=0.1,  # Guarantees rigid adherence to the provided document facts
                max_tokens=800,
            )
            
            # Extract and return the clean text layout from Groq's choices array
            return chat_completion.choices[0].message.content

        except Exception as e:
            print(f"[LLM GENERATION FAILURE] Groq API request crashed: {str(e)}")
            return "We apologize, but an internal AI core processing interruption occurred. Please re-attempt your prompt or contact the administrator."