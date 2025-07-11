from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional
import uuid
from enum import Enum
import uvicorn

app = FastAPI(
    title="Wellness Coach API",
    description="Backend for Health & Wellness application",
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- Enums ---
class DietType(str, Enum):
    VEGETARIAN = "vegetarian"
    KETO = "keto"
    BALANCED = "balanced"
    VEGAN = "vegan"
    PALEO = "paleo"

class GoalType(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    GENERAL = "general"

class CoachPreference(str, Enum):
    ZENBOT = "ZenBot"
    FITNESS = "FitnessCoach"
    NUTRITION = "NutritionExpert"

# --- Database ---
db = {
    "users": {},
    "goals": {},
    "meal_plans": {},
    "workouts": {},
    "biofeedback": {}
}

# --- Models ---
class User(BaseModel):
    name: str
    email: str
    is_premium: bool = False
    coach_preference: CoachPreference = CoachPreference.ZENBOT
    diet_preference: DietType = DietType.BALANCED

class Goal(BaseModel):
    user_id: str
    description: str
    target: str
    timeframe: str

class MealPlan(BaseModel):
    user_id: str
    plan: Dict[str, List[str]]
    diet_type: DietType = DietType.BALANCED

class WorkoutPlan(BaseModel):
    user_id: str
    exercises: Dict[str, List[str]]
    goal_type: GoalType = GoalType.GENERAL

class Biofeedback(BaseModel):
    user_id: str
    heart_rate: int
    stress_level: int
    sleep_quality: int
    timestamp: datetime = datetime.now()

# --- Helper Functions ---
def analyze_goal(text: str) -> Dict[str, str]:
    text = text.lower()
    if "lose" in text and ("weight" in text or "fat" in text):
        return {
            "type": GoalType.WEIGHT_LOSS,
            "recommendation": "Aim for 1-2 lbs per week",
            "plan": "Combine cardio and strength training"
        }
    elif "muscle" in text or "gain" in text:
        return {
            "type": GoalType.MUSCLE_GAIN,
            "recommendation": "Focus on progressive overload",
            "plan": "3-5 strength sessions per week"
        }
    return {
        "type": GoalType.GENERAL,
        "recommendation": "Stay consistent with healthy habits",
        "plan": "Balance activity and recovery"
    }

def generate_meal_plan(diet: DietType = DietType.BALANCED) -> Dict[str, List[str]]:
    plans = {
        DietType.VEGETARIAN: {
            "Monday": ["Oatmeal with berries", "Chickpea salad", "Lentil curry"],
            "Tuesday": ["Smoothie bowl", "Quinoa salad", "Vegetable stir-fry"]
        },
        DietType.KETO: {
            "Monday": ["Eggs with avocado", "Chicken Caesar salad", "Salmon with asparagus"],
            "Tuesday": ["Bulletproof coffee", "Beef stir-fry", "Cheese omelet"]
        },
        DietType.BALANCED: {
            "Monday": ["Whole grain toast", "Grilled chicken", "Fish with rice"],
            "Tuesday": ["Yogurt with nuts", "Turkey sandwich", "Pasta primavera"]
        }
    }
    return plans.get(diet, plans[DietType.BALANCED])

def generate_workout_plan(goal_type: GoalType = GoalType.GENERAL) -> Dict[str, List[str]]:
    plans = {
        GoalType.WEIGHT_LOSS: {
            "Monday": ["30 min cardio", "Bodyweight circuit"],
            "Wednesday": ["HIIT training", "Core exercises"],
            "Friday": ["Jogging", "Yoga"]
        },
        GoalType.MUSCLE_GAIN: {
            "Monday": ["Chest & Triceps", "Strength training"],
            "Wednesday": ["Back & Biceps", "Deadlifts"],
            "Friday": ["Leg day", "Squats"]
        },
        GoalType.GENERAL: {
            "Monday": ["30 min walk", "Stretching"],
            "Wednesday": ["Yoga session"],
            "Friday": ["Swimming"]
        }
    }
    return plans.get(goal_type, plans[GoalType.GENERAL])

# --- API Endpoints ---
@app.get("/")
def root():
    return {
        "message": "Wellness Coach API",
        "endpoints": {
            "users": "/users",
            "goals": "/goals",
            "meal_plans": "/meal-plans",
            "workouts": "/workouts",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0"
    }

@app.post("/users/", response_model=Dict)
def create_user(user: User):
    user_id = str(uuid.uuid4())
    user_data = user.dict()
    user_data.update({
        "id": user_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    })
    db["users"][user_id] = user_data
    return {"status": "success", "user_id": user_id, **user_data}

@app.get("/users/{user_id}", response_model=Dict)
def get_user(user_id: str):
    try:
        uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    if user_id not in db["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    return db["users"][user_id]

@app.post("/goals/", response_model=Dict)
def create_goal(goal: Goal):
    goal_id = str(uuid.uuid4())
    goal_data = goal.dict()
    analysis = analyze_goal(goal.description)
    goal_data.update({
        "id": goal_id,
        "created_at": datetime.now().isoformat(),
        **analysis
    })
    db["goals"][goal_id] = goal_data
    return {"status": "success", "goal_id": goal_id, **goal_data}

@app.get("/goals/user/{user_id}", response_model=List[Dict])
def get_user_goals(user_id: str):
    try:
        uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    return [g for g in db["goals"].values() if g["user_id"] == user_id]

@app.post("/meal-plans/", response_model=Dict)
def create_meal_plan(meal_plan: MealPlan):
    plan_id = str(uuid.uuid4())
    plan_data = meal_plan.dict()
    plan_data["id"] = plan_id
    db["meal_plans"][plan_id] = plan_data
    return {"status": "success", "plan_id": plan_id, **plan_data}

@app.get("/meal-plans/generate", response_model=Dict)
def generate_meal_plan_endpoint(diet: DietType = DietType.BALANCED):
    return {
        "status": "success",
        "diet": diet,
        "plan": generate_meal_plan(diet)
    }

@app.post("/workouts/", response_model=Dict)
def create_workout_plan(workout: WorkoutPlan):
    workout_id = str(uuid.uuid4())
    workout_data = workout.dict()
    workout_data["id"] = workout_id
    db["workouts"][workout_id] = workout_data
    return {"status": "success", "workout_id": workout_id, **workout_data}

@app.get("/workouts/generate", response_model=Dict)
def generate_workout_plan_endpoint(goal_type: GoalType = GoalType.GENERAL):
    return {
        "status": "success",
        "goal_type": goal_type,
        "plan": generate_workout_plan(goal_type)
    }

@app.post("/biofeedback/", response_model=Dict)
def add_biofeedback(data: Dict):
    if "user_id" not in data:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    try:
        uuid.UUID(data["user_id"])
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    feedback_id = str(uuid.uuid4())
    data["id"] = feedback_id
    data["timestamp"] = datetime.now().isoformat()
    db["biofeedback"][feedback_id] = data
    return {"status": "success", "feedback_id": feedback_id, **data}

@app.get("/biofeedback/user/{user_id}", response_model=List[Dict])
def get_user_biofeedback(user_id: str):
    try:
        uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    return [fb for fb in db["biofeedback"].values() if fb["user_id"] == user_id]

@app.get("/wellness-tip", response_model=Dict)
def get_wellness_tip():
    tips = [
        "Stay hydrated throughout the day",
        "Get 7-8 hours of quality sleep",
        "Take regular breaks from sitting",
        "Practice mindful breathing exercises"
    ]
    return {
        "status": "success",
        "tip": tips[datetime.now().day % len(tips)]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)