"""
AG-UI Transport Layer - Implementations for different transport mechanisms
"""
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, Optional
import asyncio
import aiohttp
import logging
from pydantic import BaseModel
from .protocol import BaseEvent, EventType
from .encoder import EventEncoder

logger = logging.getLogger(__name__)

class AGUITransport(BaseModel, ABC):
    """Abstract base class for AG-UI transport implementations"""
    
    class Config:
        arbitrary_types_allowed = True
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish transport connection"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Close transport connection"""
        pass
    
    @abstractmethod
    async def send_event(self, event: BaseEvent) -> bool:
        """Send an event through the transport"""
        pass
    
    @abstractmethod
    async def receive_event(self) -> Optional[BaseEvent]:
        """Receive an event from the transport"""
        pass

class SSETransport(AGUITransport):
    """Server-Sent Events (SSE) transport implementation"""
    
    url: str
    encoder: EventEncoder = EventEncoder()
    session: Optional[aiohttp.ClientSession] = None
    response: Optional[aiohttp.ClientResponse] = None
        
    async def connect(self) -> bool:
        """Connect to SSE endpoint"""
        try:
            self.session = aiohttp.ClientSession()
            self.response = await self.session.get(
                self.url,
                headers={"Accept": "text/event-stream"}
            )
            return True
        except Exception as e:
            logger.error(f"SSE connection error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Close SSE connection"""
        try:
            if self.response:
                await self.response.close()
            if self.session:
                await self.session.close()
            return True
        except Exception as e:
            logger.error(f"SSE disconnection error: {e}")
            return False
    
    async def send_event(self, event: BaseEvent) -> bool:
        """SSE is one-way, sending not supported"""
        raise NotImplementedError("SSE transport is receive-only")
    
    async def receive_event(self) -> Optional[BaseEvent]:
        """Receive SSE event"""
        if not self.response:
            return None
            
        try:
            async for line in self.response.content:
                if line.startswith(b"data: "):
                    data = line[6:].decode("utf-8")
                    return BaseEvent.model_validate_json(data)
        except Exception as e:
            logger.error(f"SSE receive error: {e}")
            return None

class WebSocketTransport(AGUITransport):
    """WebSocket transport implementation"""
    
    url: str
    encoder: EventEncoder = EventEncoder(accept="application/json")
    ws: Optional[aiohttp.ClientWebSocketResponse] = None
    session: Optional[aiohttp.ClientSession] = None
        
    async def connect(self) -> bool:
        """Connect to WebSocket endpoint"""
        try:
            self.session = aiohttp.ClientSession()
            self.ws = await self.session.ws_connect(self.url)
            return True
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Close WebSocket connection"""
        try:
            if self.ws:
                await self.ws.close()
            if self.session:
                await self.session.close()
            return True
        except Exception as e:
            logger.error(f"WebSocket disconnection error: {e}")
            return False
    
    async def send_event(self, event: BaseEvent) -> bool:
        """Send event through WebSocket"""
        if not self.ws:
            return False
            
        try:
            await self.ws.send_json(event.model_dump(exclude_none=True))
            return True
        except Exception as e:
            logger.error(f"WebSocket send error: {e}")
            return False
    
    async def receive_event(self) -> Optional[BaseEvent]:
        """Receive event from WebSocket"""
        if not self.ws:
            return None
            
        try:
            msg = await self.ws.receive_json()
            return BaseEvent.model_validate(msg)
        except Exception as e:
            logger.error(f"WebSocket receive error: {e}")
            return None

class HTTPTransport(AGUITransport):
    """HTTP transport implementation with webhooks"""
    
    endpoint_url: str
    webhook_url: Optional[str] = None
    encoder: EventEncoder = EventEncoder(accept="application/json")
    session: Optional[aiohttp.ClientSession] = None
        
    async def connect(self) -> bool:
        """Initialize HTTP session"""
        try:
            self.session = aiohttp.ClientSession()
            return True
        except Exception as e:
            logger.error(f"HTTP session creation error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Close HTTP session"""
        try:
            if self.session:
                await self.session.close()
            return True
        except Exception as e:
            logger.error(f"HTTP session close error: {e}")
            return False
    
    async def send_event(self, event: BaseEvent) -> bool:
        """Send event via HTTP POST"""
        if not self.session:
            return False
            
        try:
            async with self.session.post(
                self.endpoint_url,
                json=event.model_dump(exclude_none=True)
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"HTTP send error: {e}")
            return False
    
    async def receive_event(self) -> Optional[BaseEvent]:
        """HTTP transport requires webhook endpoint for receiving"""
        raise NotImplementedError(
            "HTTP transport requires webhook endpoint for receiving events"
        )

async def test_websocket():
    """Test WebSocket transport functionality"""
    transport = WebSocketTransport(url="ws://localhost:8080/agui")
    
    try:
        await transport.connect()
        event = BaseEvent(
            type=EventType.TEXT_MESSAGE_START,
            message_id="test_123",
            role="assistant"
        )
        await transport.send_event(event)
    finally:
        await transport.disconnect()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_websocket())