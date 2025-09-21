import asyncio
import json
from typing import AsyncGenerator
import uuid

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_core.events import (
    EventType, TextMessageStartEvent, TextMessageContentEvent,
    TextMessageEndEvent, RunStartedEvent, RunFinishedEvent
)
from agent_core.types import (
    RunAgentInput, Tool, Context, UserMessage
)
from agent_core.agent import Agent
from agent_core.encoder import EventEncoder

async def test_agent():
    """Test the AG-UI protocol implementation."""
    
    # Create test input
    input_data = RunAgentInput(
        thread_id=str(uuid.uuid4()),
        run_id=str(uuid.uuid4()),
        state={},
        messages=[
            UserMessage(
                id=str(uuid.uuid4()),
                role="user",
                content="Hello, can you help me build a web app?"
            )
        ],
        tools=[
            Tool(
                name="scaffold_webapp",
                description="Scaffold a new web application",
                parameters={
                    "type": "object",
                    "properties": {
                        "framework": {
                            "type": "string",
                            "enum": ["react", "next", "svelte"]
                        },
                        "name": {
                            "type": "string"
                        }
                    },
                    "required": ["framework", "name"]
                }
            )
        ],
        context=[
            Context(
                description="User's preferred framework",
                value="react"
            )
        ],
        forwarded_props={}
    )

    # Initialize agent and encoder
    agent = Agent()
    encoder = EventEncoder()

    print("🧪 Starting AG-UI protocol test...")
    print(f"Thread ID: {input_data.thread_id}")
    print(f"Run ID: {input_data.run_id}")
    
    try:
        # Process events
        async for event in agent.run_agent(input_data):
            # Encode and print each event
            encoded = encoder.encode(event)
            print("\n🔄 Event received:")
            print(encoded)
            
            # Verify event structure based on type
            if event.type == EventType.RUN_STARTED:
                assert isinstance(event, RunStartedEvent)
                assert event.thread_id == input_data.thread_id
                assert event.run_id == input_data.run_id
                print("✅ RUN_STARTED event validated")
                
            elif event.type == EventType.TEXT_MESSAGE_START:
                assert isinstance(event, TextMessageStartEvent)
                assert event.role == "assistant"
                print("✅ TEXT_MESSAGE_START event validated")
                
            elif event.type == EventType.TEXT_MESSAGE_CONTENT:
                assert isinstance(event, TextMessageContentEvent)
                assert len(event.delta) > 0
                print("✅ TEXT_MESSAGE_CONTENT event validated")
                
            elif event.type == EventType.TEXT_MESSAGE_END:
                assert isinstance(event, TextMessageEndEvent)
                print("✅ TEXT_MESSAGE_END event validated")
                
            elif event.type == EventType.RUN_FINISHED:
                assert isinstance(event, RunFinishedEvent)
                assert event.thread_id == input_data.thread_id
                assert event.run_id == input_data.run_id
                print("✅ RUN_FINISHED event validated")
        
        print("\n✅ All events processed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    print("🚀 Starting AG-UI protocol test suite...")
    asyncio.run(test_agent())