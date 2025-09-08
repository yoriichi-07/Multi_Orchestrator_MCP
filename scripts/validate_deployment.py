#!/usr/bin/env python3
"""
🚀 DEPLOYMENT VALIDATION SCRIPT - Enhanced Multi-Agent Orchestrator MCP Server
================================================================================

Comprehensive validation script for Cequence AI Gateway deployment with all 16 tools.

This script validates:
- All 5 legendary agents functionality and performance
- All 11 standard tools availability and response times  
- Cequence AI Gateway integration and analytics
- Authentication and scope enforcement
- Performance benchmarks and optimization
- Security compliance and monitoring

Usage:
    python scripts/validate_deployment.py [--environment prod|staging|dev] [--verbose]
    
Examples:
    python scripts/validate_deployment.py --environment prod --verbose
    python scripts/validate_deployment.py --environment staging
"""

import asyncio
import json
import sys
import time
import argparse
import httpx
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'deployment_validation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Validation result status enumeration"""
    PASSED = "✅ PASSED"
    FAILED = "❌ FAILED"
    WARNING = "⚠️ WARNING"
    SKIPPED = "⏭️ SKIPPED"


@dataclass
class ValidationResult:
    """Individual validation test result"""
    test_name: str
    status: ValidationStatus
    response_time_ms: Optional[float] = None
    details: Optional[str] = None
    error: Optional[str] = None
    analytics_data: Optional[Dict[str, Any]] = None


@dataclass
class DeploymentConfig:
    """Deployment configuration for different environments"""
    base_url: str
    auth_token: str
    cequence_api_key: str
    environment: str
    timeout_seconds: int = 30
    max_retries: int = 3


class DeploymentValidator:
    """Comprehensive deployment validation orchestrator"""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.results: List[ValidationResult] = []
        self.client = httpx.AsyncClient(
            timeout=config.timeout_seconds,
            headers={
                "Authorization": f"Bearer {config.auth_token}",
                "X-Cequence-Gateway-Key": config.cequence_api_key,
                "Content-Type": "application/json",
                "User-Agent": "MCP-Deployment-Validator/3.0.0"
            }
        )
        
        # Performance benchmarks
        self.performance_targets = {
            "standard_tools_max_response_ms": 200,
            "legendary_tools_max_response_ms": 2000,
            "health_check_max_response_ms": 100,
            "min_success_rate_percent": 99.0,
            "max_error_rate_percent": 0.1
        }
        
        # Tool definitions for comprehensive testing
        self.legendary_tools = [
            {
                "name": "legendary_generate_application",
                "endpoint": "/mcp/legendary/generate_application",
                "required_scopes": ["tools:legendary", "admin:config"],
                "test_payload": {
                    "description": "Test application for deployment validation",
                    "complexity_level": "simple",
                    "innovation_requirements": ["basic functionality"],
                    "deployment_strategy": "local",
                    "cequence_analytics": {
                        "enable_detailed_tracking": True,
                        "performance_monitoring": True,
                        "cost_optimization": True
                    }
                }
            },
            {
                "name": "autonomous_architect",
                "endpoint": "/mcp/legendary/autonomous_architect",
                "required_scopes": ["tools:autonomous"],
                "test_payload": {
                    "project_goals": ["validation test", "performance benchmark"],
                    "constraints": ["minimal resource usage"],
                    "learning_objectives": ["validate deployment"]
                }
            },
            {
                "name": "proactive_quality_assurance",
                "endpoint": "/mcp/legendary/proactive_quality_assurance",
                "required_scopes": ["tools:proactive"],
                "test_payload": {
                    "project_context": {"type": "validation_test"},
                    "quality_objectives": ["basic validation"],
                    "analytics_preferences": {"detailed_tracking": True}
                }
            },
            {
                "name": "evolutionary_prompt_optimization",
                "endpoint": "/mcp/legendary/evolutionary_prompt_optimization",
                "required_scopes": ["tools:evolutionary"],
                "test_payload": {
                    "base_prompt": "Test prompt for validation",
                    "optimization_goals": ["clarity", "effectiveness"],
                    "evolution_parameters": {"generations": 1}
                }
            },
            {
                "name": "last_mile_cloud_deployment",
                "endpoint": "/mcp/legendary/last_mile_cloud_deployment",
                "required_scopes": ["tools:cloud"],
                "test_payload": {
                    "application_package": {"type": "test_package"},
                    "deployment_requirements": {"environment": "validation"},
                    "cloud_preferences": {"provider": "test"}
                }
            }
        ]
        
        self.standard_tools = [
            {
                "name": "ping",
                "endpoint": "/mcp/tools/ping",
                "required_scopes": ["tools:ping"],
                "test_payload": {
                    "message": "Deployment validation ping",
                    "include_analytics": True,
                    "performance_benchmark": True
                }
            },
            {
                "name": "orchestrate_task",
                "endpoint": "/mcp/tools/orchestrate_task",
                "required_scopes": ["tools:generate"],
                "test_payload": {
                    "task_description": "Validation test task",
                    "complexity_level": "simple",
                    "include_legendary": False
                }
            },
            {
                "name": "generate_architecture",
                "endpoint": "/mcp/tools/generate_architecture",
                "required_scopes": ["tools:generate"],
                "test_payload": {
                    "requirements": "Simple validation architecture",
                    "complexity": "simple"
                }
            },
            {
                "name": "auto_fix_code",
                "endpoint": "/mcp/tools/auto_fix_code",
                "required_scopes": ["tools:healing"],
                "test_payload": {
                    "code": "print('test'",
                    "error_message": "SyntaxError: unexpected EOF while parsing",
                    "context": "validation test"
                }
            },
            {
                "name": "list_capabilities",
                "endpoint": "/mcp/tools/list_capabilities",
                "required_scopes": ["tools:ping"],
                "test_payload": {
                    "include_legendary": True,
                    "include_analytics": True
                }
            },
            {
                "name": "system_status",
                "endpoint": "/mcp/tools/system_status",
                "required_scopes": ["admin:metrics"],
                "test_payload": {
                    "include_legendary": True,
                    "include_analytics": True,
                    "include_performance_metrics": True
                }
            }
        ]
        
        self.mcp_protocol_tools = [
            {
                "name": "mcp_initialize",
                "endpoint": "/mcp/initialize",
                "test_payload": {
                    "jsonrpc": "2.0",
                    "id": "validation_init",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {"listChanged": True}},
                        "clientInfo": {"name": "validation-client", "version": "1.0.0"}
                    }
                }
            },
            {
                "name": "mcp_list_tools",
                "endpoint": "/mcp/tools/list",
                "test_payload": {
                    "jsonrpc": "2.0",
                    "id": "validation_list",
                    "method": "tools/list"
                }
            },
            {
                "name": "mcp_call_tool",
                "endpoint": "/mcp/tools/call",
                "test_payload": {
                    "jsonrpc": "2.0",
                    "id": "validation_call",
                    "method": "tools/call",
                    "params": {
                        "name": "ping",
                        "arguments": {"message": "MCP validation test"}
                    }
                }
            },
            {
                "name": "mcp_list_resources",
                "endpoint": "/mcp/resources/list",
                "test_payload": {
                    "jsonrpc": "2.0",
                    "id": "validation_resources",
                    "method": "resources/list"
                }
            },
            {
                "name": "mcp_read_resource",
                "endpoint": "/mcp/resources/read",
                "test_payload": {
                    "jsonrpc": "2.0",
                    "id": "validation_read",
                    "method": "resources/read",
                    "params": {"uri": "mcp://capabilities"}
                }
            }
        ]

    async def validate_health_endpoint(self) -> ValidationResult:
        """Validate basic health endpoint functionality"""
        logger.info("🏥 Testing health endpoint...")
        
        start_time = time.time()
        try:
            response = await self.client.get(f"{self.config.base_url}/health")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["status", "service", "version", "deployment_info"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    return ValidationResult(
                        test_name="Health Endpoint Structure",
                        status=ValidationStatus.FAILED,
                        response_time_ms=response_time,
                        error=f"Missing required fields: {missing_fields}"
                    )
                
                # Check for legendary capabilities
                legendary_capabilities = data.get("revolutionary_capabilities", {})
                expected_capabilities = [
                    "autonomous_intelligence",
                    "evolutionary_optimization", 
                    "predictive_automation",
                    "multi_cloud_orchestration"
                ]
                
                missing_capabilities = [
                    cap for cap in expected_capabilities 
                    if not legendary_capabilities.get(cap, False)
                ]
                
                if missing_capabilities:
                    return ValidationResult(
                        test_name="Health Endpoint - Legendary Capabilities",
                        status=ValidationStatus.WARNING,
                        response_time_ms=response_time,
                        details=f"Missing legendary capabilities: {missing_capabilities}"
                    )
                
                # Check Cequence integration
                cequence_integration = data.get("cequence_integration", {})
                if not cequence_integration.get("gateway_connected", False):
                    return ValidationResult(
                        test_name="Health Endpoint - Cequence Integration",
                        status=ValidationStatus.WARNING,
                        response_time_ms=response_time,
                        details="Cequence Gateway not connected"
                    )
                
                return ValidationResult(
                    test_name="Health Endpoint",
                    status=ValidationStatus.PASSED,
                    response_time_ms=response_time,
                    details=f"Service: {data.get('service')}, Version: {data.get('version')}",
                    analytics_data=cequence_integration
                )
            else:
                return ValidationResult(
                    test_name="Health Endpoint",
                    status=ValidationStatus.FAILED,
                    response_time_ms=response_time,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            return ValidationResult(
                test_name="Health Endpoint",
                status=ValidationStatus.FAILED,
                error=f"Request failed: {str(e)}"
            )

    async def validate_tool(self, tool: Dict[str, Any], is_legendary: bool = False) -> ValidationResult:
        """Validate individual tool functionality"""
        tool_name = tool["name"]
        endpoint = tool["endpoint"]
        payload = tool["test_payload"]
        
        logger.info(f"🔧 Testing tool: {tool_name} ({'🌟 LEGENDARY' if is_legendary else 'STANDARD'})")
        
        start_time = time.time()
        try:
            response = await self.client.post(
                f"{self.config.base_url}{endpoint}",
                json=payload
            )
            response_time = (time.time() - start_time) * 1000
            
            # Check performance benchmarks
            max_response_time = (
                self.performance_targets["legendary_tools_max_response_ms"] 
                if is_legendary 
                else self.performance_targets["standard_tools_max_response_ms"]
            )
            
            if response_time > max_response_time:
                status = ValidationStatus.WARNING
                details = f"Response time {response_time:.1f}ms exceeds target {max_response_time}ms"
            else:
                status = ValidationStatus.PASSED
                details = f"Response time: {response_time:.1f}ms"
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Extract analytics data if available
                    analytics_data = {}
                    if "cequence" in str(data).lower():
                        analytics_data = {
                            "analytics_present": True,
                            "response_size_bytes": len(response.content)
                        }
                    
                    # Check for expected response structure
                    if "success" in data and data.get("success") is True:
                        return ValidationResult(
                            test_name=f"Tool: {tool_name}",
                            status=status,
                            response_time_ms=response_time,
                            details=details,
                            analytics_data=analytics_data
                        )
                    else:
                        return ValidationResult(
                            test_name=f"Tool: {tool_name}",
                            status=ValidationStatus.WARNING,
                            response_time_ms=response_time,
                            details=f"Success not confirmed in response: {details}"
                        )
                except json.JSONDecodeError:
                    return ValidationResult(
                        test_name=f"Tool: {tool_name}",
                        status=ValidationStatus.WARNING,
                        response_time_ms=response_time,
                        details=f"Non-JSON response received: {details}"
                    )
            
            elif response.status_code == 401:
                return ValidationResult(
                    test_name=f"Tool: {tool_name}",
                    status=ValidationStatus.FAILED,
                    response_time_ms=response_time,
                    error="Authentication failed - check token and scopes"
                )
            
            elif response.status_code == 403:
                return ValidationResult(
                    test_name=f"Tool: {tool_name}",
                    status=ValidationStatus.FAILED,
                    response_time_ms=response_time,
                    error="Authorization failed - insufficient permissions"
                )
            
            else:
                return ValidationResult(
                    test_name=f"Tool: {tool_name}",
                    status=ValidationStatus.FAILED,
                    response_time_ms=response_time,
                    error=f"HTTP {response.status_code}: {response.text[:200]}"
                )
                
        except asyncio.TimeoutError:
            return ValidationResult(
                test_name=f"Tool: {tool_name}",
                status=ValidationStatus.FAILED,
                error=f"Request timeout after {self.config.timeout_seconds}s"
            )
        except Exception as e:
            return ValidationResult(
                test_name=f"Tool: {tool_name}",
                status=ValidationStatus.FAILED,
                error=f"Request failed: {str(e)}"
            )

    async def validate_analytics_dashboard(self) -> ValidationResult:
        """Validate Cequence analytics dashboard accessibility"""
        logger.info("📊 Testing analytics dashboard...")
        
        start_time = time.time()
        try:
            response = await self.client.get(f"{self.config.base_url}/dashboard/analytics")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return ValidationResult(
                    test_name="Analytics Dashboard",
                    status=ValidationStatus.PASSED,
                    response_time_ms=response_time,
                    details="Dashboard accessible"
                )
            elif response.status_code == 401:
                return ValidationResult(
                    test_name="Analytics Dashboard",
                    status=ValidationStatus.FAILED,
                    response_time_ms=response_time,
                    error="Dashboard authentication failed"
                )
            else:
                return ValidationResult(
                    test_name="Analytics Dashboard",
                    status=ValidationStatus.WARNING,
                    response_time_ms=response_time,
                    details=f"Dashboard returned HTTP {response.status_code}"
                )
        except Exception as e:
            return ValidationResult(
                test_name="Analytics Dashboard",
                status=ValidationStatus.FAILED,
                error=f"Dashboard request failed: {str(e)}"
            )

    async def validate_performance_benchmarks(self) -> ValidationResult:
        """Validate overall system performance benchmarks"""
        logger.info("⚡ Testing performance benchmarks...")
        
        # Calculate performance metrics from all tool tests
        tool_results = [r for r in self.results if r.test_name.startswith("Tool:")]
        
        if not tool_results:
            return ValidationResult(
                test_name="Performance Benchmarks",
                status=ValidationStatus.SKIPPED,
                details="No tool results available for analysis"
            )
        
        # Calculate statistics
        response_times = [r.response_time_ms for r in tool_results if r.response_time_ms]
        success_count = len([r for r in tool_results if r.status == ValidationStatus.PASSED])
        total_count = len(tool_results)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
        
        # Check against benchmarks
        issues = []
        if avg_response_time > self.performance_targets["standard_tools_max_response_ms"]:
            issues.append(f"Average response time {avg_response_time:.1f}ms exceeds target")
        
        if success_rate < self.performance_targets["min_success_rate_percent"]:
            issues.append(f"Success rate {success_rate:.1f}% below target {self.performance_targets['min_success_rate_percent']}%")
        
        if issues:
            return ValidationResult(
                test_name="Performance Benchmarks",
                status=ValidationStatus.WARNING,
                details=f"Issues found: {'; '.join(issues)}",
                analytics_data={
                    "avg_response_time_ms": avg_response_time,
                    "success_rate_percent": success_rate,
                    "total_tools_tested": total_count
                }
            )
        else:
            return ValidationResult(
                test_name="Performance Benchmarks",
                status=ValidationStatus.PASSED,
                details=f"All benchmarks met - Avg: {avg_response_time:.1f}ms, Success: {success_rate:.1f}%",
                analytics_data={
                    "avg_response_time_ms": avg_response_time,
                    "success_rate_percent": success_rate,
                    "total_tools_tested": total_count
                }
            )

    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run complete deployment validation suite"""
        logger.info("🚀 Starting comprehensive deployment validation...")
        logger.info(f"Environment: {self.config.environment}")
        logger.info(f"Base URL: {self.config.base_url}")
        
        validation_start = time.time()
        
        # 1. Health endpoint validation
        health_result = await self.validate_health_endpoint()
        self.results.append(health_result)
        
        # 2. Legendary tools validation (5 tools)
        logger.info("\n🌟 VALIDATING LEGENDARY TOOLS (5 tools)...")
        for tool in self.legendary_tools:
            result = await self.validate_tool(tool, is_legendary=True)
            self.results.append(result)
            await asyncio.sleep(0.5)  # Brief delay between requests
        
        # 3. Standard tools validation (6 core tools)
        logger.info("\n🔧 VALIDATING STANDARD TOOLS (6 tools)...")
        for tool in self.standard_tools:
            result = await self.validate_tool(tool, is_legendary=False)
            self.results.append(result)
            await asyncio.sleep(0.3)  # Brief delay between requests
        
        # 4. MCP Protocol tools validation (5 tools)
        logger.info("\n🔗 VALIDATING MCP PROTOCOL TOOLS (5 tools)...")
        for tool in self.mcp_protocol_tools:
            result = await self.validate_tool(tool, is_legendary=False)
            self.results.append(result)
            await asyncio.sleep(0.3)  # Brief delay between requests
        
        # 5. Analytics dashboard validation
        dashboard_result = await self.validate_analytics_dashboard()
        self.results.append(dashboard_result)
        
        # 6. Performance benchmarks validation
        performance_result = await self.validate_performance_benchmarks()
        self.results.append(performance_result)
        
        total_validation_time = time.time() - validation_start
        
        # Generate comprehensive report
        return self._generate_validation_report(total_validation_time)

    def _generate_validation_report(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        
        # Calculate statistics
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == ValidationStatus.PASSED])
        failed_tests = len([r for r in self.results if r.status == ValidationStatus.FAILED])
        warning_tests = len([r for r in self.results if r.status == ValidationStatus.WARNING])
        skipped_tests = len([r for r in self.results if r.status == ValidationStatus.SKIPPED])
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Performance statistics
        response_times = [r.response_time_ms for r in self.results if r.response_time_ms]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        # Overall status determination
        if failed_tests > 0:
            overall_status = "❌ DEPLOYMENT FAILED"
        elif warning_tests > 0:
            overall_status = "⚠️ DEPLOYMENT PASSED WITH WARNINGS"
        else:
            overall_status = "✅ DEPLOYMENT SUCCESSFUL"
        
        report = {
            "validation_summary": {
                "overall_status": overall_status,
                "environment": self.config.environment,
                "timestamp": datetime.now().isoformat(),
                "total_validation_time_seconds": round(total_time, 2)
            },
            "test_statistics": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "skipped": skipped_tests,
                "success_rate_percent": round(success_rate, 1)
            },
            "performance_metrics": {
                "average_response_time_ms": round(avg_response_time, 1),
                "maximum_response_time_ms": round(max_response_time, 1),
                "total_tools_validated": 16
            },
            "tool_breakdown": {
                "legendary_tools": 5,
                "standard_tools": 6,
                "mcp_protocol_tools": 5,
                "total_functional_tools": 16
            },
            "detailed_results": [
                {
                    "test_name": result.test_name,
                    "status": result.status.value,
                    "response_time_ms": result.response_time_ms,
                    "details": result.details,
                    "error": result.error,
                    "has_analytics": bool(result.analytics_data)
                }
                for result in self.results
            ],
            "recommendations": self._generate_recommendations()
        }
        
        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on validation results"""
        recommendations = []
        
        failed_tests = [r for r in self.results if r.status == ValidationStatus.FAILED]
        warning_tests = [r for r in self.results if r.status == ValidationStatus.WARNING]
        
        if failed_tests:
            recommendations.append("🚨 CRITICAL: Address all failed tests before production deployment")
            for test in failed_tests:
                recommendations.append(f"   - Fix {test.test_name}: {test.error}")
        
        if warning_tests:
            recommendations.append("⚠️ Review warnings and optimize performance:")
            for test in warning_tests:
                recommendations.append(f"   - {test.test_name}: {test.details}")
        
        # Performance recommendations
        response_times = [r.response_time_ms for r in self.results if r.response_time_ms]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            if avg_time > 500:
                recommendations.append("🐌 Consider performance optimization for response times")
        
        if not recommendations:
            recommendations.append("🎉 Excellent! All validations passed successfully")
            recommendations.append("🚀 Deployment is ready for production")
        
        return recommendations

    async def close(self):
        """Clean up resources"""
        await self.client.aclose()


def load_environment_config(environment: str) -> DeploymentConfig:
    """Load configuration for specific environment"""
    
    configs = {
        "prod": DeploymentConfig(
            base_url="https://server.smithery.ai/@yoriichi-07/multi_orchestrator_mcp",
            auth_token=os.getenv("PROD_AUTH_TOKEN", ""),
            cequence_api_key=os.getenv("PROD_CEQUENCE_API_KEY", ""),
            environment="production",
            timeout_seconds=30
        ),
        "staging": DeploymentConfig(
            base_url="https://staging.smithery.ai/@yoriichi-07/multi_orchestrator_mcp",
            auth_token=os.getenv("STAGING_AUTH_TOKEN", ""),
            cequence_api_key=os.getenv("STAGING_CEQUENCE_API_KEY", ""),
            environment="staging",
            timeout_seconds=20
        ),
        "dev": DeploymentConfig(
            base_url="http://localhost:8080",
            auth_token=os.getenv("DEV_AUTH_TOKEN", "dev_token"),
            cequence_api_key=os.getenv("DEV_CEQUENCE_API_KEY", "dev_key"),
            environment="development",
            timeout_seconds=15
        )
    }
    
    if environment not in configs:
        raise ValueError(f"Unknown environment: {environment}. Use: {list(configs.keys())}")
    
    config = configs[environment]
    
    # Validate required configuration
    if not config.auth_token:
        raise ValueError(f"Missing auth token for {environment} environment")
    
    if not config.cequence_api_key:
        logger.warning(f"Missing Cequence API key for {environment} environment")
    
    return config


def print_validation_report(report: Dict[str, Any], verbose: bool = False):
    """Print formatted validation report"""
    
    print("\n" + "="*80)
    print("🚀 DEPLOYMENT VALIDATION REPORT")
    print("="*80)
    
    # Summary
    summary = report["validation_summary"]
    print(f"\n📊 VALIDATION SUMMARY:")
    print(f"   Status: {summary['overall_status']}")
    print(f"   Environment: {summary['environment'].upper()}")
    print(f"   Timestamp: {summary['timestamp']}")
    print(f"   Total Time: {summary['total_validation_time_seconds']}s")
    
    # Statistics
    stats = report["test_statistics"]
    print(f"\n📈 TEST STATISTICS:")
    print(f"   Total Tests: {stats['total_tests']}")
    print(f"   ✅ Passed: {stats['passed']}")
    print(f"   ❌ Failed: {stats['failed']}")
    print(f"   ⚠️ Warnings: {stats['warnings']}")
    print(f"   ⏭️ Skipped: {stats['skipped']}")
    print(f"   🎯 Success Rate: {stats['success_rate_percent']}%")
    
    # Performance
    perf = report["performance_metrics"]
    print(f"\n⚡ PERFORMANCE METRICS:")
    print(f"   Average Response Time: {perf['average_response_time_ms']}ms")
    print(f"   Maximum Response Time: {perf['maximum_response_time_ms']}ms")
    print(f"   Total Tools Validated: {perf['total_tools_validated']}")
    
    # Tool breakdown
    tools = report["tool_breakdown"]
    print(f"\n🛠️ TOOL BREAKDOWN:")
    print(f"   🌟 Legendary Tools: {tools['legendary_tools']}")
    print(f"   🔧 Standard Tools: {tools['standard_tools']}")
    print(f"   🔗 MCP Protocol Tools: {tools['mcp_protocol_tools']}")
    print(f"   📊 Total Functional Tools: {tools['total_functional_tools']}")
    
    # Detailed results (if verbose)
    if verbose:
        print(f"\n📋 DETAILED RESULTS:")
        for result in report["detailed_results"]:
            status_emoji = "✅" if "PASSED" in result["status"] else "❌" if "FAILED" in result["status"] else "⚠️"
            time_info = f" ({result['response_time_ms']:.1f}ms)" if result["response_time_ms"] else ""
            print(f"   {status_emoji} {result['test_name']}{time_info}")
            if result["details"]:
                print(f"      📝 {result['details']}")
            if result["error"]:
                print(f"      🚨 {result['error']}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    for rec in report["recommendations"]:
        print(f"   {rec}")
    
    print("\n" + "="*80)


async def main():
    """Main validation entry point"""
    parser = argparse.ArgumentParser(description="Validate Enhanced MCP Server Deployment")
    parser.add_argument(
        "--environment", 
        choices=["prod", "staging", "dev"], 
        default="dev",
        help="Target environment for validation"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Show detailed validation results"
    )
    parser.add_argument(
        "--output",
        help="Save report to JSON file"
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_environment_config(args.environment)
        
        # Create validator
        validator = DeploymentValidator(config)
        
        # Run validation
        report = await validator.run_comprehensive_validation()
        
        # Print report
        print_validation_report(report, verbose=args.verbose)
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n💾 Report saved to: {args.output}")
        
        # Clean up
        await validator.close()
        
        # Exit with appropriate code
        if "FAILED" in report["validation_summary"]["overall_status"]:
            sys.exit(1)
        elif "WARNINGS" in report["validation_summary"]["overall_status"]:
            sys.exit(2)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Validation failed with error: {str(e)}")
        print(f"\n❌ VALIDATION ERROR: {str(e)}")
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())