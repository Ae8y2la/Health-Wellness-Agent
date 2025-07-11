from typing import Dict, Any
from src.guardrails import OutputModel
from src.hooks import LifecycleHooks
import google.generativeai as genai

class MoodDetector:
    """Tool for detecting and analyzing user mood from text"""
    
    def detect(self, text: str) -> Dict[str, Any]:
        """Detect mood from user's text input"""
        try:
            prompt = f"""
            Analyze this text and determine the user's mood:
            {text}
            
            Return a JSON object with:
            - mood (one of: happy, sad, anxious, tired, excited, neutral)
            - confidence (0-1)
            - suggested_response (a short empathetic response)
            """
            
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            # Parse the response
            mood_data = eval(response.text)  # In production, use proper JSON parsing
            
            return OutputModel(
                success=True,
                message="Mood detected successfully",
                data=mood_data
            ).model_dump()
        
        except Exception as e:
            LifecycleHooks.on_error('MoodDetector', e)
            return OutputModel(
                success=False,
                message=str(e),
                data={}
            ).model_dump()
