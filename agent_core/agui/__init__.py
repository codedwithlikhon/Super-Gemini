"""
AG-UI __init__ module
"""
from .protocol import AGUIEvent, AGUIProtocol, EventType
from .transport import AGUITransport, WebSocketTransport, SSETransport, HTTPTransport
from .middleware import (
    AGUIMiddleware,
    EventValidationMiddleware,
    StateMiddleware,
    ContextEnrichmentMiddleware,
    LoggingMiddleware,
    UIGenerationMiddleware,
    StreamingMiddleware,
    create_default_middleware_chain
)
from .connector import AGUIConnector
from .server import app as agui_server

__version__ = "0.1.0"

__all__ = [
    "AGUIEvent",
    "AGUIProtocol",
    "EventType",
    "AGUITransport",
    "WebSocketTransport",
    "SSETransport",
    "HTTPTransport",
    "AGUIMiddleware",
    "EventValidationMiddleware",
    "StateMiddleware",
    "ContextEnrichmentMiddleware",
    "LoggingMiddleware",
    "UIGenerationMiddleware",
    "StreamingMiddleware",
    "create_default_middleware_chain",
    "AGUIConnector",
    "agui_server"
]