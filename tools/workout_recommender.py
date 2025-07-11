from typing import Dict, Any
from src.guardrails import OutputModel
from src.hooks import LifecycleHooks
import google.generativeai as genai

class WorkoutRecommender:
    """Tool for generating personalized workout plans"""
    
    def generate_plan(self, goal: Dict[str, Any], injury_notes: str = None) -> Dict[str, Any]:
        """Generate a workout plan based on user's goal and any injuries"""
        try:
            prompt = f"""
            Create a weekly workout plan for someone with these goals:
            {goal['description']}
            
            Injury notes: {injury_notes or 'none'}
            
            Include:
            - 5-6 days of workouts
            - Mix of cardio and strength
            - Duration and intensity based on goal
            - Modifications for any injuries
            - Progressive overload plan
            
            Format as JSON with days as keys and exercises as arrays.
            """
            
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            # Parse the response
            plan = eval(response.text)  # In production, use proper JSON parsing
            
            return OutputModel(
                success=True,
                message="Workout plan generated successfully",
                data={'plan': plan}
            ).model_dump()
        
        except Exception as e:
            LifecycleHooks.on_error('WorkoutRecommender', e)
            return OutputModel(
                success=False,
                message=str(e),
                data={}
            ).model_dump()
