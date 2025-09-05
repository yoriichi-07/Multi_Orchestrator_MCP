"""
Test suite for healing system MCP tools
"""
import unittest
import uuid
from unittest.mock import AsyncMock, Mock, patch
import pytest

from src.healing.healing_tools import (
    start_health_monitoring,
    stop_health_monitoring,
    get_health_status,
    perform_health_check,
    start_healing_loop,
    stop_healing_loop,
    trigger_healing_session,
    get_healing_status,
    get_healing_session_details
)
from src.agents.orchestrator_mcp_tools import (
    generate_application_with_healing,
    enable_project_healing,
    disable_project_healing,
    get_orchestrator_health_status,
    trigger_orchestrator_healing,
    get_orchestrator_status,
    configure_healing_settings
)


class TestHealingMCPTools(unittest.TestCase):
    """Test cases for healing system MCP tools"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_project_id = "mcp_test_project"
        self.mock_request = Mock()
        self.mock_auth_context = Mock()
    
    @pytest.mark.asyncio
    async def test_start_health_monitoring_tool(self):
        """Test start_health_monitoring MCP tool"""
        with patch('src.healing.healing_tools.get_health_monitor') as mock_monitor:
            mock_monitor.return_value.start_continuous_monitoring.return_value = Mock()
            
            result = await start_health_monitoring(
                project_id=self.test_project_id,
                interval_seconds=60,
                request=self.mock_request,
                auth_context=self.mock_auth_context
            )
            
            self.assertTrue(result["success"])
            self.assertEqual(result["project_id"], self.test_project_id)
            self.assertTrue(result["monitoring_started"])
            self.assertIn("correlation_id", result)
    
    @pytest.mark.asyncio
    async def test_start_health_monitoring_tool_error(self):
        """Test start_health_monitoring MCP tool error handling"""
        with patch('src.healing.healing_tools.get_health_monitor') as mock_monitor:
            mock_monitor.return_value.start_continuous_monitoring.side_effect = Exception("Test error")
            
            result = await start_health_monitoring(
                project_id=self.test_project_id,
                interval_seconds=60,
                request=self.mock_request,
                auth_context=self.mock_auth_context
            )
            
            self.assertFalse(result["success"])
            self.assertIn("error", result)
            self.assertIn("correlation_id", result)
    
    @pytest.mark.asyncio
    async def test_perform_health_check_tool(self):
        """Test perform_health_check MCP tool"""
        with patch('src.healing.healing_tools.get_health_monitor') as mock_monitor:
            # Mock health report
            mock_report = Mock()
            mock_report.overall_status.value = "good"
            mock_report.health_score = 0.85
            mock_report.issues = []
            mock_report.recommendations = ["Keep up the good work"]
            mock_report.timestamp.isoformat.return_value = "2024-01-01T00:00:00"
            
            mock_monitor.return_value.perform_comprehensive_health_check.return_value = mock_report
            
            result = await perform_health_check(
                project_id=self.test_project_id,
                request=self.mock_request,
                auth_context=self.mock_auth_context
            )
            
            self.assertTrue(result["success"])
            self.assertEqual(result["project_id"], self.test_project_id)
            self.assertEqual(result["health_status"], "good")
            self.assertEqual(result["health_score"], 0.85)
            self.assertEqual(result["issues_count"], 0)
    
    @pytest.mark.asyncio
    async def test_start_healing_loop_tool(self):
        """Test start_healing_loop MCP tool"""
        with patch('src.healing.healing_tools.get_healing_loop') as mock_loop:
            mock_loop.return_value.start_healing_loop.return_value = Mock()
            mock_loop.return_value.status.value = "active"
            
            result = await start_healing_loop(
                project_id=self.test_project_id,
                request=self.mock_request,
                auth_context=self.mock_auth_context
            )
            
            self.assertTrue(result["success"])
            self.assertEqual(result["project_id"], self.test_project_id)
            self.assertTrue(result["healing_loop_started"])
            self.assertEqual(result["status"], "active")
    
    @pytest.mark.asyncio
    async def test_trigger_healing_session_tool(self):
        """Test trigger_healing_session MCP tool"""
        with patch('src.healing.healing_tools.get_healing_loop') as mock_loop:
            mock_session_id = str(uuid.uuid4())
            mock_loop.return_value.trigger_healing_session.return_value = mock_session_id
            
            result = await trigger_healing_session(
                project_id=self.test_project_id,
                issue_description="Test issue description",
                issue_severity=7,
                error_message="Test error message",
                request=self.mock_request,
                auth_context=self.mock_auth_context
            )
            
            self.assertTrue(result["success"])
            self.assertEqual(result["project_id"], self.test_project_id)
            self.assertEqual(result["session_id"], mock_session_id)
            self.assertTrue(result["healing_session_triggered"])
    
    @pytest.mark.asyncio
    async def test_trigger_healing_session_tool_failure(self):
        """Test trigger_healing_session MCP tool when session limit reached"""
        with patch('src.healing.healing_tools.get_healing_loop') as mock_loop:
            mock_loop.return_value.trigger_healing_session.return_value = None  # Session limit reached
            
            result = await trigger_healing_session(
                project_id=self.test_project_id,
                issue_description="Test issue description",
                request=self.mock_request,
                auth_context=self.mock_auth_context
            )
            
            self.assertFalse(result["success"])
            self.assertIn("Failed to trigger healing session", result["error"])
    
    @pytest.mark.asyncio
    async def test_get_healing_status_tool(self):
        """Test get_healing_status MCP tool"""
        with patch('src.healing.healing_tools.get_healing_loop') as mock_loop:
            mock_status = {
                "status": "active",
                "active_sessions": 2,
                "completed_sessions": 5,
                "learning_data": {"total_sessions": 7}
            }
            mock_loop.return_value.get_healing_status.return_value = mock_status
            
            result = await get_healing_status(
                request=self.mock_request,
                auth_context=self.mock_auth_context
            )
            
            self.assertTrue(result["success"])
            self.assertEqual(result["status"], "active")
            self.assertEqual(result["active_sessions"], 2)
            self.assertEqual(result["completed_sessions"], 5)


class TestOrchestratorMCPTools(unittest.TestCase):
    """Test cases for orchestrator MCP tools with healing integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_project_id = "orchestrator_mcp_test"
        self.mock_request = Mock()
        self.mock_auth_context = Mock()
    
    @pytest.mark.asyncio
    async def test_generate_application_with_healing_tool(self):
        """Test generate_application_with_healing MCP tool"""
        with patch('src.agents.orchestrator_mcp_tools.get_orchestrator') as mock_orchestrator:
            mock_result = {
                "project_id": self.test_project_id,
                "status": "completed",
                "generation_summary": "Test application generated"
            }
            mock_orchestrator.return_value.generate_complete_application.return_value = mock_result
            
            result = await generate_application_with_healing(
                description="Test application description",
                project_type="fullstack",
                technology_stack="React + FastAPI",
                request=self.mock_request,
                auth_context=self.mock_auth_context
            )
            
            self.assertTrue(result["success"])
            self.assertTrue(result["healing_enabled"])
            self.assertEqual(result["project_id"], self.test_project_id)
            self.assertIn("correlation_id", result)
    
    @pytest.mark.asyncio
    async def test_enable_project_healing_tool(self):
        """Test enable_project_healing MCP tool"""
        with patch('src.agents.orchestrator_mcp_tools.get_orchestrator') as mock_orchestrator:
            mock_result = {
                "success": True,
                "project_id": self.test_project_id,
                "healing_enabled": True,
                "monitoring_active": True
            }
            mock_orchestrator.return_value.enable_healing_for_project.return_value = mock_result
            
            result = await enable_project_healing(
                project_id=self.test_project_id,
                request=self.mock_request,
                auth_context=self.mock_auth_context
            )
            
            self.assertTrue(result["success"])
            self.assertEqual(result["project_id"], self.test_project_id)
            self.assertTrue(result["healing_enabled"])
            self.assertTrue(result["monitoring_active"])
    
    @pytest.mark.asyncio
    async def test_disable_project_healing_tool(self):
        """Test disable_project_healing MCP tool"""
        with patch('src.agents.orchestrator_mcp_tools.get_orchestrator') as mock_orchestrator:
            mock_result = {
                "success": True,
                "project_id": self.test_project_id,
                "healing_enabled": False
            }
            mock_orchestrator.return_value.disable_healing_for_project.return_value = mock_result
            
            result = await disable_project_healing(
                project_id=self.test_project_id,
                request=self.mock_request,
                auth_context=self.mock_auth_context
            )
            
            self.assertTrue(result["success"])
            self.assertEqual(result["project_id"], self.test_project_id)
            self.assertFalse(result["healing_enabled"])
    
    @pytest.mark.asyncio
    async def test_get_orchestrator_health_status_tool(self):
        """Test get_orchestrator_health_status MCP tool"""
        with patch('src.agents.orchestrator_mcp_tools.get_orchestrator') as mock_orchestrator:
            mock_status = {
                "project_id": self.test_project_id,
                "healing_enabled": True,
                "failure_count": 1,
                "health_status": "good",
                "health_score": 0.8
            }
            mock_orchestrator.return_value.get_project_health_status.return_value = mock_status
            
            result = await get_orchestrator_health_status(
                project_id=self.test_project_id,
                request=self.mock_request,
                auth_context=self.mock_auth_context
            )
            
            self.assertTrue(result["success"])
            self.assertEqual(result["project_id"], self.test_project_id)
            self.assertTrue(result["healing_enabled"])
            self.assertEqual(result["health_status"], "good")
    
    @pytest.mark.asyncio
    async def test_trigger_orchestrator_healing_tool(self):
        """Test trigger_orchestrator_healing MCP tool"""
        with patch('src.agents.orchestrator_mcp_tools.get_orchestrator') as mock_orchestrator:
            mock_orchestrator.return_value.trigger_healing_on_failure.return_value = True
            
            result = await trigger_orchestrator_healing(
                project_id=self.test_project_id,
                issue_description="Test orchestration issue",
                task_context={"task_type": "test_task"},
                request=self.mock_request,
                auth_context=self.mock_auth_context
            )
            
            self.assertTrue(result["success"])
            self.assertEqual(result["project_id"], self.test_project_id)
            self.assertTrue(result["healing_triggered"])
    
    @pytest.mark.asyncio
    async def test_get_orchestrator_status_tool(self):
        """Test get_orchestrator_status MCP tool"""
        with patch('src.agents.orchestrator_mcp_tools.get_orchestrator') as mock_orchestrator:
            mock_orchestrator_obj = Mock()
            mock_orchestrator_obj.active_sessions = {}
            mock_orchestrator_obj.tasks = {}
            mock_orchestrator_obj.healing_enabled = True
            mock_orchestrator_obj.auto_healing_threshold = 2
            mock_orchestrator_obj.project_health_status = {}
            mock_orchestrator_obj.get_project_health_status.return_value = {}
            
            mock_orchestrator.return_value = mock_orchestrator_obj
            
            result = await get_orchestrator_status(
                request=self.mock_request,
                auth_context=self.mock_auth_context
            )
            
            self.assertTrue(result["success"])
            self.assertIn("orchestrator_status", result)
            self.assertTrue(result["orchestrator_status"]["healing_enabled"])
            self.assertEqual(result["orchestrator_status"]["healing_threshold"], 2)
    
    @pytest.mark.asyncio
    async def test_configure_healing_settings_tool(self):
        """Test configure_healing_settings MCP tool"""
        with patch('src.agents.orchestrator_mcp_tools.get_orchestrator') as mock_orchestrator:
            mock_orchestrator_obj = Mock()
            mock_orchestrator_obj.auto_healing_threshold = 2
            mock_orchestrator_obj.healing_enabled = True
            
            mock_orchestrator.return_value = mock_orchestrator_obj
            
            result = await configure_healing_settings(
                auto_healing_threshold=3,
                healing_enabled=False,
                request=self.mock_request,
                auth_context=self.mock_auth_context
            )
            
            self.assertTrue(result["success"])
            self.assertIn("changes", result)
            self.assertIn("current_settings", result)
            
            # Check that settings were updated
            self.assertEqual(mock_orchestrator_obj.auto_healing_threshold, 3)
            self.assertFalse(mock_orchestrator_obj.healing_enabled)


class TestMCPToolsIntegration(unittest.TestCase):
    """Integration tests for MCP tools working together"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.test_project_id = "mcp_integration_test"
        self.mock_request = Mock()
        self.mock_auth_context = Mock()
    
    @pytest.mark.asyncio
    async def test_full_healing_workflow_via_mcp(self):
        """Test complete healing workflow using MCP tools"""
        # Test sequence: generate app -> enable healing -> trigger healing -> check status
        
        # 1. Generate application with healing
        with patch('src.agents.orchestrator_mcp_tools.get_orchestrator') as mock_orchestrator:
            mock_result = {
                "project_id": self.test_project_id,
                "status": "completed"
            }
            mock_orchestrator.return_value.generate_complete_application.return_value = mock_result
            
            app_result = await generate_application_with_healing(
                description="Test app",
                request=self.mock_request,
                auth_context=self.mock_auth_context
            )
            
            self.assertTrue(app_result["success"])
            self.assertTrue(app_result["healing_enabled"])
        
        # 2. Perform health check
        with patch('src.healing.healing_tools.get_health_monitor') as mock_monitor:
            mock_report = Mock()
            mock_report.overall_status.value = "warning"
            mock_report.health_score = 0.6
            mock_report.issues = [Mock()]
            mock_report.issues[0].id = "test_issue"
            mock_report.issues[0].type.value = "runtime_error"
            mock_report.issues[0].severity = 7
            mock_report.issues[0].description = "Test issue"
            mock_report.issues[0].location = "test.py:10"
            mock_report.recommendations = ["Fix the issue"]
            mock_report.timestamp.isoformat.return_value = "2024-01-01T00:00:00"
            
            mock_monitor.return_value.perform_comprehensive_health_check.return_value = mock_report
            
            health_result = await perform_health_check(
                project_id=self.test_project_id,
                request=self.mock_request,
                auth_context=self.mock_auth_context
            )
            
            self.assertTrue(health_result["success"])
            self.assertEqual(health_result["health_status"], "warning")
            self.assertEqual(health_result["issues_count"], 1)
        
        # 3. Trigger healing session
        with patch('src.healing.healing_tools.get_healing_loop') as mock_loop:
            mock_session_id = str(uuid.uuid4())
            mock_loop.return_value.trigger_healing_session.return_value = mock_session_id
            
            healing_result = await trigger_healing_session(
                project_id=self.test_project_id,
                issue_description="Runtime error needs fixing",
                issue_severity=7,
                request=self.mock_request,
                auth_context=self.mock_auth_context
            )
            
            self.assertTrue(healing_result["success"])
            self.assertTrue(healing_result["healing_session_triggered"])
            self.assertEqual(healing_result["session_id"], mock_session_id)
        
        # 4. Check healing status
        with patch('src.healing.healing_tools.get_healing_loop') as mock_loop:
            mock_status = {
                "status": "active",
                "active_sessions": 1,
                "completed_sessions": 0
            }
            mock_loop.return_value.get_healing_status.return_value = mock_status
            
            status_result = await get_healing_status(
                request=self.mock_request,
                auth_context=self.mock_auth_context
            )
            
            self.assertTrue(status_result["success"])
            self.assertEqual(status_result["status"], "active")
            self.assertEqual(status_result["active_sessions"], 1)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])