from typing import Dict, Any
from src.guardrails import InputValidator, OutputModel
from src.hooks import LifecycleHooks

class GoalAnalyzer:
    """Tool for analyzing and parsing user health/fitness goals"""
    
    def analyze(self, goal_text: str) -> Dict[str, Any]:
        """Analyze and parse a user's goal text"""
        try:
            validated = InputValidator.validate_goal_input(goal_text)
            
            # Calculate target weekly weight change
            total_days = validated['duration'] * (7 if validated['time_unit'] == 'weeks' else 30)
            weekly_change = validated['amount'] / (total_days / 7)
            
            result = {
                'description': goal_text,
                'target': validated['amount'],
                'unit': validated['unit'],
                'timeframe': f"{validated['duration']} {validated['time_unit']}",
                'weekly_target': round(weekly_change, 2),
                'direction': validated['direction']
            }
            
            return OutputModel(
                success=True,
                message="Goal successfully analyzed",
                data=result
            ).model_dump()
        
        except Exception as e:
            LifecycleHooks.on_error('GoalAnalyzer', e)
            return OutputModel(
                success=False,
                message=str(e),
                data={}
            ).model_dump()
