"""
AG-UI Core - Event types and base protocol implementation
"""
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Literal, TypeVar, Generic
from datetime import datetime
from pydantic import BaseModel, Field, model_validator

class EventType(str, Enum):
    """Standard AG-UI event types"""
    # Text Message Events
    TEXT_MESSAGE_START = "TEXT_MESSAGE_START"
    TEXT_MESSAGE_CONTENT = "TEXT_MESSAGE_CONTENT"
    TEXT_MESSAGE_END = "TEXT_MESSAGE_END"
    
    # Tool Events
    TOOL_CALL_START = "TOOL_CALL_START"
    TOOL_CALL_ARGS = "TOOL_CALL_ARGS"
    TOOL_CALL_END = "TOOL_CALL_END"
    TOOL_CALL_RESULT = "TOOL_CALL_RESULT"
    
    # State Events
    STATE_SNAPSHOT = "STATE_SNAPSHOT"
    STATE_DELTA = "STATE_DELTA"
    MESSAGES_SNAPSHOT = "MESSAGES_SNAPSHOT"
    
    # Run Lifecycle Events
    RUN_STARTED = "RUN_STARTED"
    RUN_FINISHED = "RUN_FINISHED"
    RUN_ERROR = "RUN_ERROR"
    STEP_STARTED = "STEP_STARTED"
    STEP_FINISHED = "STEP_FINISHED"
    
    # Special Events
    RAW = "RAW"
    CUSTOM = "CUSTOM"

class BaseEvent(BaseModel):
    """Base class for all AG-UI events"""
    type: EventType
    timestamp: Optional[int] = Field(default_factory=lambda: int(datetime.now().timestamp()))
    raw_event: Optional[Any] = None

class TextMessageStartEvent(BaseEvent):
    """Signals the start of a text message"""
    type: Literal[EventType.TEXT_MESSAGE_START]
    message_id: str
    role: Literal["assistant"]

class TextMessageContentEvent(BaseEvent):
    """Represents a chunk of content in a streaming text message"""
    type: Literal[EventType.TEXT_MESSAGE_CONTENT]
    message_id: str
    delta: str  # Non-empty string

    @model_validator(mode='after')
    def validate_delta(self):
        """Validate that delta is not empty"""
        if len(self.delta) == 0:
            raise ValueError("Delta must not be an empty string")
        return self

class TextMessageEndEvent(BaseEvent):
    """Signals the end of a text message"""
    type: Literal[EventType.TEXT_MESSAGE_END]
    message_id: str

class ToolCallStartEvent(BaseEvent):
    """Signals the start of a tool call"""
    type: Literal[EventType.TOOL_CALL_START]
    tool_call_id: str
    tool_call_name: str
    parent_message_id: Optional[str] = None

class ToolCallArgsEvent(BaseEvent):
    """Represents a chunk of argument data for a tool call"""
    type: Literal[EventType.TOOL_CALL_ARGS]
    tool_call_id: str
    delta: str

class ToolCallEndEvent(BaseEvent):
    """Signals the end of a tool call"""
    type: Literal[EventType.TOOL_CALL_END]
    tool_call_id: str

class ToolCallResultEvent(BaseEvent):
    """Provides the result of a tool call execution"""
    type: Literal[EventType.TOOL_CALL_RESULT]
    message_id: str
    tool_call_id: str
    content: str
    role: Optional[Literal["tool"]] = None

class StateSnapshotEvent(BaseEvent):
    """Provides a complete snapshot of an agent's state"""
    type: Literal[EventType.STATE_SNAPSHOT]
    snapshot: Dict[str, Any]  # Complete state snapshot

class StateDeltaEvent(BaseEvent):
    """Provides a partial update to an agent's state using JSON Patch"""
    type: Literal[EventType.STATE_DELTA]
    delta: List[Dict[str, Any]]  # JSON Patch operations

class MessagesSnapshotEvent(BaseEvent):
    """Provides a snapshot of all messages in a conversation"""
    type: Literal[EventType.MESSAGES_SNAPSHOT]
    messages: List[Dict[str, Any]]  # Array of message objects

class RunStartedEvent(BaseEvent):
    """Signals the start of an agent run"""
    type: Literal[EventType.RUN_STARTED]
    thread_id: str
    run_id: str

class RunFinishedEvent(BaseEvent):
    """Signals the successful completion of an agent run"""
    type: Literal[EventType.RUN_FINISHED]
    thread_id: str
    run_id: str
    result: Optional[Any] = None

class RunErrorEvent(BaseEvent):
    """Signals an error during an agent run"""
    type: Literal[EventType.RUN_ERROR]
    message: str
    code: Optional[str] = None

class StepStartedEvent(BaseEvent):
    """Signals the start of a step within an agent run"""
    type: Literal[EventType.STEP_STARTED]
    step_name: str

class StepFinishedEvent(BaseEvent):
    """Signals the completion of a step within an agent run"""
    type: Literal[EventType.STEP_FINISHED]
    step_name: str

class RawEvent(BaseEvent):
    """Used to pass through events from external systems"""
    type: Literal[EventType.RAW]
    event: Any
    source: Optional[str] = None

class CustomEvent(BaseEvent):
    """Used for application-specific custom events"""
    type: Literal[EventType.CUSTOM]
    name: str
    value: Any

    def to_json(self) -> str:
        """Convert event to JSON string"""
        return self.model_dump_json()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEvent':
        """Create appropriate event type from dictionary"""
        event_type = EventType(data["type"])
        event_class = _EVENT_TYPE_MAP.get(event_type, RawEvent)
        return event_class.model_validate(data)

class AGUIMiddleware(BaseModel):
    """Base middleware class for AG-UI protocol"""
    class Config:
        arbitrary_types_allowed = True
    
    async def process_event(self, event: BaseEvent) -> BaseEvent:
        """Process an event through the middleware chain"""
        return event
    
    async def process_input(self, input_data: RunAgentInput) -> RunAgentInput:
        """Process input data through the middleware chain"""
        return input_data

class AGUIProtocol(BaseModel):
    """Main AG-UI protocol implementation"""
    middlewares: List[AGUIMiddleware] = Field(default_factory=list)
    state: Dict[str, Any] = Field(default_factory=dict)
    messages: List[Dict[str, Any]] = Field(default_factory=list)

    def add_middleware(self, middleware: AGUIMiddleware):
        """Add a middleware to the protocol chain"""
        self.middlewares.append(middleware)

    async def emit_event(self, event: BaseEvent) -> BaseEvent:
        """Emit an event through the middleware chain"""
        processed_event = event
        
        # Update internal state based on event type
        if isinstance(event, StateSnapshotEvent):
            self.state = event.snapshot
        elif isinstance(event, StateDeltaEvent):
            self._apply_state_delta(event.delta)
        elif isinstance(event, MessagesSnapshotEvent):
            self.messages = event.messages
            
        # Process through middleware chain
        for middleware in self.middlewares:
            processed_event = await middleware.process_event(processed_event)
            
        return processed_event
    
    async def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input through the middleware chain"""
        processed_data = input_data
        for middleware in self.middlewares:
            processed_data = await middleware.process_input(processed_data)
        return processed_data
    
    def _apply_state_delta(self, delta: List[Dict[str, Any]]):
        """Apply JSON Patch operations to the current state"""
        import jsonpatch
        patch = jsonpatch.JsonPatch(delta)
        self.state = patch.apply(self.state)

# Map event types to their corresponding classes
_EVENT_TYPE_MAP = {
    EventType.TEXT_MESSAGE_START: TextMessageStartEvent,
    EventType.TEXT_MESSAGE_CONTENT: TextMessageContentEvent,
    EventType.TEXT_MESSAGE_END: TextMessageEndEvent,
    EventType.TOOL_CALL_START: ToolCallStartEvent,
    EventType.TOOL_CALL_ARGS: ToolCallArgsEvent,
    EventType.TOOL_CALL_END: ToolCallEndEvent,
    EventType.TOOL_CALL_RESULT: ToolCallResultEvent,
    EventType.STATE_SNAPSHOT: StateSnapshotEvent,
    EventType.STATE_DELTA: StateDeltaEvent,
    EventType.MESSAGES_SNAPSHOT: MessagesSnapshotEvent,
    EventType.RUN_STARTED: RunStartedEvent,
    EventType.RUN_FINISHED: RunFinishedEvent,
    EventType.RUN_ERROR: RunErrorEvent,
    EventType.STEP_STARTED: StepStartedEvent,
    EventType.STEP_FINISHED: StepFinishedEvent,
    EventType.RAW: RawEvent,
    EventType.CUSTOM: CustomEvent,
}

# Example usage:
if __name__ == "__main__":
    # Create a text message start event
    event = TextMessageStartEvent(
        type=EventType.TEXT_MESSAGE_START,
        message_id="msg_123",
        role="assistant"
    )
    
    # Print event as JSON
    print(event.to_json())