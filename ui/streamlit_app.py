import streamlit as st
from streamlit_chat import message
from datetime import datetime
import requests
from enum import Enum
from typing import Dict, List, Optional
import uuid
import sys
import os
from pathlib import Path
import base64
import random
import time
import logging
import matplotlib.pyplot as plt
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# --- Constants ---
API_BASE_URL = os.getenv("API_BASE_URL","https://fastapi-backend-production-7f8e.up.railway.app")
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# --- Enums ---
class DietPreference(str, Enum):
    VEGETARIAN = "vegetarian"
    KETO = "keto"
    BALANCED = "balanced"
    VEGAN = "vegan"
    PALEO = "paleo"

class CoachPersona(str, Enum):
    ZENBOT = "ZenBot"
    FITNESS = "FitnessCoach"
    NUTRITION = "NutritionExpert"

# --- Models ---
class UserSessionContext:
    def __init__(self, name: str, uid: str, coach_persona: CoachPersona = CoachPersona.ZENBOT):
        self.name = name
        self.uid = uid  # This should be a string UUID
        self.coach_persona = coach_persona
        self.diet_preferences = DietPreference.BALANCED
        self.streak_count = 0
        self.biofeedback = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.meal_plan = {}
        self.workout_plan = {}
        self.goal = None
        self.mood_history = []
    
    def increment_streak(self):
        self.streak_count += 1
        self.updated_at = datetime.now()
    
    def add_mood(self, mood: str):
        self.mood_history.append({
            "mood": mood,
            "timestamp": datetime.now()
        })
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "email": f"{self.name.lower()}@wellness.com",
            "coach_preference": self.coach_persona.value,
            "is_premium": False
        }

# --- API Client ---
class WellnessAPI:
    @staticmethod
    def _make_request(method, endpoint, **kwargs):
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.request(
                    method,
                    f"{API_BASE_URL}{endpoint}",
                    timeout=10,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                time.sleep(RETRY_DELAY * (attempt + 1))
    
    @staticmethod
    def check_backend_health():
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            return response.ok
        except requests.exceptions.RequestException:
            return False
    
    @staticmethod
    def create_user(user_data: Dict) -> Dict:
        return WellnessAPI._make_request("POST", "/users/", json=user_data)
    
    @staticmethod
    def generate_meal_plan(diet: str) -> Dict:
        return WellnessAPI._make_request("GET", f"/meal-plans/generate?diet={diet}")
    
    @staticmethod
    def generate_workout_plan(goal_type: str) -> Dict:
        return WellnessAPI._make_request("GET", f"/workouts/generate?goal_type={goal_type}")
    
    @staticmethod
    def add_biofeedback(user_id: str, data: Dict) -> Dict:
        if not isinstance(user_id, str):
            raise ValueError("user_id must be a string")
        
        data["user_id"] = user_id
        numeric_fields = ['heart_rate', 'stress_level', 'sleep_quality']
        for field in numeric_fields:
            if field in data:
                try:
                    data[field] = float(data[field])
                except (ValueError, TypeError):
                    data[field] = 0
        return WellnessAPI._make_request("POST", "/biofeedback/", json=data)
    
    @staticmethod
    def get_wellness_tip() -> Dict:
        return WellnessAPI._make_request("GET", "/wellness-tip")

# --- Agent ---
class WellnessAgent:
    def __init__(self, context: UserSessionContext):
        self.context = context
    
    def process_user_input(self, input_text: str) -> Dict:
        input_text = input_text.lower()
        response = ""
        
        if any(word in input_text for word in ["meal", "diet", "food", "eat"]):
            plan = WellnessAPI.generate_meal_plan(self.context.diet_preferences.value)
            self.context.meal_plan = plan.get("plan", {})
            response = f"🍽️ **{self.context.diet_preferences.value.capitalize()} Meal Plan** 🍽️\n\n"
            for day, meals in self.context.meal_plan.items():
                response += f"**{day.capitalize()}**:\n"
                response += "\n".join(f"- {meal}" for meal in meals)
                response += "\n\n"
            response += "Would you like me to adjust anything?"
        
        elif any(word in input_text for word in ["workout", "exercise", "train"]):
            plan = WellnessAPI.generate_workout_plan("general")
            self.context.workout_plan = plan.get("plan", {})
            response = "💪 **Personalized Workout Plan** 💪\n\n"
            for day, exercises in self.context.workout_plan.items():
                response += f"**{day.capitalize()}**:\n"
                response += "\n".join(f"- {exercise}" for exercise in exercises)
                response += "\n\n"
            response += "How does this plan look to you?"
        
        elif any(word in input_text for word in ["goal", "target", "objective"]):
            self.context.goal = input_text
            response = f"🎯 **Goal Successfully Set**: \n\n{input_text}\n\nWould you like me to help create a plan to achieve this?"
        
        elif any(word in input_text for word in ["tip", "advice", "suggestion"]):
            tip = WellnessAPI.get_wellness_tip()
            response = f"💡 **Today's Wellness Tip**: \n\n{tip['tip']}\n\nWould you like another tip?"
        
        elif any(word in input_text for word in ["happy", "sad", "angry", "mood"]):
            mood = "neutral"
            if any(word in input_text for word in ["happy", "joy", "good"]):
                mood = "happy"
            elif any(word in input_text for word in ["sad", "depress", "down"]):
                mood = "sad"
            elif any(word in input_text for word in ["angry", "mad", "frustrat"]):
                mood = "angry"
            
            self.context.add_mood(mood)
            response = f"🌱 Thank you for sharing your mood. I've noted that you're feeling {mood}. "
            if mood == "happy":
                response += "That's wonderful! Keep up the positive energy!"
            elif mood == "sad":
                response += "I'm here to support you. Would you like to talk about it or try a mood-boosting activity?"
            else:
                response += "How can I help you feel better today?"
        
        else:
            responses = [
                f"Hello {self.context.name}! 🙏 I'm your {self.context.coach_persona.value}. How can I help you today?",
                f"Hi {self.context.name}! 🌟 Your {self.context.coach_persona.value} here. What wellness topic shall we explore?",
                f"Welcome {self.context.name}! 🌿 As your {self.context.coach_persona.value}, I'm ready to assist.",
                f"Good to see you {self.context.name}! 💪 Your {self.context.coach_persona.value} is here."
            ]
            response = random.choice(responses)
        
        return {"response": response}

# --- App Configuration ---
st.set_page_config(
    page_title="Health-Wellness Coach",
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9f5ff 100%);
        font-family: 'Arial', sans-serif;
    }
    .header-text {
        color: #2D3748;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .header-subtext {
        color: #4A5568;
        font-size: 1.1rem;
    }
    .chat-container {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    [data-testid="stChatMessage"][aria-label="Chat message from user"] {
        background-color: #E3F2FD !important;
        border-left: 4px solid #4FD1C5 !important;
        margin-left: auto;
    }
    [data-testid="stChatMessage"][aria-label="Chat message from assistant"] {
        background-color: #FFFFFF !important;
        border-left: 4px solid #9E9E9E !important;
        margin-right: auto;
        border: 1px solid #EDF2F7 !important;
    }
    .stButton>button {
        background-color: #4FD1C5 !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
def initialize_session_state():
    if 'backend_ready' not in st.session_state:
        with st.spinner("🔌 Connecting to backend..."):
            backend_ready = False
            for _ in range(MAX_RETRIES):
                try:
                    if WellnessAPI.check_backend_health():
                        backend_ready = True
                        break
                    time.sleep(RETRY_DELAY)
                except requests.exceptions.RequestException:
                    time.sleep(RETRY_DELAY)
            
            st.session_state.backend_ready = backend_ready
            
            if not backend_ready:
                st.error(f"""
                ❌ Could not connect to backend. Please ensure:
                1. Backend server is running (`uvicorn src.backend_main:app --reload`)
                2. API_BASE_URL is correct (current: {API_BASE_URL})
                """)
                st.stop()
    
    if 'user_context' not in st.session_state:
        try:
            user_data = {
                "name": "Guest",
                "email": "guest@wellness.com",
                "is_premium": False,
                "coach_preference": "ZenBot"
            }
            api_response = WellnessAPI.create_user(user_data)
            
            user_id = str(api_response["user_id"])
            st.session_state.user_context = UserSessionContext(
                name=api_response["name"],
                uid=user_id,
                coach_persona=CoachPersona(api_response["coach_preference"])
            )
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to initialize user: {str(e)}")
            st.stop()
    
    if 'generated' not in st.session_state:
        st.session_state.generated = []
    
    if 'past' not in st.session_state:
        st.session_state.past = []
    
    if 'biofeedback' not in st.session_state:
        st.session_state.biofeedback = []
    
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now()

# --- Components ---
@st.cache_resource
def get_wellness_agent():
    return WellnessAgent(st.session_state.user_context)

def plot_mood_history(mood_history):
    if not mood_history:
        return None
    
    mood_map = {"happy": 2, "neutral": 1, "sad": 0, "angry": 0}
    dates = [entry["timestamp"] for entry in mood_history]
    moods = [mood_map.get(entry["mood"], 1) for entry in mood_history]
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(dates, moods, marker='o', color='#4FD1C5', linewidth=2)
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["Sad/Angry", "Neutral", "Happy"])
    ax.set_title("Your Mood Over Time")
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_facecolor('#F8F9FA')
    fig.patch.set_facecolor('#F8F9FA')
    
    return fig

def configure_sidebar():
    with st.sidebar:
        st.title("🧘 Health-Wellness Dashboard")
        st.markdown("---")
        
        # User Profile
        st.subheader("👤 Your Profile")
        name = st.text_input("Name", value=st.session_state.user_context.name)
        diet_prefs = st.selectbox(
            "Diet Preferences",
            [pref.value for pref in DietPreference],
            index=list(DietPreference).index(st.session_state.user_context.diet_preferences),
            key="diet_prefs"
        )
        coach_persona = st.selectbox(
            "Coach Style",
            [persona.value for persona in CoachPersona],
            index=list(CoachPersona).index(st.session_state.user_context.coach_persona),
            key="coach_persona"
        )
        
        # Update context
        st.session_state.user_context.name = name
        st.session_state.user_context.diet_preferences = DietPreference(diet_prefs)
        st.session_state.user_context.coach_persona = CoachPersona(coach_persona)
        
        # Biofeedback
        st.markdown("---")
        st.subheader("💓 Biofeedback")
        if st.button("Simulate Biofeedback Reading", key="biofeedback_btn"):
            feedback_data = {
                "heart_rate": random.randint(60, 100),
                "stress_level": random.randint(1, 10),
                "sleep_quality": random.randint(4, 10)
            }
            try:
                user_id = st.session_state.user_context.uid
                result = WellnessAPI.add_biofeedback(user_id, feedback_data)
                st.session_state.biofeedback.append(result)
                st.session_state.user_context.biofeedback = st.session_state.biofeedback
                st.success("Biofeedback recorded!")
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to record: {str(e)}")

def main_content():
    agent = get_wellness_agent()
    
    # Header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown('<p class="header-text">🌟 Your Personal Health-Wellness Coach</p>', unsafe_allow_html=True)
        st.markdown('<p class="header-subtext">Holistic health guidance tailored just for you</p>', unsafe_allow_html=True)
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3048/3048127.png", width=100)
    
    st.markdown("---")
    
    # Progress section
    st.subheader("📊 Your Health-Wellness Dashboard")
    
    if st.session_state.biofeedback:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("❤️ Heart Rate", f"{st.session_state.biofeedback[-1]['heart_rate']} bpm", 
                     help="Normal range: 60-100 bpm")
        with col2:
            st.metric("🧠 Stress Level", f"{st.session_state.biofeedback[-1]['stress_level']}/10", 
                     help="Lower is better")
        with col3:
            st.metric("😴 Sleep Quality", f"{st.session_state.biofeedback[-1]['sleep_quality']}/10", 
                     help="Higher is better")
    else:
        st.info("No biofeedback data yet. Click 'Simulate Biofeedback Reading' in the sidebar to get started.")
    
    # Mood tracking
    if hasattr(st.session_state.user_context, 'mood_history') and st.session_state.user_context.mood_history:
        st.subheader("😊 Mood Tracker")
        mood_fig = plot_mood_history(st.session_state.user_context.mood_history)
        if mood_fig:
            st.pyplot(mood_fig)
    
    # Chat interface
    st.markdown("---")
    st.subheader("💬 Chat with Your Coach")
    
    response_container = st.container()
    
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_area(
            "Your message:",
            placeholder="What would you like help with today?",
            height=100,
            key="user_input"
        )
        submit_button = st.form_submit_button(label='Send Message ➤')
    
    if submit_button and user_input:
        with st.spinner(f"{st.session_state.user_context.coach_persona.value} is thinking..."):
            try:
                output = agent.process_user_input(user_input)
                st.session_state.past.append(user_input)
                st.session_state.generated.append(output.get('response', "I didn't understand that."))
                
                if any(word in user_input.lower() for word in ["done", "completed", "finished"]):
                    st.session_state.user_context.increment_streak()
                    st.session_state.last_update = datetime.now()
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.session_state.generated.append("Sorry, I encountered an error. Please try again.")
    
    # Display conversation
    if st.session_state.generated:
        with response_container:
            for i in range(len(st.session_state.generated)):
                if i < len(st.session_state.past):
                    message(
                        st.session_state.past[i], 
                        is_user=True, 
                        key=f"user_{i}",
                        avatar_style="identicon"
                    )
                message(
                    st.session_state.generated[i], 
                    key=f"bot_{i}",
                    avatar_style="bottts"
                )

# --- Footer ---
st.markdown("---")
st.markdown("""
<p style="text-align: center; color: #4A5568;">
    Made with ❤️ by Aeyla Naseer <br>   
""", unsafe_allow_html=True)


# --- Run App ---
if __name__ == "__main__":
    try:
        initialize_session_state()
        configure_sidebar()
        main_content()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.stop()