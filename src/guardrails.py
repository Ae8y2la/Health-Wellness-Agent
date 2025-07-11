from typing import Dict, Any
from pydantic import BaseModel, ValidationError
import re
import sys
from pathlib import Path

# Add project root to path if needed
sys.path.insert(0, str(Path(__file__).parent.parent))

class InputValidator:
    """Class for validating user inputs and sanitizing outputs"""
    
    @staticmethod
    def validate_goal_input(goal_text: str) -> Dict[str, Any]:
        """Validate that goal input follows expected structure"""
        if not goal_text:
            raise ValueError("Goal text cannot be empty")
        
        pattern = r"(lose|gain)\s+(\d+)\s*(kg|lbs|pounds|kilograms)\s*(?:in|over|for)\s*(\d+)\s*(weeks|months|days)"
        match = re.search(pattern, goal_text.lower())
        
        if not match:
            raise ValueError("Goal must be in format like 'lose 5kg in 2 months'")
        
        direction, amount, unit, duration, time_unit = match.groups()
        return {
            'direction': direction,
            'amount': float(amount),
            'unit': unit,
            'duration': int(duration),
            'time_unit': time_unit
        }
    
    @staticmethod
    def validate_diet_preferences(prefs: str) -> str:
        """Validate diet preferences input"""
        allowed = ['vegetarian', 'vegan', 'keto', 'paleo', 'mediterranean', 'gluten-free', 'none']
        if prefs.lower() not in allowed:
            raise ValueError(f"Diet preference must be one of: {', '.join(allowed)}")
        return prefs.lower()
    
    @staticmethod
    def sanitize_output(output: Dict) -> Dict:
        """Sanitize output to ensure clean JSON"""
        if not isinstance(output, dict):
            raise ValueError("Output must be a dictionary")
        
        # Remove any None values or empty strings
        return {k: v for k, v in output.items() if v is not None and v != ''}

class OutputModel(BaseModel):
    """Base model for validating tool outputs"""
    success: bool
    message: str
    data: Dict[str, Any]