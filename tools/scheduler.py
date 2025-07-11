from pydantic import BaseModel
from typing import Dict, List
from src.hooks import LifecycleHooks  # Changed to match your hooks.py
from src.context import UserSessionContext
import requests
import os
from datetime import datetime

class CheckinSchedule(BaseModel):
    checkin_times: List[str]
    reminders: List[str]
    prayer_times: List[str] = []

def get_prayer_times(city: str = None, country: str = None, method: int = 2) -> List[str]:
    """Fetch prayer times with environment variable fallback"""
    city = city or os.getenv("PRAYER_CITY", "Karachi")
    country = country or os.getenv("PRAYER_COUNTRY", "Pakistan")
    
    url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method={method}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        timings = response.json()["data"]["timings"]
        return [timings["Fajr"], timings["Dhuhr"], timings["Asr"], timings["Maghrib"], timings["Isha"]]
    except Exception as e:
        LifecycleHooks.on_error("PrayerTimeAPI", e)
        return []

def time_only(time_str: str) -> str:
    """Extract HH:MM from time string"""
    return time_str.strip().split()[0].strip()

async def schedule_checkins(context: UserSessionContext) -> Dict:
    """Schedule weekly check-ins based on user context"""
    LifecycleHooks.on_tool_start("CheckinSchedulerTool", context)
    
    prayer_times = []
    if context.prayer_aware:
        prayer_times_raw = get_prayer_times()
        prayer_times = [time_only(t) for t in prayer_times_raw]

    # Generate check-in times avoiding prayer times
    candidate_times = ["09:00", "12:30", "15:30", "17:00", "20:00"]
    checkin_times = [
        t for t in candidate_times 
        if not context.prayer_aware or t not in prayer_times
    ][:3]  # Max 3 check-ins
    
    result = CheckinSchedule(
        checkin_times=checkin_times,
        reminders=[f"Check-in at {t}" for t in checkin_times],
        prayer_times=prayer_times if context.prayer_aware else []
    ).model_dump()  # Changed to match your Pydantic v2 usage
    
    LifecycleHooks.on_tool_end("CheckinSchedulerTool", context, result)
    return result

