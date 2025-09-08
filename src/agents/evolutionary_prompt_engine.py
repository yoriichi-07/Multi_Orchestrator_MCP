"""
Evolutionary Prompt Engine - Self-Improving AI Communication

This engine creates a self-improving feedback loop that allows the prompt library
to learn from mistakes and evolve towards more effective AI interactions.
"""
import asyncio
import json
import uuid
import hashlib
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import structlog
import statistics
from collections import defaultdict

from src.core.llm_manager import LLMManager

logger = structlog.get_logger()


class PromptType(Enum):
    """Types of prompts in the system"""
    SYSTEM_PROMPT = "system_prompt"
    TASK_PROMPT = "task_prompt"
    REFINEMENT_PROMPT = "refinement_prompt"
    VALIDATION_PROMPT = "validation_prompt"
    CORRECTION_PROMPT = "correction_prompt"
    OPTIMIZATION_PROMPT = "optimization_prompt"


class PromptPerformance(Enum):
    """Prompt performance ratings"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    FAILED = "failed"


@dataclass
class PromptTemplate:
    """Individual prompt template with metadata"""
    id: str
    name: str
    type: PromptType
    template: str
    variables: List[str]
    purpose: str
    context_requirements: List[str]
    expected_output_format: str
    tags: List[str]
    version: int
    created_at: datetime
    last_updated: datetime
    usage_count: int
    success_rate: float
    average_rating: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "template": self.template,
            "variables": self.variables,
            "purpose": self.purpose,
            "context_requirements": self.context_requirements,
            "expected_output_format": self.expected_output_format,
            "tags": self.tags,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "average_rating": self.average_rating
        }


@dataclass
class PromptExecution:
    """Record of a prompt execution with results and feedback"""
    execution_id: str
    prompt_id: str
    executed_prompt: str
    context: Dict[str, Any]
    response: str
    response_time: float
    success: bool
    performance_rating: PromptPerformance
    feedback: str
    error_details: Optional[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "prompt_id": self.prompt_id,
            "executed_prompt": self.executed_prompt,
            "context": self.context,
            "response": self.response,
            "response_time": self.response_time,
            "success": self.success,
            "performance_rating": self.performance_rating.value,
            "feedback": self.feedback,
            "error_details": self.error_details,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class PromptEvolution:
    """Record of prompt evolution and improvements"""
    evolution_id: str
    original_prompt_id: str
    evolved_prompt_id: str
    evolution_type: str  # "refinement", "optimization", "correction"
    changes_made: List[str]
    reason_for_change: str
    performance_improvement: float
    confidence_score: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "evolution_id": self.evolution_id,
            "original_prompt_id": self.original_prompt_id,
            "evolved_prompt_id": self.evolved_prompt_id,
            "evolution_type": self.evolution_type,
            "changes_made": self.changes_made,
            "reason_for_change": self.reason_for_change,
            "performance_improvement": self.performance_improvement,
            "confidence_score": self.confidence_score,
            "timestamp": self.timestamp.isoformat()
        }


class EvolutionaryPromptEngine:
    """
    Evolutionary Prompt Engine - The Prompt Evolution Oracle
    
    This engine analyzes prompt performance, learns from failures,
    and automatically evolves prompts to achieve better results.
    """
    
    def __init__(self, correlation_id: Optional[str] = None):
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.logger = logger.bind(correlation_id=self.correlation_id)
        
        try:
            self.llm_manager = LLMManager()
        except:
            self.llm_manager = None
            self.logger.warning("LLM manager not available - using fallback prompt evolution")
        
        # Prompt library and evolution tracking
        self.prompt_library: Dict[str, PromptTemplate] = {}
        self.execution_history: List[PromptExecution] = []
        self.evolution_history: List[PromptEvolution] = []
        
        # Performance tracking
        self.performance_metrics: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.evolution_patterns: Dict[str, List[str]] = defaultdict(list)
        
        # Load base prompt templates
        self._initialize_base_prompts()
        
        self.logger.info(
            "evolutionary_prompt_engine_initialized",
            correlation_id=self.correlation_id,
            base_prompts=len(self.prompt_library)
        )
    
    async def execute_prompt(
        self,
        prompt_name: str,
        context: Dict[str, Any],
        model: str = "claude-3-sonnet",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Tuple[str, PromptExecution]:
        """
        Execute a prompt and track its performance
        
        Args:
            prompt_name: Name of the prompt template to use
            context: Context variables for the prompt
            model: LLM model to use
            temperature: Generation temperature
            max_tokens: Maximum response tokens
        
        Returns:
            Tuple of (response, execution_record)
        """
        execution_id = str(uuid.uuid4())
        
        try:
            self.logger.info(
                "prompt_execution_started",
                execution_id=execution_id,
                prompt_name=prompt_name,
                model=model
            )
            
            # Get prompt template
            if prompt_name not in self.prompt_library:
                raise ValueError(f"Prompt template '{prompt_name}' not found")
            
            template = self.prompt_library[prompt_name]
            
            # Render prompt with context
            rendered_prompt = await self._render_prompt(template, context)
            
            # Execute the prompt
            start_time = datetime.now()
            response = await self._execute_llm_prompt(
                rendered_prompt, model, temperature, max_tokens
            )
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds()
            
            # Analyze response quality
            performance_rating, feedback = await self._analyze_response_quality(
                template, rendered_prompt, response, context
            )
            
            # Create execution record
            execution = PromptExecution(
                execution_id=execution_id,
                prompt_id=template.id,
                executed_prompt=rendered_prompt,
                context=context,
                response=response,
                response_time=response_time,
                success=performance_rating != PromptPerformance.FAILED,
                performance_rating=performance_rating,
                feedback=feedback,
                error_details=None,
                timestamp=start_time
            )
            
            # Update template statistics
            await self._update_template_stats(template, execution)
            
            # Store execution history
            self.execution_history.append(execution)
            
            # Check if evolution is needed
            await self._check_evolution_trigger(template, execution)
            
            self.logger.info(
                "prompt_execution_completed",
                execution_id=execution_id,
                performance_rating=performance_rating.value,
                response_time=response_time
            )
            
            return response, execution
            
        except Exception as e:
            self.logger.error(
                "prompt_execution_failed",
                execution_id=execution_id,
                error=str(e)
            )
            
            # Create failure execution record
            execution = PromptExecution(
                execution_id=execution_id,
                prompt_id=template.id if 'template' in locals() else "unknown",
                executed_prompt="",
                context=context,
                response="",
                response_time=0.0,
                success=False,
                performance_rating=PromptPerformance.FAILED,
                feedback=f"Execution failed: {str(e)}",
                error_details=str(e),
                timestamp=datetime.now()
            )
            
            self.execution_history.append(execution)
            raise
    
    async def evolve_prompt(
        self,
        prompt_name: str,
        evolution_context: Optional[Dict[str, Any]] = None
    ) -> PromptTemplate:
        """
        Evolve a prompt based on its performance history
        
        Args:
            prompt_name: Name of the prompt to evolve
            evolution_context: Additional context for evolution
        
        Returns:
            PromptTemplate: New evolved prompt template
        """
        evolution_id = str(uuid.uuid4())
        
        try:
            self.logger.info(
                "prompt_evolution_started",
                evolution_id=evolution_id,
                prompt_name=prompt_name
            )
            
            if prompt_name not in self.prompt_library:
                raise ValueError(f"Prompt template '{prompt_name}' not found")
            
            original_template = self.prompt_library[prompt_name]
            
            # Analyze performance history
            performance_analysis = await self._analyze_prompt_performance(original_template)
            
            # Determine evolution strategy
            evolution_strategy = await self._determine_evolution_strategy(
                original_template, performance_analysis
            )
            
            # Generate evolved prompt
            evolved_template = await self._generate_evolved_prompt(
                original_template, evolution_strategy, performance_analysis
            )
            
            # Calculate confidence score
            confidence_score = await self._calculate_evolution_confidence(
                original_template, evolved_template, performance_analysis
            )
            
            # Create evolution record
            evolution_record = PromptEvolution(
                evolution_id=evolution_id,
                original_prompt_id=original_template.id,
                evolved_prompt_id=evolved_template.id,
                evolution_type=evolution_strategy["type"],
                changes_made=evolution_strategy["changes"],
                reason_for_change=evolution_strategy["reason"],
                performance_improvement=0.0,  # Will be updated after testing
                confidence_score=confidence_score,
                timestamp=datetime.now()
            )
            
            # Add evolved template to library
            self.prompt_library[evolved_template.name] = evolved_template
            self.evolution_history.append(evolution_record)
            
            self.logger.info(
                "prompt_evolution_completed",
                evolution_id=evolution_id,
                confidence_score=confidence_score,
                evolution_type=evolution_strategy["type"]
            )
            
            return evolved_template
            
        except Exception as e:
            self.logger.error(
                "prompt_evolution_failed",
                evolution_id=evolution_id,
                error=str(e)
            )
            raise
    
    async def get_best_prompt_for_task(
        self,
        task_description: str,
        context_requirements: List[str],
        performance_threshold: float = 0.7
    ) -> Optional[PromptTemplate]:
        """
        Find the best prompt template for a specific task
        
        Args:
            task_description: Description of the task to perform
            context_requirements: Required context for the task
            performance_threshold: Minimum performance threshold
        
        Returns:
            Optional[PromptTemplate]: Best matching prompt template
        """
        try:
            self.logger.info(
                "best_prompt_search_started",
                task_description=task_description,
                performance_threshold=performance_threshold
            )
            
            # Score all prompts for this task
            prompt_scores = []
            
            for prompt_name, template in self.prompt_library.items():
                score = await self._score_prompt_for_task(
                    template, task_description, context_requirements
                )
                
                if (template.average_rating >= performance_threshold and
                    template.success_rate >= performance_threshold):
                    prompt_scores.append((score, template))
            
            if not prompt_scores:
                self.logger.warning(
                    "no_suitable_prompts_found",
                    task_description=task_description,
                    performance_threshold=performance_threshold
                )
                return None
            
            # Sort by score and return best
            prompt_scores.sort(key=lambda x: x[0], reverse=True)
            best_score, best_template = prompt_scores[0]
            
            self.logger.info(
                "best_prompt_found",
                prompt_name=best_template.name,
                score=best_score,
                success_rate=best_template.success_rate
            )
            
            return best_template
            
        except Exception as e:
            self.logger.error(
                "best_prompt_search_failed",
                error=str(e)
            )
            return None
    
    async def generate_new_prompt(
        self,
        task_description: str,
        examples: List[Dict[str, Any]],
        requirements: Dict[str, Any]
    ) -> PromptTemplate:
        """
        Generate a new prompt template from scratch
        
        Args:
            task_description: Description of the task
            examples: Example inputs and outputs
            requirements: Specific requirements for the prompt
        
        Returns:
            PromptTemplate: New prompt template
        """
        generation_id = str(uuid.uuid4())
        
        try:
            self.logger.info(
                "prompt_generation_started",
                generation_id=generation_id,
                task_description=task_description
            )
            
            if not self.llm_manager:
                return self._fallback_prompt_generation(task_description, requirements)
            
            # Generate prompt using meta-prompting
            generation_prompt = f"""
            You are a Prompt Engineering Expert. Generate a high-quality prompt template for this task.

            TASK DESCRIPTION:
            {task_description}

            EXAMPLES:
            {json.dumps(examples, indent=2)}

            REQUIREMENTS:
            {json.dumps(requirements, indent=2)}

            Create a prompt template that:
            1. Clearly defines the task and expectations
            2. Provides clear output format instructions
            3. Includes examples and edge case handling
            4. Uses effective prompt engineering techniques (few-shot, chain-of-thought, etc.)
            5. Is specific and actionable

            Response format:
            {{
                "prompt_template": "The actual prompt template with {{variable}} placeholders",
                "variables": ["list", "of", "variables"],
                "purpose": "Clear description of what this prompt accomplishes",
                "context_requirements": ["required", "context", "elements"],
                "expected_output_format": "Description of expected output format",
                "tags": ["relevant", "tags"]
            }}

            Make the prompt specific, clear, and effective.
            """
            
            result = await self.llm_manager.generate_completion(
                prompt=generation_prompt,
                model="claude-3-opus",
                temperature=0.3,
                max_tokens=3000,
                metadata={
                    "operation": "prompt_generation",
                    "correlation_id": self.correlation_id
                }
            )
            
            generated_data = json.loads(result.content)
            
            # Create new prompt template
            new_template = PromptTemplate(
                id=str(uuid.uuid4()),
                name=f"generated_{task_description.lower().replace(' ', '_')}_{generation_id[:8]}",
                type=PromptType.TASK_PROMPT,
                template=generated_data["prompt_template"],
                variables=generated_data["variables"],
                purpose=generated_data["purpose"],
                context_requirements=generated_data["context_requirements"],
                expected_output_format=generated_data["expected_output_format"],
                tags=generated_data["tags"],
                version=1,
                created_at=datetime.now(timezone.utc),
                last_updated=datetime.now(timezone.utc),
                usage_count=0,
                success_rate=0.0,
                average_rating=0.0
            )
            
            # Add to library
            self.prompt_library[new_template.name] = new_template
            
            self.logger.info(
                "prompt_generation_completed",
                generation_id=generation_id,
                prompt_name=new_template.name
            )
            
            return new_template
            
        except Exception as e:
            self.logger.error(
                "prompt_generation_failed",
                generation_id=generation_id,
                error=str(e)
            )
            raise
    
    async def _render_prompt(
        self,
        template: PromptTemplate,
        context: Dict[str, Any]
    ) -> str:
        """Render a prompt template with context variables"""
        
        rendered_prompt = template.template
        
        # Replace variables in template
        for variable in template.variables:
            if variable in context:
                placeholder = f"{{{{{variable}}}}}"
                rendered_prompt = rendered_prompt.replace(placeholder, str(context[variable]))
            else:
                self.logger.warning(
                    "missing_variable",
                    template_id=template.id,
                    variable=variable
                )
        
        return rendered_prompt
    
    async def _execute_llm_prompt(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Execute a prompt using the LLM manager"""
        
        if not self.llm_manager:
            return f"Mock response for: {prompt[:100]}..."
        
        result = await self.llm_manager.generate_completion(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            metadata={
                "operation": "prompt_execution",
                "correlation_id": self.correlation_id
            }
        )
        
        return result.content
    
    async def _analyze_response_quality(
        self,
        template: PromptTemplate,
        prompt: str,
        response: str,
        context: Dict[str, Any]
    ) -> Tuple[PromptPerformance, str]:
        """Analyze the quality of a prompt response"""
        
        # Simple heuristic analysis (could be enhanced with LLM evaluation)
        
        if not response or len(response.strip()) < 10:
            return PromptPerformance.FAILED, "Response too short or empty"
        
        # Check for expected format
        if template.expected_output_format:
            if "json" in template.expected_output_format.lower():
                try:
                    json.loads(response)
                    format_score = 1.0
                except:
                    format_score = 0.0
            else:
                format_score = 0.8  # Assume good format for non-JSON
        else:
            format_score = 0.8
        
        # Check response length appropriateness
        if len(response) < 50:
            length_score = 0.5
        elif len(response) > 5000:
            length_score = 0.7
        else:
            length_score = 1.0
        
        # Calculate overall score
        overall_score = (format_score + length_score) / 2
        
        if overall_score >= 0.9:
            return PromptPerformance.EXCELLENT, "High-quality response with proper format"
        elif overall_score >= 0.7:
            return PromptPerformance.GOOD, "Good response quality"
        elif overall_score >= 0.5:
            return PromptPerformance.AVERAGE, "Average response quality"
        elif overall_score >= 0.3:
            return PromptPerformance.POOR, "Poor response quality"
        else:
            return PromptPerformance.FAILED, "Failed to generate adequate response"
    
    async def _update_template_stats(
        self,
        template: PromptTemplate,
        execution: PromptExecution
    ) -> None:
        """Update template statistics based on execution"""
        
        template.usage_count += 1
        
        # Update success rate
        recent_executions = [
            e for e in self.execution_history[-100:]  # Last 100 executions
            if e.prompt_id == template.id
        ]
        
        if recent_executions:
            successes = sum(1 for e in recent_executions if e.success)
            template.success_rate = successes / len(recent_executions)
        
        # Update average rating
        performance_values = {
            PromptPerformance.EXCELLENT: 1.0,
            PromptPerformance.GOOD: 0.8,
            PromptPerformance.AVERAGE: 0.6,
            PromptPerformance.POOR: 0.4,
            PromptPerformance.FAILED: 0.0
        }
        
        recent_ratings = [
            performance_values[e.performance_rating]
            for e in recent_executions
        ]
        
        if recent_ratings:
            template.average_rating = statistics.mean(recent_ratings)
        
        template.last_updated = datetime.now(timezone.utc)
    
    async def _check_evolution_trigger(
        self,
        template: PromptTemplate,
        execution: PromptExecution
    ) -> None:
        """Check if prompt evolution should be triggered"""
        
        # Evolution triggers
        evolution_needed = False
        reason = ""
        
        # Poor performance trigger
        if template.average_rating < 0.6 and template.usage_count >= 10:
            evolution_needed = True
            reason = "Poor average performance"
        
        # Low success rate trigger
        elif template.success_rate < 0.7 and template.usage_count >= 10:
            evolution_needed = True
            reason = "Low success rate"
        
        # Recent failures trigger
        elif len(self.execution_history) >= 5:
            recent_failures = [
                e for e in self.execution_history[-5:]
                if e.prompt_id == template.id and not e.success
            ]
            if len(recent_failures) >= 3:
                evolution_needed = True
                reason = "Recent failure pattern"
        
        if evolution_needed:
            self.logger.info(
                "evolution_triggered",
                template_id=template.id,
                reason=reason,
                usage_count=template.usage_count,
                success_rate=template.success_rate
            )
            
            # Schedule evolution (could be done async)
            try:
                await self.evolve_prompt(template.name)
            except Exception as e:
                self.logger.error(
                    "evolution_trigger_failed",
                    template_id=template.id,
                    error=str(e)
                )
    
    async def _analyze_prompt_performance(
        self,
        template: PromptTemplate
    ) -> Dict[str, Any]:
        """Analyze detailed performance metrics for a prompt"""
        
        # Get executions for this template
        template_executions = [
            e for e in self.execution_history
            if e.prompt_id == template.id
        ]
        
        if not template_executions:
            return {"insufficient_data": True}
        
        # Analyze patterns
        failure_patterns = []
        performance_trends = []
        common_issues = []
        
        for execution in template_executions:
            if not execution.success:
                failure_patterns.append(execution.feedback)
            
            performance_values = {
                PromptPerformance.EXCELLENT: 1.0,
                PromptPerformance.GOOD: 0.8,
                PromptPerformance.AVERAGE: 0.6,
                PromptPerformance.POOR: 0.4,
                PromptPerformance.FAILED: 0.0
            }
            performance_trends.append(performance_values[execution.performance_rating])
        
        # Identify common issues
        if failure_patterns:
            issue_counts = defaultdict(int)
            for pattern in failure_patterns:
                if "format" in pattern.lower():
                    issue_counts["format_issues"] += 1
                elif "short" in pattern.lower() or "empty" in pattern.lower():
                    issue_counts["length_issues"] += 1
                elif "error" in pattern.lower():
                    issue_counts["execution_errors"] += 1
                else:
                    issue_counts["other_issues"] += 1
            
            common_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_executions": len(template_executions),
            "success_rate": template.success_rate,
            "average_rating": template.average_rating,
            "failure_patterns": failure_patterns,
            "performance_trends": performance_trends,
            "common_issues": common_issues,
            "recent_performance": performance_trends[-10:] if len(performance_trends) >= 10 else performance_trends
        }
    
    async def _determine_evolution_strategy(
        self,
        template: PromptTemplate,
        performance_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine the best evolution strategy for a prompt"""
        
        strategy = {
            "type": "refinement",
            "changes": [],
            "reason": "",
            "confidence": 0.5
        }
        
        if performance_analysis.get("insufficient_data"):
            strategy["type"] = "optimization"
            strategy["reason"] = "Insufficient performance data"
            return strategy
        
        common_issues = performance_analysis.get("common_issues", [])
        
        if common_issues:
            primary_issue = common_issues[0][0]
            
            if primary_issue == "format_issues":
                strategy["type"] = "correction"
                strategy["changes"] = ["Improve output format instructions", "Add format examples"]
                strategy["reason"] = "Frequent format violations"
                strategy["confidence"] = 0.8
            
            elif primary_issue == "length_issues":
                strategy["type"] = "refinement"
                strategy["changes"] = ["Add length requirements", "Improve task clarity"]
                strategy["reason"] = "Response length problems"
                strategy["confidence"] = 0.7
            
            elif primary_issue == "execution_errors":
                strategy["type"] = "correction"
                strategy["changes"] = ["Simplify instructions", "Add error handling guidance"]
                strategy["reason"] = "Execution failures"
                strategy["confidence"] = 0.6
        
        else:
            # General performance improvement
            if template.average_rating < 0.7:
                strategy["type"] = "optimization"
                strategy["changes"] = ["Enhance clarity", "Add examples", "Improve structure"]
                strategy["reason"] = "General performance improvement needed"
                strategy["confidence"] = 0.6
        
        return strategy
    
    async def _generate_evolved_prompt(
        self,
        original_template: PromptTemplate,
        evolution_strategy: Dict[str, Any],
        performance_analysis: Dict[str, Any]
    ) -> PromptTemplate:
        """Generate an evolved version of a prompt"""
        
        if not self.llm_manager:
            return self._fallback_evolve_prompt(original_template, evolution_strategy)
        
        evolution_prompt = f"""
        You are a Prompt Evolution Expert. Improve this prompt based on performance analysis.

        ORIGINAL PROMPT:
        {original_template.template}

        CURRENT PERFORMANCE:
        - Success Rate: {original_template.success_rate:.2f}
        - Average Rating: {original_template.average_rating:.2f}
        - Usage Count: {original_template.usage_count}

        PERFORMANCE ANALYSIS:
        {json.dumps(performance_analysis, indent=2)}

        EVOLUTION STRATEGY:
        {json.dumps(evolution_strategy, indent=2)}

        Create an improved version that addresses the identified issues.

        Guidelines:
        1. Maintain the original purpose and structure
        2. Address the specific issues identified
        3. Improve clarity and specificity
        4. Add examples if helpful
        5. Ensure output format is clear

        Return the evolved prompt template as a JSON object:
        {{
            "evolved_template": "The improved prompt template",
            "changes_made": ["list", "of", "specific", "changes"],
            "rationale": "Why these changes should improve performance"
        }}
        """
        
        try:
            result = await self.llm_manager.generate_completion(
                prompt=evolution_prompt,
                model="claude-3-opus",
                temperature=0.3,
                max_tokens=3000,
                metadata={
                    "operation": "prompt_evolution",
                    "correlation_id": self.correlation_id
                }
            )
            
            evolved_data = json.loads(result.content)
            
            # Create evolved template
            evolved_template = PromptTemplate(
                id=str(uuid.uuid4()),
                name=f"{original_template.name}_evolved_v{original_template.version + 1}",
                type=original_template.type,
                template=evolved_data["evolved_template"],
                variables=original_template.variables,  # Keep same variables
                purpose=original_template.purpose,
                context_requirements=original_template.context_requirements,
                expected_output_format=original_template.expected_output_format,
                tags=original_template.tags + ["evolved"],
                version=original_template.version + 1,
                created_at=datetime.now(timezone.utc),
                last_updated=datetime.now(timezone.utc),
                usage_count=0,
                success_rate=0.0,
                average_rating=0.0
            )
            
            return evolved_template
            
        except Exception as e:
            self.logger.error(
                "llm_evolution_failed",
                error=str(e),
                fallback="using_fallback_evolution"
            )
            return self._fallback_evolve_prompt(original_template, evolution_strategy)
    
    async def _calculate_evolution_confidence(
        self,
        original_template: PromptTemplate,
        evolved_template: PromptTemplate,
        performance_analysis: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for the evolution"""
        
        confidence_factors = []
        
        # Data quality factor
        executions = performance_analysis.get("total_executions", 0)
        if executions >= 20:
            confidence_factors.append(0.9)
        elif executions >= 10:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.5)
        
        # Performance clarity factor
        if performance_analysis.get("common_issues"):
            confidence_factors.append(0.8)  # Clear issues to address
        else:
            confidence_factors.append(0.6)  # Unclear performance problems
        
        # Evolution scope factor
        template_length_diff = abs(len(evolved_template.template) - len(original_template.template))
        if template_length_diff < 100:
            confidence_factors.append(0.8)  # Conservative change
        elif template_length_diff < 500:
            confidence_factors.append(0.7)  # Moderate change
        else:
            confidence_factors.append(0.5)  # Major change
        
        return statistics.mean(confidence_factors)
    
    async def _score_prompt_for_task(
        self,
        template: PromptTemplate,
        task_description: str,
        context_requirements: List[str]
    ) -> float:
        """Score how well a prompt template matches a task"""
        
        score = 0.0
        
        # Performance score (40% weight)
        performance_score = template.average_rating * template.success_rate
        score += performance_score * 0.4
        
        # Purpose match score (30% weight)
        purpose_match = 0.0
        if task_description.lower() in template.purpose.lower():
            purpose_match = 1.0
        elif any(word in template.purpose.lower() for word in task_description.lower().split()):
            purpose_match = 0.6
        
        score += purpose_match * 0.3
        
        # Context requirements match score (20% weight)
        context_match = 0.0
        if context_requirements:
            matched_requirements = sum(
                1 for req in context_requirements
                if req in template.context_requirements
            )
            context_match = matched_requirements / len(context_requirements)
        
        score += context_match * 0.2
        
        # Usage maturity score (10% weight)
        usage_maturity = min(template.usage_count / 50, 1.0)  # Mature at 50 uses
        score += usage_maturity * 0.1
        
        return score
    
    def _initialize_base_prompts(self) -> None:
        """Initialize the prompt library with base templates"""
        
        # System analysis prompt
        system_analysis_template = PromptTemplate(
            id=str(uuid.uuid4()),
            name="system_analysis",
            type=PromptType.SYSTEM_PROMPT,
            template="""
You are a Senior Systems Analyst. Analyze the following system or codebase:

SYSTEM/CODEBASE DETAILS:
{system_details}

ANALYSIS REQUIREMENTS:
{requirements}

Provide a comprehensive analysis that includes:
1. Architecture overview
2. Key components and their responsibilities
3. Identified strengths and weaknesses
4. Potential improvement areas
5. Risk assessment
6. Recommendations

Format your response as structured analysis with clear sections.
            """.strip(),
            variables=["system_details", "requirements"],
            purpose="Analyze systems and codebases for architecture and improvement opportunities",
            context_requirements=["system_details", "requirements"],
            expected_output_format="Structured analysis with sections",
            tags=["analysis", "system", "architecture"],
            version=1,
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
            usage_count=0,
            success_rate=0.0,
            average_rating=0.0
        )
        
        # Code generation prompt
        code_generation_template = PromptTemplate(
            id=str(uuid.uuid4()),
            name="code_generation",
            type=PromptType.TASK_PROMPT,
            template="""
You are a Senior Software Developer. Generate high-quality code for the following specification:

SPECIFICATION:
{specification}

REQUIREMENTS:
{requirements}

LANGUAGE/FRAMEWORK: {language}

Generate code that:
1. Follows best practices and conventions
2. Includes proper error handling
3. Is well-documented with comments
4. Includes type hints where applicable
5. Is production-ready and efficient

Provide the code with explanations for key design decisions.
            """.strip(),
            variables=["specification", "requirements", "language"],
            purpose="Generate high-quality code from specifications",
            context_requirements=["specification", "requirements", "language"],
            expected_output_format="Code with explanations",
            tags=["code", "generation", "development"],
            version=1,
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
            usage_count=0,
            success_rate=0.0,
            average_rating=0.0
        )
        
        # Problem solving prompt
        problem_solving_template = PromptTemplate(
            id=str(uuid.uuid4()),
            name="problem_solving",
            type=PromptType.TASK_PROMPT,
            template="""
You are a Senior Problem Solver. Address the following problem systematically:

PROBLEM DESCRIPTION:
{problem_description}

CONTEXT:
{context}

CONSTRAINTS:
{constraints}

Use a structured approach:
1. Problem Analysis: Break down the problem into components
2. Root Cause Analysis: Identify underlying causes
3. Solution Options: Generate multiple potential solutions
4. Evaluation: Assess pros and cons of each option
5. Recommendation: Select the best solution with rationale
6. Implementation Plan: Outline steps to implement the solution

Provide clear, actionable recommendations.
            """.strip(),
            variables=["problem_description", "context", "constraints"],
            purpose="Systematically solve complex problems with structured analysis",
            context_requirements=["problem_description", "context"],
            expected_output_format="Structured problem-solving analysis",
            tags=["problem", "solving", "analysis"],
            version=1,
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
            usage_count=0,
            success_rate=0.0,
            average_rating=0.0
        )
        
        # Add templates to library
        self.prompt_library[system_analysis_template.name] = system_analysis_template
        self.prompt_library[code_generation_template.name] = code_generation_template
        self.prompt_library[problem_solving_template.name] = problem_solving_template
    
    def _fallback_prompt_generation(
        self,
        task_description: str,
        requirements: Dict[str, Any]
    ) -> PromptTemplate:
        """Fallback prompt generation when LLM is not available"""
        
        return PromptTemplate(
            id=str(uuid.uuid4()),
            name=f"fallback_{task_description.lower().replace(' ', '_')}",
            type=PromptType.TASK_PROMPT,
            template=f"""
You are tasked with: {task_description}

Requirements: {requirements}

Please provide a comprehensive response that addresses all aspects of the task.
            """.strip(),
            variables=["context"],
            purpose=task_description,
            context_requirements=list(requirements.keys()) if requirements else [],
            expected_output_format="Text response",
            tags=["fallback", "generated"],
            version=1,
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
            usage_count=0,
            success_rate=0.0,
            average_rating=0.0
        )
    
    def _fallback_evolve_prompt(
        self,
        original_template: PromptTemplate,
        evolution_strategy: Dict[str, Any]
    ) -> PromptTemplate:
        """Fallback prompt evolution when LLM is not available"""
        
        # Simple evolution: add clarity instructions
        evolved_template_text = original_template.template + "\n\nPlease provide a clear, detailed, and well-structured response."
        
        return PromptTemplate(
            id=str(uuid.uuid4()),
            name=f"{original_template.name}_evolved_fallback",
            type=original_template.type,
            template=evolved_template_text,
            variables=original_template.variables,
            purpose=original_template.purpose,
            context_requirements=original_template.context_requirements,
            expected_output_format=original_template.expected_output_format,
            tags=original_template.tags + ["evolved", "fallback"],
            version=original_template.version + 1,
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
            usage_count=0,
            success_rate=0.0,
            average_rating=0.0
        )
    
    # Analytics and reporting methods
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report for all prompts"""
        
        total_prompts = len(self.prompt_library)
        total_executions = len(self.execution_history)
        total_evolutions = len(self.evolution_history)
        
        if not self.execution_history:
            return {
                "total_prompts": total_prompts,
                "total_executions": 0,
                "total_evolutions": 0,
                "average_performance": 0.0,
                "top_performers": [],
                "improvement_opportunities": []
            }
        
        # Calculate overall metrics
        all_ratings = [
            {
                PromptPerformance.EXCELLENT: 1.0,
                PromptPerformance.GOOD: 0.8,
                PromptPerformance.AVERAGE: 0.6,
                PromptPerformance.POOR: 0.4,
                PromptPerformance.FAILED: 0.0
            }[e.performance_rating] for e in self.execution_history
        ]
        
        average_performance = statistics.mean(all_ratings)
        
        # Top performers
        top_performers = sorted(
            [(name, template) for name, template in self.prompt_library.items()],
            key=lambda x: x[1].average_rating * x[1].success_rate,
            reverse=True
        )[:5]
        
        # Improvement opportunities
        improvement_opportunities = [
            (name, template) for name, template in self.prompt_library.items()
            if template.average_rating < 0.7 and template.usage_count >= 5
        ]
        
        return {
            "total_prompts": total_prompts,
            "total_executions": total_executions,
            "total_evolutions": total_evolutions,
            "average_performance": average_performance,
            "top_performers": [
                {
                    "name": name,
                    "success_rate": template.success_rate,
                    "average_rating": template.average_rating,
                    "usage_count": template.usage_count
                }
                for name, template in top_performers
            ],
            "improvement_opportunities": [
                {
                    "name": name,
                    "success_rate": template.success_rate,
                    "average_rating": template.average_rating,
                    "usage_count": template.usage_count
                }
                for name, template in improvement_opportunities
            ]
        }