import subprocess
from typing import Any
import asyncio

from agent_core.ubuntu_manager import execute_in_ubuntu

class Executor:
    """
    Executes tasks and commands using various runtimes (bash, Python, Node.js).
    """
    
    async def execute_step(self, step) -> str:
        """Execute a single step of a plan.
        
        Args:
            step: The step to execute
        
        Returns:
            The result of executing the step
        """
        try:
            action = getattr(step, "action", None)
            script = getattr(step, "script", None)
            command = getattr(step, "command", None)
            
            if action == "execute_script" and script:
                return await self.execute_script(script)
                
            elif action == "execute_in_ubuntu" and command:
                return await self.execute_in_ubuntu(command)
                
            else:
                raise ValueError(f"Unknown action type: {action}")
                
        except Exception as e:
            raise RuntimeError(f"Step execution failed: {str(e)}")

    async def execute_script(self, script_path: str) -> str:
        """
        Executes a script based on its file extension.
        
        Args:
            script_path: Path to the script to execute
            
        Returns:
            The output of the script execution
        """
        try:
            if script_path.endswith(".sh"):
                result = subprocess.run(["bash", script_path], capture_output=True, text=True, check=True)
            elif script_path.endswith(".py"):
                result = subprocess.run(["python", script_path], capture_output=True, text=True, check=True)
            elif script_path.endswith(".js"):
                result = subprocess.run(["node", script_path], capture_output=True, text=True, check=True)
            else:
                raise ValueError(f"Unsupported script type: {script_path}")
                
            return result.stdout
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Script execution failed: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {str(e)}")

    async def execute_in_ubuntu(self, command: str) -> str:
        """
        Execute a command in the Ubuntu environment.
        
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
