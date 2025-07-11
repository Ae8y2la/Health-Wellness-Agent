from typing import Dict, Any
from src.guardrails import OutputModel
from src.hooks import LifecycleHooks
from src.context import UserSessionContext

class EscalationAgent:
    """Specialized agent for handling escalation to human support"""
    
    def process(self, input_text: str, context: UserSessionContext) -> Dict[str, Any]:
        """Process requests for human support"""
        try:
            LifecycleHooks.on_tool_start('EscalationAgent', context)
            
            # Log the escalation request
            context.add_progress_log('escalation', f"User requested human support: {input_text}")
            
            response = (
                f"I've noted your request for human support, {context.name}. "
                "Our team will reach out to you within 24 hours. In the meantime, "
                "is there anything else I can help with?"
            )
            
            LifecycleHooks.on_tool_end('EscalationAgent', context, {'response': response})
            
            return OutputModel(
                success=True,
                message="Escalation handled",
                data={'response': response}
            ).model_dump()
        
        except Exception as e:
            LifecycleHooks.on_error('EscalationAgent', e, context)
            return OutputModel(
                success=False,
                message=str(e),
                data={}
            ).model_dump()
