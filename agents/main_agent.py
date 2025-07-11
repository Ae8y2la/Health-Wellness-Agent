from typing import Dict, Any
from src.agent import WellnessAgent
from src.context import UserSessionContext
from src.hooks import LifecycleHooks
import google.generativeai as genai

class MainAgent(WellnessAgent):
    """Enhanced main agent with additional coordination capabilities"""
    
    def __init__(self, context: UserSessionContext):
        super().__init__(context)
        self.current_focus = "general"
    
    def coordinate_agents(self, input_text: str) -> Dict[str, Any]:
        """Coordinate between specialized agents based on input"""
        agent_priority = [
            ("injury", ["pain", "hurt", "injury"]),
            ("nutrition", ["food", "meal", "diet", "eat"]),
            ("sleep", ["tired", "sleep", "insomnia"]),
            ("escalation", ["human", "talk to someone"])
        ]
        
        for agent, keywords in agent_priority:
            if any(keyword in input_text.lower() for keyword in keywords):
                self.current_focus = agent
                return self.specialized_agents[agent].process(input_text, self.context)
        
        self.current_focus = "general"
        return super().process_user_input(input_text)
    
    def generate_daily_summary(self) -> str:
        """Generate a daily summary using Gemini"""
        prompt = f"""
        Generate a daily wellness summary for {self.context.name}:
        
        Current Goal: {self.context.goal}
        Mood: {self.context.mood}
        Recent Progress: {self.context.progress_logs[-3:] if self.context.progress_logs else 'None'}
        
        Provide:
        1. Encouragement based on progress
        2. 1 area to focus on today
        3. Motivational quote
        
        Keep it under 200 words.
        """
        
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text