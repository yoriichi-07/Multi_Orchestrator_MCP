"""
Central agent orchestration system for autonomous software development
"""
import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import structlog

logger = structlog.get_logger()

# Healing system integration (lazy loaded to avoid circular imports)
_healing_loop = None

def get_healing_loop():
    """Get or create healing loop instance"""
    global _healing_loop
    if _healing_loop is None:
        from src.healing.healing_loop import HealingLoop
        _healing_loop = HealingLoop()
    return _healing_loop


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(Enum):
    """Available agent types"""
    FRONTEND = "frontend"
    BACKEND = "backend"
    REVIEWER = "reviewer"
    DEVOPS = "devops"


@dataclass
class Task:
    """Individual task for agent execution"""
    id: str
    type: str
    description: str
    agent_type: AgentType
    priority: int
    dependencies: List[str]
    parameters: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class AgentSession:
    """Active agent session"""
    agent_id: str
    agent_type: AgentType
    current_task_id: Optional[str] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    last_activity: Optional[datetime] = None
    performance_metrics: Dict[str, float] = None


class AgentOrchestrator:
    """Central orchestrator for multi-agent software development"""
    
    def __init__(self, correlation_id: Optional[str] = None):
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.logger = logger.bind(correlation_id=self.correlation_id)
        
        # Import agents
        from src.agents.reviewer import ReviewerAgent
        from src.agents.frontend_agent import FrontendAgent
        from src.agents.backend_agent import BackendAgent
        from src.agents.devops_agent import DevOpsAgent
        
        # Agent instances - all specialized agents now available
        self.agents = {
            AgentType.FRONTEND: FrontendAgent(correlation_id=self.correlation_id),
            AgentType.BACKEND: BackendAgent(correlation_id=self.correlation_id),
            AgentType.REVIEWER: ReviewerAgent(correlation_id=self.correlation_id),
            AgentType.DEVOPS: DevOpsAgent(correlation_id=self.correlation_id)
        }
        
        # Task management
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[str] = []
        self.active_sessions: Dict[str, AgentSession] = {}
        
        # Orchestration state
        self.workflow_templates = self._initialize_workflow_templates()
        
        # Healing integration
        self.healing_enabled = True
        self.auto_healing_threshold = 2  # Number of failures before triggering healing
        self.project_health_status = {}  # Track health status per project
        
        logger.info(
            "agent_orchestrator_initialized",
            correlation_id=self.correlation_id,
            agents_count=len(self.agents),
            healing_enabled=self.healing_enabled
        )
    
    async def generate_complete_application(
        self,
        description: str,
        project_type: str = "fullstack",
        technology_stack: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate complete application using coordinated agent workflow
        """
        start_time = datetime.utcnow()
        project_id = str(uuid.uuid4())
        
        try:
            self.logger.info(
                "generation_started",
                project_id=project_id,
                project_type=project_type,
                description_length=len(description)
            )
            
            # Enable healing for this project by default
            if self.healing_enabled:
                await self.enable_healing_for_project(project_id)
            
            # Analyze requirements and create task breakdown
            task_breakdown = await self._analyze_requirements(
                description=description,
                project_type=project_type,
                technology_stack=technology_stack
            )
            
            # Generate task execution plan
            execution_plan = await self._create_execution_plan(
                task_breakdown=task_breakdown,
                project_id=project_id
            )
            
            # Execute tasks through agent coordination
            execution_result = await self._execute_coordinated_workflow(
                execution_plan=execution_plan,
                project_id=project_id
            )
            
            # Final quality review using existing reviewer
            quality_result = await self._perform_final_quality_review(
                project_id=project_id,
                execution_result=execution_result
            )
            
            # Generate comprehensive summary
            generation_summary = await self._generate_completion_summary(
                project_id=project_id,
                task_breakdown=task_breakdown,
                execution_result=execution_result,
                quality_result=quality_result,
                start_time=start_time
            )
            
            self.logger.info(
                "generation_completed_successfully",
                project_id=project_id,
                duration_seconds=(datetime.utcnow() - start_time).total_seconds()
            )
            
            return generation_summary
            
        except Exception as e:
            self.logger.error(
                "application_generation_failed",
                project_id=project_id,
                error=str(e),
                correlation_id=self.correlation_id
            )
            
            # Trigger healing for application generation failures
            if self.healing_enabled and project_id in self.project_health_status:
                from src.healing.health_monitor import HealthIssue, IssueType
                
                trigger_issue = HealthIssue(
                    id=str(uuid.uuid4()),
                    type=IssueType.SYSTEM_ERROR,
                    severity=9,  # Very high severity for complete generation failures
                    description=f"Application generation failed: {str(e)}",
                    location=f"orchestrator_generation_{project_id}",
                    error_message=str(e),
                    stack_trace=None,
                    first_detected=datetime.utcnow(),
                    agent_context={
                        "project_id": project_id,
                        "project_type": project_type,
                        "orchestrator_correlation_id": self.correlation_id,
                        "failure_context": "application_generation"
                    }
                )
                
                healing_loop = get_healing_loop()
                session_id = await healing_loop.trigger_healing_session(project_id, trigger_issue)
                
                if session_id:
                    self.logger.info(
                        "healing_triggered_for_generation_failure",
                        project_id=project_id,
                        session_id=session_id,
                        correlation_id=self.correlation_id
                    )
            
            raise
    
    async def _analyze_requirements(
        self,
        description: str,
        project_type: str,
        technology_stack: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze project requirements to create detailed task breakdown
        """
        self.logger.info(
            "analyzing_requirements",
            project_type=project_type,
            has_tech_stack=technology_stack is not None
        )
        
        # For now, return a comprehensive mock analysis
        # This will be enhanced with LLM integration in later phases
        analysis = {
            "recommended_technology_stack": technology_stack or "React + FastAPI + PostgreSQL",
            "core_features": [
                {"name": "User Authentication", "priority": 1, "complexity": "medium"},
                {"name": "CRUD Operations", "priority": 1, "complexity": "low"},
                {"name": "Responsive UI", "priority": 2, "complexity": "medium"},
                {"name": "API Documentation", "priority": 3, "complexity": "low"},
                {"name": "Data Validation", "priority": 2, "complexity": "low"}
            ],
            "technical_architecture": {
                "frontend": "React with TypeScript",
                "backend": "FastAPI with Python",
                "database": "PostgreSQL",
                "deployment": "Docker containers"
            },
            "database_requirements": {
                "tables": ["users", "sessions", "data_entities"],
                "relationships": ["one-to-many", "many-to-many"],
                "indexes": ["user_email", "session_token"]
            },
            "api_endpoints": [
                {"path": "/auth/login", "method": "POST"},
                {"path": "/auth/logout", "method": "POST"},
                {"path": "/api/data", "method": "GET"},
                {"path": "/api/data", "method": "POST"},
                {"path": "/api/data/{id}", "method": "PUT"},
                {"path": "/api/data/{id}", "method": "DELETE"}
            ],
            "security_considerations": [
                "JWT token authentication",
                "Password hashing",
                "CORS configuration",
                "Input validation",
                "SQL injection prevention"
            ],
            "performance_requirements": {
                "max_response_time": "200ms",
                "concurrent_users": 100,
                "database_optimization": True
            }
        }
        
        self.logger.info(
            "requirements_analysis_completed",
            features_count=len(analysis["core_features"]),
            endpoints_count=len(analysis["api_endpoints"])
        )
        
        return analysis
    
    async def _create_execution_plan(
        self,
        task_breakdown: Dict[str, Any],
        project_id: str
    ) -> Dict[str, Any]:
        """
        Create detailed execution plan with task dependencies
        """
        tasks = []
        
        # Backend foundation tasks
        backend_tasks = [
            {
                "type": "database_schema",
                "description": "Design and implement database schema",
                "agent_type": AgentType.BACKEND,
                "priority": 1,
                "dependencies": [],
                "estimated_duration": 30
            },
            {
                "type": "authentication",
                "description": "Implement authentication system",
                "agent_type": AgentType.BACKEND,
                "priority": 1,
                "dependencies": ["database_schema"],
                "estimated_duration": 45
            },
            {
                "type": "api_structure",
                "description": "Create API structure and base endpoints",
                "agent_type": AgentType.BACKEND,
                "priority": 2,
                "dependencies": ["authentication"],
                "estimated_duration": 35
            },
            {
                "type": "business_logic",
                "description": "Implement core business logic",
                "agent_type": AgentType.BACKEND,
                "priority": 2,
                "dependencies": ["api_structure"],
                "estimated_duration": 50
            }
        ]
        
        # Frontend tasks
        frontend_tasks = [
            {
                "type": "ui_components",
                "description": "Create reusable UI components",
                "agent_type": AgentType.FRONTEND,
                "priority": 2,
                "dependencies": [],
                "estimated_duration": 40
            },
            {
                "type": "authentication_ui",
                "description": "Build authentication interface",
                "agent_type": AgentType.FRONTEND,
                "priority": 2,
                "dependencies": ["ui_components", "authentication"],
                "estimated_duration": 35
            },
            {
                "type": "main_interface",
                "description": "Develop main application interface",
                "agent_type": AgentType.FRONTEND,
                "priority": 3,
                "dependencies": ["authentication_ui", "api_structure"],
                "estimated_duration": 60
            },
            {
                "type": "api_integration",
                "description": "Integrate frontend with backend APIs",
                "agent_type": AgentType.FRONTEND,
                "priority": 3,
                "dependencies": ["main_interface", "business_logic"],
                "estimated_duration": 45
            }
        ]
        
        # Quality assurance tasks
        qa_tasks = [
            {
                "type": "code_review",
                "description": "Comprehensive code review and optimization",
                "agent_type": AgentType.REVIEWER,
                "priority": 4,
                "dependencies": ["business_logic", "api_integration"],
                "estimated_duration": 45
            },
            {
                "type": "security_audit",
                "description": "Security vulnerability assessment",
                "agent_type": AgentType.REVIEWER,
                "priority": 4,
                "dependencies": ["authentication", "business_logic"],
                "estimated_duration": 35
            }
        ]
        
        # DevOps tasks
        devops_tasks = [
            {
                "type": "environment_config",
                "description": "Configure deployment environment",
                "agent_type": AgentType.DEVOPS,
                "priority": 3,
                "dependencies": ["business_logic"],
                "estimated_duration": 30
            },
            {
                "type": "ci_cd_pipeline",
                "description": "Set up CI/CD pipeline",
                "agent_type": AgentType.DEVOPS,
                "priority": 5,
                "dependencies": ["environment_config"],
                "estimated_duration": 40
            },
            {
                "type": "monitoring_setup",
                "description": "Configure monitoring and alerting",
                "agent_type": AgentType.DEVOPS,
                "priority": 5,
                "dependencies": ["ci_cd_pipeline"],
                "estimated_duration": 25
            }
        ]
        
        # Combine all tasks
        all_tasks = backend_tasks + frontend_tasks + qa_tasks + devops_tasks
        
        # Create task objects with unique IDs
        for task_data in all_tasks:
            task_id = str(uuid.uuid4())
            task = Task(
                id=task_id,
                type=task_data["type"],
                description=task_data["description"],
                agent_type=task_data["agent_type"],
                priority=task_data["priority"],
                dependencies=task_data["dependencies"],
                parameters={
                    "project_id": project_id,
                    "estimated_duration": task_data["estimated_duration"],
                    "task_breakdown": task_breakdown
                }
            )
            tasks.append(task)
            self.tasks[task_id] = task
        
        # Calculate execution phases based on dependencies
        execution_phases = self._calculate_execution_phases(tasks)
        
        return {
            "tasks": tasks,
            "execution_phases": execution_phases,
            "estimated_total_duration": sum(task.parameters["estimated_duration"] for task in tasks),
            "parallel_execution_duration": self._calculate_parallel_duration(execution_phases)
        }
    
    async def _execute_coordinated_workflow(
        self,
        execution_plan: Dict[str, Any],
        project_id: str
    ) -> Dict[str, Any]:
        """
        Execute tasks through coordinated agent workflow with dependency management
        """
        execution_phases = execution_plan["execution_phases"]
        results = {}
        
        self.logger.info(
            "coordinated_workflow_started",
            project_id=project_id,
            phases_count=len(execution_phases),
            total_tasks=len(execution_plan["tasks"])
        )
        
        for phase_num, phase_tasks in execution_phases.items():
            self.logger.info(
                "execution_phase_started",
                phase=phase_num,
                tasks_count=len(phase_tasks)
            )
            
            # Execute tasks in parallel within phase
            phase_results = await asyncio.gather(
                *[self._execute_single_task(task) for task in phase_tasks],
                return_exceptions=True
            )
            
            # Process phase results
            for i, result in enumerate(phase_results):
                task = phase_tasks[i]
                if isinstance(result, Exception):
                    self.logger.error(
                        "task_execution_failed",
                        task_id=task.id,
                        task_type=task.type,
                        error=str(result)
                    )
                    task.status = TaskStatus.FAILED
                    task.error = str(result)
                else:
                    self.logger.info(
                        "task_execution_completed",
                        task_id=task.id,
                        task_type=task.type
                    )
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                
                results[task.id] = {
                    "status": task.status.value,
                    "result": task.result,
                    "error": task.error
                }
            
            # Check if any critical tasks failed
            critical_failures = [
                task for task in phase_tasks 
                if task.status == TaskStatus.FAILED and task.priority <= 2
            ]
            
            if critical_failures:
                self.logger.error(
                    "critical_tasks_failed",
                    failed_tasks=[task.type for task in critical_failures]
                )
                # For now, continue execution but log the failures
                # Recovery mechanisms will be implemented in later iterations
        
        return {
            "task_results": results,
            "execution_summary": {
                "total_tasks": len(execution_plan["tasks"]),
                "completed_tasks": len([r for r in results.values() if r["status"] == "completed"]),
                "failed_tasks": len([r for r in results.values() if r["status"] == "failed"]),
                "success_rate": len([r for r in results.values() if r["status"] == "completed"]) / len(results) if results else 0
            }
        }
    
    async def _execute_single_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute individual task through appropriate agent
        """
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        
        try:
            # Get appropriate agent
            agent = self.agents[task.agent_type]
            
            # Create agent session if needed
            session_id = f"{task.agent_type.value}_{task.id}"
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = AgentSession(
                    agent_id=session_id,
                    agent_type=task.agent_type,
                    performance_metrics={}
                )
            
            session = self.active_sessions[session_id]
            session.current_task_id = task.id
            session.last_activity = datetime.utcnow()
            
            # Execute task based on type and agent
            if task.agent_type == AgentType.BACKEND:
                result = await self._execute_backend_task(agent, task)
            elif task.agent_type == AgentType.FRONTEND:
                result = await self._execute_frontend_task(agent, task)
            elif task.agent_type == AgentType.REVIEWER:
                result = await self._execute_reviewer_task(agent, task)
            elif task.agent_type == AgentType.DEVOPS:
                result = await self._execute_devops_task(agent, task)
            else:
                raise ValueError(f"Unknown agent type: {task.agent_type}")
            
            task.completed_at = datetime.utcnow()
            session.tasks_completed += 1
            
            return result
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.utcnow()
            
            if session_id in self.active_sessions:
                self.active_sessions[session_id].tasks_failed += 1
            
            # Trigger healing on task failure if enabled
            project_id = task.parameters.get("project_id")
            if project_id:
                await self.trigger_healing_on_failure(project_id, task, str(e))
            
            raise
    
    async def _execute_reviewer_task(self, agent, task: Task) -> Dict[str, Any]:
        """Execute reviewer-specific tasks"""
        project_id = task.parameters["project_id"]
        
        if task.type == "code_review":
            # Simulate code review
            return {
                "task_type": "code_review",
                "status": "completed",
                "review_results": {
                    "overall_score": 0.89,
                    "issues_found": 3,
                    "recommendations": [
                        "Improve error handling in API endpoints",
                        "Add more comprehensive input validation",
                        "Optimize database queries"
                    ]
                }
            }
        elif task.type == "security_audit":
            # Use existing security analysis functionality
            result = await agent.analyze_project_health(
                project_id=project_id,
                focus_areas=["security"]
            )
            return {
                "task_type": "security_audit",
                "status": "completed",
                "security_results": result
            }
        else:
            raise ValueError(f"Unknown reviewer task type: {task.type}")
    
    async def _execute_backend_task(self, agent, task: Task) -> Dict[str, Any]:
        """Execute backend-specific tasks"""
        project_id = task.parameters["project_id"]
        task_breakdown = task.parameters.get("task_breakdown", {})
        
        if task.type == "database_schema":
            # Use backend agent's database design capability
            entities = [
                {"name": "User", "fields": ["id", "email", "password_hash", "created_at"]},
                {"name": "Session", "fields": ["id", "user_id", "token", "expires_at"]},
                {"name": "DataEntity", "fields": ["id", "name", "description", "user_id"]}
            ]
            relationships = [
                {"from": "Session", "to": "User", "type": "many-to-one"},
                {"from": "DataEntity", "to": "User", "type": "many-to-one"}
            ]
            
            result = await agent.design_database_schema(
                entities=entities,
                relationships=relationships,
                database_type="postgresql"
            )
            return {
                "task_type": "database_schema",
                "status": "completed",
                "database_design": result
            }
            
        elif task.type == "authentication":
            result = await agent.implement_authentication(
                auth_type="jwt",
                providers=["local"],
                roles=["user", "admin"]
            )
            return {
                "task_type": "authentication",
                "status": "completed",
                "auth_implementation": result
            }
            
        elif task.type == "api_structure":
            endpoints = task_breakdown.get("api_endpoints", [])
            results = []
            for endpoint in endpoints[:3]:  # Implement first 3 endpoints
                endpoint_result = await agent.create_api_endpoint(
                    endpoint_path=endpoint.get("path", "/api/default"),
                    http_method=endpoint.get("method", "GET"),
                    description=f"API endpoint for {endpoint.get('path', 'default')}",
                    authentication_required=True
                )
                results.append(endpoint_result)
            
            return {
                "task_type": "api_structure",
                "status": "completed",
                "api_endpoints": results
            }
            
        elif task.type == "business_logic":
            result = await agent.create_business_logic(
                service_name="CoreService",
                operations=[
                    {"name": "create_data", "type": "create"},
                    {"name": "update_data", "type": "update"},
                    {"name": "delete_data", "type": "delete"},
                    {"name": "get_data", "type": "read"}
                ],
                dependencies=["database", "authentication"]
            )
            return {
                "task_type": "business_logic",
                "status": "completed",
                "business_implementation": result
            }
        else:
            raise ValueError(f"Unknown backend task type: {task.type}")
    
    async def _execute_frontend_task(self, agent, task: Task) -> Dict[str, Any]:
        """Execute frontend-specific tasks"""
        project_id = task.parameters["project_id"]
        task_breakdown = task.parameters.get("task_breakdown", {})
        
        if task.type == "ui_components":
            # Create core UI components
            components = ["Button", "Input", "Card", "Modal", "LoadingSpinner"]
            results = []
            
            for component_name in components:
                component_result = await agent.create_component(
                    component_name=component_name,
                    requirements=f"Reusable {component_name} component with TypeScript",
                    styling_framework="css-modules"
                )
                results.append(component_result)
            
            return {
                "task_type": "ui_components",
                "status": "completed",
                "components": results
            }
            
        elif task.type == "authentication_ui":
            auth_pages = ["LoginPage", "RegisterPage", "ForgotPasswordPage"]
            results = []
            
            for page_name in auth_pages:
                page_result = await agent.create_page(
                    page_name=page_name,
                    route_path=f"/{page_name.lower().replace('page', '')}",
                    requirements=f"{page_name} with form validation and error handling",
                    layout_type="auth"
                )
                results.append(page_result)
            
            return {
                "task_type": "authentication_ui",
                "status": "completed",
                "auth_pages": results
            }
            
        elif task.type == "main_interface":
            main_pages = ["DashboardPage", "DataListPage", "ProfilePage"]
            results = []
            
            for page_name in main_pages:
                page_result = await agent.create_page(
                    page_name=page_name,
                    route_path=f"/{page_name.lower().replace('page', '')}",
                    requirements=f"{page_name} with data display and user interactions",
                    layout_type="standard"
                )
                results.append(page_result)
            
            return {
                "task_type": "main_interface",
                "status": "completed",
                "main_pages": results
            }
            
        elif task.type == "api_integration":
            api_endpoints = task_breakdown.get("api_endpoints", [])
            result = await agent.integrate_api(
                api_endpoints=api_endpoints,
                authentication_type="jwt",
                state_management="context"
            )
            
            return {
                "task_type": "api_integration",
                "status": "completed",
                "api_integration": result
            }
        else:
            raise ValueError(f"Unknown frontend task type: {task.type}")
    
    async def _execute_devops_task(self, agent, task: Task) -> Dict[str, Any]:
        """Execute DevOps-specific tasks"""
        project_id = task.parameters["project_id"]
        
        if task.type == "environment_config":
            result = await agent.create_deployment_config(
                application_type="fullstack",
                environment="production",
                platform="docker",
                scaling_requirements={"min_replicas": 2, "max_replicas": 10}
            )
            return {
                "task_type": "environment_config",
                "status": "completed",
                "deployment_config": result
            }
            
        elif task.type == "ci_cd_pipeline":
            result = await agent.setup_ci_cd_pipeline(
                project_id=project_id,
                git_provider="github",
                target_environments=["staging", "production"],
                testing_requirements=["unit", "integration", "security"]
            )
            return {
                "task_type": "ci_cd_pipeline",
                "status": "completed",
                "cicd_setup": result
            }
            
        elif task.type == "monitoring_setup":
            result = await agent.setup_monitoring(
                project_id=project_id,
                monitoring_targets=["application", "infrastructure"],
                alert_channels=["email", "slack"]
            )
            return {
                "task_type": "monitoring_setup",
                "status": "completed",
                "monitoring_config": result
            }
        else:
            raise ValueError(f"Unknown devops task type: {task.type}")
    
    async def _perform_final_quality_review(
        self,
        project_id: str,
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform final quality review using ReviewerAgent"""
        if AgentType.REVIEWER in self.agents:
            reviewer = self.agents[AgentType.REVIEWER]
            
            # Perform comprehensive health analysis
            health_analysis = await reviewer.analyze_project_health(
                project_id=project_id,
                focus_areas=["functionality", "security", "performance", "code_quality"]
            )
            
            return {
                "final_quality_score": health_analysis.get("health_score", 0.85),
                "quality_analysis": health_analysis,
                "overall_assessment": "Good" if health_analysis.get("health_score", 0) > 0.8 else "Needs Improvement"
            }
        else:
            return {
                "final_quality_score": 0.85,
                "quality_analysis": {"message": "Quality review not available"},
                "overall_assessment": "Not Reviewed"
            }
    
    async def _generate_completion_summary(
        self,
        project_id: str,
        task_breakdown: Dict[str, Any],
        execution_result: Dict[str, Any],
        quality_result: Dict[str, Any],
        start_time: datetime
    ) -> Dict[str, Any]:
        """Generate comprehensive completion summary"""
        total_duration = (datetime.utcnow() - start_time).total_seconds()
        
        return {
            "project_id": project_id,
            "generation_timestamp": datetime.utcnow().isoformat(),
            "total_duration_seconds": total_duration,
            "task_breakdown": task_breakdown,
            "execution_summary": execution_result["execution_summary"],
            "quality_metrics": quality_result,
            "agents_used": list(set(task.agent_type.value for task in self.tasks.values())),
            "files_generated": self._extract_generated_files(),
            "success": execution_result["execution_summary"]["success_rate"] > 0.8,
            "recommendations": self._generate_recommendations(execution_result, quality_result)
        }
    
    def _extract_generated_files(self) -> List[str]:
        """Extract list of generated files from task results"""
        files = []
        for task in self.tasks.values():
            if task.result and "files_generated" in task.result:
                files.extend(task.result["files_generated"])
        return files
    
    def _generate_recommendations(
        self,
        execution_result: Dict[str, Any],
        quality_result: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on execution and quality results"""
        recommendations = []
        
        success_rate = execution_result["execution_summary"]["success_rate"]
        if success_rate < 1.0:
            recommendations.append("Review and retry failed tasks for complete implementation")
        
        quality_score = quality_result.get("final_quality_score", 0.85)
        if quality_score < 0.9:
            recommendations.append("Consider additional code review and optimization")
        
        if not recommendations:
            recommendations.append("Project generated successfully with high quality standards")
        
        return recommendations
    
    def _calculate_execution_phases(self, tasks: List[Task]) -> Dict[int, List[Task]]:
        """Calculate task execution phases based on dependencies and priorities"""
        phases = {}
        task_lookup = {task.id: task for task in tasks}
        
        # Sort tasks by priority first
        sorted_tasks = sorted(tasks, key=lambda t: (t.priority, t.type))
        
        # Assign tasks to phases based on dependencies
        for task in sorted_tasks:
            min_phase = 1
            
            # Check dependency phases
            for dep_type in task.dependencies:
                # Find dependency task by type
                dep_task = next((t for t in tasks if t.type == dep_type), None)
                if dep_task:
                    # Find which phase the dependency is in
                    for phase_num, phase_tasks in phases.items():
                        if dep_task in phase_tasks:
                            min_phase = max(min_phase, phase_num + 1)
                            break
            
            # Assign to calculated phase
            if min_phase not in phases:
                phases[min_phase] = []
            phases[min_phase].append(task)
        
        return phases
    
    def _calculate_parallel_duration(self, execution_phases: Dict[int, List[Task]]) -> int:
        """Calculate total duration with parallel execution"""
        total_duration = 0
        
        for phase_tasks in execution_phases.values():
            # Phase duration is the maximum task duration in the phase
            phase_duration = max(
                task.parameters.get("estimated_duration", 30) 
                for task in phase_tasks
            )
            total_duration += phase_duration
        
        return total_duration
    
    async def enable_healing_for_project(self, project_id: str) -> Dict[str, Any]:
        """Enable self-healing monitoring for a project"""
        try:
            healing_loop = get_healing_loop()
            
            # Start health monitoring
            from src.healing.health_monitor import HealthMonitor
            health_monitor = HealthMonitor()
            
            monitor_task = await health_monitor.start_continuous_monitoring(
                project_id=project_id,
                interval_seconds=300  # Check every 5 minutes
            )
            
            # Start healing loop
            healing_task = await healing_loop.start_healing_loop(project_id)
            
            self.project_health_status[project_id] = {
                "healing_enabled": True,
                "monitor_task": monitor_task,
                "healing_task": healing_task,
                "enabled_at": datetime.utcnow(),
                "failure_count": 0
            }
            
            self.logger.info(
                "healing_enabled_for_project",
                project_id=project_id,
                correlation_id=self.correlation_id
            )
            
            return {
                "success": True,
                "project_id": project_id,
                "healing_enabled": True,
                "monitoring_active": True
            }
            
        except Exception as e:
            self.logger.error(
                "failed_to_enable_healing",
                project_id=project_id,
                error=str(e),
                correlation_id=self.correlation_id
            )
            return {
                "success": False,
                "project_id": project_id,
                "error": str(e)
            }
    
    async def disable_healing_for_project(self, project_id: str) -> Dict[str, Any]:
        """Disable self-healing monitoring for a project"""
        try:
            if project_id in self.project_health_status:
                status = self.project_health_status[project_id]
                
                # Stop health monitoring
                from src.healing.health_monitor import HealthMonitor
                health_monitor = HealthMonitor()
                await health_monitor.stop_monitoring(project_id)
                
                # Stop healing loop
                healing_loop = get_healing_loop()
                await healing_loop.stop_healing_loop(project_id)
                
                del self.project_health_status[project_id]
                
                self.logger.info(
                    "healing_disabled_for_project",
                    project_id=project_id,
                    correlation_id=self.correlation_id
                )
            
            return {
                "success": True,
                "project_id": project_id,
                "healing_enabled": False
            }
            
        except Exception as e:
            self.logger.error(
                "failed_to_disable_healing",
                project_id=project_id,
                error=str(e),
                correlation_id=self.correlation_id
            )
            return {
                "success": False,
                "project_id": project_id,
                "error": str(e)
            }
    
    async def trigger_healing_on_failure(self, project_id: str, task: Task, error: str) -> bool:
        """Trigger healing when task failures occur"""
        try:
            if not self.healing_enabled or project_id not in self.project_health_status:
                return False
            
            project_status = self.project_health_status[project_id]
            project_status["failure_count"] += 1
            
            # Check if we've hit the threshold for auto-healing
            if project_status["failure_count"] >= self.auto_healing_threshold:
                self.logger.info(
                    "triggering_auto_healing",
                    project_id=project_id,
                    failure_count=project_status["failure_count"],
                    task_type=task.type,
                    correlation_id=self.correlation_id
                )
                
                # Create a health issue for the healing system
                from src.healing.health_monitor import HealthIssue, IssueType
                
                trigger_issue = HealthIssue(
                    id=str(uuid.uuid4()),
                    type=IssueType.ORCHESTRATION_FAILURE,
                    severity=8,  # High severity for orchestration failures
                    description=f"Task '{task.type}' failed during orchestration: {error}",
                    location=f"orchestrator_task_{task.id}",
                    error_message=error,
                    stack_trace=None,
                    first_detected=datetime.utcnow(),
                    agent_context={
                        "task_id": task.id,
                        "task_type": task.type,
                        "agent_type": task.agent_type.value,
                        "orchestrator_correlation_id": self.correlation_id
                    }
                )
                
                # Trigger healing session
                healing_loop = get_healing_loop()
                session_id = await healing_loop.trigger_healing_session(project_id, trigger_issue)
                
                if session_id:
                    self.logger.info(
                        "healing_session_triggered",
                        project_id=project_id,
                        session_id=session_id,
                        task_id=task.id,
                        correlation_id=self.correlation_id
                    )
                    
                    # Reset failure count after triggering healing
                    project_status["failure_count"] = 0
                    return True
                else:
                    self.logger.warning(
                        "healing_session_not_triggered",
                        project_id=project_id,
                        task_id=task.id,
                        reason="may_be_at_session_limit",
                        correlation_id=self.correlation_id
                    )
            
            return False
            
        except Exception as e:
            self.logger.error(
                "error_triggering_healing",
                project_id=project_id,
                task_id=task.id,
                error=str(e),
                correlation_id=self.correlation_id
            )
            return False
    
    async def get_project_health_status(self, project_id: str) -> Dict[str, Any]:
        """Get current health status for a project"""
        try:
            if project_id not in self.project_health_status:
                return {
                    "project_id": project_id,
                    "healing_enabled": False,
                    "health_status": "unknown"
                }
            
            from src.healing.health_monitor import HealthMonitor
            health_monitor = HealthMonitor()
            
            # Get current health report
            health_report = await health_monitor.get_current_health_status(project_id)
            
            project_status = self.project_health_status[project_id]
            
            result = {
                "project_id": project_id,
                "healing_enabled": project_status["healing_enabled"],
                "failure_count": project_status["failure_count"],
                "enabled_at": project_status["enabled_at"].isoformat(),
                "health_status": "unknown",
                "health_score": 0.0,
                "issues_count": 0
            }
            
            if health_report:
                result.update({
                    "health_status": health_report.overall_status.value,
                    "health_score": health_report.health_score,
                    "issues_count": len(health_report.issues),
                    "last_check": health_report.timestamp.isoformat()
                })
            
            return result
            
        except Exception as e:
            self.logger.error(
                "error_getting_health_status",
                project_id=project_id,
                error=str(e),
                correlation_id=self.correlation_id
            )
            return {
                "project_id": project_id,
                "healing_enabled": False,
                "error": str(e)
            }
    
    def _initialize_workflow_templates(self) -> Dict[str, Any]:
        """Initialize workflow templates for different project types"""
        return {
            "fullstack": {
                "phases": ["foundation", "backend", "frontend", "integration", "quality"],
                "critical_tasks": ["database_schema", "authentication", "api_structure"]
            },
            "frontend": {
                "phases": ["setup", "components", "pages", "integration", "optimization"],
                "critical_tasks": ["ui_components", "state_management"]
            },
            "backend": {
                "phases": ["architecture", "database", "apis", "business_logic", "security"],
                "critical_tasks": ["database_schema", "api_structure", "authentication"]
            },
            "api": {
                "phases": ["design", "implementation", "documentation", "testing"],
                "critical_tasks": ["api_structure", "authentication", "business_logic"]
            }
        }
    
    async def generate_component(
        self,
        component_type: str,
        requirements: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate specific component using appropriate agent"""
        component_id = str(uuid.uuid4())
        
        self.logger.info(
            "generating_component",
            component_id=component_id,
            component_type=component_type,
            requirements_length=len(requirements)
        )
        
        # Simulate component generation for now
        await asyncio.sleep(1.5)
        
        result = {
            "component_id": component_id,
            "component_type": component_type,
            "requirements": requirements,
            "generated_files": [f"{component_type.lower()}.py"],
            "status": "completed",
            "agent_used": "backend" if "api" in component_type.lower() else "frontend",
            "generation_timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.info(
            "component_generation_completed",
            component_id=component_id,
            agent_used=result["agent_used"]
        )
        
        return result
    
    async def enhance_application(
        self,
        project_id: str,
        enhancement_type: str,
        specifications: str
    ) -> Dict[str, Any]:
        """Enhance existing application with new features"""
        enhancement_id = str(uuid.uuid4())
        
        self.logger.info(
            "enhancing_application",
            enhancement_id=enhancement_id,
            project_id=project_id,
            enhancement_type=enhancement_type
        )
        
        # Simulate enhancement process
        await asyncio.sleep(2)
        
        result = {
            "enhancement_id": enhancement_id,
            "project_id": project_id,
            "enhancement_type": enhancement_type,
            "status": "completed",
            "modified_files": [f"enhanced_{enhancement_type}.py"],
            "completion_timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.info(
            "application_enhancement_completed",
            enhancement_id=enhancement_id
        )
        
        return result