"""
AG-UI HTTP Server - Reference HTTP implementation for AG-UI protocol
"""
from typing import Any, Dict, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import asyncio
import json
from .protocol import AGUIEvent, AGUIProtocol, EventType
from .middleware import create_default_middleware_chain

app = FastAPI(title="AG-UI HTTP Server")
protocol = AGUIProtocol()

# Add default middleware chain
for middleware in create_default_middleware_chain():
    protocol.add_middleware(middleware)

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, event: AGUIEvent):
        for connection in self.active_connections:
            await connection.send_json(event.to_dict())

manager = ConnectionManager()

@app.websocket("/agui/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            event = AGUIEvent.from_dict(data)
            processed_event = await protocol.emit_event(event)
            await manager.broadcast(processed_event)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/agui/events")
async def create_event(event_data: Dict[str, Any]):
    """HTTP endpoint for sending events"""
    event = AGUIEvent.from_dict(event_data)
    processed_event = await protocol.emit_event(event)
    return processed_event.to_dict()

@app.get("/agui/stream")
async def event_stream():
    """SSE endpoint for streaming events"""
    async def generate():
        while True:
            # Example: emit a status event every 5 seconds
            event = AGUIEvent(
                type=EventType.AGENT_STATUS,
                payload={"status": "active"}
            )
            processed_event = await protocol.emit_event(event)
            yield f"data: {json.dumps(processed_event.to_dict())}\n\n"
            await asyncio.sleep(5)
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

@app.post("/agui/input")
async def process_input(input_data: Dict[str, Any]):
    """Process input through the middleware chain"""
    processed_data = await protocol.process_input(input_data)
    return processed_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)