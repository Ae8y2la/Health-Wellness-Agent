from ics import Calendar, Event
from datetime import datetime, timedelta
from typing import List, Dict
from src.context import UserSessionContext
from src.hooks import LifecycleHooks

class CalendarExporter:
    """Utility class for exporting plans to calendar format"""
    
    @staticmethod
    def export_meal_plan(context: UserSessionContext) -> str:
        """Export meal plan to ICS format"""
        try:
            if not context.meal_plan:
                raise ValueError("No meal plan available to export")
            
            cal = Calendar()
            start_date = datetime.now().replace(hour=8, minute=0, second=0)
            
            for day, meals in context.meal_plan.items():
                # Add breakfast
                event = Event()
                event.name = "Breakfast"
                event.description = meals.get('breakfast', 'Check app for details')
                event.begin = start_date.replace(hour=8)
                event.duration = timedelta(minutes=30)
                cal.events.add(event)
                
                # Add lunch
                event = Event()
                event.name = "Lunch"
                event.description = meals.get('lunch', 'Check app for details')
                event.begin = start_date.replace(hour=12)
                event.duration = timedelta(minutes=45)
                cal.events.add(event)
                
                # Add dinner
                event = Event()
                event.name = "Dinner"
                event.description = meals.get('dinner', 'Check app for details')
                event.begin = start_date.replace(hour=18)
                event.duration = timedelta(minutes=60)
                cal.events.add(event)
                
                start_date += timedelta(days=1)
            
            return str(cal)
        
        except Exception as e:
            LifecycleHooks.on_error('CalendarExporter', e, context)
            raise
    
    @staticmethod
    def export_workout_plan(context: UserSessionContext) -> str:
        """Export workout plan to ICS format"""
        try:
            if not context.workout_plan:
                raise ValueError("No workout plan available to export")
            
            cal = Calendar()
            start_date = datetime.now().replace(hour=7, minute=0, second=0)
            
            # Find the next Monday
            while start_date.weekday() != 0:  # Monday is 0
                start_date += timedelta(days=1)
            
            for day, workout in context.workout_plan.items():
                if workout:  # Skip rest days
                    event = Event()
                    event.name = f"Workout: {day}"
                    event.description = "\n".join(workout)
                    event.begin = start_date.replace(hour=18 if "evening" in day.lower() else 7)
                    event.duration = timedelta(minutes=60)
                    cal.events.add(event)
                
                start_date += timedelta(days=1)
            
            return str(cal)
        
        except Exception as e:
            LifecycleHooks.on_error('CalendarExporter', e, context)
            raise