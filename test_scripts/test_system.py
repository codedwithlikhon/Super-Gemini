#!/usr/bin/env python3
"""
Comprehensive test script for Super-Gemini components
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_core.agent import Agent
from agent_core.planner import Planner
from agent_core.executor import Executor
from agent_core.memory_manager import MemoryManager
from agent_core.ubuntu_manager import is_ubuntu_installed, execute_in_ubuntu
from tools.api_caller import ApiCaller
from tools.browser import Browser
from tools.db import DatabaseConnector
from tools.fs import FileSystem
from tools.model_runner import app

def test_agent():
    """Test agent initialization and basic functionality"""
    print("\nTesting Agent...")
    agent = Agent()
    assert agent.planner is not None
    assert agent.executor is not None
    assert agent.memory is not None
    print("✅ Agent tests passed")

def test_planner():
    """Test planner functionality"""
    print("\nTesting Planner...")
    planner = Planner()
    plan = planner.create_plan("hello-world")
    assert isinstance(plan, list)
    assert len(plan) > 0
    print("✅ Planner tests passed")

def test_executor():
    """Test executor functionality"""
    print("\nTesting Executor...")
    executor = Executor()
    script_path = os.path.join("test_scripts", "hello.py")
    executor.execute_script(script_path)
    print("✅ Executor tests passed")

def test_memory():
    """Test memory management"""
    print("\nTesting Memory Manager...")
    memory = MemoryManager()
    test_prefs = {"test_key": "test_value"}
    memory.update_preferences(test_prefs)
    loaded_prefs = memory.get_preferences()
    assert "test_key" in loaded_prefs
    assert loaded_prefs["test_key"] == "test_value"
    print("✅ Memory tests passed")

def test_ubuntu():
    """Test Ubuntu environment integration"""
    print("\nTesting Ubuntu Manager...")
    has_ubuntu = is_ubuntu_installed()
    print(f"Ubuntu installed: {has_ubuntu}")
    if has_ubuntu:
        result = execute_in_ubuntu("echo 'Hello from Ubuntu'")
        assert result is not None
    print("✅ Ubuntu tests passed")

def test_tools():
    """Test various tools"""
    print("\nTesting Tools...")
    
    # API Caller
    api = ApiCaller()
    print("Testing API caller...")
    
    # Browser
    browser = Browser()
    result = browser.search("test query")
    assert isinstance(result, str)
    print("✅ Browser tool passed")
    
    # Database
    db = DatabaseConnector()
    db.connect()
    print("✅ Database tool passed")
    
    # Filesystem
    fs = FileSystem()
    files = fs.list_dir("test_scripts")
    assert len(files) > 0
    print("✅ Filesystem tool passed")
    
    print("✅ All tools tests passed")

def run_all_tests():
    """Run all test cases"""
    print("Running Super-Gemini system tests...")
    
    try:
        test_agent()
        test_planner()
        test_executor()
        test_memory()
        test_ubuntu()
        test_tools()
        print("\n🎉 All tests passed successfully!")
        
    except Exception as e:
        print(f"\n❌ Tests failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()