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
planner_module = importlib.import_module("agent_core.planner")
executor_module = importlib.import_module("agent_core.executor")
memory_manager_module = importlib.import_module("agent_core.memory_manager")
ubuntu_manager_module = importlib.import_module("agent_core.ubuntu_manager")

Planner = planner_module.Planner
Executor = executor_module.Executor
MemoryManager = memory_manager_module.MemoryManager
ubuntu_manager = ubuntu_manager_module

class Agent:
    """
    The central agent that orchestrates the iterative agent loop (analyze → plan → execute → observe)
    while emitting AG-UI protocol events.
    """
    def __init__(self):
        self.planner = Planner()
        self.executor = Executor()
        self.memory = MemoryManager()
        self.ubuntu_installed = ubuntu_manager.is_ubuntu_installed()
        self.state = {
            "task_stack": [],         # Stack of tasks to be executed
            "execution_history": [],   # History of executed tasks and results
            "current_context": {},     # Current execution context
            "reflexive_state": {      # Self-monitoring state
                "success_rate": 1.0,
                "error_count": 0,
                "total_tasks": 0,
                "last_error": None
            }
        }

        if self.ubuntu_installed:
            print("✅ Ubuntu environment detected.")
        else:
            print("⚠️ Ubuntu environment not found.")

        print("Agent initialized successfully.")
            
    async def analyze(self, input: RunAgentInput) -> Dict[str, Any]:
        """Analyzes the input and current state to determine next actions.
        
        Args:
            input: The input parameters for running the agent
            
        Returns:
            Analysis results including task breakdown and context
        """
        # Update context with input
        self.state["current_context"].update({
            "messages": input.messages,
            "tools": input.tools,
            "context": input.context
        })
        
        # Analyze message history for task requirements
        latest_message = input.messages[-1] if input.messages else None
        if not latest_message:
            raise ValueError("No messages provided for analysis")
            
        # Store analysis in memory for future reference
        analysis = {
            "requirements": self._extract_requirements(latest_message),
            "constraints": self._extract_constraints(latest_message),
            "dependencies": self._extract_dependencies(latest_message),
            "context": self.state["current_context"]
        }
        
        self.memory.store_analysis(analysis)
        return analysis
    
    def _extract_requirements(self, message: Message) -> List[str]:
        """Extracts key requirements from a message."""
        # TODO: Implement NLP-based requirement extraction
        return []
        
    def _extract_constraints(self, message: Message) -> List[str]:
        """Extracts constraints from a message."""
        # TODO: Implement constraint extraction
        return []
        
    def _extract_dependencies(self, message: Message) -> List[str]:
        """Extracts dependencies from a message."""
        # TODO: Implement dependency analysis
        return []
        
    async def observe(self, result: Any, step: Any) -> None:
        """Observes execution results and updates agent state.
        
        Args:
            result: The result of the executed step
            step: The step that was executed
        """
        # Update reflexive state
        self.state["reflexive_state"]["total_tasks"] += 1
        
        if isinstance(result, Exception):
            self.state["reflexive_state"]["error_count"] += 1
            self.state["reflexive_state"]["last_error"] = str(result)
            self.state["reflexive_state"]["success_rate"] = (
                self.state["reflexive_state"]["total_tasks"] - 
                self.state["reflexive_state"]["error_count"]
            ) / self.state["reflexive_state"]["total_tasks"]
            
        # Store execution history
        self.state["execution_history"].append({
            "step": step,
            "result": result,
            "timestamp": str(uuid.uuid4()),
            "success": not isinstance(result, Exception)
        })
        
        # Update memory with new state
        self.memory.update_state(self.state)

    async def run_agent(self, input: RunAgentInput) -> AsyncGenerator[BaseEvent, None]:
        """
        Runs the iterative agent loop (analyze → plan → execute → observe) while emitting AG-UI protocol events.
        
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
                snapshot=self.state
            )

            # ANALYZE phase
            analysis = await self.analyze(input)
            
            # Create message for text response
            message_id = str(uuid.uuid4())
            yield TextMessageStartEvent(
                type=EventType.TEXT_MESSAGE_START,
                message_id=message_id,
                role="assistant"
            )

            # PLAN phase - create hierarchical plan based on analysis
            plan = await self.planner.create_plan(input, analysis)
            self.state["task_stack"] = plan

            # EXECUTE and OBSERVE phases - process each step
            while self.state["task_stack"]:
                step = self.state["task_stack"].pop(0)
                tool_call_id = str(uuid.uuid4())

                try:
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

                    # EXECUTE phase
                    result = await self.executor.execute_step(step)

                    # OBSERVE phase - process results
                    await self.observe(result, step)
                    
                    # Update state snapshot after each step
                    yield StateSnapshotEvent(
                        type=EventType.STATE_SNAPSHOT,
                        snapshot=self.state
                    )

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

                except Exception as step_error:
                    # Observe the error
                    await self.observe(step_error, step)
                    
                    # Re-plan if necessary based on error
                    if self._should_replan(step_error):
                        recovery_plan = await self.planner.create_recovery_plan(step_error, step)
                        if recovery_plan:
                            self.state["task_stack"] = recovery_plan + self.state["task_stack"]

                    # Stream error as text content
                    yield TextMessageContentEvent(
                        type=EventType.TEXT_MESSAGE_CONTENT,
                        message_id=message_id,
                        delta=f"Error executing step: {str(step_error)}"
                    )

            # Signal message completion
            yield TextMessageEndEvent(
                type=EventType.TEXT_MESSAGE_END,
                message_id=message_id
            )

            # Complete the run with final state
            yield RunFinishedEvent(
                type=EventType.RUN_FINISHED,
                thread_id=input.thread_id,
                run_id=input.run_id,
                result={"status": "success", "state": self.state}
            )

        except Exception as e:
            # Handle any errors by emitting a run error event
            yield RunErrorEvent(
                type=EventType.RUN_ERROR,
                message=str(e)
            )
            
    def _should_replan(self, error: Exception) -> bool:
        """Determines if we should attempt recovery planning based on error type."""
        # Implement error analysis logic here
        return True  # For now, always try to recover
