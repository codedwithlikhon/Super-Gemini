"""
AG-UI Middleware - Common middleware implementations for event processing
"""
from typing import Any, Dict, List, Optional
from .protocol import AGUIEvent, AGUIMiddleware

class EventValidationMiddleware(AGUIMiddleware):
    """Validates event structure and content"""
    
    async def process_event(self, event: AGUIEvent) -> AGUIEvent:
        """Validate event before processing"""
        if not event.type:
            raise ValueError("Event type is required")
        if not event.payload:
            raise ValueError("Event payload is required")
        return event

class StateMiddleware(AGUIMiddleware):
    """Handles state synchronization"""
    
    def __init__(self):
        self.state: Dict[str, Any] = {}
    
    async def process_event(self, event: AGUIEvent) -> AGUIEvent:
        """Update state based on event"""
        if event.type.value.startswith("state."):
            self.state.update(event.payload.get("state", {}))
        event.metadata = event.metadata or {}
        event.metadata["state"] = self.state
        return event

class ContextEnrichmentMiddleware(AGUIMiddleware):
    """Enriches events with additional context"""
    
    def __init__(self):
        self.context: Dict[str, Any] = {}
    
    async def process_event(self, event: AGUIEvent) -> AGUIEvent:
        """Add context to event metadata"""
        if event.type.value == "context.update":
            self.context.update(event.payload.get("context", {}))
        event.metadata = event.metadata or {}
        event.metadata["context"] = self.context
        return event

class LoggingMiddleware(AGUIMiddleware):
    """Logs all events for debugging"""
    
    async def process_event(self, event: AGUIEvent) -> AGUIEvent:
        """Log event details"""
        print(f"AG-UI Event: {event.type.value}")
        print(f"Payload: {event.payload}")
        print(f"Timestamp: {event.timestamp}")
        print("-" * 50)
        return event

class UIGenerationMiddleware(AGUIMiddleware):
    """Handles dynamic UI generation"""
    
    async def process_event(self, event: AGUIEvent) -> AGUIEvent:
        """Process UI-related events"""
        if event.type.value.startswith("ui."):
            # Add UI component metadata
            event.metadata = event.metadata or {}
            event.metadata["ui"] = {
                "version": "1.0",
                "platform": "android",
                "components": event.payload.get("components", [])
            }
        return event

class StreamingMiddleware(AGUIMiddleware):
    """Handles streaming message chunks"""
    
    def __init__(self):
        self.buffer: Dict[str, List[str]] = {}
    
    async def process_event(self, event: AGUIEvent) -> AGUIEvent:
        """Process streaming events"""
        if event.type.value == "chat.stream":
            session_id = event.session_id
            if session_id:
                if session_id not in self.buffer:
                    self.buffer[session_id] = []
                self.buffer[session_id].append(event.payload.get("content", ""))
                event.metadata = event.metadata or {}
                event.metadata["streaming"] = {
                    "buffer_size": len(self.buffer[session_id]),
                    "complete": event.payload.get("complete", False)
                }
        return event

# Example middleware chain setup:
def create_default_middleware_chain() -> List[AGUIMiddleware]:
    """Create a default chain of middlewares"""
    return [
        EventValidationMiddleware(),
        StateMiddleware(),
        ContextEnrichmentMiddleware(),
        LoggingMiddleware(),
        UIGenerationMiddleware(),
        StreamingMiddleware()
    ]