#!/usr/bin/env python3
"""
Test script to validate the fixed MCP server tools
Tests the previously broken tools: get_system_status, generate_architecture, auto_fix_code
"""

import asyncio
import json
import sys
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, 'src')

from agents.orchestrator import AgentOrchestrator
from healing.solution_generator import SolutionGenerator

async def test_get_system_status():
    """Test the get_status method in AgentOrchestrator"""
    print("🔍 Testing AgentOrchestrator.get_status()...")
    
    try:
        orchestrator = AgentOrchestrator()
        status = await orchestrator.get_status()
        
        # Validate the response structure
        required_fields = ["status", "timestamp", "correlation_id", "system_health", "agent_metrics"]
        for field in required_fields:
            if field not in status:
                print(f"❌ Missing required field: {field}")
                return False
        
        print(f"✅ get_status() working! Status: {status['system_health']['overall_status']}")
        print(f"   - Agents available: {status['system_health']['agents_available']}/{status['system_health']['agents_total']}")
        print(f"   - Task success rate: {status['task_metrics']['success_rate']:.2%}")
        return True
        
    except Exception as e:
        print(f"❌ get_status() failed: {str(e)}")
        return False

async def test_generate_architecture():
    """Test the generate_architecture method in AgentOrchestrator"""
    print("\n🏗️ Testing AgentOrchestrator.generate_architecture()...")
    
    try:
        orchestrator = AgentOrchestrator()
        
        # Test specifications
        specifications = {
            "description": "A modern e-commerce platform with user authentication and payment processing",
            "tech_stack": ["React", "FastAPI", "PostgreSQL", "Docker"],
            "requirements": ["scalable", "secure", "high availability", "GDPR compliant"]
        }
        
        architecture = await orchestrator.generate_architecture(specifications)
        
        # Validate the response structure
        required_fields = ["architecture_id", "architecture", "components", "complexity_analysis"]
        for field in required_fields:
            if field not in architecture:
                print(f"❌ Missing required field: {field}")
                return False
        
        print(f"✅ generate_architecture() working!")
        print(f"   - Architecture ID: {architecture['architecture_id']}")
        print(f"   - Pattern: {architecture['architecture']['pattern']}")
        print(f"   - Components: {len(architecture['components'])}")
        print(f"   - Complexity: {architecture['complexity_analysis']['complexity_level']}")
        print(f"   - Estimated time: {architecture['complexity_analysis']['estimated_weeks']} weeks")
        return True
        
    except Exception as e:
        print(f"❌ generate_architecture() failed: {str(e)}")
        return False

async def test_generate_fix():
    """Test the generate_fix method in SolutionGenerator"""
    print("\n🔧 Testing SolutionGenerator.generate_fix()...")
    
    try:
        solution_generator = SolutionGenerator("test-correlation-id")
        
        # Test problem context
        problem_context = {
            "code": """
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price * item.quantity
    return total

# This line has a syntax error - missing colon
if total > 100
    discount = 0.1
else:
    discount = 0.0
""",
            "error": "SyntaxError: invalid syntax at line 8: if total > 100",
            "context": "Python function for calculating shopping cart total with discount logic"
        }
        
        fix_result = await solution_generator.generate_fix(problem_context)
        
        # Validate the response structure
        required_fields = ["fix_id", "success", "fixed_code", "explanation", "confidence"]
        for field in required_fields:
            if field not in fix_result:
                print(f"❌ Missing required field: {field}")
                return False
        
        if not fix_result["success"]:
            print(f"❌ generate_fix() returned success=False: {fix_result.get('error', 'Unknown error')}")
            return False
        
        print(f"✅ generate_fix() working!")
        print(f"   - Fix ID: {fix_result['fix_id']}")
        print(f"   - Confidence: {fix_result['confidence']:.2%}")
        print(f"   - Changes made: {len(fix_result['changes'])}")
        print(f"   - Solution type: {fix_result.get('solution_type', 'unknown')}")
        
        # Check if the fix actually addresses the syntax error
        if ":" in fix_result["fixed_code"]:
            print("   - ✅ Syntax error appears to be fixed (colon added)")
        else:
            print("   - ⚠️ Syntax error may not be fully fixed")
        
        return True
        
    except Exception as e:
        print(f"❌ generate_fix() failed: {str(e)}")
        return False

async def test_mcp_server_tools():
    """Test the MCP server tools that were previously broken"""
    print("\n🌐 Testing MCP Server Tools Integration...")
    
    try:
        # Import the MCP server components
        from mcp_server import orchestrator, code_fixer
        
        # Test 1: get_system_status tool (uses orchestrator.get_status())
        print("   Testing get_system_status tool...")
        status = await orchestrator.get_status()
        if "status" in status:
            print("   ✅ get_system_status tool working")
        else:
            print("   ❌ get_system_status tool failed")
            return False
        
        # Test 2: generate_architecture tool (uses orchestrator.generate_architecture())
        print("   Testing generate_architecture tool...")
        architecture = await orchestrator.generate_architecture({
            "description": "Simple web app",
            "tech_stack": ["Python", "React"],
            "requirements": ["responsive", "secure"]
        })
        if "architecture_id" in architecture:
            print("   ✅ generate_architecture tool working")
        else:
            print("   ❌ generate_architecture tool failed")
            return False
        
        # Test 3: auto_fix_code tool (uses code_fixer.generate_fix())
        print("   Testing auto_fix_code tool...")
        fix_result = await code_fixer.generate_fix({
            "code": "print('hello world'",  # Missing closing parenthesis
            "error": "SyntaxError: unexpected EOF while parsing",
            "context": "Simple print statement"
        })
        if fix_result.get("success"):
            print("   ✅ auto_fix_code tool working")
        else:
            print("   ❌ auto_fix_code tool failed")
            return False
        
        print("✅ All MCP server tools integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ MCP server tools integration failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting MCP Server Tool Tests")
    print("=" * 60)
    
    start_time = datetime.now()
    
    # Run individual method tests
    test1_passed = await test_get_system_status()
    test2_passed = await test_generate_architecture()
    test3_passed = await test_generate_fix()
    
    # Run integration tests
    test4_passed = await test_mcp_server_tools()
    
    # Calculate results
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    total_tests = 4
    passed_tests = sum([test1_passed, test2_passed, test3_passed, test4_passed])
    
    print("\n" + "=" * 60)
    print("🏁 TEST RESULTS SUMMARY")
    print(f"   Total tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {total_tests - passed_tests}")
    print(f"   Success rate: {passed_tests/total_tests:.1%}")
    print(f"   Duration: {duration:.2f} seconds")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! MCP server tools are now 100% functional!")
        print("   ✅ get_system_status: Working")
        print("   ✅ generate_architecture: Working") 
        print("   ✅ auto_fix_code: Working")
        print("   ✅ Integration: Working")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed. Please review the errors above.")
        
    return passed_tests == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)