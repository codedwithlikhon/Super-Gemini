"""
AG-UI Connector - Default connector for integrating AG-UI with agent backends
"""
from typing import Any, Dict, Optional
import asyncio
from .protocol import AGUIEvent, AGUIProtocol, EventType
from .transport import AGUITransport, WebSocketTransport
from .middleware import create_default_middleware_chain

class AGUIConnector:
    """Default connector for AG-UI integration"""
    
    def __init__(
        self,
        transport: Optional[AGUITransport] = None,
        protocol: Optional[AGUIProtocol] = None
    ):
        self.transport = transport or WebSocketTransport("ws://localhost:8000/agui/ws")
        self.protocol = protocol or AGUIProtocol()
        
        # Add default middleware if not provided
        if not self.protocol.middlewares:
            for middleware in create_default_middleware_chain():
                self.protocol.add_middleware(middleware)
    
    async def connect(self) -> bool:
        """Connect to the transport"""
        return await self.transport.connect()
    
    async def disconnect(self) -> bool:
        """Disconnect from the transport"""
        return await self.transport.disconnect()
    
    async def send_message(
        self,
        content: str,
        role: str = "agent",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send a chat message"""
        event = AGUIEvent(
            type=EventType.CHAT_MESSAGE,
            payload={"content": content, "role": role},
            metadata=metadata
        )
        processed_event = await self.protocol.emit_event(event)
        return await self.transport.send_event(processed_event)
    
    async def start_stream(
        self,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Start a streaming session"""
        event = AGUIEvent(
            type=EventType.CHAT_START,
            payload={"streaming": True},
            session_id=session_id,
            metadata=metadata
        )
        processed_event = await self.protocol.emit_event(event)
        return await self.transport.send_event(processed_event)
    
    async def stream_chunk(
        self,
        content: str,
        session_id: str,
        is_complete: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send a streaming chunk"""
        event = AGUIEvent(
            type=EventType.CHAT_STREAM,
            payload={
                "content": content,
                "complete": is_complete
            },
            session_id=session_id,
            metadata=metadata
        )
        processed_event = await self.protocol.emit_event(event)
        return await self.transport.send_event(processed_event)
    
    async def update_context(
        self,
        context: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update context information"""
        event = AGUIEvent(
            type=EventType.CONTEXT_UPDATE,
            payload={"context": context},
            metadata=metadata
        )
        processed_event = await self.protocol.emit_event(event)
        return await self.transport.send_event(processed_event)
    
    async def render_ui(
        self,
        components: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Render UI components"""
        event = AGUIEvent(
            type=EventType.UI_RENDER,
            payload={"components": components},
            metadata=metadata
        )
        processed_event = await self.protocol.emit_event(event)
        return await self.transport.send_event(processed_event)
    
    async def handle_human_feedback(
        self,
        feedback: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Process human feedback"""
        event = AGUIEvent(
            type=EventType.HUMAN_FEEDBACK,
            payload={"feedback": feedback},
            metadata=metadata
        )
        processed_event = await self.protocol.emit_event(event)
        return await self.transport.send_event(processed_event)

# Example usage:
async def main():
    connector = AGUIConnector()
    
    # Connect to transport
    await connector.connect()
    
    try:
        # Start a streaming session
        session_id = "test-session"
        await connector.start_stream(session_id)
        
        # Send some streaming chunks
        chunks = ["Hello", " from", " AG-UI", "!"]
        for i, chunk in enumerate(chunks):
            is_last = i == len(chunks) - 1
            await connector.stream_chunk(chunk, session_id, is_last)
            await asyncio.sleep(0.5)
        
        # Update context
        await connector.update_context({
            "user_id": "test-user",
            "timestamp": "2025-09-21T12:00:00Z"
        })
        
        # Render some UI
        await connector.render_ui([
            {
                "type": "button",
                "text": "Click me!",
                "action": "custom_action"
            }
        ])
        
    finally:
        # Clean up
        await connector.disconnect()

if __name__ == "__main__":
    asyncio.run(main())