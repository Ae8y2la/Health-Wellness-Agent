from typing import Optional, List, Dict, Literal
from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from enum import Enum

# Enums for type safety
class CoachPersona(str, Enum):
    ZENBOT = "ZenBot"
    MAX = "Max"
    LILY = "Lily"

class DietPreference(str, Enum):
    NONE = "none"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    KETO = "keto"
    PALEO = "paleo"
    MEDITERRANEAN = "mediterranean"
    GLUTEN_FREE = "gluten-free"

class MoodState(str, Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANXIOUS = "anxious"
    TIRED = "tired"
    EXCITED = "excited"
    NEUTRAL = "neutral"

# Color theme configuration
class ColorTheme(BaseModel):
    primary: str = "#4FD1C5"       # Aqua Blue
    secondary: str = "#68D391"     # Mint Green
    accent: str = "#F687B3"        # Rose Pink
    text: str = "#2D3748"          # Charcoal
    muted_text: str = "#718096"    # Slate Gray
    highlight: str = "#63B3ED"     # Neon Sky Blue
    alert: str = "#E53E3E"         # Cherry Red
    success: str = "#38A169"       # Emerald Green

# Coach persona configurations
class CoachConfig(BaseModel):
    greeting: str
    tone: str
    response_style: str
    specialties: List[str]

COACH_CONFIGS = {
    CoachPersona.ZENBOT: CoachConfig(
        greeting="Namaste! Let's find your center and balance.",
        tone="calm and spiritual",
        response_style="mindful and reflective",
        specialties=["stress reduction", "mindfulness", "holistic health"]
    ),
    CoachPersona.MAX: CoachConfig(
        greeting="Hey champ! Ready to crush your goals?",
        tone="energetic and motivational",
        response_style="direct and action-oriented",
        specialties=["performance training", "muscle building", "high-intensity workouts"]
    ),
    CoachPersona.LILY: CoachConfig(
        greeting="Hello darling! Let's make wellness delightful.",
        tone="warm and nurturing",
        response_style="detailed and educational",
        specialties=["nutrition science", "meal planning", "lifestyle habits"]
    )
}

class UserSessionContext(BaseModel):
    """Main context model for tracking user health and wellness data"""
    # User identity
    name: str = "Guest"
    uid: int = 0
    is_premium: bool = False
    
    # Health goals
    goal: Optional[dict] = None
    goal_start_date: Optional[datetime] = None
    goal_target_date: Optional[datetime] = None
    
    # Preferences
    diet_preferences: DietPreference = DietPreference.NONE
    workout_intensity: Literal["low", "medium", "high"] = "medium"
    coach_persona: CoachPersona = CoachPersona.ZENBOT
    
    # Current state
    mood: Optional[MoodState] = None
    injury_notes: Optional[str] = None
    biofeedback: Optional[Dict[str, int]] = None
    
    # Plans
    meal_plan: Optional[Dict[str, Dict[str, str]]] = None
    workout_plan: Optional[Dict[str, List[str]]] = None
    
    # Tracking
    streak_count: int = 0
    last_checkin: Optional[datetime] = None
    progress_logs: List[Dict[str, str]] = []
    handoff_logs: List[str] = []
    
    # Settings
    prayer_aware: bool = False
    dark_mode: bool = False
    color_theme: ColorTheme = ColorTheme()
    notification_preferences: Dict[str, bool] = {
        "reminders": True,
        "progress_updates": True,
        "motivational": True
    }
    
    # System
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    model_config = ConfigDict(use_enum_values=True)
    
    @field_validator('coach_persona', mode='before')
    def validate_coach_persona(cls, v):
        if isinstance(v, str):
            if v in CoachPersona._value2member_map_:
                return v
            lower_map = {k.lower(): k for k in CoachPersona._value2member_map_}
            if v.lower() in lower_map:
                return lower_map[v.lower()]
            raise ValueError(f"Invalid coach persona. Must be one of: {list(CoachPersona._value2member_map_.keys())}")
        return v
    
    @field_validator('diet_preferences', mode='before')
    def validate_diet_preferences(cls, v):
        if isinstance(v, str):
            v = v.lower().replace(" ", "-")
            if v not in DietPreference._value2member_map_:
                raise ValueError(f"Invalid diet preference. Must be one of: {list(DietPreference._value2member_map_.keys())}")
        return v
    
    def update_theme(self, theme: Dict[str, str]):
        """Update the color theme"""
        self.color_theme = ColorTheme(**theme)
        self.updated_at = datetime.now()
    
    def switch_coach(self, persona: CoachPersona):
        """Switch to a different coach persona"""
        self.coach_persona = persona
        self.updated_at = datetime.now()
        return COACH_CONFIGS[persona].greeting
    
    def get_coach_config(self) -> CoachConfig:
        """Get the current coach's configuration"""
        return COACH_CONFIGS[self.coach_persona]
    
    def add_progress_log(self, log_type: str, message: str):
        """Add a new progress log entry"""
        self.progress_logs.append({
            'timestamp': datetime.now().isoformat(),
            'type': log_type,
            'message': message
        })
        self.updated_at = datetime.now()
    
    def increment_streak(self):
        """Increment the user's streak counter"""
        self.streak_count += 1
        self.add_progress_log('streak', f'Streak increased to {self.streak_count}')
    
    def reset_streak(self):
        """Reset the user's streak counter"""
        self.streak_count = 0
        self.add_progress_log('streak', 'Streak reset to 0')
    
    def to_dict(self) -> Dict:
        """Convert context to dictionary"""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create context from dictionary"""
        return cls(**data)

# Default configurations
DEFAULT_THEMES = {
    "medical": ColorTheme(),
    "vibrant": ColorTheme(
        primary="#8A2BE2",
        secondary="#FF7F50",
        accent="#FFD700",
        text="#000000",
        muted_text="#696969",
        highlight="#00BFFF",
        alert="#FF4500",
        success="#32CD32"
    ),
    "pastel": ColorTheme(
        primary="#A2D2FF",
        secondary="#BDE0FE",
        accent="#FFC8DD",
        text="#2F3E46",
        muted_text="#52796F",
        highlight="#CDB4DB",
        alert="#FFAFCC",
        success="#A7C4BC"
    )
}