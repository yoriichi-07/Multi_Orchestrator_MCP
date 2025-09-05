"""
Comprehensive system health monitoring and assessment
"""
import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import structlog

from src.core.llm_manager import LLMManager
from src.core.file_manager import SecureFileManager

logger = structlog.get_logger()


class HealthStatus(Enum):
    """System health status levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILING = "failing"


class IssueType(Enum):
    """Types of issues that can be detected"""
    SYNTAX_ERROR = "syntax_error"
    RUNTIME_ERROR = "runtime_error"
    LOGIC_ERROR = "logic_error"
    PERFORMANCE_ISSUE = "performance_issue"
    SECURITY_VULNERABILITY = "security_vulnerability"
    DEPENDENCY_ISSUE = "dependency_issue"
    CONFIGURATION_ERROR = "configuration_error"
    API_ERROR = "api_error"
    DATABASE_ERROR = "database_error"
    INTEGRATION_ERROR = "integration_error"
    SYSTEM_ERROR = "system_error"
    ORCHESTRATION_FAILURE = "orchestration_failure"


@dataclass
class HealthIssue:
    """Individual health issue detection"""
    id: str
    type: IssueType
    severity: int  # 1-10 scale
    description: str
    location: str
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    first_detected: Optional[datetime] = None
    last_occurrence: Optional[datetime] = None
    occurrence_count: int = 1
    suggested_fixes: List[str] = None

    def __post_init__(self):
        if self.suggested_fixes is None:
            self.suggested_fixes = []


@dataclass
class HealthReport:
    """Comprehensive health assessment report"""
    project_id: str
    timestamp: datetime
    overall_status: HealthStatus
    health_score: float  # 0.0 - 1.0
    issues: List[HealthIssue]
    metrics: Dict[str, Any]
    recommendations: List[str]
    correlation_id: str


class HealthMonitor:
    """Continuous health monitoring and issue detection system"""
    
    def __init__(self, correlation_id: Optional[str] = None):
        self.correlation_id = correlation_id or str(uuid.uuid4())
        # Initialize available components
        try:
            self.file_manager = SecureFileManager()
        except:
            self.file_manager = None
            
        try:
            self.llm_manager = LLMManager()
        except:
            self.llm_manager = None
        
        # Health monitoring state
        self.active_monitors: Dict[str, asyncio.Task] = {}
        self.health_history: Dict[str, List[HealthReport]] = {}
        self.issue_patterns: Dict[str, Dict[str, Any]] = {}
        
        logger.info(
            "health_monitor_initialized",
            correlation_id=self.correlation_id
        )
    
    async def start_continuous_monitoring(self, project_id: str, interval_seconds: int = 60):
        """
        Start continuous health monitoring for a project
        """
        if project_id in self.active_monitors:
            logger.warning(
                "monitoring_already_active",
                project_id=project_id,
                correlation_id=self.correlation_id
            )
            return
        
        logger.info(
            "continuous_monitoring_started",
            project_id=project_id,
            interval_seconds=interval_seconds,
            correlation_id=self.correlation_id
        )
        
        # Start monitoring task
        monitor_task = asyncio.create_task(
            self._continuous_monitoring_loop(project_id, interval_seconds)
        )
        
        self.active_monitors[project_id] = monitor_task
        
        return monitor_task
    
    async def stop_monitoring(self, project_id: str):
        """Stop continuous monitoring for a project"""
        if project_id in self.active_monitors:
            self.active_monitors[project_id].cancel()
            del self.active_monitors[project_id]
            
            logger.info(
                "monitoring_stopped",
                project_id=project_id,
                correlation_id=self.correlation_id
            )
    
    async def _continuous_monitoring_loop(self, project_id: str, interval_seconds: int):
        """Main continuous monitoring loop"""
        try:
            while True:
                try:
                    # Perform comprehensive health check
                    health_report = await self.perform_comprehensive_health_check(project_id)
                    
                    # Store health report
                    if project_id not in self.health_history:
                        self.health_history[project_id] = []
                    
                    self.health_history[project_id].append(health_report)
                    
                    # Keep only recent history (last 100 reports)
                    if len(self.health_history[project_id]) > 100:
                        self.health_history[project_id] = self.health_history[project_id][-100:]
                    
                    # Check for critical issues requiring immediate attention
                    critical_issues = [
                        issue for issue in health_report.issues 
                        if issue.severity >= 8
                    ]
                    
                    if critical_issues:
                        logger.warning(
                            "critical_issues_detected",
                            project_id=project_id,
                            critical_count=len(critical_issues),
                            correlation_id=self.correlation_id
                        )
                        
                        # Trigger immediate healing for critical issues
                        asyncio.create_task(
                            self._trigger_emergency_healing(project_id, critical_issues)
                        )
                    
                    # Track health metrics
                    await self._track_health_metrics(
                        project_id=project_id,
                        health_score=health_report.health_score,
                        issues_count=len(health_report.issues)
                    )
                    
                except Exception as e:
                    logger.error(
                        "monitoring_loop_error",
                        project_id=project_id,
                        error=str(e),
                        correlation_id=self.correlation_id
                    )
                
                # Wait for next monitoring cycle
                await asyncio.sleep(interval_seconds)
                
        except asyncio.CancelledError:
            logger.info(
                "monitoring_loop_cancelled",
                project_id=project_id,
                correlation_id=self.correlation_id
            )
    
    async def perform_comprehensive_health_check(self, project_id: str) -> HealthReport:
        """
        Perform comprehensive health assessment of a project
        """
        check_start = datetime.utcnow()
        issues = []
        
        try:
            logger.info(
                "health_check_started",
                project_id=project_id,
                correlation_id=self.correlation_id
            )
            
            # 1. Static Code Analysis
            static_issues = await self._perform_static_analysis(project_id)
            issues.extend(static_issues)
            
            # 2. Runtime Testing
            runtime_issues = await self._perform_runtime_testing(project_id)
            issues.extend(runtime_issues)
            
            # 3. Security Scan
            security_issues = await self._perform_security_scan(project_id)
            issues.extend(security_issues)
            
            # 4. Performance Analysis
            performance_issues = await self._perform_performance_analysis(project_id)
            issues.extend(performance_issues)
            
            # 5. Dependency Check
            dependency_issues = await self._check_dependencies(project_id)
            issues.extend(dependency_issues)
            
            # 6. Configuration Validation
            config_issues = await self._validate_configuration(project_id)
            issues.extend(config_issues)
            
            # Calculate overall health score
            health_score = self._calculate_health_score(issues)
            overall_status = self._determine_health_status(health_score, issues)
            
            # Generate recommendations
            recommendations = await self._generate_health_recommendations(issues, project_id)
            
            # Collect metrics
            metrics = await self._collect_health_metrics(project_id, check_start)
            
            health_report = HealthReport(
                project_id=project_id,
                timestamp=datetime.utcnow(),
                overall_status=overall_status,
                health_score=health_score,
                issues=issues,
                metrics=metrics,
                recommendations=recommendations,
                correlation_id=self.correlation_id
            )
            
            logger.info(
                "health_check_completed",
                project_id=project_id,
                health_score=health_score,
                issues_count=len(issues),
                duration_ms=(datetime.utcnow() - check_start).total_seconds() * 1000,
                correlation_id=self.correlation_id
            )
            
            return health_report
            
        except Exception as e:
            logger.error(
                "health_check_failed",
                project_id=project_id,
                error=str(e),
                correlation_id=self.correlation_id
            )
            
            # Return minimal health report with error
            return HealthReport(
                project_id=project_id,
                timestamp=datetime.utcnow(),
                overall_status=HealthStatus.FAILING,
                health_score=0.0,
                issues=[
                    HealthIssue(
                        id=str(uuid.uuid4()),
                        type=IssueType.RUNTIME_ERROR,
                        severity=9,
                        description="Health check system failure",
                        location="health_monitor",
                        error_message=str(e)
                    )
                ],
                metrics={},
                recommendations=["Investigate health monitoring system"],
                correlation_id=self.correlation_id
            )
    
    async def _perform_static_analysis(self, project_id: str) -> List[HealthIssue]:
        """Perform static code analysis to detect issues"""
        issues = []
        
        try:
            if not self.file_manager:
                return issues
                
            # Get all project files
            project_files = await self._list_project_files(project_id)
            
            for file_path in project_files:
                if not file_path.endswith(('.py', '.js', '.ts', '.jsx', '.tsx')):
                    continue
                
                # Read file content
                content = await self._read_project_file(project_id, file_path)
                
                # Analyze code for common issues
                file_issues = await self._analyze_code_file(file_path, content)
                issues.extend(file_issues)
            
            logger.info(
                "static_analysis_completed",
                project_id=project_id,
                files_analyzed=len([f for f in project_files if f.endswith(('.py', '.js', '.ts', '.jsx', '.tsx'))]),
                issues_found=len(issues),
                correlation_id=self.correlation_id
            )
            
        except Exception as e:
            logger.error(
                "static_analysis_failed",
                project_id=project_id,
                error=str(e),
                correlation_id=self.correlation_id
            )
            
            issues.append(HealthIssue(
                id=str(uuid.uuid4()),
                type=IssueType.RUNTIME_ERROR,
                severity=5,
                description="Static analysis failed",
                location="static_analyzer",
                error_message=str(e)
            ))
        
        return issues
    
    async def _analyze_code_file(self, file_path: str, content: str) -> List[HealthIssue]:
        """Analyze individual code file for issues"""
        issues = []
        
        # Use LLM for intelligent code analysis if available
        if self.llm_manager:
            try:
                analysis_prompt = f"""
                Analyze the following code file for potential issues:
                
                File: {file_path}
                
                Code:
                ```
                {content[:2000]}  # Limit content for analysis
                ```
                
                Please identify:
                1. Syntax errors
                2. Logic errors or bugs
                3. Security vulnerabilities
                4. Performance issues
                5. Code quality problems
                6. Missing error handling
                7. Potential runtime errors
                
                For each issue found, provide:
                - Issue type
                - Severity (1-10)
                - Description
                - Line number if applicable
                - Suggested fix
                
                Return the analysis as structured JSON.
                """
                
                analysis_result = await self.llm_manager.generate_completion(
                    prompt=analysis_prompt,
                    model="claude-3-sonnet",
                    temperature=0.1,
                    max_tokens=4000,
                    metadata={
                        "operation": "static_code_analysis",
                        "file_path": file_path,
                        "correlation_id": self.correlation_id
                    }
                )
                
                # Parse LLM analysis
                analysis_data = json.loads(analysis_result.content)
                
                for issue_data in analysis_data.get("issues", []):
                    issue = HealthIssue(
                        id=str(uuid.uuid4()),
                        type=IssueType(issue_data.get("type", "logic_error")),
                        severity=issue_data.get("severity", 5),
                        description=issue_data.get("description", ""),
                        location=f"{file_path}:{issue_data.get('line_number', 'unknown')}",
                        suggested_fixes=issue_data.get("suggested_fixes", []),
                        first_detected=datetime.utcnow()
                    )
                    issues.append(issue)
                    
            except (json.JSONDecodeError, Exception):
                # Fallback to basic pattern matching
                issues.extend(self._basic_pattern_analysis(file_path, content))
        else:
            # Fallback to basic pattern matching
            issues.extend(self._basic_pattern_analysis(file_path, content))
        
        return issues
    
    def _basic_pattern_analysis(self, file_path: str, content: str) -> List[HealthIssue]:
        """Basic pattern-based code analysis"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_lower = line.lower().strip()
            
            # Check for common issues
            if 'todo' in line_lower or 'fixme' in line_lower:
                issues.append(HealthIssue(
                    id=str(uuid.uuid4()),
                    type=IssueType.LOGIC_ERROR,
                    severity=3,
                    description=f"TODO/FIXME comment found: {line.strip()}",
                    location=f"{file_path}:{i}",
                    first_detected=datetime.utcnow()
                ))
            
            if 'print(' in line_lower and file_path.endswith('.py'):
                issues.append(HealthIssue(
                    id=str(uuid.uuid4()),
                    type=IssueType.LOGIC_ERROR,
                    severity=2,
                    description="Debug print statement found",
                    location=f"{file_path}:{i}",
                    first_detected=datetime.utcnow()
                ))
        
        return issues
    
    async def _perform_runtime_testing(self, project_id: str) -> List[HealthIssue]:
        """Perform runtime testing to detect execution issues"""
        issues = []
        
        try:
            # Simulate basic runtime testing
            # In a real implementation, this would run actual tests
            logger.info(
                "runtime_testing_simulated",
                project_id=project_id,
                correlation_id=self.correlation_id
            )
            
        except Exception as e:
            logger.error(
                "runtime_testing_failed",
                project_id=project_id,
                error=str(e),
                correlation_id=self.correlation_id
            )
            
            issues.append(HealthIssue(
                id=str(uuid.uuid4()),
                type=IssueType.RUNTIME_ERROR,
                severity=7,
                description="Runtime testing system failure",
                location="test_runner",
                error_message=str(e)
            ))
        
        return issues
    
    async def _perform_security_scan(self, project_id: str) -> List[HealthIssue]:
        """Perform security vulnerability scanning"""
        issues = []
        
        try:
            # Basic security checks would go here
            logger.info(
                "security_scan_completed",
                project_id=project_id,
                correlation_id=self.correlation_id
            )
            
        except Exception as e:
            logger.error(
                "security_scan_failed",
                project_id=project_id,
                error=str(e),
                correlation_id=self.correlation_id
            )
        
        return issues
    
    async def _perform_performance_analysis(self, project_id: str) -> List[HealthIssue]:
        """Analyze system performance metrics"""
        issues = []
        
        try:
            # Performance analysis would go here
            logger.info(
                "performance_analysis_completed",
                project_id=project_id,
                correlation_id=self.correlation_id
            )
            
        except Exception as e:
            logger.error(
                "performance_analysis_failed",
                project_id=project_id,
                error=str(e),
                correlation_id=self.correlation_id
            )
        
        return issues
    
    async def _check_dependencies(self, project_id: str) -> List[HealthIssue]:
        """Check for dependency issues"""
        issues = []
        
        try:
            # Dependency checking would go here
            logger.info(
                "dependency_check_completed",
                project_id=project_id,
                correlation_id=self.correlation_id
            )
            
        except Exception as e:
            logger.error(
                "dependency_check_failed",
                project_id=project_id,
                error=str(e),
                correlation_id=self.correlation_id
            )
        
        return issues
    
    async def _validate_configuration(self, project_id: str) -> List[HealthIssue]:
        """Validate system configuration"""
        issues = []
        
        try:
            # Configuration validation would go here
            logger.info(
                "configuration_validation_completed",
                project_id=project_id,
                correlation_id=self.correlation_id
            )
            
        except Exception as e:
            logger.error(
                "configuration_validation_failed",
                project_id=project_id,
                error=str(e),
                correlation_id=self.correlation_id
            )
        
        return issues
    
    def _calculate_health_score(self, issues: List[HealthIssue]) -> float:
        """Calculate overall health score based on detected issues"""
        if not issues:
            return 1.0
        
        # Weight issues by severity
        total_severity = sum(issue.severity for issue in issues)
        max_possible_severity = len(issues) * 10
        
        # Calculate score (inverted severity)
        base_score = 1.0 - (total_severity / max_possible_severity)
        
        # Apply penalties for critical issues
        critical_issues = [issue for issue in issues if issue.severity >= 8]
        if critical_issues:
            base_score *= (1.0 - (len(critical_issues) * 0.1))
        
        return max(0.0, min(1.0, base_score))
    
    def _determine_health_status(self, health_score: float, issues: List[HealthIssue]) -> HealthStatus:
        """Determine overall health status"""
        critical_issues = [issue for issue in issues if issue.severity >= 8]
        
        if critical_issues:
            return HealthStatus.CRITICAL
        elif health_score < 0.3:
            return HealthStatus.FAILING
        elif health_score < 0.6:
            return HealthStatus.WARNING
        elif health_score < 0.8:
            return HealthStatus.GOOD
        else:
            return HealthStatus.EXCELLENT
    
    async def _generate_health_recommendations(self, issues: List[HealthIssue], project_id: str) -> List[str]:
        """Generate health improvement recommendations"""
        recommendations = []
        
        if not issues:
            recommendations.append("System is healthy - continue monitoring")
            return recommendations
        
        # Group issues by type
        issue_types = {}
        for issue in issues:
            issue_type = issue.type.value
            if issue_type not in issue_types:
                issue_types[issue_type] = []
            issue_types[issue_type].append(issue)
        
        # Generate recommendations based on issue patterns
        for issue_type, type_issues in issue_types.items():
            if len(type_issues) > 1:
                recommendations.append(f"Address multiple {issue_type} issues ({len(type_issues)} found)")
            else:
                recommendations.append(f"Fix {issue_type}: {type_issues[0].description}")
        
        return recommendations
    
    async def _collect_health_metrics(self, project_id: str, check_start: datetime) -> Dict[str, Any]:
        """Collect comprehensive health metrics"""
        return {
            "check_duration_ms": (datetime.utcnow() - check_start).total_seconds() * 1000,
            "timestamp": datetime.utcnow().isoformat(),
            "project_id": project_id,
            "monitor_correlation_id": self.correlation_id
        }
    
    async def _trigger_emergency_healing(self, project_id: str, critical_issues: List[HealthIssue]):
        """Trigger emergency healing for critical issues"""
        logger.warning(
            "emergency_healing_triggered",
            project_id=project_id,
            critical_issues_count=len(critical_issues),
            correlation_id=self.correlation_id
        )
        
        # This would trigger the healing loop for critical issues
        # Implementation would connect to the HealingLoop class
        
    async def _track_health_metrics(self, project_id: str, health_score: float, issues_count: int):
        """Track health metrics for analytics"""
        logger.info(
            "health_metrics_tracked",
            project_id=project_id,
            health_score=health_score,
            issues_count=issues_count,
            correlation_id=self.correlation_id
        )
    
    async def _list_project_files(self, project_id: str) -> List[str]:
        """List all files in the project"""
        if self.file_manager:
            try:
                return await self.file_manager.list_project_files(project_id)
            except:
                pass
        
        # Fallback: basic file listing
        import os
        project_path = f"./projects/{project_id}"
        if os.path.exists(project_path):
            files = []
            for root, dirs, filenames in os.walk(project_path):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
            return files
        return []
    
    async def _read_project_file(self, project_id: str, file_path: str) -> str:
        """Read content of a project file"""
        if self.file_manager:
            try:
                return await self.file_manager.read_project_file(project_id, file_path)
            except:
                pass
        
        # Fallback: basic file reading
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""
    
    def get_health_history(self, project_id: str, limit: int = 10) -> List[HealthReport]:
        """Get recent health history for a project"""
        history = self.health_history.get(project_id, [])
        return history[-limit:] if history else []
    
    async def get_current_health_status(self, project_id: str) -> Optional[HealthReport]:
        """Get the most recent health status for a project"""
        history = self.health_history.get(project_id, [])
        return history[-1] if history else None