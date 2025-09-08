"""
Advanced error analysis and root cause identification
"""
import asyncio
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import structlog

from src.core.llm_manager import LLMManager
from src.healing.health_monitor import HealthIssue, IssueType

logger = structlog.get_logger()


class ErrorPattern:
    """Common error pattern for matching and analysis"""
    def __init__(self, pattern: str, issue_type: IssueType, severity_range: Tuple[int, int]):
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.issue_type = issue_type
        self.severity_range = severity_range


class ErrorAnalyzer:
    """Advanced error analysis and root cause identification"""
    
    def __init__(self, correlation_id: str):
        self.correlation_id = correlation_id
        try:
            self.llm_manager = LLMManager()
        except:
            self.llm_manager = None
        
        # Initialize error patterns
        self.error_patterns = self._initialize_error_patterns()
        
        # Error classification model
        self.classification_model = self._initialize_classification_model()
    
    def _initialize_error_patterns(self) -> List[ErrorPattern]:
        """Initialize common error patterns for quick classification"""
        return [
            # Python errors
            ErrorPattern(r"SyntaxError", IssueType.SYNTAX_ERROR, (6, 8)),
            ErrorPattern(r"IndentationError", IssueType.SYNTAX_ERROR, (5, 7)),
            ErrorPattern(r"NameError.*not defined", IssueType.LOGIC_ERROR, (6, 8)),
            ErrorPattern(r"TypeError.*object", IssueType.LOGIC_ERROR, (6, 8)),
            ErrorPattern(r"AttributeError.*no attribute", IssueType.LOGIC_ERROR, (6, 8)),
            ErrorPattern(r"KeyError", IssueType.LOGIC_ERROR, (5, 7)),
            ErrorPattern(r"IndexError", IssueType.LOGIC_ERROR, (5, 7)),
            ErrorPattern(r"ValueError", IssueType.LOGIC_ERROR, (5, 7)),
            ErrorPattern(r"ImportError|ModuleNotFoundError", IssueType.DEPENDENCY_ISSUE, (7, 9)),
            ErrorPattern(r"ConnectionError|TimeoutError", IssueType.API_ERROR, (6, 8)),
            
            # JavaScript/TypeScript errors
            ErrorPattern(r"ReferenceError.*not defined", IssueType.LOGIC_ERROR, (6, 8)),
            ErrorPattern(r"TypeError.*undefined", IssueType.LOGIC_ERROR, (6, 8)),
            ErrorPattern(r"SyntaxError.*Unexpected", IssueType.SYNTAX_ERROR, (6, 8)),
            ErrorPattern(r"Cannot read property.*undefined", IssueType.LOGIC_ERROR, (5, 7)),
            ErrorPattern(r"Module not found", IssueType.DEPENDENCY_ISSUE, (7, 9)),
            ErrorPattern(r"Network Error|Failed to fetch", IssueType.API_ERROR, (6, 8)),
            
            # Database errors
            ErrorPattern(r"connection.*refused", IssueType.DATABASE_ERROR, (8, 9)),
            ErrorPattern(r"authentication.*failed", IssueType.SECURITY_VULNERABILITY, (8, 9)),
            ErrorPattern(r"table.*doesn't exist", IssueType.DATABASE_ERROR, (7, 8)),
            ErrorPattern(r"SQL.*syntax.*error", IssueType.SYNTAX_ERROR, (6, 8)),
            
            # Security issues
            ErrorPattern(r"SQL injection", IssueType.SECURITY_VULNERABILITY, (9, 10)),
            ErrorPattern(r"XSS|Cross.*site.*scripting", IssueType.SECURITY_VULNERABILITY, (8, 10)),
            ErrorPattern(r"CSRF", IssueType.SECURITY_VULNERABILITY, (8, 9)),
            ErrorPattern(r"unauthorized|forbidden", IssueType.SECURITY_VULNERABILITY, (7, 9)),
            
            # Performance issues
            ErrorPattern(r"timeout|slow.*query", IssueType.PERFORMANCE_ISSUE, (5, 7)),
            ErrorPattern(r"memory.*leak|out.*of.*memory", IssueType.PERFORMANCE_ISSUE, (7, 9)),
            ErrorPattern(r"high.*cpu|performance.*degradation", IssueType.PERFORMANCE_ISSUE, (6, 8)),
        ]
    
    def _initialize_classification_model(self) -> Dict[str, Any]:
        """Initialize error classification model parameters"""
        return {
            "confidence_threshold": 0.7,
            "max_context_length": 2000,
            "analysis_temperature": 0.1,
            "root_cause_depth": 3
        }
    
    async def analyze_error(
        self,
        error_message: str,
        stack_trace: Optional[str] = None,
        code_context: Optional[str] = None,
        project_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive error analysis with root cause identification
        """
        analysis_start = datetime.now(timezone.utc)
        
        try:
            # 1. Quick pattern matching for known errors
            pattern_match = self._match_error_patterns(error_message, stack_trace)
            
            # 2. Advanced LLM-based analysis
            llm_analysis = await self._perform_llm_analysis(
                error_message=error_message,
                stack_trace=stack_trace,
                code_context=code_context,
                project_context=project_context,
                pattern_match=pattern_match
            )
            
            # 3. Root cause identification
            root_causes = await self._identify_root_causes(
                error_message=error_message,
                stack_trace=stack_trace,
                llm_analysis=llm_analysis,
                project_context=project_context
            )
            
            # 4. Impact assessment
            impact_assessment = await self._assess_error_impact(
                error_analysis=llm_analysis,
                root_causes=root_causes,
                project_context=project_context
            )
            
            # 5. Generate fix recommendations
            fix_recommendations = await self._generate_fix_recommendations(
                error_analysis=llm_analysis,
                root_causes=root_causes,
                impact_assessment=impact_assessment
            )
            
            analysis_duration = (datetime.now(timezone.utc) - analysis_start).total_seconds()
            
            comprehensive_analysis = {
                "analysis_id": f"analysis_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
                "error_classification": {
                    "primary_type": llm_analysis.get("primary_type", "unknown"),
                    "secondary_types": llm_analysis.get("secondary_types", []),
                    "severity": llm_analysis.get("severity", 5),
                    "confidence": llm_analysis.get("confidence", 0.5)
                },
                "root_causes": root_causes,
                "impact_assessment": impact_assessment,
                "fix_recommendations": fix_recommendations,
                "pattern_match": pattern_match,
                "analysis_metadata": {
                    "duration_seconds": analysis_duration,
                    "correlation_id": self.correlation_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
            logger.info(
                "error_analysis_completed",
                error_type=llm_analysis.get("primary_type"),
                severity=llm_analysis.get("severity"),
                root_causes_count=len(root_causes),
                duration_seconds=analysis_duration,
                correlation_id=self.correlation_id
            )
            
            return comprehensive_analysis
            
        except Exception as e:
            logger.error(
                "error_analysis_failed",
                error=str(e),
                correlation_id=self.correlation_id
            )
            
            # Return minimal analysis on failure
            return {
                "analysis_id": f"failed_analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "error_classification": {
                    "primary_type": "analysis_failure",
                    "severity": 8,
                    "confidence": 0.0
                },
                "root_causes": [{"cause": "Error analysis system failure", "confidence": 1.0}],
                "fix_recommendations": [{"action": "Investigate error analysis system"}],
                "analysis_error": str(e)
            }
    
    def _match_error_patterns(
        self,
        error_message: str,
        stack_trace: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Match error against known patterns for quick classification"""
        search_text = f"{error_message} {stack_trace or ''}"
        
        for pattern in self.error_patterns:
            if pattern.pattern.search(search_text):
                severity = (pattern.severity_range[0] + pattern.severity_range[1]) // 2
                
                return {
                    "matched_pattern": pattern.pattern.pattern,
                    "issue_type": pattern.issue_type.value,
                    "estimated_severity": severity,
                    "confidence": 0.8
                }
        
        return None
    
    async def _perform_llm_analysis(
        self,
        error_message: str,
        stack_trace: Optional[str],
        code_context: Optional[str],
        project_context: Optional[Dict[str, Any]],
        pattern_match: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform advanced LLM-based error analysis"""
        
        if not self.llm_manager:
            # Fallback to pattern-based analysis
            if pattern_match:
                return {
                    "primary_type": pattern_match["issue_type"],
                    "severity": pattern_match["estimated_severity"],
                    "confidence": 0.6,
                    "analysis_source": "pattern_match_fallback"
                }
            else:
                return {
                    "primary_type": "unknown",
                    "severity": 5,
                    "confidence": 0.1,
                    "analysis_source": "minimal_fallback"
                }
        
        analysis_prompt = f"""
        Perform comprehensive error analysis for the following error:

        ERROR MESSAGE:
        {error_message}

        STACK TRACE:
        {stack_trace or "Not provided"}

        CODE CONTEXT:
        {code_context or "Not provided"}

        PROJECT CONTEXT:
        {json.dumps(project_context or {}, indent=2)}

        PATTERN MATCH (if available):
        {json.dumps(pattern_match or {}, indent=2)}

        Please provide detailed analysis including:

        1. ERROR CLASSIFICATION:
           - Primary error type (syntax_error, runtime_error, logic_error, etc.)
           - Secondary error types (if applicable)
           - Severity rating (1-10 scale)
           - Confidence in classification (0.0-1.0)

        2. TECHNICAL ANALYSIS:
           - Specific cause of the error
           - Code location and context
           - Related components affected
           - Error propagation path

        3. CONTEXT ANALYSIS:
           - How this error fits in the project architecture
           - Dependencies and integrations involved
           - Potential cascading effects

        4. URGENCY ASSESSMENT:
           - Immediate impact on functionality
           - Long-term consequences
           - Risk to system stability

        Provide response as structured JSON for programmatic processing.
        """
        
        try:
            result = await self.llm_manager.generate_completion(
                prompt=analysis_prompt,
                model="claude-3-opus",  # Use most advanced model for analysis
                temperature=self.classification_model["analysis_temperature"],
                max_tokens=4000,
                metadata={
                    "operation": "error_analysis",
                    "correlation_id": self.correlation_id
                }
            )
            
            return json.loads(result.content)
            
        except json.JSONDecodeError as e:
            logger.warning(
                "llm_analysis_parsing_failed",
                error=str(e),
                correlation_id=self.correlation_id
            )
            
            # Return basic analysis based on pattern match
            if pattern_match:
                return {
                    "primary_type": pattern_match["issue_type"],
                    "severity": pattern_match["estimated_severity"],
                    "confidence": 0.6,
                    "analysis_source": "pattern_match_fallback"
                }
            else:
                return {
                    "primary_type": "unknown",
                    "severity": 5,
                    "confidence": 0.1,
                    "analysis_source": "minimal_fallback"
                }
    
    async def _identify_root_causes(
        self,
        error_message: str,
        stack_trace: Optional[str],
        llm_analysis: Dict[str, Any],
        project_context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify potential root causes of the error"""
        
        if not self.llm_manager:
            # Return basic root cause based on error type
            return [{
                "cause": f"Error type: {llm_analysis.get('primary_type', 'unknown')}",
                "confidence": 0.5,
                "evidence": error_message,
                "verification": "Manual code review required"
            }]
        
        root_cause_prompt = f"""
        Based on the following error analysis, identify the most likely root causes:

        ERROR: {error_message}
        STACK TRACE: {stack_trace or "Not provided"}
        ANALYSIS: {json.dumps(llm_analysis, indent=2)}
        PROJECT CONTEXT: {json.dumps(project_context or {}, indent=2)}

        For each potential root cause, provide:
        1. Description of the root cause
        2. Confidence level (0.0-1.0)
        3. Evidence supporting this cause
        4. How to verify this cause
        5. Dependencies or prerequisites

        Focus on actionable root causes that can be programmatically addressed.
        Return as structured JSON array.
        """
        
        try:
            result = await self.llm_manager.generate_completion(
                prompt=root_cause_prompt,
                model="claude-3-sonnet",
                temperature=0.05,  # Very low temperature for factual analysis
                max_tokens=3000,
                metadata={
                    "operation": "root_cause_analysis",
                    "correlation_id": self.correlation_id
                }
            )
            
            root_causes = json.loads(result.content)
            
            # Sort by confidence and return top causes
            if isinstance(root_causes, list):
                return sorted(
                    root_causes,
                    key=lambda x: x.get("confidence", 0.0),
                    reverse=True
                )[:self.classification_model["root_cause_depth"]]
            else:
                return [root_causes]
                
        except Exception as e:
            logger.warning(
                "root_cause_analysis_failed",
                error=str(e),
                correlation_id=self.correlation_id
            )
            
            # Return basic root cause based on error type
            return [{
                "cause": f"Error type: {llm_analysis.get('primary_type', 'unknown')}",
                "confidence": 0.5,
                "evidence": error_message,
                "verification": "Manual code review required"
            }]
    
    async def _assess_error_impact(
        self,
        error_analysis: Dict[str, Any],
        root_causes: List[Dict[str, Any]],
        project_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess the impact of the error on the system"""
        
        # Basic impact assessment
        severity = error_analysis.get("severity", 5)
        primary_type = error_analysis.get("primary_type", "unknown")
        
        impact_assessment = {
            "severity_level": severity,
            "immediate_impact": self._determine_immediate_impact(severity, primary_type),
            "long_term_consequences": self._determine_long_term_consequences(severity, primary_type),
            "affected_components": self._identify_affected_components(root_causes),
            "user_impact": self._assess_user_impact(severity, primary_type),
            "business_impact": self._assess_business_impact(severity, primary_type)
        }
        
        if self.llm_manager:
            try:
                # Enhanced LLM-based impact assessment
                impact_prompt = f"""
                Assess the comprehensive impact of this error:

                ERROR ANALYSIS: {json.dumps(error_analysis, indent=2)}
                ROOT CAUSES: {json.dumps(root_causes, indent=2)}
                PROJECT CONTEXT: {json.dumps(project_context or {}, indent=2)}

                Provide detailed impact assessment including:
                1. Immediate system impacts
                2. Cascading effects
                3. User experience impact
                4. Security implications
                5. Performance degradation
                6. Data integrity risks
                7. Recovery complexity

                Return as structured JSON.
                """
                
                result = await self.llm_manager.generate_completion(
                    prompt=impact_prompt,
                    model="claude-3-sonnet",
                    temperature=0.1,
                    max_tokens=2000,
                    metadata={
                        "operation": "impact_assessment",
                        "correlation_id": self.correlation_id
                    }
                )
                
                llm_impact = json.loads(result.content)
                impact_assessment.update(llm_impact)
                
            except Exception as e:
                logger.warning(
                    "llm_impact_assessment_failed",
                    error=str(e),
                    correlation_id=self.correlation_id
                )
        
        return impact_assessment
    
    async def _generate_fix_recommendations(
        self,
        error_analysis: Dict[str, Any],
        root_causes: List[Dict[str, Any]],
        impact_assessment: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate fix recommendations based on analysis"""
        
        recommendations = []
        
        # Basic recommendations based on error type
        primary_type = error_analysis.get("primary_type", "unknown")
        severity = error_analysis.get("severity", 5)
        
        if primary_type == "syntax_error":
            recommendations.append({
                "action": "Fix syntax error",
                "priority": "high",
                "complexity": "low",
                "description": "Correct syntax issues in the code"
            })
        elif primary_type == "dependency_issue":
            recommendations.append({
                "action": "Resolve dependency issue",
                "priority": "medium",
                "complexity": "medium",
                "description": "Install or update required dependencies"
            })
        elif primary_type == "security_vulnerability":
            recommendations.append({
                "action": "Apply security patch",
                "priority": "critical",
                "complexity": "high",
                "description": "Address security vulnerability immediately"
            })
        
        if self.llm_manager:
            try:
                # Enhanced LLM-based recommendations
                fix_prompt = f"""
                Generate specific fix recommendations for this error:

                ERROR ANALYSIS: {json.dumps(error_analysis, indent=2)}
                ROOT CAUSES: {json.dumps(root_causes, indent=2)}
                IMPACT ASSESSMENT: {json.dumps(impact_assessment, indent=2)}

                For each recommendation, provide:
                1. Specific action to take
                2. Priority level (low, medium, high, critical)
                3. Implementation complexity (low, medium, high)
                4. Detailed description
                5. Required resources
                6. Risk level
                7. Verification steps

                Return as structured JSON array.
                """
                
                result = await self.llm_manager.generate_completion(
                    prompt=fix_prompt,
                    model="claude-3-sonnet",
                    temperature=0.1,
                    max_tokens=2000,
                    metadata={
                        "operation": "fix_recommendations",
                        "correlation_id": self.correlation_id
                    }
                )
                
                llm_recommendations = json.loads(result.content)
                if isinstance(llm_recommendations, list):
                    recommendations.extend(llm_recommendations)
                else:
                    recommendations.append(llm_recommendations)
                
            except Exception as e:
                logger.warning(
                    "llm_fix_recommendations_failed",
                    error=str(e),
                    correlation_id=self.correlation_id
                )
        
        return recommendations
    
    def _determine_immediate_impact(self, severity: int, error_type: str) -> str:
        """Determine immediate impact based on severity and type"""
        if severity >= 8:
            return "System functionality severely compromised"
        elif severity >= 6:
            return "Moderate functionality impact"
        elif severity >= 4:
            return "Minor functionality impact"
        else:
            return "Minimal immediate impact"
    
    def _determine_long_term_consequences(self, severity: int, error_type: str) -> str:
        """Determine long-term consequences"""
        if error_type == "security_vulnerability":
            return "Potential security breach and data exposure"
        elif error_type == "performance_issue":
            return "Gradual system degradation and user dissatisfaction"
        elif severity >= 7:
            return "System instability and maintenance burden"
        else:
            return "Technical debt accumulation"
    
    def _identify_affected_components(self, root_causes: List[Dict[str, Any]]) -> List[str]:
        """Identify components affected by the error"""
        components = set()
        for cause in root_causes:
            # Extract component information from root causes
            cause_text = cause.get("cause", "").lower()
            if "database" in cause_text:
                components.add("database")
            if "api" in cause_text:
                components.add("api")
            if "frontend" in cause_text or "ui" in cause_text:
                components.add("frontend")
            if "backend" in cause_text or "server" in cause_text:
                components.add("backend")
        
        return list(components) if components else ["unknown"]
    
    def _assess_user_impact(self, severity: int, error_type: str) -> str:
        """Assess impact on end users"""
        if error_type in ["api_error", "runtime_error"] and severity >= 7:
            return "High - users cannot access core functionality"
        elif severity >= 5:
            return "Medium - users experience degraded functionality"
        else:
            return "Low - minimal user-facing impact"
    
    def _assess_business_impact(self, severity: int, error_type: str) -> str:
        """Assess business impact"""
        if error_type == "security_vulnerability" and severity >= 8:
            return "Critical - potential legal and financial consequences"
        elif severity >= 7:
            return "High - significant operational disruption"
        elif severity >= 5:
            return "Medium - reduced efficiency and customer satisfaction"
        else:
            return "Low - minimal business disruption"
    
    def get_error_pattern_stats(self) -> Dict[str, Any]:
        """Get statistics about error pattern matching"""
        return {
            "total_patterns": len(self.error_patterns),
            "pattern_types": {
                pattern.issue_type.value: len([p for p in self.error_patterns if p.issue_type == pattern.issue_type])
                for pattern in self.error_patterns
            },
            "classification_model": self.classification_model
        }