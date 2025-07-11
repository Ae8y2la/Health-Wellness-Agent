import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.context import UserSessionContext
from src.guardrails import InputValidator, OutputModel
from src.hooks import LifecycleHooks
import google.generativeai as genai

# Tool imports
from tools.goal_analyzer import GoalAnalyzer
from tools.meal_planner import MealPlanner
from tools.workout_recommender import WorkoutRecommender
from tools.mood_detector import MoodDetector
from tools.biofeedback_simulator import BiofeedbackSimulator

# Specialized agents
from agents.nutrition_expert_agent import NutritionExpertAgent
from agents.injury_support_agent import InjurySupportAgent
from agents.sleep_advisor_agent import SleepAdvisorAgent
from agents.escalation_agent import EscalationAgent

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

class WellnessAgent:
    """Main agent class handling conversation and tool orchestration"""
    
    def __init__(self, user_context: UserSessionContext):
        self.context = user_context
        self.tools = {
            'goal_analyzer': GoalAnalyzer(),
            'meal_planner': MealPlanner(),
            'workout_recommender': WorkoutRecommender(),
            'mood_detector': MoodDetector(),
            'biofeedback_simulator': BiofeedbackSimulator()
        }
        self.specialized_agents = {
            'nutrition': NutritionExpertAgent(),
            'injury': InjurySupportAgent(),
            'sleep': SleepAdvisorAgent(),
            'escalation': EscalationAgent()
        }

    def process_user_input(self, input_text: str) -> Dict[str, Any]:
        """Process user input and return response dictionary"""
        try:
            # Validate input
            if not InputValidator.validate_input(input_text):
                return {
                    'response': "Please ask a health-related question",
                    'status': 'validation_error'
                }

            # Route to specialized agent if needed
            specialized_agent = self._detect_specialized_agent_needed(input_text)
            if specialized_agent:
                return self._handle_specialized_agent(input_text, specialized_agent)

            # Route to appropriate tool
            tool_response = self._route_to_tool(input_text)
            if tool_response:
                return tool_response

            # Default generative response
            return {
                'response': self.generate_response(input_text),
                'status': 'success'
            }

        except Exception as e:
            LifecycleHooks.on_error('WellnessAgent', e, self.context)
            return {
                'response': f"Sorry, I encountered an error: {str(e)}",
                'status': 'error'
            }

    def _handle_specialized_agent(self, input_text: str, agent_type: str) -> Dict[str, Any]:
        """Handle specialized agent processing"""
        LifecycleHooks.on_handoff('WellnessAgent', agent_type, self.context)
        agent_response = self.specialized_agents[agent_type].process(input_text, self.context)
        return {
            'response': agent_response.get('response', self.generate_response(input_text)),
            'status': 'success',
            'agent_type': agent_type,
            **agent_response
        }

    def _route_to_tool(self, input_text: str) -> Optional[Dict[str, Any]]:
        """Route input to appropriate tool"""
        input_lower = input_text.lower()
        
        if "goal" in input_lower or "target" in input_lower:
            return self._process_with_tool('goal_analyzer', input_text)
        elif "meal" in input_lower or "food" in input_lower:
            return self._process_with_tool('meal_planner', input_text)
        elif "workout" in input_lower or "exercise" in input_lower:
            return self._process_with_tool('workout_recommender', input_text)
        elif "mood" in input_lower or "feel" in input_lower:
            return self._process_with_tool('mood_detector', input_text)
        return None

    def _process_with_tool(self, tool_name: str, input_text: str) -> Dict[str, Any]:
        """Process input with specified tool"""
        LifecycleHooks.on_tool_start(tool_name, self.context)
        result = self.tools[tool_name].process(input_text, self.context)
        LifecycleHooks.on_tool_end(tool_name, self.context, result)
        
        return {
            'response': self.generate_response(input_text),
            'status': 'success',
            'tool': tool_name,
            'data': result
        }
    
    def _detect_specialized_agent_needed(self, input_text: str) -> Optional[str]:
        """Determine if a specialized agent is needed"""
        prompt = f"""
        Analyze this user input and determine if it requires a specialized agent:
        {input_text}
        
        Options:
        - nutrition: for diet-specific questions, allergies, diabetes
        - injury: for pain, physical limitations
        - sleep: for fatigue, insomnia
        - escalation: when user asks for human support
        
        Return only the keyword or None if no specialized agent needed.
        """
        response = model.generate_content(prompt)
        return response.text.lower() if response.text.lower() in ['nutrition', 'injury', 'sleep', 'escalation'] else None
    
    def _process_goal(self, input_text: str) -> Dict[str, Any]:
        """Process goal-related input"""
        LifecycleHooks.on_tool_start('goal_analyzer', self.context)
        result = self.tools['goal_analyzer'].analyze(input_text)
        self.context.goal = result['data']
        LifecycleHooks.on_tool_end('goal_analyzer', self.context, result)
        return {'response': self.generate_response(input_text), 'goal': result}
    
    def _process_meal(self, input_text: str) -> Dict[str, Any]:
        """Process meal-related input"""
        LifecycleHooks.on_tool_start('meal_planner', self.context)
        result = self.tools['meal_planner'].generate_plan(
            self.context.goal, 
            self.context.diet_preferences
        )
        self.context.meal_plan = result['data']['plan']
        LifecycleHooks.on_tool_end('meal_planner', self.context, result)
        return {'response': self.generate_response(input_text), 'meal_plan': result}
    
    def _process_workout(self, input_text: str) -> Dict[str, Any]:
        """Process workout-related input"""
        LifecycleHooks.on_tool_start('workout_recommender', self.context)
        result = self.tools['workout_recommender'].generate_plan(
            self.context.goal,
            self.context.injury_notes
        )
        self.context.workout_plan = result['data']['plan']
        LifecycleHooks.on_tool_end('workout_recommender', self.context, result)
        return {'response': self.generate_response(input_text), 'workout_plan': result}
    
    def _process_mood(self, input_text: str) -> Dict[str, Any]:
        """Process mood-related input"""
        LifecycleHooks.on_tool_start('mood_detector', self.context)
        result = self.tools['mood_detector'].detect(input_text)
        self.context.mood = result['data']['mood']
        LifecycleHooks.on_tool_end('mood_detector', self.context, result)
        return {'response': self.generate_response(input_text), 'mood': result}