import asyncio
import pytest
from dataclasses import dataclass
from typing import Optional

from agent_core.executor import Executor

@dataclass
class TestStep:
    action: str
    script: Optional[str] = None
    command: Optional[str] = None

@pytest.mark.asyncio
async def test_execute_script():
    """Test executing scripts of different types."""
    executor = Executor()
    
    # Test bash script
    result = await executor.execute_script("test_scripts/hello.sh")
    assert "Hello from bash" in result.lower()
    
    # Test python script
    result = await executor.execute_script("test_scripts/hello.py")
    assert "Hello from python" in result.lower()
    
    # Test node script
    result = await executor.execute_script("test_scripts/hello.js")
    assert "Hello from node" in result.lower()
    
    # Test invalid extension
    with pytest.raises(ValueError, match="Unsupported script type"):
        await executor.execute_script("test_scripts/invalid.xyz")

@pytest.mark.asyncio
async def test_execute_step():
    """Test executing individual plan steps."""
    executor = Executor()
    
    # Test script execution step
    step = TestStep(action="execute_script", script="test_scripts/hello.py")
    result = await executor.execute_step(step)
    assert "Hello from python" in result.lower()
    
    # Test Ubuntu command step
    step = TestStep(action="execute_in_ubuntu", command="echo 'Hello from Ubuntu'")
    result = await executor.execute_step(step)
    assert "Hello from Ubuntu" in result.lower()
    
    # Test invalid action
    step = TestStep(action="invalid_action")
    with pytest.raises(ValueError, match="Unknown action type"):
        await executor.execute_step(step)

if __name__ == "__main__":
    asyncio.run(test_execute_script())
    asyncio.run(test_execute_step())