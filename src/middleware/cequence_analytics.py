"""
Analytics and metrics tracking for the Multi-Agent Orchestrator
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()


class CequenceAnalytics:
    """Analytics and metrics tracking system"""
    
    def __init__(self):
        self.metrics_store: Dict[str, List[Dict[str, Any]]] = {}
        self.session_data: Dict[str, Dict[str, Any]] = {}
        
        logger.info("cequence_analytics_initialized")
    
    async def track_health_metrics(
        self,
        project_id: str,
        health_score: float,
        issues_count: int,
        correlation_id: Optional[str] = None
    ) -> None:
        """Track health monitoring metrics"""
        metric_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "project_id": project_id,
            "health_score": health_score,
            "issues_count": issues_count,
            "correlation_id": correlation_id,
            "metric_type": "health"
        }
        
        metric_key = f"health_{project_id}"
        if metric_key not in self.metrics_store:
            self.metrics_store[metric_key] = []
        
        self.metrics_store[metric_key].append(metric_data)
        
        # Keep only recent metrics (last 1000)
        if len(self.metrics_store[metric_key]) > 1000:
            self.metrics_store[metric_key] = self.metrics_store[metric_key][-1000:]
        
        logger.info(
            "health_metrics_tracked",
            project_id=project_id,
            health_score=health_score,
            issues_count=issues_count,
            correlation_id=correlation_id
        )
    
    async def track_healing_session(
        self,
        session_id: str,
        project_id: str,
        session_data: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> None:
        """Track healing session metrics"""
        metric_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "project_id": project_id,
            "correlation_id": correlation_id,
            "metric_type": "healing_session",
            **session_data
        }
        
        metric_key = f"healing_{project_id}"
        if metric_key not in self.metrics_store:
            self.metrics_store[metric_key] = []
        
        self.metrics_store[metric_key].append(metric_data)
        
        logger.info(
            "healing_session_tracked",
            session_id=session_id,
            project_id=project_id,
            success=session_data.get("success", False),
            correlation_id=correlation_id
        )
    
    async def track_agent_performance(
        self,
        agent_id: str,
        agent_type: str,
        task_id: str,
        performance_data: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> None:
        """Track agent performance metrics"""
        metric_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "agent_type": agent_type,
            "task_id": task_id,
            "correlation_id": correlation_id,
            "metric_type": "agent_performance",
            **performance_data
        }
        
        metric_key = f"agent_{agent_type}"
        if metric_key not in self.metrics_store:
            self.metrics_store[metric_key] = []
        
        self.metrics_store[metric_key].append(metric_data)
        
        logger.info(
            "agent_performance_tracked",
            agent_id=agent_id,
            agent_type=agent_type,
            task_id=task_id,
            correlation_id=correlation_id
        )
    
    async def track_llm_usage(
        self,
        model_name: str,
        operation: str,
        token_count: int,
        duration: float,
        correlation_id: Optional[str] = None
    ) -> None:
        """Track LLM usage metrics"""
        metric_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "model_name": model_name,
            "operation": operation,
            "token_count": token_count,
            "duration": duration,
            "correlation_id": correlation_id,
            "metric_type": "llm_usage"
        }
        
        metric_key = "llm_usage"
        if metric_key not in self.metrics_store:
            self.metrics_store[metric_key] = []
        
        self.metrics_store[metric_key].append(metric_data)
        
        logger.info(
            "llm_usage_tracked",
            model_name=model_name,
            operation=operation,
            token_count=token_count,
            duration=duration,
            correlation_id=correlation_id
        )
    
    async def get_health_trends(
        self,
        project_id: str,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """Get health trends for a project"""
        metric_key = f"health_{project_id}"
        metrics = self.metrics_store.get(metric_key, [])
        
        if not metrics:
            return {
                "project_id": project_id,
                "trend_data": [],
                "average_health_score": 0.0,
                "health_improvement": 0.0
            }
        
        # Filter recent metrics
        cutoff_time = datetime.utcnow().timestamp() - (days_back * 24 * 3600)
        recent_metrics = [
            m for m in metrics
            if datetime.fromisoformat(m["timestamp"]).timestamp() > cutoff_time
        ]
        
        if not recent_metrics:
            return {
                "project_id": project_id,
                "trend_data": [],
                "average_health_score": 0.0,
                "health_improvement": 0.0
            }
        
        # Calculate trends
        health_scores = [m["health_score"] for m in recent_metrics]
        average_health_score = sum(health_scores) / len(health_scores)
        
        # Calculate improvement (first vs last score)
        health_improvement = 0.0
        if len(health_scores) > 1:
            health_improvement = health_scores[-1] - health_scores[0]
        
        return {
            "project_id": project_id,
            "trend_data": recent_metrics,
            "average_health_score": average_health_score,
            "health_improvement": health_improvement,
            "total_data_points": len(recent_metrics)
        }
    
    async def get_healing_statistics(
        self,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get healing session statistics"""
        if project_id:
            metric_key = f"healing_{project_id}"
            metrics = self.metrics_store.get(metric_key, [])
        else:
            # Get all healing metrics
            metrics = []
            for key, values in self.metrics_store.items():
                if key.startswith("healing_"):
                    metrics.extend(values)
        
        if not metrics:
            return {
                "total_sessions": 0,
                "success_rate": 0.0,
                "average_duration": 0.0,
                "most_common_issues": []
            }
        
        total_sessions = len(metrics)
        successful_sessions = len([m for m in metrics if m.get("success", False)])
        success_rate = (successful_sessions / total_sessions) * 100 if total_sessions > 0 else 0
        
        # Calculate average duration
        durations = [m.get("duration_seconds", 0) for m in metrics if m.get("duration_seconds")]
        average_duration = sum(durations) / len(durations) if durations else 0
        
        # Find most common issue types
        issue_types = {}
        for metric in metrics:
            issue_type = metric.get("trigger_issue_type", "unknown")
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        most_common_issues = sorted(
            issue_types.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "total_sessions": total_sessions,
            "success_rate": round(success_rate, 2),
            "average_duration": round(average_duration, 2),
            "most_common_issues": most_common_issues
        }
    
    async def get_agent_performance_summary(
        self,
        agent_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get agent performance summary"""
        if agent_type:
            metric_key = f"agent_{agent_type}"
            metrics = self.metrics_store.get(metric_key, [])
        else:
            # Get all agent metrics
            metrics = []
            for key, values in self.metrics_store.items():
                if key.startswith("agent_"):
                    metrics.extend(values)
        
        if not metrics:
            return {
                "total_tasks": 0,
                "success_rate": 0.0,
                "average_duration": 0.0,
                "performance_trends": []
            }
        
        total_tasks = len(metrics)
        successful_tasks = len([m for m in metrics if m.get("success", False)])
        success_rate = (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        # Calculate average duration
        durations = [m.get("duration_seconds", 0) for m in metrics if m.get("duration_seconds")]
        average_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total_tasks": total_tasks,
            "success_rate": round(success_rate, 2),
            "average_duration": round(average_duration, 2),
            "performance_trends": metrics[-10:]  # Last 10 data points
        }
    
    async def get_llm_usage_summary(self) -> Dict[str, Any]:
        """Get LLM usage summary"""
        metrics = self.metrics_store.get("llm_usage", [])
        
        if not metrics:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "average_response_time": 0.0,
                "models_used": []
            }
        
        total_requests = len(metrics)
        total_tokens = sum(m.get("token_count", 0) for m in metrics)
        
        durations = [m.get("duration", 0) for m in metrics]
        average_response_time = sum(durations) / len(durations) if durations else 0
        
        # Get unique models used
        models_used = list(set(m.get("model_name", "unknown") for m in metrics))
        
        return {
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "average_response_time": round(average_response_time, 3),
            "models_used": models_used
        }
    
    def clear_metrics(self, metric_type: Optional[str] = None) -> None:
        """Clear stored metrics"""
        if metric_type:
            # Clear specific metric type
            keys_to_remove = [key for key in self.metrics_store.keys() if key.startswith(metric_type)]
            for key in keys_to_remove:
                del self.metrics_store[key]
        else:
            # Clear all metrics
            self.metrics_store.clear()
        
        logger.info(
            "metrics_cleared",
            metric_type=metric_type or "all"
        )