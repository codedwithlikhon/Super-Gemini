import subprocess
import asyncio
import os
import sys
import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import logging
import signal
from contextlib import asynccontextmanager

from agent_core.ubuntu_manager import execute_in_ubuntu

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ExecutionResult:
    """Represents the result of executing a step"""
    success: bool
    output: str
    error: Optional[str] = None
    runtime: Optional[str] = None
    duration: Optional[float] = None
    resource_usage: Optional[Dict[str, float]] = None

class RuntimeManager:
    """Manages different runtime environments"""
    
    def __init__(self):
        self.runtimes = {
            "python": {
                "command": sys.executable,
                "version_flag": "--version",
                "requirements_file": "requirements.txt",
                "install_command": ["-m", "pip", "install"]
            },
            "node": {
                "command": "node",
                "version_flag": "--version",
                "requirements_file": "package.json",
                "install_command": ["npm", "install"]
            },
            "bash": {
                "command": "bash",
                "version_flag": "--version",
                "requirements_file": None,
                "install_command": None
            }
        }
        
    async def verify_runtime(self, runtime: str) -> bool:
        """Verifies if a runtime is available and working."""
        if runtime not in self.runtimes:
            return False
            
        try:
            config = self.runtimes[runtime]
            proc = await asyncio.create_subprocess_exec(
                config["command"],
                config["version_flag"],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await proc.wait()
            return proc.returncode == 0
            
        except Exception as e:
            logger.error(f"Runtime verification failed for {runtime}: {str(e)}")
            return False
            
    async def install_dependencies(self, runtime: str, working_dir: str) -> bool:
        """Installs dependencies for a specific runtime."""
        config = self.runtimes.get(runtime)
        if not config or not config["requirements_file"]:
            return True
            
        requirements_path = os.path.join(working_dir, config["requirements_file"])
        if not os.path.exists(requirements_path):
            return True
            
        try:
            cmd = [config["command"]] + config["install_command"]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await proc.wait()
            return proc.returncode == 0
            
        except Exception as e:
            logger.error(f"Dependency installation failed for {runtime}: {str(e)}")
            return False

class Executor:
    """
    Enhanced executor that handles multiple runtime environments and provides robust execution capabilities.
    """
    
    def __init__(self):
        self.runtime_manager = RuntimeManager()
        self.max_execution_time = 300  # 5 minutes default timeout
        self.current_processes: List[asyncio.subprocess.Process] = []
        
    async def execute_step(self, step: Any) -> ExecutionResult:
        """
        Executes a single step of a plan with enhanced error handling and resource monitoring.
        
        Args:
            step: The step to execute (PlanStep object)
            
        Returns:
            ExecutionResult object containing execution results and metadata
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Validate required tools/runtimes
            for tool in step.required_tools:
                if not await self.runtime_manager.verify_runtime(tool):
                    raise RuntimeError(f"Required runtime {tool} is not available")
            
            # Execute based on action type
            if step.action == "execute_script":
                result = await self.execute_script(step.params["script"])
            elif step.action == "execute_in_ubuntu":
                result = await self.execute_in_ubuntu(step.params["command"])
            elif step.action == "python":
                result = await self.execute_python_code(step.params.get("code", ""), step.params.get("args", {}))
            elif step.action == "node":
                result = await self.execute_node_code(step.params.get("code", ""), step.params.get("args", {}))
            else:
                raise ValueError(f"Unknown action type: {step.action}")
            
            duration = asyncio.get_event_loop().time() - start_time
            
            return ExecutionResult(
                success=True,
                output=result,
                runtime=step.tool_name,
                duration=duration,
                resource_usage=await self._get_resource_usage()
            )
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                runtime=step.tool_name,
                duration=duration,
                resource_usage=await self._get_resource_usage()
            )
            
    async def execute_script(self, script_path: str) -> str:
        """
        Executes a script with enhanced security and monitoring.
        
        Args:
            script_path: Path to the script to execute
            
        Returns:
            The output of the script execution
        """
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found: {script_path}")
            
        runtime = self._get_runtime_for_script(script_path)
        
        async with self._managed_process(runtime["command"], script_path) as proc:
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                raise RuntimeError(f"Script execution failed: {stderr.decode()}")
                
            return stdout.decode()
            
    async def execute_python_code(self, code: str, args: Dict[str, Any] = None) -> str:
        """
        Executes Python code with arguments.
        
        Args:
            code: Python code to execute
            args: Optional dictionary of arguments
            
        Returns:
            The output of the code execution
        """
        with self._create_temp_script(".py", code) as script_path:
            if args:
                with open(script_path, 'r') as f:
                    content = f.read()
                with open(script_path, 'w') as f:
                    f.write(f"args = {json.dumps(args)}\n")
                    f.write(content)
                    
            return await self.execute_script(script_path)
            
    async def execute_node_code(self, code: str, args: Dict[str, Any] = None) -> str:
        """
        Executes Node.js code with arguments.
        
        Args:
            code: JavaScript code to execute
            args: Optional dictionary of arguments
            
        Returns:
            The output of the code execution
        """
        with self._create_temp_script(".js", code) as script_path:
            if args:
                with open(script_path, 'r') as f:
                    content = f.read()
                with open(script_path, 'w') as f:
                    f.write(f"const args = {json.dumps(args)};\n")
                    f.write(content)
                    
            return await self.execute_script(script_path)
            
    async def execute_in_ubuntu(self, command: str) -> str:
        """
        Executes a command in the Ubuntu environment with improved error handling.
        
        Args:
            command: The command to execute
            
        Returns:
            The output of the command execution
        """
        try:
            result = await execute_in_ubuntu(command)
            return result
        except Exception as e:
            raise RuntimeError(f"Ubuntu command execution failed: {str(e)}")
            
    def _get_runtime_for_script(self, script_path: str) -> Dict[str, str]:
        """Determines the appropriate runtime for a script based on its extension."""
        ext = os.path.splitext(script_path)[1].lower()
        
        runtimes = {
            ".sh": {"command": "bash", "args": []},
            ".py": {"command": sys.executable, "args": []},
            ".js": {"command": "node", "args": []},
        }
        
        if ext not in runtimes:
            raise ValueError(f"Unsupported script type: {ext}")
            
        return runtimes[ext]
        
    @asynccontextmanager
    async def _managed_process(self, *args, **kwargs):
        """Context manager for process execution with timeout and resource management."""
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            **kwargs
        )
        
        self.current_processes.append(proc)
        
        try:
            yield proc
        finally:
            self.current_processes.remove(proc)
            if proc.returncode is None:
                try:
                    proc.terminate()
                    await asyncio.wait_for(proc.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    proc.kill()
                    
    async def _get_resource_usage(self) -> Dict[str, float]:
        """Collects resource usage statistics for the current execution."""
        # This is a simplified version - in practice, you'd want to use
        # psutil or a similar library to get detailed resource metrics
        return {
            "cpu_percent": 0.0,
            "memory_mb": 0.0,
            "disk_io": 0.0
        }
        
    def cleanup(self):
        """Cleanup any remaining processes."""
        for proc in self.current_processes:
            if proc.returncode is None:
                try:
                    proc.terminate()
                except Exception:
                    pass
