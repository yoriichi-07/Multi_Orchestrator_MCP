"""
Backend agent specialized for API development, databases, and server-side logic
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from src.agents.base_agent import BaseAgent


class BackendAgent(BaseAgent):
    """Specialized agent for backend development"""
    
    def __init__(self, correlation_id: Optional[str] = None):
        super().__init__(agent_type="backend", correlation_id=correlation_id)
    
    def _get_model_preferences(self) -> Dict[str, str]:
        """Backend-optimized model preferences"""
        return {
            "code_generation": "claude-3-sonnet",    # Excellent for complex logic
            "database_design": "gpt-4",              # Great for data modeling
            "api_design": "claude-3-sonnet",         # Good for API architecture
            "security": "claude-3-sonnet",           # Strong security reasoning
            "optimization": "gpt-4"                  # Excellent for performance
        }
    
    def _initialize_prompt_templates(self) -> Dict[str, str]:
        """Initialize backend-specific prompt templates"""
        return {
            "api": """
You are an expert Backend API developer. Create robust, secure, and scalable APIs.

Focus on:
- RESTful design principles
- Proper HTTP status codes and error handling
- Input validation and sanitization
- Authentication and authorization
- API documentation (OpenAPI/Swagger)
- Performance and caching strategies
- Database integration with proper ORM usage
            """,
            
            "database": """
You are an expert Database architect and developer.

Focus on:
- Normalized database schema design
- Proper indexing strategies
- Foreign key relationships
- Data integrity constraints
- Migration scripts
- Query optimization
- Connection pooling and transactions
            """,
            
            "authentication": """
You are an expert Security developer specializing in authentication systems.

Focus on:
- Secure authentication flows (JWT, OAuth2)
- Password hashing and validation
- Session management
- Role-based access control (RBAC)
- Security headers and CORS
- Rate limiting and brute force protection
- Audit logging
            """,
            
            "business_logic": """
You are an expert Backend developer creating business logic and services.

Focus on:
- Clean architecture patterns
- Service layer design
- Error handling and logging
- Data validation and transformation
- Business rule implementation
- Integration with external services
- Testable and maintainable code
            """,
            
            "default": """
You are an expert Backend developer with deep knowledge of server-side technologies.
Create secure, scalable, and maintainable backend systems.
            """
        }
    
    def _get_agent_capabilities(self) -> List[str]:
        """Backend agent capabilities"""
        return [
            "RESTful API development",
            "Database design and optimization",
            "Authentication and authorization systems",
            "Business logic implementation",
            "Security best practices",
            "Performance optimization",
            "Microservices architecture",
            "Message queues and async processing",
            "Caching strategies",
            "Testing (unit, integration, load)"
        ]
    
    async def create_api_endpoint(
        self,
        endpoint_path: str,
        http_method: str,
        description: str,
        request_schema: Optional[Dict[str, Any]] = None,
        response_schema: Optional[Dict[str, Any]] = None,
        authentication_required: bool = True
    ) -> Dict[str, Any]:
        """
        Create a REST API endpoint with full implementation
        """
        self.logger.info(
            "creating_api_endpoint",
            path=endpoint_path,
            method=http_method,
            auth_required=authentication_required
        )
        
        context = {
            "endpoint_path": endpoint_path,
            "http_method": http_method,
            "description": description,
            "request_schema": request_schema,
            "response_schema": response_schema,
            "authentication_required": authentication_required
        }
        
        prompt = f"""
Create a REST API endpoint implementation.

Endpoint: {http_method} {endpoint_path}
Description: {description}
Authentication Required: {authentication_required}

Request Schema: {request_schema if request_schema else "Define based on requirements"}
Response Schema: {response_schema if response_schema else "Define based on requirements"}

Generate:
1. FastAPI route handler with proper typing
2. Pydantic models for request/response
3. Input validation and error handling
4. Database operations (if needed)
5. Authentication middleware (if required)
6. Unit tests for the endpoint
7. OpenAPI documentation
"""
        
        result = await self.generate_code(
            prompt=prompt,
            context=context,
            code_type="api"
        )
        
        # Add API-specific metadata
        if result.get("success"):
            result["api_metadata"] = {
                "endpoint": f"{http_method} {endpoint_path}",
                "authentication": authentication_required,
                "has_validation": True,
                "has_tests": True,
                "files_generated": [
                    f"routes/{endpoint_path.replace('/', '_').strip('_')}.py",
                    f"models/{endpoint_path.replace('/', '_').strip('_')}_models.py",
                    f"tests/test_{endpoint_path.replace('/', '_').strip('_')}.py"
                ]
            }
        
        return result
    
    async def design_database_schema(
        self,
        entities: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        database_type: str = "postgresql"
    ) -> Dict[str, Any]:
        """
        Design complete database schema with migrations
        """
        self.logger.info(
            "designing_database_schema",
            entities_count=len(entities),
            relationships_count=len(relationships),
            db_type=database_type
        )
        
        context = {
            "entities": entities,
            "relationships": relationships,
            "database_type": database_type
        }
        
        prompt = f"""
Design a complete database schema for {database_type}.

Entities: {entities}
Relationships: {relationships}

Generate:
1. SQLAlchemy model definitions
2. Database migration scripts
3. Indexes for optimal performance
4. Constraints and validations
5. Seed data scripts
6. Database utility functions
7. Connection and session management
"""
        
        result = await self.generate_code(
            prompt=prompt,
            context=context,
            code_type="database"
        )
        
        # Add database-specific metadata
        if result.get("success"):
            result["database_metadata"] = {
                "database_type": database_type,
                "entities_count": len(entities),
                "relationships_count": len(relationships),
                "has_migrations": True,
                "has_indexes": True,
                "files_generated": [
                    "models/__init__.py",
                    "models/base.py",
                    "alembic/versions/001_initial_schema.py",
                    "database/connection.py",
                    "database/seeds.py"
                ] + [f"models/{entity['name'].lower()}.py" for entity in entities]
            }
        
        return result
    
    async def implement_authentication(
        self,
        auth_type: str = "jwt",
        providers: List[str] = None,
        roles: List[str] = None
    ) -> Dict[str, Any]:
        """
        Implement complete authentication system
        """
        providers = providers or ["local"]
        roles = roles or ["user", "admin"]
        
        self.logger.info(
            "implementing_authentication",
            auth_type=auth_type,
            providers=providers,
            roles=roles
        )
        
        context = {
            "auth_type": auth_type,
            "providers": providers,
            "roles": roles
        }
        
        prompt = f"""
Implement a complete authentication system.

Authentication Type: {auth_type}
Providers: {providers}
Roles: {roles}

Generate:
1. Authentication service with {auth_type}
2. User model and management
3. Role-based access control (RBAC)
4. Password hashing and validation
5. Token management and refresh
6. Authentication middleware
7. Security utilities and helpers
8. Rate limiting for auth endpoints
"""
        
        result = await self.generate_code(
            prompt=prompt,
            context=context,
            code_type="authentication"
        )
        
        # Add auth-specific metadata
        if result.get("success"):
            result["auth_metadata"] = {
                "auth_type": auth_type,
                "providers": providers,
                "roles": roles,
                "has_rate_limiting": True,
                "has_rbac": True,
                "files_generated": [
                    "auth/service.py",
                    "auth/models.py",
                    "auth/middleware.py",
                    "auth/utils.py",
                    "auth/dependencies.py",
                    "models/user.py",
                    "models/role.py"
                ]
            }
        
        return result
    
    async def create_business_logic(
        self,
        service_name: str,
        operations: List[Dict[str, Any]],
        dependencies: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create business logic service layer
        """
        dependencies = dependencies or []
        
        self.logger.info(
            "creating_business_logic",
            service=service_name,
            operations_count=len(operations)
        )
        
        context = {
            "service_name": service_name,
            "operations": operations,
            "dependencies": dependencies
        }
        
        prompt = f"""
Create a business logic service for {service_name}.

Operations: {operations}
Dependencies: {dependencies}

Generate:
1. Service class with clean architecture
2. Business rule implementations
3. Data validation and transformation
4. Error handling and logging
5. Integration with database layer
6. Unit tests for business logic
7. Service interfaces and contracts
"""
        
        result = await self.generate_code(
            prompt=prompt,
            context=context,
            code_type="business_logic"
        )
        
        # Add business logic metadata
        if result.get("success"):
            result["business_metadata"] = {
                "service_name": service_name,
                "operations_count": len(operations),
                "dependencies": dependencies,
                "has_validation": True,
                "has_tests": True,
                "files_generated": [
                    f"services/{service_name.lower()}_service.py",
                    f"services/interfaces/{service_name.lower()}_interface.py",
                    f"tests/services/test_{service_name.lower()}_service.py"
                ]
            }
        
        return result
    
    async def optimize_database_performance(
        self,
        project_id: str,
        performance_targets: List[str]
    ) -> Dict[str, Any]:
        """
        Optimize database performance
        """
        self.logger.info(
            "optimizing_database",
            project_id=project_id,
            targets=performance_targets
        )
        
        # Simulate database analysis
        await asyncio.sleep(2)
        
        optimizations = []
        
        for target in performance_targets:
            if target == "query_performance":
                optimizations.append({
                    "type": "query_optimization",
                    "actions": [
                        "Add database indexes on frequently queried columns",
                        "Optimize N+1 query problems with eager loading",
                        "Implement query result caching",
                        "Use database connection pooling"
                    ],
                    "expected_improvement": "50-80% faster queries"
                })
            elif target == "connection_management":
                optimizations.append({
                    "type": "connection_optimization",
                    "actions": [
                        "Configure connection pooling",
                        "Implement connection retry logic",
                        "Add connection health checks",
                        "Optimize connection timeouts"
                    ],
                    "expected_improvement": "30-50% better concurrency"
                })
            elif target == "data_structure":
                optimizations.append({
                    "type": "schema_optimization",
                    "actions": [
                        "Normalize database schema",
                        "Add appropriate indexes",
                        "Implement partitioning for large tables",
                        "Optimize data types and constraints"
                    ],
                    "expected_improvement": "25-40% storage efficiency"
                })
        
        return {
            "project_id": project_id,
            "optimization_plan": optimizations,
            "total_optimizations": len(optimizations),
            "estimated_performance_gain": "40-70% overall improvement",
            "implementation_time": "3-6 hours",
            "priority_order": [opt["type"] for opt in optimizations]
        }
    
    async def security_audit(
        self,
        project_id: str,
        endpoints: List[str]
    ) -> Dict[str, Any]:
        """
        Perform backend security audit
        """
        self.logger.info(
            "security_audit",
            project_id=project_id,
            endpoints_count=len(endpoints)
        )
        
        # Simulate security audit
        await asyncio.sleep(2)
        
        audit_results = []
        
        for endpoint in endpoints:
            # Simulate endpoint security analysis
            vulnerabilities = []
            score = 88  # Mock score
            
            # Common security issues simulation
            if "login" in endpoint.lower():
                vulnerabilities.append({
                    "severity": "high",
                    "type": "authentication",
                    "issue": "Missing rate limiting on login endpoint",
                    "solution": "Implement rate limiting to prevent brute force attacks"
                })
            
            if "upload" in endpoint.lower():
                vulnerabilities.append({
                    "severity": "medium",
                    "type": "file_upload",
                    "issue": "File type validation insufficient",
                    "solution": "Add comprehensive file type and size validation"
                })
            
            audit_results.append({
                "endpoint": endpoint,
                "security_score": score,
                "vulnerabilities": vulnerabilities,
                "compliance_level": "Good" if score > 80 else "Needs Improvement",
                "recommendations": [
                    "Implement input sanitization",
                    "Add CSRF protection",
                    "Use secure headers",
                    "Enable audit logging"
                ]
            })
        
        overall_score = sum(result["security_score"] for result in audit_results) / len(audit_results)
        
        return {
            "project_id": project_id,
            "overall_security_score": overall_score,
            "compliance_level": "Good" if overall_score > 80 else "Needs Improvement",
            "endpoint_audits": audit_results,
            "total_vulnerabilities": sum(len(result["vulnerabilities"]) for result in audit_results),
            "critical_issues": [
                vuln for result in audit_results 
                for vuln in result["vulnerabilities"] 
                if vuln["severity"] == "high"
            ],
            "security_recommendations": [
                "Implement comprehensive input validation",
                "Add rate limiting to all authentication endpoints",
                "Use HTTPS everywhere with HSTS headers",
                "Implement proper error handling without information leakage",
                "Add security monitoring and alerting"
            ]
        }