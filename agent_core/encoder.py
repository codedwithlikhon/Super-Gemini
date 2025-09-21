import json
from typing import Union, Any
from .events import BaseEvent

class EventEncoder:
    """Encodes AG-UI protocol events for transmission."""

    def __init__(self, accept: str = None):
        """Initialize the event encoder.
        
        Args:
            accept: Optional content type accepted by the client
        """
        self.accept = accept
    
    def encode(self, event: BaseEvent) -> str:
        """Encode an event into its string representation.
        
        Args:
            event: The event to encode
            
        Returns:
            A string representation of the event in SSE format
        """
        # Convert event to JSON-compatible dict
        event_dict = event.model_dump(mode='json')

        # Convert to JSON string
        json_str = json.dumps(event_dict)

        # Format as SSE
        return f"data: {json_str}\n\n"
    
    def get_content_type(self) -> str:
        """Get the content type for the encoded events.
        
        Returns:
            The MIME type for server-sent events
        """
        return "text/event-stream"