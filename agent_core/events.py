from enum import Enum, auto
from typing import Any, Optional, List, Literal
from pydantic import BaseModel

class EventType(str, Enum):
    """Event types in the AG-UI protocol."""
    TEXT_MESSAGE_START = "TEXT_MESSAGE_START"
    TEXT_MESSAGE_CONTENT = "TEXT_MESSAGE_CONTENT" 
    TEXT_MESSAGE_END = "TEXT_MESSAGE_END"
    TOOL_CALL_START = "TOOL_CALL_START"
    TOOL_CALL_ARGS = "TOOL_CALL_ARGS"
    TOOL_CALL_END = "TOOL_CALL_END"
    TOOL_CALL_RESULT = "TOOL_CALL_RESULT"
    STATE_SNAPSHOT = "STATE_SNAPSHOT"
    STATE_DELTA = "STATE_DELTA"
    MESSAGES_SNAPSHOT = "MESSAGES_SNAPSHOT"
    RAW = "RAW"
    CUSTOM = "CUSTOM"
    RUN_STARTED = "RUN_STARTED"
    RUN_FINISHED = "RUN_FINISHED" 
    RUN_ERROR = "RUN_ERROR"
    STEP_STARTED = "STEP_STARTED"
    STEP_FINISHED = "STEP_FINISHED"

class BaseEvent(BaseModel):
    """Base class for all AG-UI protocol events."""
    type: EventType
    timestamp: Optional[int] = None
    raw_event: Optional[Any] = None

class RunStartedEvent(BaseEvent):
    """Event emitted when an agent run begins."""
    type: Literal[EventType.RUN_STARTED]
    thread_id: str
    run_id: str

class RunFinishedEvent(BaseEvent):
    """Event emitted when an agent run completes successfully."""
    type: Literal[EventType.RUN_FINISHED]
    thread_id: str
    run_id: str
    result: Optional[Any] = None

class RunErrorEvent(BaseEvent):
    """Event emitted when an agent run encounters an error."""
    type: Literal[EventType.RUN_ERROR]
    message: str
    code: Optional[str] = None

class StepStartedEvent(BaseEvent):
    """Event emitted when a step within an agent run begins."""
    type: Literal[EventType.STEP_STARTED]
    step_name: str

class StepFinishedEvent(BaseEvent):
    """Event emitted when a step within an agent run completes."""
    type: Literal[EventType.STEP_FINISHED]
    step_name: str

class TextMessageStartEvent(BaseEvent):
    """Event emitted when text generation begins."""
    type: Literal[EventType.TEXT_MESSAGE_START]
    message_id: str
    role: Literal["assistant"]

class TextMessageContentEvent(BaseEvent):
    """Event emitted for each chunk of generated text content."""
    type: Literal[EventType.TEXT_MESSAGE_CONTENT]
    message_id: str
    delta: str  # Non-empty string
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.delta:
            raise ValueError("delta must not be empty")

class TextMessageEndEvent(BaseEvent):
    """Event emitted when text generation completes."""
    type: Literal[EventType.TEXT_MESSAGE_END]
    message_id: str

class ToolCallStartEvent(BaseEvent):
    """Event emitted when a tool call begins."""
    type: Literal[EventType.TOOL_CALL_START]
    tool_call_id: str
    tool_call_name: str
    parent_message_id: Optional[str] = None

class ToolCallArgsEvent(BaseEvent):
    """Event emitted with tool call argument data."""
    type: Literal[EventType.TOOL_CALL_ARGS]
    tool_call_id: str
    delta: str

class ToolCallEndEvent(BaseEvent):
    """Event emitted when a tool call completes."""
    type: Literal[EventType.TOOL_CALL_END]
    tool_call_id: str

class ToolCallResultEvent(BaseEvent):
    """Event emitted with tool call results."""
    type: Literal[EventType.TOOL_CALL_RESULT]
    message_id: str
    tool_call_id: str
    content: str
    role: Optional[Literal["tool"]] = None

class StateSnapshotEvent(BaseEvent):
    """Event providing complete agent state."""
    type: Literal[EventType.STATE_SNAPSHOT]
    snapshot: Any  # Complete state snapshot

class StateDeltaEvent(BaseEvent):
    """Event providing partial state update using JSON Patch."""
    type: Literal[EventType.STATE_DELTA]
    delta: List[Any]  # JSON Patch operations (RFC 6902)

class MessagesSnapshotEvent(BaseEvent):
    """Event providing complete message history."""
    type: Literal[EventType.MESSAGES_SNAPSHOT]
    messages: List[Any]  # List[Message]

class RawEvent(BaseEvent):
    """Event for passing through external system events."""
    type: Literal[EventType.RAW]
    event: Any
    source: Optional[str] = None

class CustomEvent(BaseEvent):
    """Event for application-specific custom events."""
    type: Literal[EventType.CUSTOM]
    name: str
    value: Any