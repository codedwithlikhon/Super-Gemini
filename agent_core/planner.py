import os
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import json
import re

@dataclass
class PlanStep:
    """Represents a single step in an execution plan"""
    action: str
    tool_name: str
    params: Dict[str, Any]
    description: str
    estimated_duration: float  # in seconds
    required_tools: List[str]
    fallback_actions: Optional[List[Dict]] = None

class Planner:
    """
    Intelligent planner that breaks down high-level goals into executable tasks.
    """
    def __init__(self):
        self.known_patterns = {
            r"install|setup|configure": self._create_setup_plan,
            r"create|make|generate": self._create_generation_plan,
            r"analyze|examine|check": self._create_analysis_plan,
            r"run|execute|start": self._create_execution_plan,
            r"fix|repair|debug": self._create_debugging_plan
        }
        
        self.available_tools = {
            "filesystem": ["read", "write", "delete", "list"],
            "browser": ["open", "navigate", "click", "type"],
            "shell": ["execute", "background_process"],
            "python": ["run_script", "install_package"],
            "node": ["run_script", "npm_install"],
            "time": ["sleep", "schedule"]
        }

    async def create_plan(self, input_data: Any, analysis: Dict) -> List[PlanStep]:
        """
        Creates an intelligent execution plan based on user input and analysis.
        
        Args:
            input_data: Raw input data including messages and context
            analysis: Analysis results including requirements and constraints
            
        Returns:
            List of plan steps to execute
        """
        request = input_data.messages[-1].content if input_data.messages else ""
        requirements = analysis.get("requirements", [])
        constraints = analysis.get("constraints", [])
        
        # Identify the type of plan needed
        plan_creator = self._identify_plan_type(request)
        
        # Create the base plan
        plan = await plan_creator(request, requirements, constraints)
        
        # Add setup and validation steps
        plan = self._add_setup_steps(plan)
        plan = self._add_validation_steps(plan)
        
        return plan

    async def create_recovery_plan(self, error: Exception, failed_step: PlanStep) -> List[PlanStep]:
        """
        Creates a recovery plan when a step fails.
        
        Args:
            error: The error that occurred
            failed_step: The step that failed
            
        Returns:
            List of recovery steps to try
        """
        recovery_plan = []
        
        # Add diagnostic steps
        recovery_plan.append(PlanStep(
            action="analyze_error",
            tool_name="python",
            params={"error": str(error)},
            description="Analyzing error cause",
            estimated_duration=1.0,
            required_tools=["python"]
        ))
        
        # Add cleanup steps if needed
        if failed_step.action in ["create", "modify"]:
            recovery_plan.append(PlanStep(
                action="cleanup",
                tool_name="filesystem",
                params={"target": failed_step.params.get("path")},
                description="Cleaning up failed operation",
                estimated_duration=1.0,
                required_tools=["filesystem"]
            ))
            
        # Add retry with modified parameters
        if failed_step.fallback_actions:
            for fallback in failed_step.fallback_actions:
                recovery_plan.append(PlanStep(
                    action=fallback["action"],
                    tool_name=fallback["tool"],
                    params=fallback["params"],
                    description=f"Retrying with fallback: {fallback['description']}",
                    estimated_duration=failed_step.estimated_duration * 1.5,
                    required_tools=[fallback["tool"]]
                ))
                
        return recovery_plan

    def _identify_plan_type(self, request: str) -> callable:
        """Identifies which type of plan creator to use based on the request."""
        for pattern, creator in self.known_patterns.items():
            if re.search(pattern, request, re.IGNORECASE):
                return creator
        return self._create_general_plan  # Default plan creator

    async def _create_setup_plan(self, request: str, requirements: List, constraints: List) -> List[PlanStep]:
        """Creates a plan for setup/installation tasks."""
        plan = []
        
        # Add environment check
        plan.append(PlanStep(
            action="check_environment",
            tool_name="shell",
            params={"command": "python3 -V && node -v"},
            description="Checking runtime versions",
            estimated_duration=1.0,
            required_tools=["shell"]
        ))
        
        # Add dependency installation
        if "python" in requirements:
            plan.append(PlanStep(
                action="install_dependencies",
                tool_name="python",
                params={"packages": requirements},
                description="Installing Python dependencies",
                estimated_duration=5.0,
                required_tools=["python"]
            ))
            
        return plan

    async def _create_generation_plan(self, request: str, requirements: List, constraints: List) -> List[PlanStep]:
        """Creates a plan for generation tasks."""
        plan = []
        
        # Add generation step
        plan.append(PlanStep(
            action="generate",
            tool_name="python",
            params={"template": "default", "output": "generated"},
            description="Generating requested content",
            estimated_duration=3.0,
            required_tools=["python"]
        ))
        
        return plan

    async def _create_analysis_plan(self, request: str, requirements: List, constraints: List) -> List[PlanStep]:
        """Creates a plan for analysis tasks."""
        plan = []
        
        # Add analysis steps
        plan.append(PlanStep(
            action="analyze",
            tool_name="python",
            params={"target": request},
            description="Analyzing request",
            estimated_duration=2.0,
            required_tools=["python"]
        ))
        
        return plan

    async def _create_execution_plan(self, request: str, requirements: List, constraints: List) -> List[PlanStep]:
        """Creates a plan for execution tasks."""
        plan = []
        
        # Add execution step
        plan.append(PlanStep(
            action="execute",
            tool_name="shell",
            params={"command": request},
            description="Executing command",
            estimated_duration=2.0,
            required_tools=["shell"]
        ))
        
        return plan

    async def _create_debugging_plan(self, request: str, requirements: List, constraints: List) -> List[PlanStep]:
        """Creates a plan for debugging tasks."""
        plan = []
        
        # Add debugging steps
        plan.append(PlanStep(
            action="debug",
            tool_name="python",
            params={"target": request},
            description="Debugging issue",
            estimated_duration=5.0,
            required_tools=["python"]
        ))
        
        return plan

    async def _create_general_plan(self, request: str, requirements: List, constraints: List) -> List[PlanStep]:
        """Creates a general purpose plan when no specific pattern is matched."""
        plan = []
        
        # Add general execution step
        plan.append(PlanStep(
            action="process",
            tool_name="python",
            params={"request": request},
            description="Processing general request",
            estimated_duration=2.0,
            required_tools=["python"]
        ))
        
        return plan

    def _add_setup_steps(self, plan: List[PlanStep]) -> List[PlanStep]:
        """Adds any necessary setup steps to the beginning of the plan."""
        setup_steps = []
        
        # Add verification of required tools
        required_tools = set()
        for step in plan:
            required_tools.update(step.required_tools)
            
        for tool in required_tools:
            setup_steps.append(PlanStep(
                action="verify_tool",
                tool_name="shell",
                params={"tool": tool},
                description=f"Verifying {tool} availability",
                estimated_duration=1.0,
                required_tools=["shell"]
            ))
            
        return setup_steps + plan

    def _add_validation_steps(self, plan: List[PlanStep]) -> List[PlanStep]:
        """Adds validation steps after critical operations."""
        validated_plan = []
        
        for step in plan:
            validated_plan.append(step)
            
            # Add validation after critical operations
            if step.action in ["create", "modify", "delete"]:
                validated_plan.append(PlanStep(
                    action="validate",
                    tool_name="python",
                    params={"target": step.params},
                    description=f"Validating {step.action} operation",
                    estimated_duration=1.0,
                    required_tools=["python"]
                ))
                
        return validated_plan
