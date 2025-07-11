from typing import Dict, Any, List
from src.guardrails import OutputModel
from src.hooks import LifecycleHooks
import google.generativeai as genai

class MealPlanner:
    """Tool for generating personalized meal plans"""
    
    def generate_plan(self, goal: Dict[str, Any], diet_prefs: str = None) -> Dict[str, Any]:
        """Generate a meal plan based on user's goal and preferences"""
        try:
            prompt = f"""
            Create a 7-day meal plan for someone with these goals:
            {goal['description']}
            
            Dietary preferences: {diet_prefs or 'none'}
            
            Include:
            - 3 meals and 2 snacks per day
            - Calorie targets based on goal
            - Macronutrient breakdown
            - Shopping list
            
            Format as JSON with days as keys and meals as arrays.
            """
            
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            # Parse the response (Gemini should return properly formatted JSON)
            plan = eval(response.text)  # In production, use proper JSON parsing
            
            return OutputModel(
                success=True,
                message="Meal plan generated successfully",
                data={'plan': plan}
            ).model_dump()
        
        except Exception as e:
            LifecycleHooks.on_error('MealPlanner', e)
            return OutputModel(
                success=False,
                message=str(e),
                data={}
            ).model_dump()
