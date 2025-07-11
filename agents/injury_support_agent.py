from typing import Dict, Any
from src.guardrails import OutputModel
from src.hooks import LifecycleHooks
import google.generativeai as genai
from src.context import UserSessionContext

class InjurySupportAgent:
    """Specialized agent for injury-related queries"""
    
    def process(self, input_text: str, context: UserSessionContext) -> Dict[str, Any]:
        """Process injury-related queries"""
        try:
            LifecycleHooks.on_tool_start('InjurySupportAgent', context)
            
            prompt = f"""
            You are a physical therapist assisting {context.name} with injury support.
            
            Context:
            - Current injury notes: {context.injury_notes}
            - Current workout plan: {context.workout_plan if context.workout_plan else 'none'}
            
            User question: {input_text}
            
            Provide a detailed, professional response considering:
            - Safe modifications to their routine
            - Recovery timeline expectations
            - When to seek medical attention
            - Pain management strategies
            
            Keep the response under 300 words.
            """
            
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            # Update injury notes if new information was provided
            if "injur" in input_text.lower() or "pain" in input_text.lower():
                context.injury_notes = input_text
            
            LifecycleHooks.on_tool_end('InjurySupportAgent', context, {'response': response.text})
            
            return OutputModel(
                success=True,
                message="Injury support response generated",
                data={'response': response.text}
            ).model_dump()
        
        except Exception as e:
            LifecycleHooks.on_error('InjurySupportAgent', e, context)
            return OutputModel(
                success=False,
                message=str(e),
                data={}
            ).model_dump()
