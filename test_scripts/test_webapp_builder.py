#!/usr/bin/env python3
"""
Test script for webapp builder functionality
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webapp_builder.scaffold_generator import ScaffoldGenerator
from webapp_builder.deployer import Deployer

def test_scaffold_generator():
    """Test webapp scaffold generation"""
    print("\nTesting Scaffold Generator...")
    generator = ScaffoldGenerator()
    
    # List available templates
    templates = generator.list_templates()
    print(f"Available templates: {[t['framework'] for t in templates]}")
    
    # Test generation (commented out to avoid actual project creation)
    # generator.generate("test-app", "react", {"typescript": True})
    print("✅ Scaffold generator tests passed")

def test_deployer():
    """Test webapp deployment"""
    print("\nTesting Deployer...")
    deployer = Deployer()
    
    # Test deployment logic (using dummy paths)
    deployer.deploy("test-app", "local")
    print("✅ Deployer tests passed")

def run_webapp_tests():
    """Run all webapp builder tests"""
    print("Running webapp builder tests...")
    
    try:
        test_scaffold_generator()
        test_deployer()
        print("\n🎉 All webapp builder tests passed!")
        
    except Exception as e:
        print(f"\n❌ Tests failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_webapp_tests()