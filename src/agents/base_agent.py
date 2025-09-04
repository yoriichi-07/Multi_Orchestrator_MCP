"""
Base agent class with common functionality for all specialized agents
"""
import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
import json
import re

logger = structlog.get_logger()


class BaseAgent(ABC):
    """Base class for all specialized agents"""
    
    def __init__(self, agent_type: str, correlation_id: Optional[str] = None):
        self.agent_type = agent_type
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.logger = logger.bind(
            agent_type=agent_type,
            correlation_id=self.correlation_id
        )
        
        # Agent-specific configuration
        self.model_preferences = self._get_model_preferences()
        self.prompt_templates = self._initialize_prompt_templates()
        
        self.logger.info(
            "agent_initialized",
            agent_type=agent_type,
            correlation_id=self.correlation_id
        )
    
    @abstractmethod
    def _get_model_preferences(self) -> Dict[str, str]:
        """Get LLM model preferences for this agent type"""
        pass
    
    @abstractmethod
    def _initialize_prompt_templates(self) -> Dict[str, str]:
        """Initialize agent-specific prompt templates"""
        pass
    
    async def generate_code(
        self,
        prompt: str,
        context: Dict[str, Any],
        code_type: str = "implementation",
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """
        Generate code using LLM with agent-specific optimizations
        """
        # Select optimal model for code generation
        model = self.model_preferences.get("code_generation", "claude-3-sonnet")
        
        # Enhance prompt with agent-specific context
        enhanced_prompt = self._enhance_prompt_with_context(prompt, context, code_type)
        
        # Track generation start
        generation_start = datetime.utcnow()
        
        try:
            # For now, simulate LLM response since we don't have LLMManager yet
            # This will be replaced with actual LLM integration
            result = await self._simulate_llm_response(enhanced_prompt, code_type)
            
            # Parse and validate generated code
            parsed_result = await self._parse_and_validate_code(result, code_type)
            
            # Track successful generation
            generation_duration = (datetime.utcnow() - generation_start).total_seconds()
            self.logger.info(
                "code_generation_successful",
                agent_type=self.agent_type,
                code_type=code_type,
                duration_seconds=generation_duration
            )
            
            return parsed_result
            
        except Exception as e:
            # Track failed generation
            generation_duration = (datetime.utcnow() - generation_start).total_seconds()
            self.logger.error(
                "code_generation_failed",
                agent_type=self.agent_type,
                code_type=code_type,
                error=str(e),
                duration_seconds=generation_duration
            )
            raise
    
    async def _simulate_llm_response(self, prompt: str, code_type: str) -> str:
        """Simulate LLM response for testing purposes"""
        await asyncio.sleep(1)  # Simulate processing time
        
        # Generate mock code based on type and agent
        if code_type == "implementation":
            if self.agent_type == "frontend":
                return self._generate_mock_frontend_code()
            elif self.agent_type == "backend":
                return self._generate_mock_backend_code()
            elif self.agent_type == "devops":
                return self._generate_mock_devops_code()
            else:
                return self._generate_mock_generic_code()
        else:
            return f"# Mock {code_type} code for {self.agent_type}"
    
    def _generate_mock_frontend_code(self) -> str:
        """Generate mock frontend code"""
        return '''
```jsx
// React Component
import React, { useState, useEffect } from 'react';
import './Component.css';

const Component = ({ data, onUpdate }) => {
    const [state, setState] = useState(null);
    
    useEffect(() => {
        fetchData();
    }, []);
    
    const fetchData = async () => {
        try {
            const response = await fetch('/api/data');
            const result = await response.json();
            setState(result);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };
    
    return (
        <div className="component">
            <h2>Component Title</h2>
            {state && (
                <div className="content">
                    {state.map(item => (
                        <div key={item.id} className="item">
                            {item.name}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Component;
```

```css
/* Component.css */
.component {
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
    margin: 10px 0;
}

.content {
    margin-top: 15px;
}

.item {
    padding: 10px;
    margin: 5px 0;
    background-color: #f5f5f5;
    border-radius: 4px;
}
```
'''
    
    def _generate_mock_backend_code(self) -> str:
        """Generate mock backend code"""
        return '''
```python
# FastAPI Backend Implementation
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="API Service", version="1.0.0")

class DataModel(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    created_at: Optional[str] = None

class DataCreate(BaseModel):
    name: str
    description: Optional[str] = None

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

@app.get("/api/data", response_model=List[DataModel])
async def get_data(skip: int = 0, limit: int = 100):
    # Mock data retrieval
    return [
        DataModel(id=1, name="Item 1", description="First item"),
        DataModel(id=2, name="Item 2", description="Second item")
    ]

@app.post("/api/data", response_model=DataModel)
async def create_data(data: DataCreate):
    # Mock data creation
    new_item = DataModel(
        id=999,
        name=data.name,
        description=data.description,
        created_at="2024-01-01T00:00:00Z"
    )
    return new_item

@app.put("/api/data/{item_id}", response_model=DataModel)
async def update_data(item_id: int, data: DataCreate):
    # Mock data update
    updated_item = DataModel(
        id=item_id,
        name=data.name,
        description=data.description,
        created_at="2024-01-01T00:00:00Z"
    )
    return updated_item

@app.delete("/api/data/{item_id}")
async def delete_data(item_id: int):
    return {"message": f"Item {item_id} deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```
'''
    
    def _generate_mock_devops_code(self) -> str:
        """Generate mock DevOps code"""
        return '''
```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/appdb
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=appdb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

```dockerfile
# Backend Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```
'''
    
    def _generate_mock_generic_code(self) -> str:
        """Generate mock generic code"""
        return f'''
```python
# {self.agent_type.title()} Implementation
import asyncio
from datetime import datetime
from typing import Dict, Any

class {self.agent_type.title()}Service:
    def __init__(self):
        self.created_at = datetime.utcnow()
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Process the data
        result = {{
            "status": "processed",
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "{self.agent_type}",
            "data": data
        }}
        return result
    
    def get_status(self) -> Dict[str, Any]:
        return {{
            "agent_type": "{self.agent_type}",
            "status": "active",
            "uptime": (datetime.utcnow() - self.created_at).total_seconds()
        }}
```
'''
    
    async def _parse_and_validate_code(self, raw_response: str, code_type: str) -> Dict[str, Any]:
        """Parse and validate generated code response"""
        try:
            # Extract code blocks from markdown format
            code_blocks = self._extract_code_blocks(raw_response)
            
            # Validate syntax for each code block
            validated_blocks = {}
            for lang, code in code_blocks.items():
                validation_result = await self._validate_code_syntax(code, lang)
                validated_blocks[lang] = {
                    "code": code,
                    "valid": validation_result["valid"],
                    "errors": validation_result.get("errors", [])
                }
            
            return {
                "success": True,
                "code_blocks": validated_blocks,
                "languages": list(code_blocks.keys()),
                "total_lines": sum(len(code.split('\n')) for code in code_blocks.values()),
                "validation_summary": {
                    "valid_blocks": sum(1 for block in validated_blocks.values() if block["valid"]),
                    "total_blocks": len(validated_blocks),
                    "overall_valid": all(block["valid"] for block in validated_blocks.values())
                }
            }
            
        except Exception as e:
            self.logger.error(
                "code_parsing_failed",
                error=str(e),
                agent_type=self.agent_type
            )
            return {
                "success": False,
                "error": str(e),
                "raw_response": raw_response[:500]  # First 500 chars for debugging
            }
    
    def _extract_code_blocks(self, text: str) -> Dict[str, str]:
        """Extract code blocks from markdown-formatted text"""
        code_blocks = {}
        
        # Pattern to match code blocks with language specifier
        pattern = r'```(\w+)?\s*\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for i, (lang, code) in enumerate(matches):
            # Use language if specified, otherwise generic
            language = lang.lower() if lang else f"code_{i}"
            code_blocks[language] = code.strip()
        
        return code_blocks
    
    async def _validate_code_syntax(self, code: str, language: str) -> Dict[str, Any]:
        """Validate code syntax for the given language"""
        try:
            if language in ["python", "py"]:
                # Basic Python syntax validation
                compile(code, '<string>', 'exec')
                return {"valid": True}
            elif language in ["javascript", "js", "jsx"]:
                # Basic JavaScript/JSX validation (simplified)
                # In production, would use proper JS parser
                if "function" in code or "=>" in code or "const" in code:
                    return {"valid": True}
                return {"valid": True}  # Assume valid for now
            elif language in ["yaml", "yml"]:
                # Basic YAML validation
                if ":" in code and ("-" in code or "version:" in code):
                    return {"valid": True}
                return {"valid": True}  # Assume valid for now
            else:
                # For other languages, assume valid
                return {"valid": True}
                
        except SyntaxError as e:
            return {
                "valid": False,
                "errors": [f"Syntax error: {str(e)}"]
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"]
            }
    
    def _enhance_prompt_with_context(
        self,
        prompt: str,
        context: Dict[str, Any],
        code_type: str
    ) -> str:
        """Enhance prompt with agent-specific context and templates"""
        
        # Get base template for the code type
        template = self.prompt_templates.get(code_type, self.prompt_templates.get("default", ""))
        
        # Build context information
        context_info = self._build_context_information(context)
        
        # Combine template, prompt, and context
        enhanced_prompt = f"""
{template}

Task: {prompt}

Context Information:
{context_info}

Requirements:
- Generate production-ready code
- Include proper error handling
- Follow best practices for {self.agent_type} development
- Provide clear, maintainable code structure
- Include appropriate comments and documentation

Please generate the code with clear language identifiers for each code block.
"""
        
        return enhanced_prompt.strip()
    
    def _build_context_information(self, context: Dict[str, Any]) -> str:
        """Build formatted context information for prompts"""
        context_lines = []
        
        if context.get("project_type"):
            context_lines.append(f"Project Type: {context['project_type']}")
        
        if context.get("technology_stack"):
            context_lines.append(f"Technology Stack: {context['technology_stack']}")
        
        if context.get("existing_code"):
            context_lines.append(f"Existing Code Context: {context['existing_code'][:500]}...")
        
        if context.get("requirements"):
            context_lines.append(f"Requirements: {context['requirements']}")
        
        if context.get("constraints"):
            context_lines.append(f"Constraints: {context['constraints']}")
        
        return "\n".join(context_lines) if context_lines else "No additional context provided"
    
    async def save_generated_files(
        self,
        project_id: str,
        generated_code: Dict[str, Any],
        file_mappings: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Save generated code to appropriate project files
        """
        saved_files = []
        
        try:
            # For now, simulate file saving since we don't have FileManager yet
            for file_type, file_path in file_mappings.items():
                if file_type in generated_code.get("code_blocks", {}):
                    code_content = generated_code["code_blocks"][file_type]["code"]
                    
                    # Simulate file saving
                    await asyncio.sleep(0.1)
                    
                    saved_files.append({
                        "file_path": file_path,
                        "file_type": file_type,
                        "size_bytes": len(code_content.encode('utf-8'))
                    })
            
            self.logger.info(
                "files_saved_successfully",
                agent_type=self.agent_type,
                project_id=project_id,
                files_count=len(saved_files)
            )
            
            return {
                "success": True,
                "saved_files": saved_files,
                "total_files": len(saved_files)
            }
            
        except Exception as e:
            self.logger.error(
                "file_saving_failed",
                agent_type=self.agent_type,
                project_id=project_id,
                error=str(e)
            )
            raise
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics"""
        return {
            "agent_type": self.agent_type,
            "correlation_id": self.correlation_id,
            "status": "active",
            "model_preferences": self.model_preferences,
            "available_templates": list(self.prompt_templates.keys()),
            "capabilities": self._get_agent_capabilities()
        }
    
    @abstractmethod
    def _get_agent_capabilities(self) -> List[str]:
        """Get list of agent-specific capabilities"""
        pass