from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel
from src.hooks import LifecycleHooks
from src.context import UserSessionContext
import random

class ProgressMetrics(BaseModel):
    streak: int
    goal_progress: float
    mood_trend: List[float]
    workout_consistency: float
    meal_adherence: float

class WellnessTracker:
    """Tracks and analyzes user progress metrics"""
    
    def __init__(self, context: UserSessionContext):
        self.context = context
    
    def update_progress(self) -> Dict:
        """Update all progress metrics"""
        metrics = {
            "streak": self._calculate_streak(),
            "goal_progress": self._calculate_goal_progress(),
            "mood_trend": self._analyze_mood_trend(),
            "workout_consistency": self._calculate_workout_consistency(),
            "meal_adherence": self._calculate_meal_adherence(),
            "last_updated": datetime.now().isoformat()
        }
        
        self.context.progress_logs.append({
            "type": "metrics_update",
            "data": metrics
        })
        
        return metrics
    
    def _calculate_streak(self) -> int:
        """Calculate current streak"""
        return self.context.streak_count
    
    def _calculate_goal_progress(self) -> float:
        """Calculate progress toward goal (0-1)"""
        if not self.context.goal:
            return 0.0
            
        # Simulate progress - in real app would use actual data
        days_passed = (datetime.now() - self.context.goal_start_date).days
        total_days = (self.context.goal_target_date - self.context.goal_start_date).days
        
        progress = min(0.9, days_passed / total_days)  # Cap at 90% for simulation
        return round(progress, 2)
    
    def _analyze_mood_trend(self) -> List[float]:
        """Analyze mood trends from logs"""
        mood_map = {
            "happy": 1.0,
            "excited": 0.8,
            "neutral": 0.5,
            "tired": 0.3,
            "anxious": 0.2,
            "sad": 0.0
        }
        
        moods = [
            mood_map[log["data"]["mood"]]
            for log in self.context.progress_logs
            if log.get("type") == "mood_update"
        ][-7:]  # Last 7 entries
        
        return moods or [0.5] * 3  # Default neutral trend
    
    def _calculate_workout_consistency(self) -> float:
        """Calculate workout consistency (0-1)"""
        # Simulated - would use actual workout logs
        return round(random.uniform(0.3, 0.9), 2)
    
    def _calculate_meal_adherence(self) -> float:
        """Calculate meal plan adherence (0-1)"""
        # Simulated - would use actual meal logs
        return round(random.uniform(0.4, 0.95), 2)
