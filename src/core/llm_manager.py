"""
Basic LLM Manager for testing and development
"""
import asyncio
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """LLM response wrapper"""
    content: str
    model: str
    metadata: Dict[str, Any]


class LLMManager:
    """
    Basic LLM Manager for testing purposes
    In production, this would integrate with actual LLM services
    """
    
    def __init__(self):
        self.available_models = [
            "claude-3-sonnet",
            "gpt-4", 
            "gpt-3.5-turbo"
        ]
    
    async def generate_completion(
        self, 
        prompt: str, 
        model: str = "claude-3-sonnet",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """
        Generate completion for given prompt
        For testing, returns mock responses based on prompt content
        """
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Mock different responses based on prompt content
        if "syntax error" in prompt.lower():
            content = json.dumps({
                "issues": [{
                    "type": "syntax_error",
                    "severity": 8,
                    "description": "Missing closing bracket",
                    "line_number": 15,
                    "suggested_fixes": ["Add closing bracket at line 15"]
                }]
            })
        elif "analyze" in prompt.lower():
            content = json.dumps({
                "root_cause": "Missing import statement",
                "impact_assessment": "High - prevents module loading",
                "urgency": "high", 
                "recommendations": ["Add import statement at top of file"]
            })
        elif "solution" in prompt.lower():
            content = json.dumps({
                "feasibility_score": 0.9,
                "risk_assessment": "Low risk",
                "implementation_complexity": "Simple",
                "estimated_success_rate": 0.95
            })
        else:
            content = json.dumps({
                "analysis": "Code appears functional",
                "recommendations": ["Continue monitoring"]
            })
        
        return LLMResponse(
            content=content,
            model=model,
            metadata=metadata or {}
        )
    
    async def generate_response(
        self,
        prompt: str,
        model: str = "claude-3-sonnet",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Alternative interface for response generation
        Returns dict instead of LLMResponse object
        """
        response = await self.generate_completion(prompt, model, **kwargs)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"response": response.content}