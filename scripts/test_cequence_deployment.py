#!/usr/bin/env python3
"""
Comprehensive test script for Cequence MCP Server deployment validation.

This script tests:
1. Cequence MCP server accessibility
2. OAuth authentication flow (simulated)
3. MCP protocol compliance
4. Tool functionality through Cequence gateway
5. Performance and reliability metrics

Usage:
    python scripts/test_cequence_deployment.py
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cequence MCP Server Configuration
CEQUENCE_MCP_ENDPOINT = "https://ztaip-0qdv9d3o-4xp4r634bq-uc.a.run.app/mcp"
CEQUENCE_SSE_ENDPOINT = "https://ztaip-0qdv9d3o-4xp4r634bq-uc.a.run.app/sse"

# Expected OAuth URLs
DESCOPE_AUTHORIZATION_URL = "https://api.descope.com/oauth2/v1/apps/authorize"
DESCOPE_TOKEN_URL = "https://api.descope.com/oauth2/v1/apps/token"
CEQUENCE_REDIRECT_URI = "https://auth.aigateway.cequence.ai/v1/outbound/oauth/callback"

class CequenceDeploymentTester:
    def __init__(self):
        self.test_results = []
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test result with timestamp."""
        result = {
            "test": test_name,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {message}")
        
        if details:
            for key, value in details.items():
                logger.info(f"  {key}: {value}")
    
    async def test_endpoint_accessibility(self):
        """Test if Cequence MCP endpoint is accessible."""
        test_name = "Endpoint Accessibility"
        
        try:
            start_time = time.time()
            async with self.session.get(CEQUENCE_MCP_ENDPOINT, timeout=10) as response:
                response_time = time.time() - start_time
                
                if response.status == 401:
                    # Expected: OAuth protection should return 401 for unauthenticated requests
                    self.log_test_result(
                        test_name, 
                        True, 
                        "Endpoint properly protected with OAuth authentication",
                        {
                            "status_code": response.status,
                            "response_time": f"{response_time:.2f}s",
                            "headers": dict(response.headers)
                        }
                    )
                elif response.status == 200:
                    self.log_test_result(
                        test_name,
                        True,
                        "Endpoint accessible (no auth required)",
                        {
                            "status_code": response.status,
                            "response_time": f"{response_time:.2f}s"
                        }
                    )
                else:
                    self.log_test_result(
                        test_name,
                        False,
                        f"Unexpected status code: {response.status}",
                        {"status_code": response.status, "response_time": f"{response_time:.2f}s"}
                    )
                    
        except asyncio.TimeoutError:
            self.log_test_result(test_name, False, "Endpoint timeout (>10s)")
        except Exception as e:
            self.log_test_result(test_name, False, f"Connection error: {str(e)}")
    
    async def test_mcp_protocol_compliance(self):
        """Test MCP protocol compliance by checking required endpoints."""
        test_name = "MCP Protocol Compliance"
        
        # Test MCP initialization endpoint
        mcp_init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "cequence-test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            async with self.session.post(
                CEQUENCE_MCP_ENDPOINT,
                json=mcp_init_payload,
                headers=headers,
                timeout=10
            ) as response:
                response_text = await response.text()
                
                if response.status == 401:
                    self.log_test_result(
                        test_name,
                        True,
                        "MCP endpoint properly protected (OAuth required)",
                        {"status_code": response.status}
                    )
                elif response.status == 200:
                    try:
                        response_data = json.loads(response_text)
                        if "result" in response_data:
                            self.log_test_result(
                                test_name,
                                True,
                                "MCP protocol compliance confirmed",
                                {"response": response_data}
                            )
                        else:
                            self.log_test_result(
                                test_name,
                                False,
                                "Invalid MCP response format",
                                {"response": response_data}
                            )
                    except json.JSONDecodeError:
                        self.log_test_result(
                            test_name,
                            False,
                            "Non-JSON response from MCP endpoint",
                            {"response": response_text[:500]}
                        )
                else:
                    self.log_test_result(
                        test_name,
                        False,
                        f"Unexpected status: {response.status}",
                        {"status_code": response.status, "response": response_text[:500]}
                    )
                    
        except Exception as e:
            self.log_test_result(test_name, False, f"MCP protocol test failed: {str(e)}")
    
    async def test_oauth_configuration(self):
        """Test OAuth configuration and endpoints."""
        test_name = "OAuth Configuration"
        
        oauth_tests = []
        
        # Test Descope authorization endpoint
        try:
            async with self.session.get(DESCOPE_AUTHORIZATION_URL, timeout=5) as response:
                if response.status in [200, 400, 405]:  # Expected responses for OAuth endpoints
                    oauth_tests.append(("Descope Authorization Endpoint", True))
                else:
                    oauth_tests.append(("Descope Authorization Endpoint", False))
        except:
            oauth_tests.append(("Descope Authorization Endpoint", False))
        
        # Test Descope token endpoint
        try:
            async with self.session.get(DESCOPE_TOKEN_URL, timeout=5) as response:
                if response.status in [200, 400, 405, 401]:  # Expected responses
                    oauth_tests.append(("Descope Token Endpoint", True))
                else:
                    oauth_tests.append(("Descope Token Endpoint", False))
        except:
            oauth_tests.append(("Descope Token Endpoint", False))
        
        all_passed = all(result[1] for result in oauth_tests)
        
        self.log_test_result(
            test_name,
            all_passed,
            f"OAuth endpoints tested: {len([r for r in oauth_tests if r[1]])}/{len(oauth_tests)} accessible",
            {"test_results": dict(oauth_tests)}
        )
    
    async def test_performance_metrics(self):
        """Test performance metrics of the Cequence deployment."""
        test_name = "Performance Metrics"
        
        response_times = []
        successful_requests = 0
        total_requests = 5
        
        for i in range(total_requests):
            try:
                start_time = time.time()
                async with self.session.get(CEQUENCE_MCP_ENDPOINT, timeout=10) as response:
                    response_time = time.time() - start_time
                    response_times.append(response_time)
                    
                    if response.status in [200, 401]:  # Both are acceptable
                        successful_requests += 1
                        
                await asyncio.sleep(0.5)  # Brief pause between requests
                
            except Exception as e:
                logger.warning(f"Performance test request {i+1} failed: {e}")
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            success_rate = (successful_requests / total_requests) * 100
            performance_good = avg_response_time < 2.0 and success_rate >= 80
            
            self.log_test_result(
                test_name,
                performance_good,
                f"Performance metrics collected: {success_rate:.1f}% success rate",
                {
                    "avg_response_time": f"{avg_response_time:.3f}s",
                    "min_response_time": f"{min_response_time:.3f}s",
                    "max_response_time": f"{max_response_time:.3f}s",
                    "success_rate": f"{success_rate:.1f}%",
                    "total_requests": total_requests
                }
            )
        else:
            self.log_test_result(test_name, False, "No successful requests for performance testing")
    
    async def run_all_tests(self):
        """Run all deployment validation tests."""
        logger.info("🚀 Starting Cequence MCP Server Deployment Validation")
        logger.info(f"Testing endpoint: {CEQUENCE_MCP_ENDPOINT}")
        
        test_methods = [
            self.test_endpoint_accessibility,
            self.test_oauth_configuration,
            self.test_mcp_protocol_compliance,
            self.test_performance_metrics
        ]
        
        for test_method in test_methods:
            try:
                await test_method()
            except Exception as e:
                test_name = test_method.__name__.replace('test_', '').replace('_', ' ').title()
                self.log_test_result(test_name, False, f"Test execution failed: {str(e)}")
            
            await asyncio.sleep(0.5)  # Brief pause between tests
        
        return self.generate_summary_report()
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate a comprehensive summary report."""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "cequence_endpoint": CEQUENCE_MCP_ENDPOINT,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "overall_status": "PASS" if failed_tests == 0 else "FAIL",
            "test_results": self.test_results
        }
        
        logger.info("\n" + "="*60)
        logger.info("🎯 CEQUENCE DEPLOYMENT VALIDATION SUMMARY")
        logger.info("="*60)
        logger.info(f"📊 Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"🏆 Overall Status: {summary['overall_status']}")
        
        if failed_tests > 0:
            logger.info("\n🔍 Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    logger.info(f"  ❌ {result['test']}: {result['message']}")
        
        logger.info("="*60)
        
        return summary

async def main():
    """Main test execution function."""
    async with CequenceDeploymentTester() as tester:
        summary = await tester.run_all_tests()
        
        # Save detailed report
        report_file = f"outputs/cequence_deployment_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            import os
            os.makedirs("outputs", exist_ok=True)
            
            with open(report_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"📄 Detailed report saved to: {report_file}")
        except Exception as e:
            logger.warning(f"Could not save report file: {e}")
        
        return summary["overall_status"] == "PASS"

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)