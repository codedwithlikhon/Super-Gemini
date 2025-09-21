import importlib
import uuid
from typing import Any, AsyncGenerator, Dict, List, Optional

from .events import (
    EventType, BaseEvent, RunStartedEvent, RunFinishedEvent,
    RunErrorEvent, TextMessageStartEvent, TextMessageContentEvent,
    TextMessageEndEvent, ToolCallStartEvent, ToolCallArgsEvent,
    ToolCallEndEvent, StateSnapshotEvent
)
from .types import RunAgentInput, Message, Tool, Context

# Dynamically import planner, executor, and memory_manager
planner_module = importlib.import_module("agent-core.planner")
executor_module = importlib.import_module("agent-core.executor")
memory_manager_module = importlib.import_module("agent-core.memory_manager")
ubuntu_manager_module = importlib.import_module("agent-core.ubuntu_manager")

Planner = planner_module.Planner
Executor = executor_module.Executor
MemoryManager = memory_manager_module.MemoryManager
ubuntu_manager = ubuntu_manager_module

class Agent:
    """
    The central agent that orchestrates the planner, executor, and memory while
    emitting AG-UI protocol events.
    """
    def __init__(self):
        self.planner = Planner()
        self.executor = Executor()
        self.memory = MemoryManager()
        self.ubuntu_installed = ubuntu_manager.is_ubuntu_installed()

        if self.ubuntu_installed:
            print("✅ Ubuntu environment detected.")
        else:
            print("⚠️ Ubuntu environment not found.")

        print("Agent initialized successfully.")

    async def run_agent(self, input: RunAgentInput) -> AsyncGenerator[BaseEvent, None]:
        """
        Runs the agent with the provided input, yielding AG-UI protocol events.
        
        Args:
            input: The input parameters for running the agent
            
        Yields:
            A stream of AG-UI protocol events
        """
        try:
            # Start the run
            yield RunStartedEvent(
                type=EventType.RUN_STARTED,
                thread_id=input.thread_id,
                run_id=input.run_id
            )

            # Send initial state snapshot
            yield StateSnapshotEvent(
                type=EventType.STATE_SNAPSHOT,
                snapshot=self.memory.get_preferences()
            )

            # Create message for text response
            message_id = str(uuid.uuid4())
            yield TextMessageStartEvent(
                type=EventType.TEXT_MESSAGE_START,
                message_id=message_id,
                role="assistant"
            )

            # Create and execute plan
            plan = await self.planner.create_plan(input)

            # Execute each step of the plan
            for step in plan:
                tool_call_id = str(uuid.uuid4())

                # Signal tool call start
                yield ToolCallStartEvent(
                    type=EventType.TOOL_CALL_START,
                    tool_call_id=tool_call_id,
                    tool_call_name=step.tool_name,
                    parent_message_id=message_id
                )

                # Stream tool arguments
                args_json = step.to_json()
                yield ToolCallArgsEvent(
                    type=EventType.TOOL_CALL_ARGS,
                    tool_call_id=tool_call_id,
                    delta=args_json
                )

                # Execute the step
                result = await self.executor.execute_step(step)

                # Signal tool call end
                yield ToolCallEndEvent(
                    type=EventType.TOOL_CALL_END,
                    tool_call_id=tool_call_id
                )

                # Stream step result as text content
                yield TextMessageContentEvent(
                    type=EventType.TEXT_MESSAGE_CONTENT,
                    message_id=message_id,
                    delta=str(result)
                )

            # Signal message completion
            yield TextMessageEndEvent(
                type=EventType.TEXT_MESSAGE_END,
                message_id=message_id
            )

            # Complete the run
            yield RunFinishedEvent(
                type=EventType.RUN_FINISHED,
                thread_id=input.thread_id,
                run_id=input.run_id,
                result={"status": "success"}
            )

        except Exception as e:
            # Handle any errors by emitting a run error event
            yield RunErrorEvent(
                type=EventType.RUN_ERROR,
                message=str(e)
            )
