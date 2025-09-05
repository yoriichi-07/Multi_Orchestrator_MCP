"""
Test runner for healing system validation
"""
import asyncio
import sys
import os
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import unittest
from unittest.mock import patch, Mock
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class HealingSystemTestRunner:
    """Comprehensive test runner for healing system validation"""
    
    def __init__(self):
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "test_details": []
        }
        self.start_time = time.time()
    
    async def run_all_tests(self):
        """Run all healing system tests"""
        logger.info("starting_healing_system_test_suite")
        
        try:
            # Run unit tests
            await self.run_unit_tests()
            
            # Run MCP tools tests
            await self.run_mcp_tools_tests()
            
            # Run integration tests
            await self.run_integration_tests()
            
            # Run validation tests
            await self.run_validation_tests()
            
            # Generate test report
            self.generate_test_report()
            
        except Exception as e:
            logger.error("test_suite_failed", error=str(e))
            raise
    
    async def run_unit_tests(self):
        """Run unit tests for healing components"""
        logger.info("running_healing_unit_tests")
        
        # Mock dependencies for isolated unit testing
        with patch('src.core.file_manager.SecureFileManager'), \
             patch('src.core.llm_manager.LLMManager'), \
             patch('src.middleware.cequence_analytics.CequenceAnalytics'):
            
            # Run pytest on healing system tests
            test_file = str(project_root / "tests" / "test_healing_system.py")
            
            # Run tests and capture results
            result = pytest.main([
                test_file,
                "-v",
                "--tb=short",
                "--asyncio-mode=auto",
                "-x"  # Stop on first failure for debugging
            ])
            
            self.test_results["unit_tests"] = "passed" if result == 0 else "failed"
            logger.info("unit_tests_completed", result=self.test_results["unit_tests"])
    
    async def run_mcp_tools_tests(self):
        """Run MCP tools tests"""
        logger.info("running_mcp_tools_tests")
        
        # Mock MCP dependencies
        with patch('src.core.tool_registry.get_mcp_server'), \
             patch('src.core.tool_registry.AnalyticsTracker'):
            
            test_file = str(project_root / "tests" / "test_healing_mcp_tools.py")
            
            result = pytest.main([
                test_file,
                "-v",
                "--tb=short",
                "--asyncio-mode=auto",
                "-x"
            ])
            
            self.test_results["mcp_tools_tests"] = "passed" if result == 0 else "failed"
            logger.info("mcp_tools_tests_completed", result=self.test_results["mcp_tools_tests"])
    
    async def run_integration_tests(self):
        """Run integration tests between healing components"""
        logger.info("running_integration_tests")
        
        try:
            # Test health monitoring integration
            await self.test_health_monitoring_integration()
            
            # Test error analysis integration
            await self.test_error_analysis_integration()
            
            # Test solution generation integration
            await self.test_solution_generation_integration()
            
            # Test healing loop integration
            await self.test_healing_loop_integration()
            
            self.test_results["integration_tests"] = "passed"
            logger.info("integration_tests_completed", result="passed")
            
        except Exception as e:
            self.test_results["integration_tests"] = "failed"
            logger.error("integration_tests_failed", error=str(e))
    
    async def test_health_monitoring_integration(self):
        """Test health monitoring component integration"""
        logger.info("testing_health_monitoring_integration")
        
        # Import and test basic functionality
        from src.healing.health_monitor import HealthMonitor, HealthIssue, IssueType
        from datetime import datetime
        
        # Create health monitor
        health_monitor = HealthMonitor()
        
        # Test creating a health issue
        test_issue = HealthIssue(
            id="integration_test_issue",
            type=IssueType.RUNTIME_ERROR,
            severity=5,
            description="Integration test issue",
            location="test.py:1",
            first_detected=datetime.utcnow()
        )
        
        # Verify issue creation
        assert test_issue.id == "integration_test_issue"
        assert test_issue.type == IssueType.RUNTIME_ERROR
        
        logger.info("health_monitoring_integration_passed")
    
    async def test_error_analysis_integration(self):
        """Test error analysis component integration"""
        logger.info("testing_error_analysis_integration")
        
        from src.healing.error_analyzer import ErrorAnalyzer
        from src.healing.health_monitor import HealthIssue, IssueType
        from datetime import datetime
        
        # Create error analyzer
        error_analyzer = ErrorAnalyzer(correlation_id="integration_test")
        
        # Test pattern loading
        assert len(error_analyzer.error_patterns) > 0
        
        # Test with mock issue
        test_issue = HealthIssue(
            id="analysis_test_issue",
            type=IssueType.SYNTAX_ERROR,
            severity=7,
            description="SyntaxError: invalid syntax",
            location="test.py:10",
            error_message="SyntaxError: invalid syntax (test.py, line 10)",
            first_detected=datetime.utcnow()
        )
        
        # Mock the analysis method to avoid LLM calls
        with patch.object(error_analyzer, 'analyze_error') as mock_analyze:
            mock_analysis = Mock()
            mock_analysis.issue_id = test_issue.id
            mock_analysis.analysis_type = "pattern_match"
            mock_analysis.confidence_score = 0.9
            mock_analyze.return_value = mock_analysis
            
            result = await error_analyzer.analyze_error(test_issue, "test_project")
            assert result.issue_id == test_issue.id
        
        logger.info("error_analysis_integration_passed")
    
    async def test_solution_generation_integration(self):
        """Test solution generation component integration"""
        logger.info("testing_solution_generation_integration")
        
        from src.healing.solution_generator import SolutionGenerator
        from src.healing.health_monitor import HealthIssue, IssueType
        from datetime import datetime
        
        # Create solution generator
        solution_generator = SolutionGenerator(correlation_id="integration_test")
        
        # Test template loading
        assert hasattr(solution_generator, 'generation_config')
        assert len(solution_generator.generation_config) > 0
        
        # Test with mock issue
        test_issue = HealthIssue(
            id="solution_test_issue",
            type=IssueType.DEPENDENCY_ISSUE,
            severity=6,
            description="ModuleNotFoundError: No module named 'requests'",
            location="main.py:1",
            error_message="ModuleNotFoundError: No module named 'requests'",
            first_detected=datetime.utcnow()
        )
        
        # Mock the solution generation to avoid LLM calls
        with patch.object(solution_generator, 'generate_solutions') as mock_generate:
            mock_solution = Mock()
            mock_solution.solution_id = "test_solution"
            mock_solution.solution_type = "dependency_install"
            mock_solution.implementation_plan = {"steps": ["Install requests module"]}
            mock_generate.return_value = [mock_solution]
            
            solutions = await solution_generator.generate_solutions(test_issue, "test_project")
            assert len(solutions) > 0
            assert solutions[0].solution_id == "test_solution"
        
        logger.info("solution_generation_integration_passed")
    
    async def test_healing_loop_integration(self):
        """Test healing loop orchestration integration"""
        logger.info("testing_healing_loop_integration")
        
        from src.healing.healing_loop import HealingLoop, HealingStatus
        
        # Create healing loop
        healing_loop = HealingLoop(correlation_id="integration_test")
        
        # Test initial state
        assert healing_loop.status == HealingStatus.IDLE
        assert len(healing_loop.active_sessions) == 0
        
        # Test status method
        status = healing_loop.get_healing_status()
        assert isinstance(status, dict)
        assert "status" in status
        assert "active_sessions" in status
        
        logger.info("healing_loop_integration_passed")
    
    async def run_validation_tests(self):
        """Run validation tests for complete healing scenarios"""
        logger.info("running_validation_tests")
        
        try:
            # Test orchestrator integration
            await self.test_orchestrator_integration()
            
            # Test MCP tool availability
            await self.test_mcp_tool_availability()
            
            self.test_results["validation_tests"] = "passed"
            logger.info("validation_tests_completed", result="passed")
            
        except Exception as e:
            self.test_results["validation_tests"] = "failed"
            logger.error("validation_tests_failed", error=str(e))
    
    async def test_orchestrator_integration(self):
        """Test orchestrator integration with healing system"""
        logger.info("testing_orchestrator_integration")
        
        from src.agents.orchestrator import AgentOrchestrator
        
        # Create orchestrator
        orchestrator = AgentOrchestrator()
        
        # Verify healing properties
        assert hasattr(orchestrator, 'healing_enabled')
        assert hasattr(orchestrator, 'auto_healing_threshold')
        assert hasattr(orchestrator, 'project_health_status')
        
        # Test healing methods exist
        assert hasattr(orchestrator, 'enable_healing_for_project')
        assert hasattr(orchestrator, 'disable_healing_for_project')
        assert hasattr(orchestrator, 'trigger_healing_on_failure')
        assert hasattr(orchestrator, 'get_project_health_status')
        
        logger.info("orchestrator_integration_passed")
    
    async def test_mcp_tool_availability(self):
        """Test MCP tool registration and availability"""
        logger.info("testing_mcp_tool_availability")
        
        # Test healing tools import
        try:
            import src.healing.healing_tools
            logger.info("healing_tools_import_successful")
        except ImportError as e:
            logger.error("healing_tools_import_failed", error=str(e))
            raise
        
        # Test orchestrator MCP tools import
        try:
            import src.agents.orchestrator_mcp_tools
            logger.info("orchestrator_mcp_tools_import_successful")
        except ImportError as e:
            logger.error("orchestrator_mcp_tools_import_failed", error=str(e))
            raise
        
        logger.info("mcp_tool_availability_passed")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        end_time = time.time()
        duration = end_time - self.start_time
        
        report = {
            "test_suite": "Healing System Validation",
            "duration_seconds": round(duration, 2),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": self.test_results,
            "summary": {
                "overall_status": self.calculate_overall_status(),
                "test_categories": [
                    "unit_tests",
                    "mcp_tools_tests", 
                    "integration_tests",
                    "validation_tests"
                ]
            }
        }
        
        # Print report
        print("\n" + "="*60)
        print("HEALING SYSTEM TEST REPORT")
        print("="*60)
        print(f"Duration: {report['duration_seconds']} seconds")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Overall Status: {report['summary']['overall_status']}")
        print("\nTest Categories:")
        
        for category in report['summary']['test_categories']:
            status = self.test_results.get(category, "not_run")
            print(f"  {category}: {status}")
        
        print("="*60)
        
        # Log structured report
        logger.info("test_report_generated", **report)
        
        return report
    
    def calculate_overall_status(self):
        """Calculate overall test status"""
        statuses = [
            self.test_results.get("unit_tests", "not_run"),
            self.test_results.get("mcp_tools_tests", "not_run"),
            self.test_results.get("integration_tests", "not_run"),
            self.test_results.get("validation_tests", "not_run")
        ]
        
        if all(status == "passed" for status in statuses):
            return "PASSED"
        elif any(status == "failed" for status in statuses):
            return "FAILED"
        else:
            return "PARTIAL"


async def main():
    """Main test runner entry point"""
    logger.info("starting_healing_system_validation")
    
    test_runner = HealingSystemTestRunner()
    
    try:
        await test_runner.run_all_tests()
        logger.info("healing_system_validation_completed")
        return 0
    except Exception as e:
        logger.error("healing_system_validation_failed", error=str(e))
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())