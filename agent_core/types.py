from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field

# Role types
Role = Literal["developer", "system", "assistant", "user", "tool"]

class BaseMessage(BaseModel):
    """Base class for all message types."""
    id: str
    role: Role
    name: Optional[str] = None

class DeveloperMessage(BaseMessage):
    """Message from a developer."""
    role: Literal["developer"]
    content: str

class SystemMessage(BaseMessage):
    """System message providing instructions or context."""
    role: Literal["system"]
    content: str

class FunctionCall(BaseModel):
    """Function call details in a tool call."""
    name: str
    arguments: str  # JSON-encoded string of arguments

class ToolCall(BaseModel):
    """Tool call made by an agent."""
    id: str
    type: Literal["function"]
    function: FunctionCall

class AssistantMessage(BaseMessage):
    """Message from an AI assistant."""
    role: Literal["assistant"]
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None

class UserMessage(BaseMessage):
    """Message from a user."""
    role: Literal["user"]
    content: str

class ToolMessage(BaseMessage):
    """Message containing tool call results."""
    role: Literal["tool"]
    content: str
    tool_call_id: str
    error: Optional[str] = None

Message = Union[
    DeveloperMessage,
    SystemMessage, 
    AssistantMessage,
    UserMessage,
    ToolMessage
]

class Context(BaseModel):
    """Context information provided to an agent."""
    description: str
    value: str

class Tool(BaseModel):
    """Tool definition that can be called by an agent."""
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema

class RunAgentInput(BaseModel):
    """Input parameters for running an agent."""
    thread_id: str
    run_id: str
    state: Any
    messages: List[Message]
    tools: List[Tool]
    context: List[Context]
    forwarded_props: Any

# Type aliases
State = Any  # Agent state can be any JSON-serializable data