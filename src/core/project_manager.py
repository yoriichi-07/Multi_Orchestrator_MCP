"""
Project management utilities for multi-agent orchestrator
"""
import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()


class ProjectManager:
    """Manages project lifecycle and metadata"""
    
    def __init__(self):
        self.projects: Dict[str, Dict[str, Any]] = {}
        logger.info("project_manager_initialized")
    
    async def create_project(
        self,
        project_name: str,
        project_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new project"""
        project_id = str(uuid.uuid4())
        
        project_data = {
            "project_id": project_id,
            "name": project_name,
            "type": project_type,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active",
            "metadata": metadata or {},
            "files": [],
            "dependencies": [],
            "health_history": []
        }
        
        self.projects[project_id] = project_data
        
        logger.info(
            "project_created",
            project_id=project_id,
            name=project_name,
            type=project_type
        )
        
        return project_id
    
    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project information"""
        return self.projects.get(project_id)
    
    async def update_project(
        self,
        project_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update project information"""
        if project_id not in self.projects:
            return False
        
        self.projects[project_id].update(updates)
        self.projects[project_id]["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info(
            "project_updated",
            project_id=project_id,
            updates=list(updates.keys())
        )
        
        return True
    
    async def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        if project_id not in self.projects:
            return False
        
        del self.projects[project_id]
        
        logger.info(
            "project_deleted",
            project_id=project_id
        )
        
        return True
    
    async def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects"""
        return list(self.projects.values())
    
    async def get_project_health_summary(self, project_id: str) -> Dict[str, Any]:
        """Get project health summary"""
        project = self.projects.get(project_id)
        if not project:
            return {}
        
        health_history = project.get("health_history", [])
        
        if not health_history:
            return {
                "project_id": project_id,
                "health_status": "unknown",
                "last_check": None,
                "issue_count": 0
            }
        
        latest_health = health_history[-1]
        
        return {
            "project_id": project_id,
            "health_status": latest_health.get("status", "unknown"),
            "health_score": latest_health.get("score", 0.0),
            "last_check": latest_health.get("timestamp"),
            "issue_count": len(latest_health.get("issues", []))
        }