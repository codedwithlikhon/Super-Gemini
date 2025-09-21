"""
Shell execution tool for Super-Gemini.
"""
import asyncio
import subprocess
from typing import Dict, Any, Optional

class ShellTool:
    """Tool for executing shell commands with proper safety checks."""
    
    def __init__(self, allowed_commands: Optional[list] = None):
        """
        Initialize the shell tool.
        
        Args:
            allowed_commands: Optional list of allowed command prefixes.
                            If None, all commands are allowed (use with caution).
        """
        self.allowed_commands = allowed_commands
        
    def _validate_command(self, command: str) -> bool:
        """
        Validate that a command is allowed to run.
        
        Args:
            command: The command to validate
            
        Returns:
            bool: True if command is allowed
            
        Raises:
            ValueError: If command is not allowed
        """
        if not self.allowed_commands:
            return True
            
        if any(command.startswith(cmd) for cmd in self.allowed_commands):
            return True
            
        raise ValueError(f"Command '{command}' is not in allowed commands list")
        
    async def execute(self, command: str, env: Optional[Dict[str, str]] = None, 
                     timeout: int = 30, cwd: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a shell command asynchronously.
        
        Args:
            command: The command to execute
            env: Optional environment variables
            timeout: Maximum execution time in seconds
            cwd: Working directory for command execution
            
        Returns:
            Dict containing execution results
        """
        # Validate command
        self._validate_command(command)
        
        # Set up environment
        proc_env = None
        if env:
            proc_env = {**dict(os.environ), **env}
        
        try:
            # Create and run process
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=proc_env,
                cwd=cwd
            )
            
            # Run with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                return {
                    "status": "success" if process.returncode == 0 else "error",
                    "return_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                    "command": command
                }
                
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "status": "timeout",
                    "error": f"Command timed out after {timeout}s",
                    "command": command
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "command": command
            }