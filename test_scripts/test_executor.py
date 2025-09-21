"""
Test suite for the executor module with enhanced runtime and code execution testing.
"""

import os
import pytest
import asyncio
from pathlib import Path
from agent_core.executor import Executor, RuntimeManager

@pytest.fixture
def executor():
    return Executor()

@pytest.mark.asyncio
async def test_python_execution(executor):
    code = """
print("Hello from Python!")
x = 5 + 3
print(f"Result: {x}")
"""
    result = await executor.execute_code(code, runtime="python")
    
    assert result["status"] == "success"
    assert result["return_code"] == 0
    assert "Hello from Python!" in result["stdout"]
    assert "Result: 8" in result["stdout"]
    assert result["runtime"] == "python"
    assert "execution_time" in result
    
@pytest.mark.asyncio
async def test_node_execution(executor):
    code = """
console.log("Hello from Node!");
const x = 5 + 3;
console.log(`Result: ${x}`);
"""
    result = await executor.execute_code(code, runtime="node")
    
    assert result["status"] == "success"
    assert result["return_code"] == 0
    assert "Hello from Node!" in result["stdout"]
    assert "Result: 8" in result["stdout"]
    assert result["runtime"] == "node"
    
@pytest.mark.asyncio
async def test_bash_execution(executor):
    code = """
echo "Hello from Bash!"
x=$((5 + 3))
echo "Result: $x"
"""
    result = await executor.execute_code(code, runtime="bash")
    
    assert result["status"] == "success"
    assert result["return_code"] == 0
    assert "Hello from Bash!" in result["stdout"]
    assert "Result: 8" in result["stdout"]
    assert result["runtime"] == "bash"
    
@pytest.mark.asyncio
async def test_runtime_detection(executor):
    # Python detection
    py_code = "print('Python detected')"
    result = await executor.execute_code(py_code)
    assert result["runtime"] == "python"
    
    # Node detection  
    js_code = "console.log('Node detected');"
    result = await executor.execute_code(js_code)
    assert result["runtime"] == "node"
    
    # Bash detection
    sh_code = "echo 'Bash detected'"
    result = await executor.execute_code(sh_code)
    assert result["runtime"] == "bash"
    
@pytest.mark.asyncio
async def test_execution_timeout(executor):
    code = """
import time
time.sleep(2)
"""
    result = await executor.execute_code(code, timeout=1)
    assert result["status"] == "timeout"
    assert "timed out" in result["error"]
    
@pytest.mark.asyncio
async def test_execution_error(executor):
    code = "undefined_function()"
    result = await executor.execute_code(code)
    assert result["status"] == "error"
    assert result["return_code"] != 0
    
@pytest.mark.asyncio
async def test_environment_vars(executor):
    code = """
import os
print(f"TEST_VAR={os.environ.get('TEST_VAR')}")
"""
    env = {"TEST_VAR": "123"}
    result = await executor.execute_code(code, env=env)
    assert result["status"] == "success"
    assert "TEST_VAR=123" in result["stdout"]
    
@pytest.mark.asyncio
async def test_cleanup(executor):
    code = "print('Testing cleanup')"
    await executor.execute_code(code)
    
    # Check temp directory is clean
    files = list(Path(executor.runtime_manager.temp_dir).glob("*"))
    assert len(files) == 0
    
@pytest.mark.asyncio
async def test_execution_history(executor):
    code = "print('Testing history')"
    result = await executor.execute_code(code)
    
    last_execution = executor.runtime_manager.last_execution
    assert last_execution["code_hash"] == hash(code)
    assert last_execution["runtime"] == "python"
    assert last_execution["result"] == result

@pytest.mark.asyncio
async def test_execute_script():
    """Test executing existing script files."""
    executor = Executor()
    
    # Test bash script
    result = await executor.execute_code(
        Path("test_scripts/hello.sh").read_text(),
        runtime="bash"
    )
    assert "Hello from bash" in result["stdout"].lower()
    
    # Test python script
    result = await executor.execute_code(
        Path("test_scripts/hello.py").read_text(),
        runtime="python"
    )
    assert "Hello from python" in result["stdout"].lower()
    
    # Test node script
    result = await executor.execute_code(
        Path("test_scripts/hello.js").read_text(),
        runtime="node"
    )
    assert "Hello from node" in result["stdout"].lower()
    
@pytest.mark.asyncio
async def test_runtime_errors():
    """Test various runtime error conditions."""
    executor = Executor()
    
    # Test invalid runtime
    with pytest.raises(ValueError):
        await executor.execute_code("print(1)", runtime="invalid")
        
    # Test missing runtime executable
    executor.runtime_manager.runtimes["test"] = "/nonexistent"
    with pytest.raises(ValueError):
        await executor.execute_code("test", runtime="test")