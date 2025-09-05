"""
Comprehensive test suite for the self-healing loop system
"""
import asyncio
import unittest
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
import pytest

from src.healing.health_monitor import HealthMonitor, HealthIssue, IssueType, HealthStatus
from src.healing.error_analyzer import ErrorAnalyzer
from src.healing.solution_generator import SolutionGenerator
from src.healing.healing_loop import HealingLoop, HealingPhase, HealingStatus
from src.core.project_manager import ProjectManager


class TestHealthMonitor(unittest.TestCase):
    """Test cases for HealthMonitor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.health_monitor = HealthMonitor()
        self.test_project_id = "test_project_123"
    
    @pytest.mark.asyncio
    async def test_health_monitor_initialization(self):
        """Test health monitor initializes correctly"""
        self.assertIsNotNone(self.health_monitor)
        self.assertEqual(len(self.health_monitor.monitors), 0)
        self.assertEqual(len(self.health_monitor.health_history), 0)
    
    @pytest.mark.asyncio
    async def test_health_check_creation(self):
        """Test creating a basic health check"""
        # Mock project structure for testing
        with patch('src.core.file_manager.SecureFileManager') as mock_fm:
            mock_fm.return_value.read_file.return_value = "print('hello world')"
            mock_fm.return_value.list_files.return_value = ["main.py", "requirements.txt"]
            
            health_report = await self.health_monitor.perform_comprehensive_health_check(
                self.test_project_id
            )
            
            self.assertIsNotNone(health_report)
            self.assertEqual(health_report.project_id, self.test_project_id)
            self.assertIsInstance(health_report.health_score, float)
            self.assertGreaterEqual(health_report.health_score, 0.0)
            self.assertLessEqual(health_report.health_score, 1.0)
    
    @pytest.mark.asyncio
    async def test_continuous_monitoring_start_stop(self):
        """Test starting and stopping continuous monitoring"""
        # Start monitoring
        monitor_task = await self.health_monitor.start_continuous_monitoring(
            self.test_project_id, interval_seconds=1
        )
        
        self.assertIn(self.test_project_id, self.health_monitor.monitors)
        
        # Let it run briefly
        await asyncio.sleep(2.1)
        
        # Stop monitoring
        await self.health_monitor.stop_monitoring(self.test_project_id)
        
        self.assertNotIn(self.test_project_id, self.health_monitor.monitors)
    
    @pytest.mark.asyncio
    async def test_issue_detection(self):
        """Test various issue detection scenarios"""
        # Mock error scenarios
        with patch('src.core.file_manager.SecureFileManager') as mock_fm:
            # Syntax error scenario
            mock_fm.return_value.read_file.return_value = "print('unclosed string"
            mock_fm.return_value.list_files.return_value = ["broken.py"]
            
            health_report = await self.health_monitor.perform_comprehensive_health_check(
                self.test_project_id
            )
            
            # Should detect syntax error
            syntax_issues = [issue for issue in health_report.issues 
                           if issue.type == IssueType.SYNTAX_ERROR]
            self.assertGreater(len(syntax_issues), 0)
    
    @pytest.mark.asyncio
    async def test_health_history_tracking(self):
        """Test health history is properly tracked"""
        # Perform multiple health checks
        for i in range(3):
            await self.health_monitor.perform_comprehensive_health_check(
                self.test_project_id
            )
            await asyncio.sleep(0.1)
        
        # Check history
        history = self.health_monitor.get_health_history(self.test_project_id)
        self.assertGreaterEqual(len(history), 3)
        
        # Check chronological order
        timestamps = [report.timestamp for report in history]
        self.assertEqual(timestamps, sorted(timestamps))


class TestErrorAnalyzer(unittest.TestCase):
    """Test cases for ErrorAnalyzer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.error_analyzer = ErrorAnalyzer(correlation_id="test_analyzer_123")
        self.test_project_id = "test_project_456"
    
    @pytest.mark.asyncio
    async def test_error_analyzer_initialization(self):
        """Test error analyzer initializes correctly"""
        self.assertIsNotNone(self.error_analyzer)
        self.assertGreater(len(self.error_analyzer.error_patterns), 0)
    
    @pytest.mark.asyncio
    async def test_pattern_matching(self):
        """Test error pattern matching"""
        # Create test issue
        test_issue = HealthIssue(
            id="test_issue_1",
            type=IssueType.SYNTAX_ERROR,
            severity=7,
            description="SyntaxError: invalid syntax",
            location="test.py:10",
            error_message="SyntaxError: invalid syntax (test.py, line 10)",
            first_detected=datetime.utcnow()
        )
        
        # Analyze error
        analysis = await self.error_analyzer.analyze_error(test_issue, self.test_project_id)
        
        self.assertIsNotNone(analysis)
        self.assertEqual(analysis.issue_id, test_issue.id)
        self.assertIsNotNone(analysis.analysis_type)
        self.assertIsInstance(analysis.confidence_score, float)
    
    @pytest.mark.asyncio
    async def test_llm_analysis(self):
        """Test LLM-based error analysis"""
        with patch('src.core.llm_manager.LLMManager') as mock_llm:
            mock_llm.return_value.generate_response.return_value = {
                "root_cause": "Missing semicolon",
                "impact_assessment": "High - prevents compilation",
                "urgency": "high",
                "recommendations": ["Add semicolon at line 10"]
            }
            
            test_issue = HealthIssue(
                id="test_issue_2",
                type=IssueType.RUNTIME_ERROR,
                severity=8,
                description="Complex runtime error",
                location="complex.py:50",
                error_message="AttributeError: 'NoneType' object has no attribute 'value'",
                first_detected=datetime.utcnow()
            )
            
            analysis = await self.error_analyzer.analyze_error(test_issue, self.test_project_id)
            
            self.assertIsNotNone(analysis.root_cause_analysis)
            self.assertIsNotNone(analysis.impact_assessment)
    
    @pytest.mark.asyncio
    async def test_context_gathering(self):
        """Test error context gathering"""
        with patch('src.core.file_manager.SecureFileManager') as mock_fm:
            mock_fm.return_value.read_file.return_value = "test file content"
            mock_fm.return_value.list_files.return_value = ["test.py", "utils.py"]
            
            test_issue = HealthIssue(
                id="test_issue_3",
                type=IssueType.LOGIC_ERROR,
                severity=6,
                description="Logic error in calculation",
                location="calc.py:25",
                first_detected=datetime.utcnow()
            )
            
            context = await self.error_analyzer._gather_error_context(
                test_issue, self.test_project_id
            )
            
            self.assertIsInstance(context, dict)
            self.assertIn("file_content", context)
            self.assertIn("surrounding_files", context)


class TestSolutionGenerator(unittest.TestCase):
    """Test cases for SolutionGenerator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.solution_generator = SolutionGenerator(correlation_id="test_generator_789")
        self.test_project_id = "test_project_789"
    
    @pytest.mark.asyncio
    async def test_solution_generator_initialization(self):
        """Test solution generator initializes correctly"""
        self.assertIsNotNone(self.solution_generator)
        self.assertGreater(len(self.solution_generator.solution_templates), 0)
    
    @pytest.mark.asyncio
    async def test_solution_generation(self):
        """Test basic solution generation"""
        with patch('src.healing.error_analyzer.ErrorAnalyzer') as mock_analyzer:
            # Mock error analysis
            mock_analysis = Mock()
            mock_analysis.issue_id = "test_issue_1"
            mock_analysis.root_cause_analysis = "Missing import statement"
            mock_analysis.impact_assessment = "Medium impact"
            mock_analysis.confidence_score = 0.85
            
            mock_analyzer.return_value.analyze_error.return_value = mock_analysis
            
            test_issue = HealthIssue(
                id="test_issue_1",
                type=IssueType.DEPENDENCY_ISSUE,
                severity=5,
                description="ModuleNotFoundError: No module named 'requests'",
                location="main.py:1",
                error_message="ModuleNotFoundError: No module named 'requests'",
                first_detected=datetime.utcnow()
            )
            
            solutions = await self.solution_generator.generate_solutions(
                test_issue, self.test_project_id
            )
            
            self.assertIsInstance(solutions, list)
            self.assertGreater(len(solutions), 0)
            
            # Check solution structure
            solution = solutions[0]
            self.assertIsNotNone(solution.solution_id)
            self.assertIsNotNone(solution.solution_type)
            self.assertIsNotNone(solution.implementation_plan)
    
    @pytest.mark.asyncio
    async def test_solution_evaluation(self):
        """Test solution evaluation and ranking"""
        with patch('src.core.llm_manager.LLMManager') as mock_llm:
            mock_llm.return_value.generate_response.return_value = {
                "feasibility_score": 0.9,
                "risk_assessment": "Low risk",
                "implementation_complexity": "Simple",
                "estimated_success_rate": 0.95
            }
            
            test_issue = HealthIssue(
                id="test_issue_2",
                type=IssueType.CONFIGURATION_ERROR,
                severity=4,
                description="Configuration file missing",
                location="config/",
                first_detected=datetime.utcnow()
            )
            
            solutions = await self.solution_generator.generate_solutions(
                test_issue, self.test_project_id
            )
            
            # Should have ranked solutions
            self.assertGreater(len(solutions), 0)
            
            # Check ranking (solutions should be sorted by score)
            if len(solutions) > 1:
                self.assertGreaterEqual(
                    solutions[0].feasibility_score,
                    solutions[1].feasibility_score
                )
    
    @pytest.mark.asyncio
    async def test_implementation_plan_generation(self):
        """Test implementation plan generation"""
        test_issue = HealthIssue(
            id="test_issue_3",
            type=IssueType.SYNTAX_ERROR,
            severity=7,
            description="Syntax error in function",
            location="utils.py:15",
            error_message="SyntaxError: invalid syntax",
            first_detected=datetime.utcnow()
        )
        
        solutions = await self.solution_generator.generate_solutions(
            test_issue, self.test_project_id
        )
        
        # Check implementation plan structure
        solution = solutions[0]
        plan = solution.implementation_plan
        
        self.assertIsInstance(plan, dict)
        self.assertIn("steps", plan)
        self.assertIsInstance(plan["steps"], list)
        self.assertGreater(len(plan["steps"]), 0)


class TestHealingLoop(unittest.TestCase):
    """Test cases for HealingLoop orchestrator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.healing_loop = HealingLoop(correlation_id="test_loop_heal")
        self.test_project_id = "test_project_loop"
    
    @pytest.mark.asyncio
    async def test_healing_loop_initialization(self):
        """Test healing loop initializes correctly"""
        self.assertIsNotNone(self.healing_loop)
        self.assertEqual(self.healing_loop.status, HealingStatus.IDLE)
        self.assertEqual(len(self.healing_loop.active_sessions), 0)
    
    @pytest.mark.asyncio
    async def test_healing_loop_start_stop(self):
        """Test starting and stopping healing loop"""
        # Start healing loop
        healing_task = await self.healing_loop.start_healing_loop(self.test_project_id)
        
        self.assertEqual(self.healing_loop.status, HealingStatus.ACTIVE)
        
        # Stop healing loop
        await self.healing_loop.stop_healing_loop(self.test_project_id)
        
        self.assertEqual(self.healing_loop.status, HealingStatus.IDLE)
    
    @pytest.mark.asyncio
    async def test_healing_session_trigger(self):
        """Test triggering a healing session"""
        # Start healing loop first
        await self.healing_loop.start_healing_loop(self.test_project_id)
        
        test_issue = HealthIssue(
            id="test_session_issue",
            type=IssueType.RUNTIME_ERROR,
            severity=8,
            description="Critical runtime error",
            location="app.py:100",
            error_message="ValueError: invalid literal for int()",
            first_detected=datetime.utcnow()
        )
        
        # Trigger healing session
        session_id = await self.healing_loop.trigger_healing_session(
            self.test_project_id, test_issue
        )
        
        self.assertIsNotNone(session_id)
        self.assertIn(session_id, self.healing_loop.active_sessions)
        
        # Let healing process run briefly
        await asyncio.sleep(1)
        
        # Check session status
        session_details = self.healing_loop.get_session_details(session_id)
        self.assertIsNotNone(session_details)
    
    @pytest.mark.asyncio
    async def test_concurrent_healing_sessions(self):
        """Test handling multiple concurrent healing sessions"""
        await self.healing_loop.start_healing_loop(self.test_project_id)
        
        # Create multiple issues
        issues = []
        for i in range(3):
            issue = HealthIssue(
                id=f"concurrent_issue_{i}",
                type=IssueType.LOGIC_ERROR,
                severity=5 + i,
                description=f"Test issue {i}",
                location=f"test_{i}.py:10",
                first_detected=datetime.utcnow()
            )
            issues.append(issue)
        
        # Trigger concurrent sessions
        session_ids = []
        for issue in issues:
            session_id = await self.healing_loop.trigger_healing_session(
                self.test_project_id, issue
            )
            if session_id:
                session_ids.append(session_id)
        
        # Should handle multiple sessions (up to limit)
        self.assertGreater(len(session_ids), 0)
        self.assertLessEqual(len(session_ids), self.healing_loop.max_concurrent_sessions)
    
    @pytest.mark.asyncio
    async def test_healing_status_reporting(self):
        """Test healing status reporting"""
        status = self.healing_loop.get_healing_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("status", status)
        self.assertIn("active_sessions", status)
        self.assertIn("completed_sessions", status)
        self.assertEqual(status["status"], HealingStatus.IDLE.value)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for complete healing scenarios"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.health_monitor = HealthMonitor()
        self.healing_loop = HealingLoop()
        self.test_project_id = "integration_test_project"
    
    @pytest.mark.asyncio
    async def test_end_to_end_healing_flow(self):
        """Test complete end-to-end healing flow"""
        # 1. Start healing loop
        await self.healing_loop.start_healing_loop(self.test_project_id)
        
        # 2. Start health monitoring
        await self.health_monitor.start_continuous_monitoring(
            self.test_project_id, interval_seconds=2
        )
        
        # 3. Simulate an issue being detected
        test_issue = HealthIssue(
            id="integration_issue",
            type=IssueType.API_ERROR,
            severity=9,
            description="API endpoint returning 500 errors",
            location="api/users.py:45",
            error_message="Internal Server Error",
            first_detected=datetime.utcnow()
        )
        
        # 4. Trigger healing
        session_id = await self.healing_loop.trigger_healing_session(
            self.test_project_id, test_issue
        )
        
        self.assertIsNotNone(session_id)
        
        # 5. Let healing process run
        await asyncio.sleep(3)
        
        # 6. Check results
        session_details = self.healing_loop.get_session_details(session_id)
        self.assertIsNotNone(session_details)
        
        # 7. Cleanup
        await self.health_monitor.stop_monitoring(self.test_project_id)
        await self.healing_loop.stop_healing_loop(self.test_project_id)
    
    @pytest.mark.asyncio
    async def test_healing_with_orchestrator_integration(self):
        """Test healing integration with agent orchestrator"""
        from src.agents.orchestrator import AgentOrchestrator
        
        # Create orchestrator with healing enabled
        orchestrator = AgentOrchestrator()
        
        # Enable healing for test project
        result = await orchestrator.enable_healing_for_project(self.test_project_id)
        self.assertTrue(result["success"])
        
        # Check health status
        health_status = await orchestrator.get_project_health_status(self.test_project_id)
        self.assertEqual(health_status["project_id"], self.test_project_id)
        self.assertTrue(health_status["healing_enabled"])
        
        # Cleanup
        await orchestrator.disable_healing_for_project(self.test_project_id)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])