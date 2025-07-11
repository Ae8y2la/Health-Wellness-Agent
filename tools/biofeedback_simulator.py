from typing import Dict, Any
from src.guardrails import OutputModel
from src.hooks import LifecycleHooks
import random
from datetime import datetime

class BiofeedbackSimulator:
    """Tool for simulating biofeedback data"""
    
    def generate_data(self) -> Dict[str, Any]:
        """Generate simulated biofeedback data"""
        try:
            now = datetime.now()
            hour = now.hour
            
            # Simulate heart rate based on time of day
            if 6 <= hour < 10:
                hr = random.randint(65, 75)  # Morning
            elif 10 <= hour < 18:
                hr = random.randint(70, 85)  # Daytime
            elif 18 <= hour < 22:
                hr = random.randint(75, 90)  # Evening
            else:
                hr = random.randint(60, 70)  # Night
            
            # Simulate steps (more likely to be higher later in the day)
            steps = min(12000, random.randint(2000, 8000) + (hour * 200))
            
            data = {
                'heart_rate': hr,
                'steps': steps,
                'hydration_alert': random.random() > 0.7,
                'timestamp': now.isoformat()
            }
            
            return OutputModel(
                success=True,
                message="Biofeedback data generated",
                data=data
            ).model_dump()
        
        except Exception as e:
            LifecycleHooks.on_error('BiofeedbackSimulator', e)
            return OutputModel(
                success=False,
                message=str(e),
                data={}
            ).model_dump()
