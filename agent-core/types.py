"""
Core type definitions for the agent system.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any, Union

class MessageRole(str, Enum):
    """
    Possible roles for message senders.
    """
    DEVELOPER = "developer"
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"
    TOOL = "tool"

@dataclass
class Message:
    """
    Represents a message in the conversation.
    """
    role: MessageRole
    content: str
    id: str
    name: Optional[str] = None
    tool_calls: Optional[List["ToolCall"]] = None

@dataclass
class Tool:
    """
    Defines a tool that can be used by the agent.
    """
    name: str
    description: str
    parameters: Dict[str, Any]

@dataclass
class Context:
    """
    Contextual information for the agent.
    """
    description: str
    value: str

@dataclass
class RunAgentInput:
    """
    Input parameters for running an agent.
    """
    thread_id: str
    run_id: str
    state: Any
    messages: List[Message]
    tools: List[Tool]
    context: List[Context]
    forwarded_props: Dict[str, Any]

@dataclass
class ToolCall:
    """
    Represents a tool call made by the agent.
    """
    id: str
    tool_name: str
    arguments: Dict[str, Any]
    description: Optional[str] = None