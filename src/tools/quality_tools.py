"""
Quality assurance and testing tools
"""
import asyncio
import json
import uuid
import time
from typing import Dict, Any, List, Optional

from src.core.tool_registry import mcp_tool, AnalyticsTracker
from src.core.descope_auth import AuthContext
from src.agents.reviewer import ReviewerAgent
from src.agents.orchestrator import AgentOrchestrator
from src.testing.test_runner import TestRunner
import structlog

logger = structlog.get_logger()


@mcp_tool(
    name="test_application", 
    description="Run comprehensive tests on generated application",
    required_scopes=["tools:review"],
    timeout_seconds=300
)
async def test_application_tool(
    project_id: str,
    test_types: Optional[List[str]] = None,
    auth_context: AuthContext = None,
    request=None
) -> Dict[str, Any]:
    """
    Run comprehensive test suite on application
    
    Args:
        project_id: ID of the project to test
        test_types: Types of tests to run (unit, integration, security, performance)
    """
    correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
    tracker = AnalyticsTracker(correlation_id)
    
    if test_types is None:
        test_types = ["unit", "integration", "security", "linting"]
    
    try:
        logger.info(
            "test_application_started",
            user_id=auth_context.user_id,
            project_id=project_id,
            test_types=test_types,
            correlation_id=correlation_id
        )
        
        test_runner = TestRunner(correlation_id=correlation_id)
        
        # Run specified tests
        test_results = await test_runner.run_comprehensive_tests(
            project_id=project_id,
            test_types=test_types,
            user_context={
                "user_id": auth_context.user_id,
                "scopes": auth_context.scopes
            }
        )
        
        await tracker.track_operation(
            operation_type="test_application",
            agent_type="tester",
            success=True,
            metadata={
                "project_id": project_id,
                "test_types": test_types,
                "total_tests": test_results.get("total_tests", 0),
                "success_rate": test_results.get("success_rate", 0.0),
                "user_id": auth_context.user_id
            }
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "status": "completed",
                        "project_id": project_id,
                        "test_summary": {
                            "total_tests": test_results.get("total_tests", 0),
                            "passed_tests": test_results.get("passed_tests", 0),
                            "failed_tests": test_results.get("failed_tests", 0),
                            "skipped_tests": test_results.get("skipped_tests", 0),
                            "success_rate": test_results.get("success_rate", 0.0)
                        },
                        "test_details": test_results.get("test_details", {}),
                        "failures": test_results.get("failures", []),
                        "recommendations": test_results.get("recommendations", [])
                    }, indent=2)
                }
            ]
        }
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="test_application",
            agent_type="tester",
            success=False,
            metadata={
                "project_id": project_id,
                "error": str(e),
                "user_id": auth_context.user_id
            }
        )
        
        logger.error(
            "test_application_failed",
            project_id=project_id,
            error=str(e),
            correlation_id=correlation_id
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Testing failed: {str(e)}"
                }
            ],
            "isError": True
        }


@mcp_tool(
    name="self_heal",
    description="Automatically analyze and fix issues in generated code", 
    required_scopes=["tools:fix"],
    timeout_seconds=600
)
async def self_heal_tool(
    project_id: str,
    issue_context: Optional[str] = None,
    max_attempts: int = 3,
    auth_context: AuthContext = None,
    request=None
) -> Dict[str, Any]:
    """
    Autonomous self-healing system - the key innovation
    
    Args:
        project_id: ID of the project to heal
        issue_context: Optional context about known issues
        max_attempts: Maximum number of healing attempts
    """
    correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
    tracker = AnalyticsTracker(correlation_id)
    healing_attempts = []
    
    try:
        reviewer_agent = ReviewerAgent(correlation_id=correlation_id)
        orchestrator = AgentOrchestrator(correlation_id=correlation_id)
        
        logger.info(
            "self_healing_started",
            user_id=auth_context.user_id,
            project_id=project_id,
            max_attempts=max_attempts,
            correlation_id=correlation_id
        )
        
        for attempt in range(max_attempts):
            logger.info(
                "self_healing_attempt",
                project_id=project_id,
                attempt=attempt + 1,
                max_attempts=max_attempts,
                correlation_id=correlation_id
            )
            
            # Analyze current state
            analysis_result = await reviewer_agent.analyze_project_health(
                project_id=project_id,
                focus_areas=["functionality", "security", "performance", "code_quality"]
            )
            
            # If no issues found, healing is complete
            if not analysis_result.get("issues_found"):
                healing_attempts.append({
                    "attempt": attempt + 1,
                    "status": "no_issues_found",
                    "analysis": analysis_result
                })
                break
            
            # Generate fixes for identified issues
            fix_recommendations = await reviewer_agent.generate_fix_recommendations(
                issues=analysis_result.get("issues", []),
                project_context=analysis_result.get("project_context", {})
            )
            
            # Apply fixes
            fix_result = await orchestrator.apply_automated_fixes(
                project_id=project_id,
                fix_recommendations=fix_recommendations,
                user_context={
                    "user_id": auth_context.user_id,
                    "scopes": auth_context.scopes
                }
            )
            
            healing_attempts.append({
                "attempt": attempt + 1,
                "issues_found": len(analysis_result.get("issues", [])),
                "fixes_applied": len(fix_result.get("fixes_applied", [])),
                "fixes_failed": len(fix_result.get("fixes_failed", [])),
                "status": "fixes_applied" if fix_result.get("fixes_applied") else "no_fixes_applied"
            })
            
            # If all fixes were successful, run verification
            if fix_result.get("fixes_applied") and not fix_result.get("fixes_failed"):
                verification_result = await reviewer_agent.verify_fixes(
                    project_id=project_id,
                    applied_fixes=fix_result.get("fixes_applied", [])
                )
                
                if verification_result.get("all_fixes_successful"):
                    healing_attempts[-1]["verification"] = "successful"
                    break
                else:
                    healing_attempts[-1]["verification"] = "failed"
        
        # Generate final summary
        total_issues_fixed = sum(attempt.get("fixes_applied", 0) for attempt in healing_attempts)
        final_status = "completed" if healing_attempts and healing_attempts[-1].get("verification") == "successful" else "partial"
        
        await tracker.track_operation(
            operation_type="self_healing",
            agent_type="reviewer",
            success=final_status == "completed",
            metadata={
                "project_id": project_id,
                "total_attempts": len(healing_attempts),
                "total_issues_fixed": total_issues_fixed,
                "user_id": auth_context.user_id
            }
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "status": final_status,
                        "project_id": project_id,
                        "healing_summary": {
                            "total_attempts": len(healing_attempts),
                            "total_issues_fixed": total_issues_fixed,
                            "final_health_score": analysis_result.get("health_score", 0.0),
                            "remaining_issues": analysis_result.get("issues", []) if final_status != "completed" else []
                        },
                        "healing_attempts": healing_attempts,
                        "next_steps": [
                            "Run tests to verify fixes",
                            "Review generated code changes",
                            "Deploy updated application"
                        ]
                    }, indent=2)
                }
            ]
        }
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="self_healing",
            agent_type="reviewer",
            success=False,
            metadata={
                "project_id": project_id,
                "error": str(e),
                "user_id": auth_context.user_id
            }
        )
        
        logger.error(
            "self_healing_failed",
            project_id=project_id,
            error=str(e),
            correlation_id=correlation_id
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Self-healing failed: {str(e)}"
                }
            ],
            "isError": True
        }


@mcp_tool(
    name="code_review",
    description="Perform automated code review with quality analysis",
    required_scopes=["tools:review"]
)
async def code_review_tool(
    project_id: str,
    review_type: str = "comprehensive",
    focus_areas: Optional[List[str]] = None,
    auth_context: AuthContext = None,
    request=None
) -> Dict[str, Any]:
    """
    Perform comprehensive code review
    
    Args:
        project_id: ID of the project to review
        review_type: Type of review (security, performance, quality, comprehensive)
        focus_areas: Specific areas to focus on
    """
    correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
    tracker = AnalyticsTracker(correlation_id)
    
    if focus_areas is None:
        focus_areas = ["security", "performance", "maintainability", "documentation"]
    
    try:
        reviewer_agent = ReviewerAgent(correlation_id=correlation_id)
        
        logger.info(
            "code_review_started",
            user_id=auth_context.user_id,
            project_id=project_id,
            review_type=review_type,
            focus_areas=focus_areas,
            correlation_id=correlation_id
        )
        
        # Perform comprehensive analysis
        analysis_result = await reviewer_agent.analyze_project_health(
            project_id=project_id,
            focus_areas=focus_areas
        )
        
        await tracker.track_operation(
            operation_type="code_review",
            agent_type="reviewer",
            success=True,
            metadata={
                "project_id": project_id,
                "review_type": review_type,
                "health_score": analysis_result.get("health_score", 0.0),
                "issues_found": len(analysis_result.get("issues", [])),
                "user_id": auth_context.user_id
            }
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "status": "completed",
                        "project_id": project_id,
                        "review_type": review_type,
                        "health_score": analysis_result.get("health_score", 0.0),
                        "issues_found": len(analysis_result.get("issues", [])),
                        "issues": analysis_result.get("issues", []),
                        "recommendations": analysis_result.get("recommendations", []),
                        "focus_areas_analyzed": focus_areas,
                        "project_context": analysis_result.get("project_context", {}),
                        "review_timestamp": analysis_result.get("analysis_timestamp")
                    }, indent=2)
                }
            ]
        }
        
    except Exception as e:
        await tracker.track_operation(
            operation_type="code_review",
            agent_type="reviewer",
            success=False,
            metadata={
                "project_id": project_id,
                "review_type": review_type,
                "error": str(e),
                "user_id": auth_context.user_id
            }
        )
        
        logger.error(
            "code_review_failed",
            project_id=project_id,
            error=str(e),
            correlation_id=correlation_id
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Code review failed: {str(e)}"
                }
            ],
            "isError": True
        }