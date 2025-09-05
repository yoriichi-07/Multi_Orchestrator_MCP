"""
Main healing loop coordinator that integrates all healing components
and manages the complete healing cycle
"""
import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import structlog

from src.healing.health_monitor import HealthMonitor, HealthReport, HealthIssue, HealthStatus
from src.healing.error_analyzer import ErrorAnalyzer
from src.healing.solution_generator import SolutionGenerator, Solution
from src.core.llm_manager import LLMManager
from src.core.file_manager import SecureFileManager

logger = structlog.get_logger()


class HealingPhase(Enum):
    """Phases of the healing loop"""
    MONITORING = "monitoring"
    DETECTION = "detection"
    ANALYSIS = "analysis"
    SOLUTION_GENERATION = "solution_generation"
    IMPLEMENTATION = "implementation"
    VALIDATION = "validation"
    LEARNING = "learning"
    COMPLETED = "completed"
    FAILED = "failed"


class HealingStatus(Enum):
    """Status of healing operations"""
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    EMERGENCY = "emergency"
    MAINTENANCE = "maintenance"


class HealingSession:
    """Individual healing session tracking"""
    def __init__(
        self,
        session_id: str,
        project_id: str,
        trigger_issue: HealthIssue,
        correlation_id: str
    ):
        self.session_id = session_id
        self.project_id = project_id
        self.trigger_issue = trigger_issue
        self.correlation_id = correlation_id
        self.start_time = datetime.utcnow()
        self.end_time: Optional[datetime] = None
        self.current_phase = HealingPhase.DETECTION
        self.error_analysis: Optional[Dict[str, Any]] = None
        self.generated_solutions: List[Solution] = []
        self.applied_solution: Optional[Solution] = None
        self.validation_results: Optional[Dict[str, Any]] = None
        self.success = False
        self.failure_reason: Optional[str] = None
        self.healing_logs: List[Dict[str, Any]] = []
    
    def add_log(self, phase: HealingPhase, message: str, data: Optional[Dict[str, Any]] = None):
        """Add log entry to healing session"""
        self.healing_logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "phase": phase.value,
            "message": message,
            "data": data or {}
        })
    
    def complete_session(self, success: bool, failure_reason: Optional[str] = None):
        """Mark healing session as completed"""
        self.end_time = datetime.utcnow()
        self.success = success
        self.failure_reason = failure_reason
        self.current_phase = HealingPhase.COMPLETED if success else HealingPhase.FAILED
    
    def get_duration(self) -> timedelta:
        """Get duration of healing session"""
        end_time = self.end_time or datetime.utcnow()
        return end_time - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert healing session to dictionary"""
        return {
            "session_id": self.session_id,
            "project_id": self.project_id,
            "trigger_issue": {
                "id": self.trigger_issue.id,
                "type": self.trigger_issue.type.value,
                "severity": self.trigger_issue.severity,
                "description": self.trigger_issue.description
            },
            "correlation_id": self.correlation_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.get_duration().total_seconds(),
            "current_phase": self.current_phase.value,
            "success": self.success,
            "failure_reason": self.failure_reason,
            "solutions_generated": len(self.generated_solutions),
            "solution_applied": self.applied_solution.solution_id if self.applied_solution else None,
            "healing_logs_count": len(self.healing_logs)
        }


class HealingLoop:
    """Main self-healing loop orchestrator"""
    
    def __init__(self, correlation_id: Optional[str] = None):
        self.correlation_id = correlation_id or str(uuid.uuid4())
        
        # Initialize healing components
        self.health_monitor = HealthMonitor(correlation_id=self.correlation_id)
        self.error_analyzer = ErrorAnalyzer(correlation_id=self.correlation_id)
        self.solution_generator = SolutionGenerator(correlation_id=self.correlation_id)
        
        # Initialize supporting components
        try:
            self.llm_manager = LLMManager()
        except:
            self.llm_manager = None
            
        try:
            self.file_manager = SecureFileManager()
        except:
            self.file_manager = None
        
        # Healing loop state
        self.status = HealingStatus.IDLE
        self.active_sessions: Dict[str, HealingSession] = {}
        self.completed_sessions: List[HealingSession] = []
        self.learning_data: Dict[str, Any] = {}
        
        # Configuration
        self.config = {
            "max_concurrent_sessions": 3,
            "emergency_healing_timeout": 300,  # 5 minutes
            "validation_timeout": 120,  # 2 minutes
            "max_solution_attempts": 3,
            "learning_enabled": True,
            "auto_apply_high_confidence": True,
            "confidence_threshold": 0.8
        }
        
        logger.info(
            "healing_loop_initialized",
            correlation_id=self.correlation_id,
            config=self.config
        )
    
    async def start_healing_loop(self, project_id: str):
        """Start the main healing loop for a project"""
        try:
            logger.info(
                "healing_loop_started",
                project_id=project_id,
                correlation_id=self.correlation_id
            )
            
            self.status = HealingStatus.ACTIVE
            
            # Start continuous health monitoring
            await self.health_monitor.start_continuous_monitoring(
                project_id=project_id,
                interval_seconds=60
            )
            
            # Start healing orchestration loop
            healing_task = asyncio.create_task(
                self._healing_orchestration_loop(project_id)
            )
            
            return healing_task
            
        except Exception as e:
            logger.error(
                "healing_loop_start_failed",
                project_id=project_id,
                error=str(e),
                correlation_id=self.correlation_id
            )
            self.status = HealingStatus.FAILED
            raise
    
    async def stop_healing_loop(self, project_id: str):
        """Stop the healing loop for a project"""
        try:
            await self.health_monitor.stop_monitoring(project_id)
            
            # Complete any active sessions
            for session in list(self.active_sessions.values()):
                if session.project_id == project_id:
                    session.complete_session(False, "Healing loop stopped")
                    self.completed_sessions.append(session)
                    del self.active_sessions[session.session_id]
            
            self.status = HealingStatus.IDLE
            
            logger.info(
                "healing_loop_stopped",
                project_id=project_id,
                correlation_id=self.correlation_id
            )
            
        except Exception as e:
            logger.error(
                "healing_loop_stop_failed",
                project_id=project_id,
                error=str(e),
                correlation_id=self.correlation_id
            )
    
    async def _healing_orchestration_loop(self, project_id: str):
        """Main healing orchestration loop"""
        try:
            while self.status == HealingStatus.ACTIVE:
                try:
                    # Check for critical issues requiring immediate healing
                    current_health = await self.health_monitor.get_current_health_status(project_id)
                    
                    if current_health:
                        await self._process_health_report(current_health)
                    
                    # Process active healing sessions
                    await self._process_active_sessions()
                    
                    # Clean up completed sessions
                    self._cleanup_completed_sessions()
                    
                    # Update learning data
                    if self.config["learning_enabled"]:
                        await self._update_learning_data()
                    
                    # Wait before next iteration
                    await asyncio.sleep(30)  # Check every 30 seconds
                    
                except Exception as e:
                    logger.error(
                        "healing_orchestration_error",
                        project_id=project_id,
                        error=str(e),
                        correlation_id=self.correlation_id
                    )
                    await asyncio.sleep(60)  # Wait longer on error
                    
        except asyncio.CancelledError:
            logger.info(
                "healing_orchestration_cancelled",
                project_id=project_id,
                correlation_id=self.correlation_id
            )
    
    async def _process_health_report(self, health_report: HealthReport):
        """Process health report and trigger healing if needed"""
        try:
            # Check for critical issues
            critical_issues = [
                issue for issue in health_report.issues
                if issue.severity >= 8
            ]
            
            for issue in critical_issues:
                await self.trigger_healing_session(health_report.project_id, issue)
            
            # Check for patterns of recurring issues
            recurring_issues = await self._detect_recurring_issues(health_report)
            for issue in recurring_issues:
                await self.trigger_healing_session(health_report.project_id, issue)
                
        except Exception as e:
            logger.error(
                "health_report_processing_failed",
                project_id=health_report.project_id,
                error=str(e),
                correlation_id=self.correlation_id
            )
    
    async def trigger_healing_session(self, project_id: str, trigger_issue: HealthIssue) -> str:
        """Trigger a new healing session for an issue"""
        try:
            # Check if we can start a new session
            if len(self.active_sessions) >= self.config["max_concurrent_sessions"]:
                logger.warning(
                    "healing_session_limit_reached",
                    project_id=project_id,
                    active_sessions=len(self.active_sessions),
                    correlation_id=self.correlation_id
                )
                return None
            
            # Create new healing session
            session_id = str(uuid.uuid4())
            session = HealingSession(
                session_id=session_id,
                project_id=project_id,
                trigger_issue=trigger_issue,
                correlation_id=self.correlation_id
            )
            
            self.active_sessions[session_id] = session
            
            logger.info(
                "healing_session_triggered",
                session_id=session_id,
                project_id=project_id,
                issue_type=trigger_issue.type.value,
                issue_severity=trigger_issue.severity,
                correlation_id=self.correlation_id
            )
            
            # Start healing process
            asyncio.create_task(self._execute_healing_session(session))
            
            return session_id
            
        except Exception as e:
            logger.error(
                "healing_session_trigger_failed",
                project_id=project_id,
                issue_id=trigger_issue.id,
                error=str(e),
                correlation_id=self.correlation_id
            )
            return None
    
    async def _execute_healing_session(self, session: HealingSession):
        """Execute complete healing session"""
        try:
            session.add_log(HealingPhase.DETECTION, "Healing session started")
            
            # Phase 1: Error Analysis
            session.current_phase = HealingPhase.ANALYSIS
            session.add_log(HealingPhase.ANALYSIS, "Starting error analysis")
            
            error_analysis = await self.error_analyzer.analyze_error(
                error_message=session.trigger_issue.error_message or session.trigger_issue.description,
                stack_trace=session.trigger_issue.stack_trace,
                code_context=session.trigger_issue.context
            )
            
            session.error_analysis = error_analysis
            session.add_log(HealingPhase.ANALYSIS, "Error analysis completed", {
                "primary_type": error_analysis.get("error_classification", {}).get("primary_type"),
                "severity": error_analysis.get("error_classification", {}).get("severity"),
                "confidence": error_analysis.get("error_classification", {}).get("confidence")
            })
            
            # Phase 2: Solution Generation
            session.current_phase = HealingPhase.SOLUTION_GENERATION
            session.add_log(HealingPhase.SOLUTION_GENERATION, "Starting solution generation")
            
            solutions = await self.solution_generator.generate_solutions(
                error_analysis=error_analysis,
                project_id=session.project_id
            )
            
            session.generated_solutions = solutions
            session.add_log(HealingPhase.SOLUTION_GENERATION, "Solution generation completed", {
                "solutions_count": len(solutions),
                "best_confidence": max([s.confidence for s in solutions]) if solutions else 0
            })
            
            # Phase 3: Solution Implementation
            if solutions:
                session.current_phase = HealingPhase.IMPLEMENTATION
                
                # Select best solution
                best_solution = max(solutions, key=lambda s: s.confidence)
                
                # Auto-apply if high confidence and enabled
                if (self.config["auto_apply_high_confidence"] and 
                    best_solution.confidence >= self.config["confidence_threshold"]):
                    
                    session.add_log(HealingPhase.IMPLEMENTATION, f"Auto-applying high confidence solution", {
                        "solution_id": best_solution.solution_id,
                        "confidence": best_solution.confidence
                    })
                    
                    implementation_result = await self._implement_solution(session, best_solution)
                    
                    if implementation_result["success"]:
                        session.applied_solution = best_solution
                        
                        # Phase 4: Validation
                        session.current_phase = HealingPhase.VALIDATION
                        validation_result = await self._validate_solution(session)
                        
                        if validation_result["success"]:
                            session.complete_session(True)
                            session.add_log(HealingPhase.COMPLETED, "Healing session completed successfully")
                        else:
                            session.complete_session(False, "Solution validation failed")
                            session.add_log(HealingPhase.FAILED, "Solution validation failed", validation_result)
                    else:
                        session.complete_session(False, "Solution implementation failed")
                        session.add_log(HealingPhase.FAILED, "Solution implementation failed", implementation_result)
                else:
                    session.complete_session(False, "No auto-applicable solution found")
                    session.add_log(HealingPhase.FAILED, "Manual intervention required", {
                        "reason": "Low confidence or auto-apply disabled",
                        "best_confidence": best_solution.confidence
                    })
            else:
                session.complete_session(False, "No solutions generated")
                session.add_log(HealingPhase.FAILED, "No solutions could be generated")
            
            # Phase 5: Learning
            if self.config["learning_enabled"]:
                session.current_phase = HealingPhase.LEARNING
                await self._update_learning_from_session(session)
                session.add_log(HealingPhase.LEARNING, "Learning data updated")
            
        except Exception as e:
            session.complete_session(False, f"Healing session exception: {str(e)}")
            session.add_log(HealingPhase.FAILED, "Healing session failed with exception", {"error": str(e)})
            
            logger.error(
                "healing_session_execution_failed",
                session_id=session.session_id,
                project_id=session.project_id,
                error=str(e),
                correlation_id=self.correlation_id
            )
        
        finally:
            # Move session to completed
            if session.session_id in self.active_sessions:
                del self.active_sessions[session.session_id]
                self.completed_sessions.append(session)
                
                logger.info(
                    "healing_session_completed",
                    session_id=session.session_id,
                    project_id=session.project_id,
                    success=session.success,
                    duration_seconds=session.get_duration().total_seconds(),
                    correlation_id=self.correlation_id
                )
    
    async def _implement_solution(self, session: HealingSession, solution: Solution) -> Dict[str, Any]:
        """Implement a solution"""
        try:
            # Basic implementation simulation
            # In a real implementation, this would execute the solution steps
            
            session.add_log(HealingPhase.IMPLEMENTATION, f"Implementing solution: {solution.description}")
            
            # Simulate implementation delay
            await asyncio.sleep(2)
            
            # For now, simulate success based on confidence
            success = solution.confidence > 0.7
            
            return {
                "success": success,
                "solution_id": solution.solution_id,
                "implementation_time": 2.0,
                "changes_made": solution.files_to_modify,
                "error": None if success else "Simulated implementation failure"
            }
            
        except Exception as e:
            return {
                "success": False,
                "solution_id": solution.solution_id,
                "error": str(e)
            }
    
    async def _validate_solution(self, session: HealingSession) -> Dict[str, Any]:
        """Validate that a solution fixed the issue"""
        try:
            session.add_log(HealingPhase.VALIDATION, "Starting solution validation")
            
            # Basic validation simulation
            # In a real implementation, this would run tests and checks
            
            # Simulate validation delay
            await asyncio.sleep(1)
            
            # For now, simulate success based on solution confidence
            success = session.applied_solution.confidence > 0.6 if session.applied_solution else False
            
            validation_result = {
                "success": success,
                "validation_time": 1.0,
                "tests_passed": 5 if success else 2,
                "tests_failed": 0 if success else 3,
                "error": None if success else "Simulated validation failure"
            }
            
            session.validation_results = validation_result
            return validation_result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _process_active_sessions(self):
        """Process and monitor active healing sessions"""
        for session in list(self.active_sessions.values()):
            # Check for timeout
            if session.get_duration().total_seconds() > self.config["emergency_healing_timeout"]:
                session.complete_session(False, "Session timeout")
                session.add_log(HealingPhase.FAILED, "Session timed out")
                
                del self.active_sessions[session.session_id]
                self.completed_sessions.append(session)
                
                logger.warning(
                    "healing_session_timeout",
                    session_id=session.session_id,
                    duration_seconds=session.get_duration().total_seconds(),
                    correlation_id=self.correlation_id
                )
    
    def _cleanup_completed_sessions(self):
        """Clean up old completed sessions"""
        # Keep only recent completed sessions (last 100)
        if len(self.completed_sessions) > 100:
            self.completed_sessions = self.completed_sessions[-100:]
    
    async def _detect_recurring_issues(self, health_report: HealthReport) -> List[HealthIssue]:
        """Detect recurring issues that need healing"""
        recurring_issues = []
        
        # Simple pattern detection - look for issues that appear frequently
        for issue in health_report.issues:
            if issue.occurrence_count > 3:  # Issue occurred more than 3 times
                recurring_issues.append(issue)
        
        return recurring_issues
    
    async def _update_learning_data(self):
        """Update learning data from healing sessions"""
        try:
            # Analyze successful and failed sessions
            successful_sessions = [s for s in self.completed_sessions if s.success]
            failed_sessions = [s for s in self.completed_sessions if not s.success]
            
            self.learning_data.update({
                "total_sessions": len(self.completed_sessions),
                "success_rate": len(successful_sessions) / len(self.completed_sessions) if self.completed_sessions else 0,
                "average_healing_time": sum(s.get_duration().total_seconds() for s in successful_sessions) / len(successful_sessions) if successful_sessions else 0,
                "common_failure_reasons": self._analyze_failure_reasons(failed_sessions),
                "most_effective_solutions": self._analyze_effective_solutions(successful_sessions),
                "last_updated": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.warning(
                "learning_data_update_failed",
                error=str(e),
                correlation_id=self.correlation_id
            )
    
    async def _update_learning_from_session(self, session: HealingSession):
        """Update learning data from a specific session"""
        # This would implement machine learning or pattern recognition
        # to improve future healing performance
        pass
    
    def _analyze_failure_reasons(self, failed_sessions: List[HealingSession]) -> Dict[str, int]:
        """Analyze common failure reasons"""
        failure_reasons = {}
        for session in failed_sessions:
            reason = session.failure_reason or "unknown"
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
        return failure_reasons
    
    def _analyze_effective_solutions(self, successful_sessions: List[HealingSession]) -> Dict[str, int]:
        """Analyze most effective solution types"""
        solution_types = {}
        for session in successful_sessions:
            if session.applied_solution:
                solution_type = session.applied_solution.solution_type
                solution_types[solution_type] = solution_types.get(solution_type, 0) + 1
        return solution_types
    
    def get_healing_status(self) -> Dict[str, Any]:
        """Get current healing loop status"""
        return {
            "status": self.status.value,
            "active_sessions": len(self.active_sessions),
            "completed_sessions": len(self.completed_sessions),
            "learning_data": self.learning_data,
            "config": self.config,
            "correlation_id": self.correlation_id
        }
    
    def get_session_details(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific healing session"""
        # Check active sessions
        if session_id in self.active_sessions:
            return self.active_sessions[session_id].to_dict()
        
        # Check completed sessions
        for session in self.completed_sessions:
            if session.session_id == session_id:
                return session.to_dict()
        
        return None