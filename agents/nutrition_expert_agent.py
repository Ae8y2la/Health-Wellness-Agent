from typing import Dict, Any
from src.guardrails import OutputModel
from src.hooks import LifecycleHooks
import google.generativeai as genai
from src.context import UserSessionContext

class NutritionExpertAgent:
    """Specialized agent for nutrition-related queries"""
    
    def process(self, input_text: str, context: UserSessionContext) -> Dict[str, Any]:
        """Process nutrition-related queries"""
        try:
            LifecycleHooks.on_tool_start('NutritionExpertAgent', context)
            
            prompt = f"""
            You are a nutrition expert assisting {context.name}.
            
            Context:
            - Goal: {context.goal}
            - Diet preferences: {context.diet_preferences}
            - Known allergies: {context.injury_notes if context.injury_notes else 'none'}
            
            User question: {input_text}
            
            Provide a detailed, professional response considering:
            - Nutritional requirements for their goal
            - Any dietary restrictions
            - Practical meal planning tips
            
            Keep the response under 300 words.
            """
            
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            LifecycleHooks.on_tool_end('NutritionExpertAgent', context, {'response': response.text})
            
            return OutputModel(
                success=True,
                message="Nutrition expert response generated",
                data={'response': response.text}
            ).model_dump()
        
        except Exception as e:
            LifecycleHooks.on_error('NutritionExpertAgent', e, context)
            return OutputModel(
                success=False,
                message=str(e),
                data={}
            ).model_dump()
