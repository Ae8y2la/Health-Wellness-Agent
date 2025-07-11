from typing import Callable, Any, Dict
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Corrected import
from src.context import UserSessionContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LifecycleHooks:
    """Class containing all lifecycle hook functions"""
    
    @staticmethod
    def on_tool_start(tool_name: str, user_context: UserSessionContext):
        """Triggered when a tool starts execution"""
        logger.info(f"Tool {tool_name} started for user {user_context.name}")
        user_context.add_progress_log('tool_start', f"Started {tool_name}")
    
    @staticmethod
    def on_tool_end(tool_name: str, user_context: UserSessionContext, result: Dict):
        """Triggered when a tool completes execution"""
        logger.info(f"Tool {tool_name} completed for user {user_context.name}")
        user_context.add_progress_log('tool_end', f"Completed {tool_name} with result: {result}")
    
    @staticmethod
    def on_handoff(from_tool: str, to_tool: str, user_context: UserSessionContext):
        """Triggered when control is handed between tools"""
        logger.info(f"Handoff from {from_tool} to {to_tool} for user {user_context.name}")
        user_context.handoff_logs.append(f"{from_tool} → {to_tool}")
    
    @staticmethod
    def on_error(tool_name: str, error: Exception, user_context: UserSessionContext):
        """Triggered when a tool encounters an error"""
        logger.error(f"Error in {tool_name}: {str(error)}")
        user_context.add_progress_log('error', f"Error in {tool_name}: {str(error)}")
    
    @staticmethod
    def on_goal_completed(user_context: UserSessionContext):
        """Triggered when a user completes their goal"""
        logger.info(f"User {user_context.name} completed their goal!")
        user_context.add_progress_log('goal_completed', "Congratulations! Goal completed")
    
    @staticmethod
    def register_custom_hook(hook_name: str, callback: Callable[[Any], None]):
        """Register a custom lifecycle hook"""
        setattr(LifecycleHooks, hook_name, staticmethod(callback))