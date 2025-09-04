"""
Secure file manager for project operations
"""
import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import structlog

logger = structlog.get_logger()


class SecureFileManager:
    """Secure file operations for project management"""
    
    def __init__(self, base_path: str = "outputs"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    async def read_project_file(self, project_id: str, file_path: str) -> str:
        """Read a file from a project"""
        project_dir = self.base_path / project_id
        target_file = project_dir / file_path
        
        # Security check - ensure file is within project directory
        if not self._is_safe_path(target_file, project_dir):
            raise ValueError(f"Unsafe file path: {file_path}")
        
        if not target_file.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        return target_file.read_text(encoding='utf-8')
    
    async def write_project_file(self, project_id: str, file_path: str, content: str) -> bool:
        """Write a file to a project"""
        project_dir = self.base_path / project_id
        project_dir.mkdir(exist_ok=True)
        
        target_file = project_dir / file_path
        
        # Security check
        if not self._is_safe_path(target_file, project_dir):
            raise ValueError(f"Unsafe file path: {file_path}")
        
        # Ensure parent directory exists
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        target_file.write_text(content, encoding='utf-8')
        return True
    
    async def list_project_files(self, project_id: str) -> List[str]:
        """List all files in a project"""
        project_dir = self.base_path / project_id
        
        if not project_dir.exists():
            return []
        
        files = []
        for file_path in project_dir.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(project_dir)
                files.append(str(relative_path))
        
        return sorted(files)
    
    def _is_safe_path(self, target_path: Path, base_path: Path) -> bool:
        """Check if target path is safely within base path"""
        try:
            target_path.resolve().relative_to(base_path.resolve())
            return True
        except ValueError:
            return False


class ProjectManager:
    """Manage project lifecycle and metadata"""
    
    def __init__(self, base_path: str = "outputs"):
        self.base_path = Path(base_path)
        self.file_manager = SecureFileManager(base_path)
    
    async def get_project_structure(self, project_id: str) -> Dict[str, Any]:
        """Get project structure and metadata"""
        project_dir = self.base_path / project_id
        
        if not project_dir.exists():
            raise ValueError(f"Project not found: {project_id}")
        
        files = await self.file_manager.list_project_files(project_id)
        
        # Load project metadata if it exists
        metadata_file = project_dir / "project.json"
        metadata = {}
        if metadata_file.exists():
            try:
                metadata = json.loads(metadata_file.read_text())
            except json.JSONDecodeError:
                logger.warning("Invalid project metadata", project_id=project_id)
        
        return {
            "project_id": project_id,
            "files": files,
            "file_count": len(files),
            "metadata": metadata,
            "created_at": metadata.get("created_at", "unknown"),
            "project_type": metadata.get("project_type", "unknown"),
            "technology_stack": metadata.get("technology_stack", "unknown")
        }
    
    async def get_active_project_count(self) -> int:
        """Get count of active projects"""
        if not self.base_path.exists():
            return 0
        
        count = 0
        for item in self.base_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                count += 1
        
        return count
    
    async def create_project(self, project_id: str, metadata: Dict[str, Any]) -> bool:
        """Create a new project with metadata"""
        project_dir = self.base_path / project_id
        project_dir.mkdir(exist_ok=True)
        
        # Save project metadata
        metadata_file = project_dir / "project.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))
        
        logger.info("project_created", project_id=project_id, metadata=metadata)
        
        return True