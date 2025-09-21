"""
Python script execution tool.
"""
import ast
import asyncio
from typing import Dict, Any, Optional
import tempfile
import os
from pathlib import Path
import sys

class PythonTool:
    """Tool for executing Python code with safety checks."""
    
    def __init__(self, allowed_imports: Optional[list] = None):
        """
        Initialize the Python tool.
        
        Args:
            allowed_imports: Optional list of allowed import modules.
                           If None, all imports are allowed (use with caution).
        """
        self.allowed_imports = allowed_imports or [
            'datetime', 'json', 'math', 'os', 're', 'sys',
            'time', 'typing', 'uuid', 'pathlib'
        ]
        
    def _validate_code(self, code: str) -> bool:
        """
        Validate Python code for security.
        
        Args:
            code: Python code to validate
            
        Returns:
            bool: True if code is safe
            
        Raises:
            ValueError: If code contains disallowed imports or syntax errors
        """
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Check imports
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module = node.names[0].name.split('.')[0]
                    if module not in self.allowed_imports:
                        raise ValueError(f"Import of '{module}' is not allowed")
                        
                # Prevent exec/eval
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['exec', 'eval']:
                            raise ValueError(f"Use of {node.func.id}() is not allowed")
                            
            return True
            
        except SyntaxError as e:
            raise ValueError(f"Python syntax error: {str(e)}")
            
    async def execute(self, code: str, env: Optional[Dict[str, str]] = None,
                     timeout: int = 30, capture_output: bool = True) -> Dict[str, Any]:
        """
        Execute Python code safely.
        
        Args:
            code: Python code to execute
            env: Optional environment variables
            timeout: Maximum execution time in seconds
            capture_output: Whether to capture stdout/stderr
            
        Returns:
            Dict containing execution results
        """
        # Validate code
        self._validate_code(code)
        
        # Create temporary file for code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = Path(f.name)
            
        try:
            # Set up environment
            proc_env = None
            if env:
                proc_env = {**dict(os.environ), **env}
                
            # Create and run process
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                str(temp_file),
                stdout=subprocess.PIPE if capture_output else None,
                stderr=subprocess.PIPE if capture_output else None,
                env=proc_env
            )
            
            try:
                # Run with timeout
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                result = {
                    "status": "success" if process.returncode == 0 else "error",
                    "return_code": process.returncode
                }
                
                if capture_output:
                    result.update({
                        "stdout": stdout.decode() if stdout else "",
                        "stderr": stderr.decode() if stderr else ""
                    })
                    
                return result
                
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "status": "timeout",
                    "error": f"Code execution timed out after {timeout}s"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
        finally:
            # Clean up temp file
            try:
                temp_file.unlink()
            except:
                pass