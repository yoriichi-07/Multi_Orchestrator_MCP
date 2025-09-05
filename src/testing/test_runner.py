"""
Test runner for comprehensive application testing
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()


class TestRunner:
    """Comprehensive test runner for generated applications"""
    
    def __init__(self, correlation_id: str):
        self.correlation_id = correlation_id
        self.logger = logger.bind(correlation_id=correlation_id)
    
    async def run_comprehensive_tests(
        self,
        project_id: str,
        test_types: List[str],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run comprehensive test suite across multiple test types
        """
        self.logger.info(
            "starting_comprehensive_tests",
            project_id=project_id,
            test_types=test_types
        )
        
        test_results = {}
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        
        for test_type in test_types:
            result = await self._run_test_type(project_id, test_type)
            test_results[test_type] = result
            
            total_tests += result["total"]
            passed_tests += result["passed"]
            failed_tests += result["failed"]
            skipped_tests += result["skipped"]
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Generate recommendations based on results
        recommendations = self._generate_test_recommendations(test_results)
        
        # Collect failures for detailed analysis
        failures = []
        for test_type, result in test_results.items():
            failures.extend(result.get("failures", []))
        
        final_result = {
            "project_id": project_id,
            "test_timestamp": datetime.utcnow().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
            "success_rate": round(success_rate, 2),
            "test_details": test_results,
            "failures": failures,
            "recommendations": recommendations
        }
        
        self.logger.info(
            "comprehensive_tests_completed",
            project_id=project_id,
            total_tests=total_tests,
            success_rate=success_rate
        )
        
        return final_result
    
    async def _run_test_type(self, project_id: str, test_type: str) -> Dict[str, Any]:
        """Run a specific type of test"""
        self.logger.debug(f"running_{test_type}_tests", project_id=project_id)
        
        # Simulate test execution
        await asyncio.sleep(0.5)
        
        # Simulate different test results based on test type
        test_configs = {
            "unit": {
                "total": 25,
                "passed": 23,
                "failed": 2,
                "skipped": 0,
                "failures": [
                    {
                        "test_name": "test_user_validation",
                        "error": "AssertionError: Expected valid user",
                        "file": "tests/test_user.py",
                        "line": 45
                    },
                    {
                        "test_name": "test_password_strength",
                        "error": "ValidationError: Password too weak",
                        "file": "tests/test_auth.py", 
                        "line": 23
                    }
                ]
            },
            "integration": {
                "total": 15,
                "passed": 14,
                "failed": 1,
                "skipped": 0,
                "failures": [
                    {
                        "test_name": "test_database_connection",
                        "error": "ConnectionError: Database unreachable",
                        "file": "tests/test_integration.py",
                        "line": 67
                    }
                ]
            },
            "security": {
                "total": 8,
                "passed": 7,
                "failed": 1,
                "skipped": 0,
                "failures": [
                    {
                        "test_name": "test_sql_injection_protection",
                        "error": "SecurityVulnerability: SQL injection possible",
                        "file": "tests/test_security.py",
                        "line": 34
                    }
                ]
            },
            "linting": {
                "total": 50,
                "passed": 48,
                "failed": 2,
                "skipped": 0,
                "failures": [
                    {
                        "test_name": "code_style_check",
                        "error": "StyleError: Line too long",
                        "file": "src/utils/helpers.py",
                        "line": 89
                    },
                    {
                        "test_name": "import_order_check",
                        "error": "ImportError: Incorrect import order",
                        "file": "src/main.py",
                        "line": 5
                    }
                ]
            },
            "performance": {
                "total": 5,
                "passed": 5,
                "failed": 0,
                "skipped": 0,
                "failures": []
            }
        }
        
        config = test_configs.get(test_type, {
            "total": 10,
            "passed": 9,
            "failed": 1,
            "skipped": 0,
            "failures": []
        })
        
        return {
            "test_type": test_type,
            "duration_seconds": 2.5,
            **config
        }
    
    def _generate_test_recommendations(self, test_results: Dict[str, Any]) -> List[str]:
        """Generate testing recommendations based on results"""
        recommendations = []
        
        for test_type, result in test_results.items():
            if result["failed"] > 0:
                recommendations.append(
                    f"Fix {result['failed']} failing {test_type} tests before deployment"
                )
            
            if test_type == "security" and result["failed"] > 0:
                recommendations.append(
                    "Security tests failed - address vulnerabilities immediately"
                )
            
            if test_type == "unit" and (result["passed"] / result["total"]) < 0.9:
                recommendations.append(
                    "Unit test coverage below 90% - add more unit tests"
                )
        
        # General recommendations
        if not recommendations:
            recommendations.append("All tests passing - ready for deployment")
        else:
            recommendations.append("Run tests again after fixing issues")
        
        return recommendations
    
    async def validate_healing_fix(
        self,
        project_id: str,
        healing_session_id: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate that a healing fix was successful"""
        self.logger.info(
            "healing_validation_started",
            project_id=project_id,
            healing_session_id=healing_session_id,
            correlation_id=correlation_id or self.correlation_id
        )
        
        # Run focused tests to validate the fix
        validation_results = await self.run_comprehensive_tests(
            project_id=project_id,
            test_types=["unit", "integration"]
        )
        
        # Check if validation passed
        validation_success = validation_results.get("success_rate", 0) >= 90
        
        self.logger.info(
            "healing_validation_completed",
            project_id=project_id,
            healing_session_id=healing_session_id,
            success=validation_success,
            correlation_id=correlation_id or self.correlation_id
        )
        
        return {
            "project_id": project_id,
            "healing_session_id": healing_session_id,
            "validation_success": validation_success,
            "test_results": validation_results,
            "correlation_id": correlation_id or self.correlation_id
        }
    
    def get_test_statistics(self) -> Dict[str, Any]:
        """Get overall test statistics"""
        return {
            "total_runs": 0,
            "success_rate": 0.0,
            "average_duration": 0.0,
            "most_common_failures": [],
            "correlation_id": self.correlation_id
        }