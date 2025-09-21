"""
AG-UI Event Encoder - Encodes events for transport
"""
from typing import Any, Dict, Optional
import json
from .protocol import BaseEvent

from pydantic import BaseModel, Field

class EventEncoder(BaseModel):
    """Encodes AG-UI events for transport"""
    accept: str = Field(
        default="text/event-stream", 
        description="Content type accepted by client"
    )
        
    def encode(self, event: BaseEvent) -> str:
        """Encode an event for transport"""
        if self.accept == "text/event-stream":
            return self._encode_sse(event)
        elif self.accept == "application/json":
            return self._encode_json(event)
        else:
            # Default to SSE format
            return self._encode_sse(event)
    
    def get_content_type(self) -> str:
        """Get the appropriate content type for encoded events"""
        return self.accept
    
    def _encode_sse(self, event: BaseEvent) -> str:
        """Encode event as Server-Sent Event"""
        event_dict = event.model_dump(exclude_none=True)
        return f"data: {json.dumps(event_dict)}\n\n"
    
    def _encode_json(self, event: BaseEvent) -> str:
        """Encode event as JSON"""
        event_dict = event.model_dump(exclude_none=True)
        return json.dumps(event_dict)