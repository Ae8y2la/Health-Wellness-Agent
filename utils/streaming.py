import google.generativeai as genai
from typing import Generator
from src.hooks import LifecycleHooks
from src.context import UserSessionContext

class ResponseStreamer:
    """Utility class for streaming responses from Gemini"""
    
    @staticmethod
    def stream_response(prompt: str, context: UserSessionContext) -> Generator[str, None, None]:
        """Stream a response from Gemini"""
        try:
            full_prompt = f"""
            Respond to the user as {context.coach_persona}, their health coach.
            User: {context.name}
            Goal: {context.goal}
            Mood: {context.mood}
            
            User message: {prompt}
            
            Respond conversationally in short chunks suitable for streaming.
            """
            
            model = genai.GenerativeModel('gemini-pro')
            for chunk in model.generate_content_stream(full_prompt):
                yield chunk.text
        
        except Exception as e:
            LifecycleHooks.on_error('ResponseStreamer', e, context)
            yield "I encountered an error processing your request. Please try again."