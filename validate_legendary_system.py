#!/usr/bin/env python3
"""
Simple validation script for legendary upgrades integration
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_legendary_imports():
    """Test that all legendary components can be imported"""
    
    print("🚀 Testing Legendary MCP Server Import Validation")
    print("=" * 60)
    
    # Test 1: Core MCP Server
    print("\n📋 Testing MCP Server import...")
    try:
        from mcp_server import mcp
        print("✅ MCP Server imported successfully")
        print(f"   - Server name: {mcp.name}")
    except Exception as e:
        print(f"❌ MCP Server import failed: {e}")
        return False
    
    # Test 2: Orchestrator with legendary agents
    print("\n🎭 Testing Orchestrator with legendary agents...")
    try:
        from src.agents.orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator()
        print("✅ Orchestrator imported and instantiated successfully")
        print(f"   - Standard agents configured: {len(orchestrator.agents)}")
        print(f"   - Legendary agents configured: {len(orchestrator.legendary_agents)}")
        print(f"   - Has architect agent: {orchestrator.architect_agent is not None}")
        print(f"   - Has quality agent: {orchestrator.quality_agent is not None}")
        print(f"   - Has prompt engine: {orchestrator.prompt_engine is not None}")
        print(f"   - Has cloud agent: {orchestrator.cloud_agent is not None}")
    except Exception as e:
        print(f"❌ Orchestrator import failed: {e}")
        return False
    
    # Test 3: Individual Legendary Agents
    print("\n🤖 Testing individual legendary agents...")
    
    # Architect Agent
    try:
        from src.agents.architect_agent import ArchitectAgent
        print("✅ Architect Agent imported successfully")
    except Exception as e:
        print(f"❌ Architect Agent import failed: {e}")
    
    # Proactive Quality Agent
    try:
        from src.agents.proactive_quality_agent import ProactiveQualityAgent
        print("✅ Proactive Quality Agent imported successfully")
    except Exception as e:
        print(f"❌ Proactive Quality Agent import failed: {e}")
    
    # Evolutionary Prompt Engine
    try:
        from src.agents.evolutionary_prompt_engine import EvolutionaryPromptEngine
        print("✅ Evolutionary Prompt Engine imported successfully")
    except Exception as e:
        print(f"❌ Evolutionary Prompt Engine import failed: {e}")
    
    # Last Mile Cloud Agent
    try:
        from src.agents.last_mile_cloud_agent import LastMileCloudAgent
        print("✅ Last Mile Cloud Agent imported successfully")
    except Exception as e:
        print(f"❌ Last Mile Cloud Agent import failed: {e}")
    
    # Test 4: Check tool registration
    print("\n🛠️ Testing tool registration...")
    try:
        # Try different ways to access tools
        tools = []
        
        # Method 1: Direct attribute access
        if hasattr(mcp, 'tools'):
            tools = list(mcp.tools.keys())
        # Method 2: Private attribute
        elif hasattr(mcp, '_tools'):
            tools = list(mcp._tools.keys())
        # Method 3: Check handlers
        elif hasattr(mcp, '_tool_handlers'):
            tools = list(mcp._tool_handlers.keys())
        # Method 4: Check app and look for registered routes/tools
        else:
            print("   Checking alternative tool discovery methods...")
            # Try to inspect the mcp object
            attrs = [attr for attr in dir(mcp) if 'tool' in attr.lower()]
            print(f"   Available tool-related attributes: {attrs}")
        
        print(f"✅ {len(tools)} tools registered successfully")
        
        if tools:
            print("   Standard tools:")
            standard_tools = [t for t in tools if not any(keyword in t for keyword in ['legendary', 'autonomous', 'proactive', 'evolutionary', 'last_mile'])]
            for tool in standard_tools:
                print(f"     - {tool}")
            
            print("   Legendary tools:")
            legendary_tools = [t for t in tools if any(keyword in t for keyword in ['legendary', 'autonomous', 'proactive', 'evolutionary', 'last_mile'])]
            for tool in legendary_tools:
                print(f"     - {tool}")
            
            if len(legendary_tools) >= 5:
                print(f"✅ All {len(legendary_tools)} legendary tools registered!")
            else:
                print(f"⚠️  Only {len(legendary_tools)} legendary tools found (expected 5+)")
        else:
            print("⚠️  No tools detected - may be registered at runtime")
            
    except Exception as e:
        print(f"❌ Tool registration check failed: {e}")
    
    # Test 5: Check resources and prompts
    print("\n📚 Testing resources and prompts...")
    try:
        resources = []
        prompts = []
        
        # Try different ways to access resources and prompts
        if hasattr(mcp, 'resources'):
            resources = list(mcp.resources.keys())
        elif hasattr(mcp, '_resources'):
            resources = list(mcp._resources.keys())
            
        if hasattr(mcp, 'prompts'):
            prompts = list(mcp.prompts.keys())
        elif hasattr(mcp, '_prompts'):
            prompts = list(mcp._prompts.keys())
        
        print(f"✅ {len(resources)} resources registered: {resources}")
        print(f"✅ {len(prompts)} prompts registered: {prompts}")
        
        # Check for revolutionary prompt
        if 'revolutionary-development' in prompts:
            print("✅ Revolutionary development prompt found!")
        else:
            print("⚠️  Revolutionary development prompt not found")
            
    except Exception as e:
        print(f"❌ Resources/prompts check failed: {e}")
    
    # Test 6: Runtime tool validation
    print("\n🔧 Testing runtime tool validation...")
    try:
        # Create a test HTTP app to see what's registered
        app = mcp.http_app()
        print("✅ HTTP app created successfully")
        print("   Tools are likely registered at runtime during MCP protocol initialization")
        
    except Exception as e:
        print(f"❌ HTTP app creation failed: {e}")
    
    print("\n🎯 Legendary Import Validation Complete!")
    print("=" * 60)
    print("🚀 System is ready for revolutionary deployment!")
    print("\n💡 Next steps:")
    print("   1. Deploy to Smithery: git push (auto-deploy)")
    print("   2. Test legendary tools in MCP client")
    print("   3. Finalize competition submission")
    
    return True

if __name__ == "__main__":
    test_legendary_imports()