#!/usr/bin/env python3
"""
Repository cleanup validation script
Validates that the repository structure is clean and organized after cleanup
"""

import os
import sys
from pathlib import Path

def validate_directory_structure():
    """Validate that directories are properly organized"""
    root_dir = Path(__file__).parent.parent
    
    # Expected directory structure
    expected_dirs = {
        'api': ['openapi.json', 'openapi.yaml', 'openapi_legendary.yaml'],
        'docs/deployment': ['DEPLOYMENT_COMPLETE.md', 'DESCOPE_CONFIGURATION_GUIDE.md', 'REVOLUTIONARY_DEPLOYMENT_GUIDE.md'],
        'docs/competition': ['COMPETITION_SUBMISSION.md', 'FINAL_COMPLETION_GUIDE.md', 'SUBMISSION_CHECKLIST.md'],
        'tests/integration': ['test_legendary_integration.py', 'final_legendary_test.py', 'validate_legendary_system.py'],
        'tests/competition': ['competition_final_test.py'],
        'archive': ['main.py', 'main_fastapi.py'],
        'src/agents': ['architect_agent.py', 'evolutionary_prompt_engine.py', 'last_mile_cloud_agent.py', 'proactive_quality_agent.py']
    }
    
    # Essential root files that should remain
    essential_root_files = [
        'mcp_server.py',
        'requirements.txt', 
        'pyproject.toml',
        'README.md',
        'Dockerfile',
        'smithery.json',
        'smithery.yaml'
    ]
    
    print("🧹 Repository Cleanup Validation")
    print("=" * 50)
    
    # Check directory structure
    all_valid = True
    for dir_path, expected_files in expected_dirs.items():
        full_dir = root_dir / dir_path
        if not full_dir.exists():
            print(f"❌ Missing directory: {dir_path}")
            all_valid = False
            continue
            
        print(f"✅ Directory exists: {dir_path}")
        
        # Check files in directory
        for expected_file in expected_files:
            file_path = full_dir / expected_file
            if file_path.exists():
                print(f"  ✅ {expected_file}")
            else:
                print(f"  ❌ Missing: {expected_file}")
                all_valid = False
    
    print("\n📁 Root Directory Files:")
    for essential_file in essential_root_files:
        file_path = root_dir / essential_file
        if file_path.exists():
            print(f"  ✅ {essential_file}")
        else:
            print(f"  ❌ Missing: {essential_file}")
            all_valid = False
    
    # Check that cleanup removed unwanted files
    print("\n🗑️ Cleanup Verification:")
    unwanted_files = [
        'competition_final_test.py',  # Should be in tests/competition/
        'COMPETITION_SUBMISSION.md',  # Should be in docs/competition/
        'DEPLOYMENT_COMPLETE.md',     # Should be in docs/deployment/
        'FINAL_COMPLETION_GUIDE.md',  # Should be in docs/competition/
        'SUBMISSION_CHECKLIST.md'     # Should be in docs/competition/
    ]
    
    for unwanted_file in unwanted_files:
        file_path = root_dir / unwanted_file
        if not file_path.exists():
            print(f"  ✅ Removed from root: {unwanted_file}")
        else:
            print(f"  ❌ Still in root: {unwanted_file}")
            all_valid = False
    
    # Check for cache directories (should be cleaned)
    cache_dirs = ['__pycache__', '.pytest_cache', 'htmlcov']
    print("\n🧽 Cache Cleanup:")
    for cache_dir in cache_dirs:
        cache_path = root_dir / cache_dir
        if not cache_path.exists():
            print(f"  ✅ Cleaned: {cache_dir}")
        else:
            print(f"  ⚠️  Still exists: {cache_dir} (will be regenerated)")
    
    return all_valid

def validate_imports():
    """Validate that imports still work after cleanup"""
    print("\n🔍 Import Validation:")
    
    # Add parent directory to path for imports
    root_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(root_dir))
    
    try:
        import mcp_server
        print("  ✅ mcp_server imports successfully")
    except ImportError as e:
        print(f"  ❌ mcp_server import failed: {e}")
        return False
    
    try:
        from src.agents import architect_agent, evolutionary_prompt_engine, last_mile_cloud_agent, proactive_quality_agent
        print("  ✅ All legendary agents import successfully")
    except ImportError as e:
        print(f"  ❌ Legendary agents import failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Multi-Agent Orchestrator MCP - Repository Cleanup Validation")
    print("=" * 70)
    
    structure_valid = validate_directory_structure()
    imports_valid = validate_imports()
    
    print("\n" + "=" * 70)
    if structure_valid and imports_valid:
        print("🎉 VALIDATION PASSED - Repository is clean and organized!")
        print("✨ Ready for professional deployment and development")
        sys.exit(0)
    else:
        print("❌ VALIDATION FAILED - Issues found with repository structure")
        sys.exit(1)