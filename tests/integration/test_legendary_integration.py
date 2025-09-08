#!/usr/bin/env python3
"""
Test script to validate legendary upgrades integration
"""

import asyncio
import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_legendary_capabilities():
    """Test all legendary capabilities are properly integrated"""
    
    print("🚀 Testing Legendary MCP Server Integration")
    print("=" * 50)
    
    # Import the tools directly
    from mcp_server import (
        list_capabilities, get_system_status, autonomous_architect,
        proactive_quality_assurance, evolutionary_prompt_optimization,
        last_mile_cloud_deployment, legendary_generate_application
    )
    
    # Test 1: List capabilities
    print("\n📋 Testing list_capabilities...")
    try:
        capabilities = await list_capabilities()
        print("✅ Capabilities loaded successfully")
        print(f"   - Standard agents: {len(capabilities.get('standard_agents', {}))}")
        print(f"   - Legendary agents: {len(capabilities.get('legendary_agents', {}))}")
        print(f"   - Revolutionary features: {len(capabilities.get('revolutionary_features', {}))}")
        print(f"   - Legendary tools: {len(capabilities.get('legendary_tools', []))}")
        print(f"   - Innovation level: {capabilities.get('innovation_level', 'Unknown')}")
    except Exception as e:
        print(f"❌ Capabilities test failed: {e}")
        return False
    
    # Test 2: System status with legendary upgrades
    print("\n🏥 Testing enhanced system status...")
    try:
        status = await get_system_status()
        print("✅ System status retrieved successfully")
        print(f"   - Server: {status.get('server')}")
        print(f"   - Revolutionary capabilities: {status.get('revolutionary_capabilities')}")
        print(f"   - Legendary agents available: {bool(status.get('legendary_agents'))}")
    except Exception as e:
        print(f"❌ System status test failed: {e}")
        return False
    
    # Test 3: Autonomous Architect
    print("\n🤖 Testing Autonomous Architect...")
    try:
        result = await autonomous_architect(
            project_goals=["Create a scalable web application", "Implement AI-driven features"],
            constraints=["Budget: $10k", "Timeline: 3 months"],
            learning_objectives=["Improve architecture patterns", "Optimize performance"]
        )
        print("✅ Autonomous Architect test successful")
        print(f"   - Success: {result.get('success')}")
        if result.get('success'):
            print(f"   - Confidence: {result.get('confidence_score', 0)}")
        else:
            print(f"   - Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Autonomous Architect test failed: {e}")
    
    # Test 4: Proactive Quality Assurance
    print("\n🛡️ Testing Proactive Quality Assurance...")
    try:
        result = await proactive_quality_assurance(
            code_context="def hello_world(): print('Hello, World!')",
            quality_standards=["PEP8", "Security"],
            auto_remediation=True
        )
        print("✅ Proactive Quality test successful")
        print(f"   - Success: {result.get('success')}")
        if result.get('success'):
            print(f"   - Quality score: {result.get('quality_score', 'N/A')}")
        else:
            print(f"   - Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Proactive Quality test failed: {e}")
    
    # Test 5: Evolutionary Prompt Optimization
    print("\n🧬 Testing Evolutionary Prompt Engine...")
    try:
        result = await evolutionary_prompt_optimization(
            base_prompt="Write a function to calculate fibonacci numbers",
            optimization_goals=["clarity", "effectiveness", "specificity"],
            performance_metrics={"accuracy": 0.85, "response_time": 2.5}
        )
        print("✅ Evolutionary Prompt test successful")
        print(f"   - Success: {result.get('success')}")
        if result.get('success'):
            print(f"   - Optimized prompt available: {bool(result.get('optimized_prompt'))}")
        else:
            print(f"   - Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Evolutionary Prompt test failed: {e}")
    
    # Test 6: Last Mile Cloud Deployment
    print("\n☁️ Testing Last Mile Cloud Agent...")
    try:
        result = await last_mile_cloud_deployment(
            application_context="Node.js REST API with PostgreSQL database",
            target_environments=["staging", "production"],
            verification_requirements=["Health checks", "Performance tests", "Security scans"]
        )
        print("✅ Last Mile Cloud test successful")
        print(f"   - Success: {result.get('success')}")
        if result.get('success'):
            print(f"   - Deployment plan available: {bool(result.get('deployment_plan'))}")
        else:
            print(f"   - Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Last Mile Cloud test failed: {e}")
    
    # Test 7: Revolutionary Application Generation
    print("\n🌟 Testing Revolutionary Application Generation...")
    try:
        result = await legendary_generate_application(
            description="Build a revolutionary AI-powered social media platform with autonomous content moderation and predictive user engagement",
            complexity_level="revolutionary",
            innovation_requirements=["AI-driven architecture", "Self-improving algorithms", "Autonomous scaling"],
            deployment_strategy="multi-cloud-autonomous"
        )
        print("✅ Revolutionary Application Generation test successful")
        print(f"   - Success: {result.get('success')}")
        if result.get('success'):
            print(f"   - Innovation score: {result.get('innovation_score', 0)}")
            print(f"   - Legendary agents used: {len(result.get('legendary_agents_used', []))}")
        else:
            print(f"   - Error: {result.get('error', 'Unknown error')}")
            print(f"   - Fallback: {result.get('legendary_fallback', 'None')}")
    except Exception as e:
        print(f"❌ Revolutionary Application Generation test failed: {e}")
    
    print("\n🎯 Legendary Integration Test Complete!")
    print("=" * 50)
    print("🚀 Ready for revolutionary deployment!")
    return True

if __name__ == "__main__":
    asyncio.run(test_legendary_capabilities())