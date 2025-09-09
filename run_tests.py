#!/usr/bin/env python3
"""
Test runner that starts server and runs tests
"""

import subprocess
import time
import sys
import signal
import os

def run_test():
    """Start server and run tests"""
    print("Starting MCP server...")
    
    # Start the server process
    server_process = subprocess.Popen(
        [sys.executable, "mcp_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    try:
        # Run the test
        print("Running Smithery scan simulation...")
        test_process = subprocess.run(
            [sys.executable, "simulate_smithery_scan.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print("Test output:")
        print(test_process.stdout)
        if test_process.stderr:
            print("Test errors:")
            print(test_process.stderr)
            
        return test_process.returncode == 0
        
    finally:
        # Stop the server
        print("Stopping server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()

if __name__ == "__main__":
    success = run_test()
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)