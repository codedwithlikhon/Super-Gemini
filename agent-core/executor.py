"""
Executor module for running code across multiple runtimes with execution monitoring
and error handling.
"""

import os
import sys
import asyncio
import importlib
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple

from .planner import PlanStep, CodeAct
from .types import ToolCall

class RuntimeManager:
    """
    Manages different runtime environments for code execution.
    """
    def __init__(self):
        self.runtimes = {
            "python": sys.executable or "/usr/bin/python3",
            "node": "/usr/bin/node",
            "bash": "/bin/bash"
        }
        self.temp_dir = Path(tempfile.mkdtemp(prefix="agent_runtime_"))
        self.last_execution: Dict[str, Any] = {}
        
    def detect_runtime(self, code: str) -> str:
        """
        Detect appropriate runtime for code.
        
        Args:
            code: Code to analyze
            
        Returns:
            str: Detected runtime name
        """
        # Check for specific runtime indicators
        if code.startswith("#!/usr/bin/env python") or code.endswith(".py"):
            return "python"
        elif code.startswith("#!/usr/bin/env node") or code.endswith(".js"):
            return "node"
        elif code.startswith("#!/bin/bash") or code.endswith(".sh"):
            return "bash"
            
        # Try to detect by code patterns
        if "import " in code or "from " in code:
            return "python"
        elif "require(" in code or "module.exports" in code:
            return "node"
        elif "#!/bin/" in code or ";" in code:
            return "bash"
            
        # Default to Python
        return "python"
            
    def get_runtime_path(self, runtime: str) -> str:
        """
        Get path to runtime executable.
        
        Args:
            runtime: Name of the runtime
            
        Returns:
            str: Path to runtime executable
        """
        # Check if runtime exists
        path = self.runtimes.get(runtime)
        if not path or not os.path.exists(path):
            raise ValueError(f"Runtime '{runtime}' not found")
            
        return path
        
    def prepare_code_file(self, code: str, runtime: str) -> Path:
        """
        Prepare code file for execution.
        
        Args:
            code: Code to save
            runtime: Runtime name
            
        Returns:
            Path: Path to prepared code file
        """
        extensions = {
            "python": ".py",
            "node": ".js",
            "bash": ".sh"
        }
        
        # Create temp file with appropriate extension
        ext = extensions.get(runtime, ".txt")
        temp_file = self.temp_dir / f"code_{hash(code)}{ext}"
        
        # Save code to file
        temp_file.write_text(code)
        
        # Make executable if needed
        if runtime == "bash":
            temp_file.chmod(0o755)
            
        return temp_file
        
    def cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir.exists():
            for file in self.temp_dir.glob("*"):
                file.unlink()
            self.temp_dir.rmdir()

class ToolManager:
    """
    Manages loading and execution of agent tools.
    """
    def __init__(self):
        self.tools: Dict[str, Any] = {}
        self._load_tools()
        
    def _load_tools(self):
        """Load all available tools."""
        tools_dir = os.path.join(os.path.dirname(__file__), "..", "tools")
        
        if not os.path.exists(tools_dir):
            print(f"Warning: Tools directory not found at {tools_dir}")
            return
            
        for filename in os.listdir(tools_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f"tools.{module_name}")
                    tool_class = getattr(module, f"{module_name.capitalize()}Tool", None)
                    if tool_class:
                        self.tools[module_name] = tool_class()
                except Exception as e:
                    print(f"Error loading tool {module_name}: {str(e)}")
                    
    async def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name with arguments."""
        tool = self.tools.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
            
        if asyncio.iscoroutinefunction(tool.execute):
            return await tool.execute(**kwargs)
        else:
            return tool.execute(**kwargs)

class Executor:
    """
    Handles execution of code and tools across different runtimes.
    """
    def __init__(self):
        self.runtime_manager = RuntimeManager()
        self.tool_manager = ToolManager()
        
    async def execute_step(self, step: PlanStep) -> Dict[str, Any]:
        """
        Execute a single plan step.
        
        Args:
            step: The plan step to execute
            
        Returns:
            Dict containing execution results
        """
        try:
            # Execute tool if specified
            if step.tool_name:
                return await self.tool_manager.execute_tool(
                    step.tool_name,
                    **step.args
                )
                
            raise ValueError("Invalid step: no tool name specified")
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "step": step
            }
            
    async def execute_code(
        self,
        code: str,
        runtime: Optional[str] = None,
        timeout: int = 30,
        env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Execute code in specified runtime with monitoring.
        
        Args:
            code: Code to execute
            runtime: Optional runtime override
            timeout: Maximum execution time in seconds
            env: Optional environment variables
            
        Returns:
            Dict containing execution results and metrics
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            if not runtime:
                runtime = self.runtime_manager.detect_runtime(code)
                
            runtime_path = self.runtime_manager.get_runtime_path(runtime)
            
            # Prepare code file
            code_file = self.runtime_manager.prepare_code_file(code, runtime)
            
            # Set up environment
            proc_env = os.environ.copy()
            if env:
                proc_env.update(env)
                
            # Create process
            process = await asyncio.create_subprocess_exec(
                runtime_path,
                str(code_file),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=proc_env
            )
            
            try:
                # Run with timeout and capture output
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                # Calculate execution time
                execution_time = asyncio.get_event_loop().time() - start_time
                
                result = {
                    "status": "success" if process.returncode == 0 else "error",
                    "return_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                    "execution_time": execution_time,
                    "runtime": runtime,
                    "code_hash": hash(code)
                }
                
                # Store execution details for monitoring
                self.runtime_manager.last_execution = {
                    "timestamp": start_time,
                    "runtime": runtime,
                    "code_hash": hash(code),
                    "result": result
                }
                
                return result
                
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "status": "timeout",
                    "error": f"Execution timed out after {timeout}s",
                    "execution_time": timeout,
                    "runtime": runtime,
                    "code_hash": hash(code)
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "runtime": runtime,
                "code_hash": hash(code)
            }
            
        finally:
            # Clean up code file
            if "code_file" in locals():
                code_file.unlink()
            
    async def execute_tool_call(self, tool_call: ToolCall) -> Dict[str, Any]:
        """
        Execute a tool call and return results.
        
        Args:
            tool_call: The tool call to execute
            
        Returns:
            Dict containing execution results
        """
        return await self.tool_manager.execute_tool(
            tool_call.tool_name,
            **tool_call.arguments
        )