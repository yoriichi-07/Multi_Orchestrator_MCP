"""
Self-Healing Loop System

This module provides comprehensive autonomous error detection, analysis,
and resolution capabilities for the Multi-Agent Orchestrator system.

Components:
- HealthMonitor: Continuous system health assessment and monitoring
- ErrorAnalyzer: Advanced error analysis and root cause identification
- SolutionGenerator: AI-powered solution generation and implementation planning
- HealingLoop: Main orchestrator for the complete healing cycle

The self-healing system enables zero-human-intervention error resolution
through intelligent monitoring, analysis, and automated fixes.
"""

from .health_monitor import HealthMonitor, HealthStatus, IssueType, HealthIssue, HealthReport
from .error_analyzer import ErrorAnalyzer, ErrorPattern
from .solution_generator import SolutionGenerator, Solution, SolutionType

__all__ = [
    "HealthMonitor",
    "HealthStatus", 
    "IssueType",
    "HealthIssue",
    "HealthReport",
    "ErrorAnalyzer",
    "ErrorPattern",
    "SolutionGenerator",
    "Solution",
    "SolutionType"
]

__version__ = "1.0.0"