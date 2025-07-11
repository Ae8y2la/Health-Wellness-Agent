from typing import Dict, List, Any
from src.guardrails import OutputModel
from src.hooks import LifecycleHooks
import google.generativeai as genai

class FAQResponder:
    """Handles frequently asked questions with canned responses"""
    
    def __init__(self):
        self.common_questions = {
            "how to start": "Begin by setting a clear goal using the 'Set Goal' feature.",
            "meal tips": "Focus on whole foods and balanced macros. Use our meal planner!",
            "workout frequency": "3-5 times weekly is ideal for most goals.",
            "track progress": "Use our daily check-ins and journal features.",
            "contact support": "Use the 'Help' button to reach our team."
        }
    
    def respond(self, question: str, context: Any = None) -> Dict[str, Any]:
        """Generate response to FAQ"""
        try:
            # First check for exact matches
            lower_q = question.lower()
            for q, answer in self.common_questions.items():
                if q in lower_q:
                    return OutputModel(
                        success=True,
                        message="Standard FAQ response",
                        data={"response": answer, "is_faq": True}
                    ).model_dump()
            
            # If no match, use Gemini
            prompt = f"""
            Answer this health/wellness question concisely:
            {question}
            
            Context:
            User: {context.name if context else 'unknown'}
            Goal: {context.goal if context else 'not set'}
            
            Respond in 1-2 sentences maximum.
            """
            
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            return OutputModel(
                success=True,
                message="Generated FAQ response",
                data={"response": response.text, "is_faq": False}
            ).model_dump()
            
        except Exception as e:
            LifecycleHooks.on_error('FAQResponder', e)
            return OutputModel(
                success=False,
                message=str(e),
                data={"response": "I couldn't process that question. Please try rephrasing."}
            ).model_dump()