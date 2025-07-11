from typing import Dict, Any
from src.guardrails import OutputModel
from src.hooks import LifecycleHooks
import google.generativeai as genai
from src.context import UserSessionContext

class SleepAdvisorAgent:
    """Specialized agent for sleep-related queries"""
    
    def process(self, input_text: str, context: UserSessionContext) -> Dict[str, Any]:
        """Process sleep-related queries"""
        try:
            LifecycleHooks.on_tool_start('SleepAdvisorAgent', context)
            
            prompt = f"""
            You are a sleep specialist assisting {context.name}.
            
            Context:
            - Current mood: {context.mood}
            - Current goal: {context.goal}
            
            User question: {input_text}
            
            Provide a detailed, professional response considering:
            - Sleep hygiene recommendations
            - Relaxation techniques
            - Sleep schedule adjustments
            - When to consult a doctor
            
            Keep the response under 300 words.
            """
            
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            LifecycleHooks.on_tool_end('SleepAdvisorAgent', context, {'response': response.text})
            
            return OutputModel(
                success=True,
                message="Sleep advisor response generated",
                data={'response': response.text}
            ).model_dump()
        
        except Exception as e:
            LifecycleHooks.on_error('SleepAdvisorAgent', e, context)
            return OutputModel(
                success=False,
                message=str(e),
                data={}
            ).model_dump()
