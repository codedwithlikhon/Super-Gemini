"""
Planner module that handles task analysis and plan generation.
"""

import asyncio
import json
import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, AsyncIterator, Tuple, Union

from .types import RunAgentInput, Message, Tool, ToolCall
from .memory_manager import MemoryManager

@dataclass
class PlanStep:
    """
    Represents a single step in an execution plan.
    """
    tool_name: str
    args: Dict[str, Any]
    description: str

    def to_json(self) -> str:
        """Convert step arguments to JSON string."""
        import json
        return json.dumps(self.args)

@dataclass
class TaskAnalysis:
    """
    Results from analyzing a user task.
    """
    task_type: str
    requirements: List[str]
    constraints: List[str]
    dependencies: List[str]
    context_needs: List[str]
    code_blocks: List[Dict[str, str]] = None  # Each dict has 'code', 'language', and 'purpose' keys

@dataclass
class CodeAct:
    """
    Represents a code generation action.
    """
    language: str
    purpose: str
    code: str
    dependencies: List[str]
    runtime: str
    
    def to_tool_call(self) -> ToolCall:
        """Convert CodeAct to a ToolCall."""
        return ToolCall(
            id=f"code_{hash(self.code)}", 
            tool_name="execute_code",
            arguments={
                "code": self.code,
                "runtime": self.runtime,
                "timeout": 30  # Default timeout
            },
            description=self.purpose
        )

class Planner:
    """
    The Planner class handles task analysis and plan generation.
    """
    def __init__(self):
        """Initialize the planner with required components."""
        self.memory = MemoryManager()
        self.last_analysis: Optional[TaskAnalysis] = None
        self.code_templates = {
            "python": {
                "file_operations": '''
                    import os
                    
                    def {operation}_file(path: str, content: str = None) -> bool:
                        try:
                            if "{operation}" == "read":
                                with open(path, "r") as f:
                                    return f.read()
                            else:  # write
                                with open(path, "w") as f:
                                    f.write(content)
                                return True
                        except Exception as e:
                            print(f"Error: {str(e)}")
                            return False
                ''',
                "system_check": '''
                    import os
                    import sys
                    import platform
                    
                    def check_system():
                        return {
                            "os": platform.system(),
                            "python": sys.version,
                            "cwd": os.getcwd(),
                            "uid": os.getuid()
                        }
                '''
            },
            "javascript": {
                "file_operations": '''
                    const fs = require('fs').promises;
                    
                    async function {operation}File(path, content) {
                        try {
                            if ("{operation}" === "read") {
                                return await fs.readFile(path, 'utf8');
                            } else {  // write
                                await fs.writeFile(path, content);
                                return true;
                            }
                        } catch (error) {
                            console.error(`Error: ${error.message}`);
                            return false;
                        }
                    }
                ''',
                "system_check": '''
                    const os = require('os');
                    
                    function checkSystem() {
                        return {
                            os: process.platform,
                            node: process.version,
                            cwd: process.cwd(),
                            uid: process.getuid()
                        };
                    }
                '''
            }
        }

    async def analyze_task(self, input: RunAgentInput) -> TaskAnalysis:
        """
        Analyze the task to understand requirements and constraints.
        
        Args:
            input: The input parameters containing messages and context
            
        Returns:
            TaskAnalysis: Analysis results for the task
        """
        # Extract the latest user message
        latest_message = next(
            (msg for msg in reversed(input.messages) if msg.role == "user"),
            None
        )
        
        if not latest_message:
            raise ValueError("No user message found in input")

        # Default analysis
        analysis = TaskAnalysis(
            task_type="command",
            requirements=[],
            constraints=[],
            dependencies=[],
            context_needs=[]
        )

        # Determine task type and requirements
        content = latest_message.content.lower()
        
        # Check for specific task patterns
        if any(kw in content for kw in ["create", "new", "generate"]):
            analysis.task_type = "creation"
            analysis.requirements.append("file system access")
        
        elif any(kw in content for kw in ["install", "setup", "configure"]):
            analysis.task_type = "system"
            analysis.requirements.append("system access")
            analysis.requirements.append("package management")
        
        elif any(kw in content for kw in ["run", "execute", "start"]):
            analysis.task_type = "execution"
            analysis.requirements.append("runtime environment")
            analysis.requirements.append("process management")

        # Check context needs
        if "file" in content or "directory" in content:
            analysis.context_needs.append("file system status")
        
        if any(kw in content for kw in ["installed", "package", "dependency"]):
            analysis.context_needs.append("package information")
        
        if "status" in content or "running" in content:
            analysis.context_needs.append("process status")

        # Remember the analysis for later steps
        self.last_analysis = analysis
        return analysis

    def generate_code(self, language: str, template_key: str, **kwargs) -> str:
        """
        Generate code from template.
        
        Args:
            language: Programming language to use
            template_key: Template identifier
            **kwargs: Template parameters
            
        Returns:
            str: Generated code
        """
        template = self.code_templates.get(language, {}).get(template_key)
        if not template:
            raise ValueError(f"No template found for {language}/{template_key}")
            
        return template.format(**kwargs).strip()

    async def create_plan(self, input: RunAgentInput) -> List[PlanStep]:
        """
        Create an execution plan based on task analysis.
        
        Args:
            input: The input parameters containing messages and context
            
        Returns:
            List[PlanStep]: Sequence of steps to execute
        """
        # First analyze the task
        analysis = await self.analyze_task(input)
        steps = []
        
        # Initialize code blocks if needed
        if analysis.code_blocks is None:
            analysis.code_blocks = []

        # Generate code for system tasks
        if analysis.task_type == "system":
            # Add system check code
            python_check = self.generate_code("python", "system_check")
            analysis.code_blocks.append({
                "code": python_check,
                "language": "python",
                "purpose": "Check system status"
            })
            
            steps.append(
                PlanStep(
                    tool_name="check_system_status",
                    args={"requirements": analysis.requirements},
                    description="Verify system requirements"
                )
            )

        # Generate code for creation tasks
        elif analysis.task_type == "creation":
            # Add file operations code
            python_file_ops = self.generate_code(
                "python",
                "file_operations",
                operation="write"
            )
            analysis.code_blocks.append({
                "code": python_file_ops,
                "language": "python",
                "purpose": "File system operations"
            })
            
            steps.append(
                PlanStep(
                    tool_name="verify_filesystem",
                    args={"operation": "write"},
                    description="Check file system access"
                )
            )

        # Generate code for execution tasks
        elif analysis.task_type == "execution":
            # We'll determine appropriate runtime and generate execution code
            runtime_step = PlanStep(
                tool_name="verify_runtime",
                args={"type": "python"},  # Default to Python
                description="Check runtime environment"
            )
            steps.append(runtime_step)
            
            # If we have specific code blocks from analysis, add them
            for code_block in analysis.code_blocks:
                steps.append(
                    PlanStep(
                        tool_name="execute_code",
                        args={
                            "code": code_block["code"],
                            "runtime": code_block["language"]
                        },
                        description=code_block["purpose"]
                    )
                )

        # Add context gathering steps
        for need in analysis.context_needs:
            steps.append(
                PlanStep(
                    tool_name="gather_context",
                    args={"type": need},
                    description=f"Gather {need}"
                )
            )
            
        # Convert any code blocks to CodeActs
        for block in analysis.code_blocks:
            code_act = CodeAct(
                language=block["language"],
                purpose=block["purpose"],
                code=block["code"],
                dependencies=[],  # We could analyze dependencies here
                runtime=block["language"]  # Use language as runtime
            )
            # Add tool call from code act
            steps.append(code_act.to_tool_call())

        return steps

    async def update_plan(self, input: RunAgentInput, results: List[Dict[str, Any]]) -> List[PlanStep]:
        """
        Update the execution plan based on results from previous steps.
        
        Args:
            input: The input parameters containing messages and context
            results: Results from previously executed steps
            
        Returns:
            List[PlanStep]: Updated sequence of steps
        """
        if not self.last_analysis:
            # If no previous analysis, create a new plan
            return await self.create_plan(input)
            
        steps = []
        
        # Analyze results and add necessary follow-up steps
        for result in results:
            if result.get("status") == "error":
                # Add error handling step
                steps.append(
                    PlanStep(
                        tool_name="handle_error",
                        args={"error": result.get("error")},
                        description="Handle execution error"
                    )
                )
            elif result.get("needs_followup"):
                # Add any necessary follow-up steps
                steps.append(
                    PlanStep(
                        tool_name=result["followup_tool"],
                        args=result["followup_args"],
                        description=result["followup_description"]
                    )
                )
                
        return steps