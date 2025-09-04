"""
DevOps agent specialized for deployment, infrastructure, and CI/CD
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from src.agents.base_agent import BaseAgent


class DevOpsAgent(BaseAgent):
    """Specialized agent for DevOps and infrastructure"""
    
    def __init__(self, correlation_id: Optional[str] = None):
        super().__init__(agent_type="devops", correlation_id=correlation_id)
    
    def _get_model_preferences(self) -> Dict[str, str]:
        """DevOps-optimized model preferences"""
        return {
            "code_generation": "claude-3-sonnet",    # Good for infrastructure code
            "config_management": "gpt-4",            # Excellent for complex configs
            "monitoring": "claude-3-sonnet",         # Strong monitoring setup
            "security": "claude-3-sonnet",           # Good security practices
            "optimization": "gpt-4"                  # Performance optimization
        }
    
    def _initialize_prompt_templates(self) -> Dict[str, str]:
        """Initialize DevOps-specific prompt templates"""
        return {
            "deployment": """
You are an expert DevOps engineer specializing in deployment automation.

Focus on:
- Containerization with Docker and Docker Compose
- Kubernetes orchestration and manifests
- Infrastructure as Code (Terraform, CloudFormation)
- Zero-downtime deployment strategies
- Environment configuration management
- Service discovery and load balancing
- Health checks and readiness probes
            """,
            
            "cicd": """
You are an expert DevOps engineer creating CI/CD pipelines.

Focus on:
- Automated testing and quality gates
- Build optimization and caching
- Security scanning and vulnerability checks
- Deployment automation and rollback strategies
- Environment promotion workflows
- Monitoring and alerting integration
- Performance and load testing
            """,
            
            "monitoring": """
You are an expert DevOps engineer setting up monitoring and observability.

Focus on:
- Application and infrastructure monitoring
- Log aggregation and analysis
- Metrics collection and alerting
- Distributed tracing
- Performance monitoring
- Error tracking and debugging
- Dashboard and visualization setup
            """,
            
            "infrastructure": """
You are an expert DevOps engineer designing cloud infrastructure.

Focus on:
- Scalable and resilient architecture
- Security best practices
- Cost optimization
- Disaster recovery and backup
- Network security and isolation
- Auto-scaling and load balancing
- Multi-environment setup
            """,
            
            "default": """
You are an expert DevOps engineer with deep knowledge of infrastructure and deployment.
Create secure, scalable, and maintainable DevOps solutions.
            """
        }
    
    def _get_agent_capabilities(self) -> List[str]:
        """DevOps agent capabilities"""
        return [
            "Docker containerization",
            "Kubernetes orchestration",
            "CI/CD pipeline automation",
            "Infrastructure as Code (IaC)",
            "Monitoring and observability",
            "Security and compliance",
            "Performance optimization",
            "Disaster recovery planning",
            "Cloud platform integration",
            "Environment management"
        ]
    
    async def create_deployment_config(
        self,
        application_type: str,
        environment: str,
        platform: str = "docker",
        scaling_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create deployment configuration for the application
        """
        self.logger.info(
            "creating_deployment_config",
            app_type=application_type,
            environment=environment,
            platform=platform
        )
        
        context = {
            "application_type": application_type,
            "environment": environment,
            "platform": platform,
            "scaling_requirements": scaling_requirements or {}
        }
        
        prompt = f"""
Create deployment configuration for a {application_type} application.

Environment: {environment}
Platform: {platform}
Scaling Requirements: {scaling_requirements}

Generate:
1. Docker containers with multi-stage builds
2. Docker Compose for local development
3. Kubernetes manifests (if applicable)
4. Environment configuration files
5. Health check implementations
6. Service discovery configuration
7. Load balancer setup
"""
        
        result = await self.generate_code(
            prompt=prompt,
            context=context,
            code_type="deployment"
        )
        
        # Add deployment-specific metadata
        if result.get("success"):
            result["deployment_metadata"] = {
                "application_type": application_type,
                "environment": environment,
                "platform": platform,
                "has_scaling": bool(scaling_requirements),
                "has_health_checks": True,
                "files_generated": [
                    "Dockerfile",
                    "docker-compose.yml",
                    "k8s/deployment.yaml",
                    "k8s/service.yaml",
                    "k8s/configmap.yaml",
                    ".env.example"
                ]
            }
        
        return result
    
    async def setup_ci_cd_pipeline(
        self,
        project_id: str,
        git_provider: str = "github",
        target_environments: List[str] = None,
        testing_requirements: List[str] = None
    ) -> Dict[str, Any]:
        """
        Set up complete CI/CD pipeline
        """
        target_environments = target_environments or ["staging", "production"]
        testing_requirements = testing_requirements or ["unit", "integration", "security"]
        
        self.logger.info(
            "setting_up_cicd",
            project_id=project_id,
            git_provider=git_provider,
            environments=target_environments
        )
        
        context = {
            "project_id": project_id,
            "git_provider": git_provider,
            "target_environments": target_environments,
            "testing_requirements": testing_requirements
        }
        
        prompt = f"""
Create a complete CI/CD pipeline configuration.

Git Provider: {git_provider}
Target Environments: {target_environments}
Testing Requirements: {testing_requirements}

Generate:
1. CI/CD workflow files ({git_provider} Actions/GitLab CI)
2. Build and test automation
3. Security scanning integration
4. Deployment automation scripts
5. Environment promotion workflows
6. Rollback and recovery procedures
7. Notification and alerting setup
"""
        
        result = await self.generate_code(
            prompt=prompt,
            context=context,
            code_type="cicd"
        )
        
        # Add CI/CD-specific metadata
        if result.get("success"):
            result["cicd_metadata"] = {
                "git_provider": git_provider,
                "environments": target_environments,
                "testing_stages": testing_requirements,
                "has_security_scanning": True,
                "has_rollback": True,
                "files_generated": [
                    f".{git_provider}/workflows/ci.yml",
                    f".{git_provider}/workflows/cd.yml",
                    "scripts/deploy.sh",
                    "scripts/rollback.sh",
                    "tests/integration/pipeline_test.py"
                ]
            }
        
        return result
    
    async def setup_monitoring(
        self,
        project_id: str,
        monitoring_targets: List[str] = None,
        alert_channels: List[str] = None
    ) -> Dict[str, Any]:
        """
        Set up comprehensive monitoring and observability
        """
        monitoring_targets = monitoring_targets or ["application", "infrastructure", "business"]
        alert_channels = alert_channels or ["email", "slack"]
        
        self.logger.info(
            "setting_up_monitoring",
            project_id=project_id,
            targets=monitoring_targets,
            alerts=alert_channels
        )
        
        context = {
            "project_id": project_id,
            "monitoring_targets": monitoring_targets,
            "alert_channels": alert_channels
        }
        
        prompt = f"""
Create comprehensive monitoring and observability setup.

Monitoring Targets: {monitoring_targets}
Alert Channels: {alert_channels}

Generate:
1. Application metrics collection
2. Infrastructure monitoring setup
3. Log aggregation configuration
4. Dashboard definitions
5. Alerting rules and notifications
6. Health check endpoints
7. Performance monitoring tools
"""
        
        result = await self.generate_code(
            prompt=prompt,
            context=context,
            code_type="monitoring"
        )
        
        # Add monitoring-specific metadata
        if result.get("success"):
            result["monitoring_metadata"] = {
                "targets": monitoring_targets,
                "alert_channels": alert_channels,
                "has_dashboards": True,
                "has_alerting": True,
                "files_generated": [
                    "monitoring/prometheus.yml",
                    "monitoring/grafana-dashboard.json",
                    "monitoring/alertmanager.yml",
                    "logging/fluentd.conf",
                    "health/health_check.py"
                ]
            }
        
        return result
    
    async def optimize_infrastructure(
        self,
        project_id: str,
        optimization_targets: List[str]
    ) -> Dict[str, Any]:
        """
        Optimize infrastructure for cost and performance
        """
        self.logger.info(
            "optimizing_infrastructure",
            project_id=project_id,
            targets=optimization_targets
        )
        
        # Simulate infrastructure analysis
        await asyncio.sleep(2)
        
        optimizations = []
        
        for target in optimization_targets:
            if target == "cost":
                optimizations.append({
                    "type": "cost_optimization",
                    "actions": [
                        "Right-size compute instances based on usage",
                        "Implement auto-scaling policies",
                        "Use spot instances for non-critical workloads",
                        "Optimize storage tiers and lifecycle policies"
                    ],
                    "expected_savings": "25-40% cost reduction"
                })
            elif target == "performance":
                optimizations.append({
                    "type": "performance_optimization",
                    "actions": [
                        "Implement CDN for static assets",
                        "Add caching layers (Redis/Memcached)",
                        "Optimize database connection pooling",
                        "Implement horizontal pod autoscaling"
                    ],
                    "expected_improvement": "40-60% performance boost"
                })
            elif target == "reliability":
                optimizations.append({
                    "type": "reliability_optimization",
                    "actions": [
                        "Implement multi-AZ deployment",
                        "Add circuit breakers for resilience",
                        "Set up automated backup and recovery",
                        "Implement chaos engineering practices"
                    ],
                    "expected_improvement": "99.9% uptime target"
                })
        
        return {
            "project_id": project_id,
            "optimization_plan": optimizations,
            "total_optimizations": len(optimizations),
            "estimated_benefits": "30-50% overall improvement",
            "implementation_time": "1-2 weeks",
            "priority_order": [opt["type"] for opt in optimizations]
        }
    
    async def security_hardening(
        self,
        project_id: str,
        security_requirements: List[str]
    ) -> Dict[str, Any]:
        """
        Implement security hardening measures
        """
        self.logger.info(
            "security_hardening",
            project_id=project_id,
            requirements=security_requirements
        )
        
        # Simulate security analysis
        await asyncio.sleep(1.5)
        
        hardening_measures = []
        
        for requirement in security_requirements:
            if requirement == "network_security":
                hardening_measures.append({
                    "category": "Network Security",
                    "measures": [
                        "Implement network segmentation with VPCs",
                        "Configure security groups and NACLs",
                        "Set up WAF for web application protection",
                        "Enable DDoS protection"
                    ],
                    "priority": "high"
                })
            elif requirement == "data_protection":
                hardening_measures.append({
                    "category": "Data Protection",
                    "measures": [
                        "Enable encryption at rest and in transit",
                        "Implement key management system",
                        "Set up database encryption",
                        "Configure backup encryption"
                    ],
                    "priority": "critical"
                })
            elif requirement == "access_control":
                hardening_measures.append({
                    "category": "Access Control",
                    "measures": [
                        "Implement RBAC with principle of least privilege",
                        "Set up multi-factor authentication",
                        "Configure service account permissions",
                        "Enable audit logging for all access"
                    ],
                    "priority": "high"
                })
        
        return {
            "project_id": project_id,
            "hardening_plan": hardening_measures,
            "total_measures": sum(len(measure["measures"]) for measure in hardening_measures),
            "compliance_frameworks": ["SOC2", "ISO27001", "GDPR"],
            "implementation_timeline": "2-3 weeks",
            "security_score_improvement": "85-95% security posture"
        }
    
    async def disaster_recovery_plan(
        self,
        project_id: str,
        rto_hours: int = 4,
        rpo_hours: int = 1
    ) -> Dict[str, Any]:
        """
        Create disaster recovery and business continuity plan
        """
        self.logger.info(
            "creating_dr_plan",
            project_id=project_id,
            rto=rto_hours,
            rpo=rpo_hours
        )
        
        # Simulate DR planning
        await asyncio.sleep(1.5)
        
        dr_components = [
            {
                "component": "Data Backup Strategy",
                "description": "Automated backup with point-in-time recovery",
                "rpo_compliance": rpo_hours <= 1,
                "implementation": [
                    "Set up automated database backups every hour",
                    "Implement cross-region backup replication",
                    "Test backup restoration procedures weekly",
                    "Document backup and restore procedures"
                ]
            },
            {
                "component": "Failover Procedures",
                "description": "Automated failover to secondary environment",
                "rto_compliance": rto_hours <= 4,
                "implementation": [
                    "Set up hot standby environment",
                    "Implement DNS failover automation",
                    "Create runbook for manual failover",
                    "Test failover procedures monthly"
                ]
            },
            {
                "component": "Communication Plan",
                "description": "Stakeholder notification and updates",
                "critical": True,
                "implementation": [
                    "Define incident response team roles",
                    "Set up automated status page updates",
                    "Create communication templates",
                    "Establish escalation procedures"
                ]
            }
        ]
        
        return {
            "project_id": project_id,
            "rto_target_hours": rto_hours,
            "rpo_target_hours": rpo_hours,
            "dr_components": dr_components,
            "compliance_level": "Enterprise" if rto_hours <= 4 and rpo_hours <= 1 else "Standard",
            "estimated_cost": "$500-1500/month",
            "implementation_time": "3-4 weeks",
            "testing_schedule": "Monthly failover tests, Quarterly full DR exercises"
        }