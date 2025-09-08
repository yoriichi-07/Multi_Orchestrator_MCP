"""
AI-powered solution generation and fix recommendations
"""
import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timezone
import structlog

from src.core.llm_manager import LLMManager
from src.core.file_manager import SecureFileManager
from src.healing.error_analyzer import ErrorAnalyzer

logger = structlog.get_logger()


class SolutionType:
    """Types of automated solutions"""
    CODE_FIX = "code_fix"
    CONFIGURATION_CHANGE = "configuration_change"
    DEPENDENCY_UPDATE = "dependency_update"
    ARCHITECTURAL_CHANGE = "architectural_change"
    SECURITY_PATCH = "security_patch"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"


class Solution:
    """Individual solution recommendation"""
    def __init__(
        self,
        solution_id: str,
        solution_type: str,
        description: str,
        confidence: float,
        implementation_complexity: int,
        estimated_time_minutes: int,
        files_to_modify: List[str],
        implementation_steps: List[Dict[str, Any]],
        rollback_plan: List[Dict[str, Any]],
        verification_steps: List[str],
        risk_assessment: Dict[str, Any]
    ):
        self.solution_id = solution_id
        self.solution_type = solution_type
        self.description = description
        self.confidence = confidence
        self.implementation_complexity = implementation_complexity
        self.estimated_time_minutes = estimated_time_minutes
        self.files_to_modify = files_to_modify
        self.implementation_steps = implementation_steps
        self.rollback_plan = rollback_plan
        self.verification_steps = verification_steps
        self.risk_assessment = risk_assessment
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert solution to dictionary representation"""
        return {
            "solution_id": self.solution_id,
            "solution_type": self.solution_type,
            "description": self.description,
            "confidence": self.confidence,
            "implementation_complexity": self.implementation_complexity,
            "estimated_time_minutes": self.estimated_time_minutes,
            "files_to_modify": self.files_to_modify,
            "implementation_steps": self.implementation_steps,
            "rollback_plan": self.rollback_plan,
            "verification_steps": self.verification_steps,
            "risk_assessment": self.risk_assessment
        }


class SolutionGenerator:
    """Advanced solution generation for automated problem resolution"""
    
    def __init__(self, correlation_id: str):
        self.correlation_id = correlation_id
        try:
            self.llm_manager = LLMManager()
        except:
            self.llm_manager = None
            
        try:
            self.file_manager = SecureFileManager()
        except:
            self.file_manager = None
            
        self.error_analyzer = ErrorAnalyzer(correlation_id)
        
        # Solution generation parameters
        self.generation_config = {
            "max_solutions": 5,
            "min_confidence": 0.6,
            "complexity_limit": 8,  # 1-10 scale
            "time_limit_minutes": 60
        }
    
    async def generate_solutions(
        self,
        error_analysis: Dict[str, Any],
        project_id: str,
        project_context: Optional[Dict[str, Any]] = None
    ) -> List[Solution]:
        """
        Generate comprehensive solution recommendations for identified issues
        """
        generation_start = datetime.now(timezone.utc)
        
        try:
            logger.info(
                "solution_generation_started",
                project_id=project_id,
                error_type=error_analysis.get("error_classification", {}).get("primary_type"),
                correlation_id=self.correlation_id
            )
            
            # 1. Gather additional project context
            enhanced_context = await self._gather_project_context(project_id, project_context)
            
            # 2. Generate solution candidates
            solution_candidates = await self._generate_solution_candidates(
                error_analysis=error_analysis,
                project_context=enhanced_context
            )
            
            # 3. Evaluate and rank solutions
            evaluated_solutions = await self._evaluate_solutions(
                candidates=solution_candidates,
                error_analysis=error_analysis,
                project_context=enhanced_context
            )
            
            # 4. Create detailed implementation plans
            detailed_solutions = await self._create_implementation_plans(
                solutions=evaluated_solutions,
                project_id=project_id,
                project_context=enhanced_context
            )
            
            # 5. Filter and rank final solutions
            final_solutions = self._filter_and_rank_solutions(detailed_solutions)
            
            generation_duration = (datetime.now(timezone.utc) - generation_start).total_seconds()
            
            logger.info(
                "solution_generation_completed",
                project_id=project_id,
                solutions_count=len(final_solutions),
                duration_seconds=generation_duration,
                correlation_id=self.correlation_id
            )
            
            return final_solutions
            
        except Exception as e:
            logger.error(
                "solution_generation_failed",
                project_id=project_id,
                error=str(e),
                correlation_id=self.correlation_id
            )
            raise
    
    async def _gather_project_context(
        self, 
        project_id: str, 
        existing_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Gather comprehensive project context for solution generation"""
        context = existing_context or {}
        
        try:
            # Add project metadata
            context.update({
                "project_id": project_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "correlation_id": self.correlation_id
            })
            
            # Get project structure if file manager is available
            if self.file_manager:
                try:
                    project_files = await self._list_project_files(project_id)
                    context["project_structure"] = {
                        "total_files": len(project_files),
                        "file_types": self._analyze_file_types(project_files),
                        "key_files": self._identify_key_files(project_files)
                    }
                except:
                    pass
            
            # Add technology stack detection
            context["technology_stack"] = self._detect_technology_stack(context)
            
        except Exception as e:
            logger.warning(
                "project_context_gathering_partial_failure",
                project_id=project_id,
                error=str(e),
                correlation_id=self.correlation_id
            )
        
        return context
    
    async def _generate_solution_candidates(
        self,
        error_analysis: Dict[str, Any],
        project_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate initial solution candidates using LLM"""
        
        if not self.llm_manager:
            # Fallback to basic solution generation
            return self._generate_basic_solution_candidates(error_analysis)
        
        candidate_prompt = f"""
        Generate comprehensive solution candidates for the following error analysis:

        ERROR ANALYSIS:
        {json.dumps(error_analysis, indent=2)}

        PROJECT CONTEXT:
        {json.dumps(project_context, indent=2)}

        For each solution candidate, provide:

        1. SOLUTION OVERVIEW:
           - Solution type (code_fix, configuration_change, dependency_update, etc.)
           - Brief description
           - Confidence level (0.0-1.0)
           - Implementation complexity (1-10)
           - Estimated time in minutes

        2. TECHNICAL DETAILS:
           - Root cause addressed
           - Files that need modification
           - Key implementation points
           - Potential side effects

        3. APPROACH:
           - Step-by-step approach outline
           - Required tools or frameworks
           - Testing requirements
           - Rollback considerations

        Generate {self.generation_config["max_solutions"]} diverse solution candidates.
        Prioritize solutions that are:
        - Automated and programmatically implementable
        - Low risk with clear rollback paths
        - Well-tested approaches for similar issues
        - Minimal impact on existing functionality

        Return as structured JSON array.
        """
        
        try:
            result = await self.llm_manager.generate_completion(
                prompt=candidate_prompt,
                model="claude-3-opus",
                temperature=0.3,  # Some creativity for solution diversity
                max_tokens=6000,
                metadata={
                    "operation": "solution_candidate_generation",
                    "correlation_id": self.correlation_id
                }
            )
            
            candidates = json.loads(result.content)
            
            if isinstance(candidates, list):
                return candidates
            else:
                return [candidates]
                
        except json.JSONDecodeError as e:
            logger.warning(
                "solution_candidate_parsing_failed",
                error=str(e),
                correlation_id=self.correlation_id
            )
            
            # Return basic solution candidate
            return self._generate_basic_solution_candidates(error_analysis)
    
    def _generate_basic_solution_candidates(self, error_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate basic solution candidates without LLM"""
        error_type = error_analysis.get("error_classification", {}).get("primary_type", "unknown")
        severity = error_analysis.get("error_classification", {}).get("severity", 5)
        
        basic_solutions = []
        
        if error_type == "syntax_error":
            basic_solutions.append({
                "solution_type": SolutionType.CODE_FIX,
                "description": "Fix syntax error in code",
                "confidence": 0.8,
                "implementation_complexity": 3,
                "estimated_time_minutes": 15
            })
        elif error_type == "dependency_issue":
            basic_solutions.append({
                "solution_type": SolutionType.DEPENDENCY_UPDATE,
                "description": "Update or install missing dependencies",
                "confidence": 0.7,
                "implementation_complexity": 4,
                "estimated_time_minutes": 30
            })
        elif error_type == "configuration_error":
            basic_solutions.append({
                "solution_type": SolutionType.CONFIGURATION_CHANGE,
                "description": "Fix configuration settings",
                "confidence": 0.6,
                "implementation_complexity": 5,
                "estimated_time_minutes": 45
            })
        else:
            basic_solutions.append({
                "solution_type": "manual_review",
                "description": "Manual code review and fix required",
                "confidence": 0.3,
                "implementation_complexity": 8,
                "estimated_time_minutes": 120
            })
        
        return basic_solutions
    
    async def _evaluate_solutions(
        self,
        candidates: List[Dict[str, Any]],
        error_analysis: Dict[str, Any],
        project_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Evaluate and score solution candidates"""
        evaluated_solutions = []
        
        for candidate in candidates:
            try:
                # Calculate evaluation score
                score = self._calculate_solution_score(candidate, error_analysis, project_context)
                candidate["evaluation_score"] = score
                
                # Filter by minimum confidence and complexity
                if (candidate.get("confidence", 0) >= self.generation_config["min_confidence"] and
                    candidate.get("implementation_complexity", 10) <= self.generation_config["complexity_limit"]):
                    evaluated_solutions.append(candidate)
                
            except Exception as e:
                logger.warning(
                    "solution_evaluation_failed",
                    candidate_type=candidate.get("solution_type"),
                    error=str(e),
                    correlation_id=self.correlation_id
                )
        
        # Sort by evaluation score
        evaluated_solutions.sort(key=lambda x: x.get("evaluation_score", 0), reverse=True)
        
        return evaluated_solutions
    
    def _calculate_solution_score(
        self,
        candidate: Dict[str, Any],
        error_analysis: Dict[str, Any],
        project_context: Dict[str, Any]
    ) -> float:
        """Calculate evaluation score for a solution candidate"""
        confidence = candidate.get("confidence", 0.5)
        complexity = candidate.get("implementation_complexity", 5)
        time_estimate = candidate.get("estimated_time_minutes", 60)
        
        # Base score from confidence
        score = confidence
        
        # Penalty for high complexity
        complexity_penalty = (complexity - 1) / 9 * 0.3  # Max 0.3 penalty
        score -= complexity_penalty
        
        # Penalty for long implementation time
        time_penalty = min(time_estimate / self.generation_config["time_limit_minutes"], 1) * 0.2
        score -= time_penalty
        
        # Bonus for matching error severity with solution type
        error_severity = error_analysis.get("error_classification", {}).get("severity", 5)
        if error_severity >= 8 and candidate.get("solution_type") in [SolutionType.SECURITY_PATCH, "critical_fix"]:
            score += 0.2
        
        return max(0.0, min(1.0, score))
    
    async def _create_implementation_plans(
        self,
        solutions: List[Dict[str, Any]],
        project_id: str,
        project_context: Dict[str, Any]
    ) -> List[Solution]:
        """Create detailed implementation plans for evaluated solutions"""
        
        detailed_solutions = []
        
        for solution_data in solutions:
            try:
                # Generate detailed implementation plan
                implementation_plan = await self._generate_implementation_plan(
                    solution_data=solution_data,
                    project_id=project_id,
                    project_context=project_context
                )
                
                # Create Solution object
                solution = Solution(
                    solution_id=str(uuid.uuid4()),
                    solution_type=solution_data.get("solution_type", "unknown"),
                    description=solution_data.get("description", ""),
                    confidence=solution_data.get("confidence", 0.5),
                    implementation_complexity=solution_data.get("implementation_complexity", 5),
                    estimated_time_minutes=solution_data.get("estimated_time_minutes", 30),
                    files_to_modify=implementation_plan.get("files_to_modify", []),
                    implementation_steps=implementation_plan.get("implementation_steps", []),
                    rollback_plan=implementation_plan.get("rollback_plan", []),
                    verification_steps=implementation_plan.get("verification_steps", []),
                    risk_assessment=implementation_plan.get("risk_assessment", {})
                )
                
                detailed_solutions.append(solution)
                
            except Exception as e:
                logger.warning(
                    "implementation_plan_creation_failed",
                    solution_type=solution_data.get("solution_type"),
                    error=str(e),
                    correlation_id=self.correlation_id
                )
        
        return detailed_solutions
    
    async def _generate_implementation_plan(
        self,
        solution_data: Dict[str, Any],
        project_id: str,
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed implementation plan for a solution"""
        
        if not self.llm_manager:
            # Return minimal implementation plan
            return {
                "files_to_modify": [],
                "implementation_steps": [
                    {"step": "Manual implementation required", "type": "manual"}
                ],
                "rollback_plan": [
                    {"step": "Restore from backup", "type": "restore"}
                ],
                "verification_steps": ["Manual verification required"],
                "risk_assessment": {"risk_level": "medium", "mitigation": "Manual oversight"}
            }
        
        implementation_prompt = f"""
        Create a detailed, step-by-step implementation plan for the following solution:

        SOLUTION:
        {json.dumps(solution_data, indent=2)}

        PROJECT ID: {project_id}
        PROJECT CONTEXT:
        {json.dumps(project_context, indent=2)}

        Provide a comprehensive implementation plan with:

        1. FILES TO MODIFY:
           - List of specific files that need changes
           - Type of change for each file (modify, create, delete)
           - Backup requirements

        2. IMPLEMENTATION STEPS:
           - Detailed step-by-step instructions
           - Order of operations
           - Code changes with exact file paths
           - Configuration updates
           - Command line operations

        3. ROLLBACK PLAN:
           - Steps to undo changes if implementation fails
           - Backup restoration procedures
           - Verification of rollback success

        4. VERIFICATION STEPS:
           - How to test that the fix works
           - Specific tests to run
           - Success criteria
           - Performance impact checks

        5. RISK ASSESSMENT:
           - Potential risks and mitigation strategies
           - Impact on system stability
           - Dependencies affected
           - User impact assessment

        Make the plan specific enough for autonomous execution by an AI agent.
        Return as structured JSON.
        """
        
        try:
            result = await self.llm_manager.generate_completion(
                prompt=implementation_prompt,
                model="claude-3-sonnet",
                temperature=0.1,  # Low temperature for precise implementation details
                max_tokens=5000,
                metadata={
                    "operation": "implementation_plan_generation",
                    "solution_type": solution_data.get("solution_type"),
                    "correlation_id": self.correlation_id
                }
            )
            
            return json.loads(result.content)
            
        except json.JSONDecodeError as e:
            logger.warning(
                "implementation_plan_parsing_failed",
                error=str(e),
                correlation_id=self.correlation_id
            )
            
            # Return minimal implementation plan
            return {
                "files_to_modify": [],
                "implementation_steps": [
                    {"step": "Manual implementation required", "type": "manual"}
                ],
                "rollback_plan": [
                    {"step": "Restore from backup", "type": "restore"}
                ],
                "verification_steps": ["Manual verification required"],
                "risk_assessment": {"risk_level": "medium", "mitigation": "Manual oversight"}
            }
    
    def _filter_and_rank_solutions(self, solutions: List[Solution]) -> List[Solution]:
        """Filter and rank final solutions"""
        # Filter solutions that meet criteria
        filtered_solutions = [
            solution for solution in solutions
            if (solution.confidence >= self.generation_config["min_confidence"] and
                solution.implementation_complexity <= self.generation_config["complexity_limit"])
        ]
        
        # Sort by confidence and complexity
        filtered_solutions.sort(
            key=lambda s: (s.confidence, -s.implementation_complexity),
            reverse=True
        )
        
        # Return top solutions
        return filtered_solutions[:self.generation_config["max_solutions"]]
    
    async def _list_project_files(self, project_id: str) -> List[str]:
        """List all files in the project"""
        if self.file_manager:
            try:
                return await self.file_manager.list_project_files(project_id)
            except:
                pass
        
        # Fallback: basic file listing
        import os
        project_path = f"./projects/{project_id}"
        if os.path.exists(project_path):
            files = []
            for root, dirs, filenames in os.walk(project_path):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
            return files
        return []
    
    def _analyze_file_types(self, project_files: List[str]) -> Dict[str, int]:
        """Analyze file types in the project"""
        file_types = {}
        for file_path in project_files:
            extension = file_path.split('.')[-1].lower() if '.' in file_path else 'no_extension'
            file_types[extension] = file_types.get(extension, 0) + 1
        return file_types
    
    def _identify_key_files(self, project_files: List[str]) -> List[str]:
        """Identify key files in the project"""
        key_patterns = [
            'main.py', 'app.py', 'server.py', 'index.js', 'package.json',
            'requirements.txt', 'setup.py', 'config.py', 'settings.py',
            'docker-compose.yml', 'Dockerfile', 'README.md'
        ]
        
        key_files = []
        for file_path in project_files:
            filename = file_path.split('/')[-1].split('\\')[-1]  # Get just filename
            if filename in key_patterns:
                key_files.append(file_path)
        
        return key_files
    
    def _detect_technology_stack(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Detect technology stack from project context"""
        stack = {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "deployment": []
        }
        
        file_types = context.get("project_structure", {}).get("file_types", {})
        
        # Detect languages
        if "py" in file_types:
            stack["languages"].append("Python")
        if any(ext in file_types for ext in ["js", "jsx", "ts", "tsx"]):
            stack["languages"].append("JavaScript/TypeScript")
        if "java" in file_types:
            stack["languages"].append("Java")
        if any(ext in file_types for ext in ["cpp", "c", "cc"]):
            stack["languages"].append("C/C++")
        
        # Detect frameworks (simplified detection)
        key_files = context.get("project_structure", {}).get("key_files", [])
        key_files_str = " ".join(key_files).lower()
        
        if "package.json" in key_files_str:
            stack["frameworks"].append("Node.js")
        if "requirements.txt" in key_files_str or "setup.py" in key_files_str:
            stack["frameworks"].append("Python")
        if "dockerfile" in key_files_str:
            stack["deployment"].append("Docker")
        
        return stack
    
    async def generate_fix(self, problem_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate intelligent fixes for code issues using AI-powered analysis
        
        Args:
            problem_context: Dict containing code, error, context information
        """
        fix_id = str(uuid.uuid4())
        
        try:
            logger.info(
                "fix_generation_started",
                fix_id=fix_id,
                error_type=problem_context.get("error", "unknown"),
                correlation_id=self.correlation_id
            )
            
            # Extract problem details
            code = problem_context.get("code", "")
            error_message = problem_context.get("error", "")
            context = problem_context.get("context", "")
            
            if not code and not error_message:
                return {
                    "fix_id": fix_id,
                    "success": False,
                    "error": "Insufficient problem context provided"
                }
            
            # Analyze the error using the error analyzer
            error_analysis = await self.error_analyzer.analyze_error(
                error_message=error_message,
                code_context=code,
                project_context={
                    "additional_context": context
                }
            )
            
            # Generate solution using the existing solution generation pipeline
            solutions = await self.generate_solutions(
                error_analysis=error_analysis,
                project_id=f"fix_session_{fix_id}",
                project_context={
                    "fix_context": True,
                    "original_code": code,
                    "error_message": error_message,
                    "additional_context": context
                }
            )
            
            if not solutions:
                # Fallback to basic fix generation
                fix_result = await self._generate_basic_fix(
                    code=code,
                    error_message=error_message,
                    context=context
                )
            else:
                # Use the best solution to generate the fix
                best_solution = solutions[0]
                fix_result = await self._implement_solution_as_fix(
                    solution=best_solution,
                    original_code=code,
                    error_message=error_message
                )
            
            logger.info(
                "fix_generation_completed",
                fix_id=fix_id,
                confidence=fix_result.get("confidence", 0.0),
                correlation_id=self.correlation_id
            )
            
            return {
                "fix_id": fix_id,
                "success": True,
                "fixed_code": fix_result.get("fixed_code", code),
                "explanation": fix_result.get("explanation", "Fix applied using AI analysis"),
                "confidence": fix_result.get("confidence", 0.7),
                "changes": fix_result.get("changes", []),
                "solution_type": fix_result.get("solution_type", "code_fix"),
                "verification_steps": fix_result.get("verification_steps", []),
                "rollback_instructions": fix_result.get("rollback_instructions", "Restore original code"),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(
                "fix_generation_failed",
                fix_id=fix_id,
                error=str(e),
                correlation_id=self.correlation_id
            )
            return {
                "fix_id": fix_id,
                "success": False,
                "error": str(e),
                "original_code": problem_context.get("code", ""),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def _generate_basic_fix(
        self, code: str, error_message: str, context: str
    ) -> Dict[str, Any]:
        """Generate basic fix without complex AI analysis"""
        
        # Analyze error type for basic patterns
        error_lower = error_message.lower()
        
        if "syntaxerror" in error_lower or "invalid syntax" in error_lower:
            return await self._fix_syntax_error(code, error_message)
        elif "nameerror" in error_lower or "not defined" in error_lower:
            return await self._fix_name_error(code, error_message)
        elif "importerror" in error_lower or "modulenotfounderror" in error_lower:
            return await self._fix_import_error(code, error_message)
        elif "indentationerror" in error_lower:
            return await self._fix_indentation_error(code, error_message)
        elif "typeerror" in error_lower:
            return await self._fix_type_error(code, error_message)
        else:
            return await self._generate_generic_fix(code, error_message, context)
    
    async def _fix_syntax_error(self, code: str, error_message: str) -> Dict[str, Any]:
        """Fix common syntax errors"""
        fixed_code = code
        changes = []
        
        # Fix missing colons
        if "invalid syntax" in error_message and ":" not in code.split('\n')[-1]:
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if any(keyword in line for keyword in ["if ", "elif ", "else", "for ", "while ", "def ", "class ", "try", "except", "finally"]):
                    if not line.strip().endswith(':'):
                        lines[i] = line.rstrip() + ':'
                        changes.append(f"Added missing colon at line {i+1}")
            fixed_code = '\n'.join(lines)
        
        # Fix mismatched parentheses/brackets
        elif "unexpected EOF" in error_message or "closing parenthesis" in error_message:
            open_parens = code.count('(')
            close_parens = code.count(')')
            if open_parens > close_parens:
                fixed_code = code + ')' * (open_parens - close_parens)
                changes.append(f"Added {open_parens - close_parens} missing closing parentheses")
        
        return {
            "fixed_code": fixed_code,
            "confidence": 0.8,
            "explanation": "Fixed syntax error by correcting common syntax issues",
            "changes": changes,
            "solution_type": SolutionType.CODE_FIX,
            "verification_steps": ["Run python -m py_compile to verify syntax"]
        }
    
    async def _fix_name_error(self, code: str, error_message: str) -> Dict[str, Any]:
        """Fix name/variable not defined errors"""
        fixed_code = code
        changes = []
        
        # Extract variable name from error message
        import re
        match = re.search(r"name '(\w+)' is not defined", error_message)
        if match:
            var_name = match.group(1)
            
            # Common fixes for undefined variables
            if var_name in ["pd", "pandas"]:
                fixed_code = "import pandas as pd\n" + code
                changes.append("Added pandas import")
            elif var_name in ["np", "numpy"]:
                fixed_code = "import numpy as np\n" + code
                changes.append("Added numpy import")
            elif var_name in ["os"]:
                fixed_code = "import os\n" + code
                changes.append("Added os import")
            elif var_name in ["sys"]:
                fixed_code = "import sys\n" + code
                changes.append("Added sys import")
            else:
                # Initialize undefined variable with None
                lines = code.split('\n')
                first_use_line = next((i for i, line in enumerate(lines) if var_name in line), 0)
                lines.insert(first_use_line, f"{var_name} = None  # Auto-initialized")
                fixed_code = '\n'.join(lines)
                changes.append(f"Initialized undefined variable '{var_name}' with None")
        
        return {
            "fixed_code": fixed_code,
            "confidence": 0.7,
            "explanation": f"Fixed NameError by addressing undefined variable",
            "changes": changes,
            "solution_type": SolutionType.CODE_FIX,
            "verification_steps": ["Check if the variable is properly initialized before use"]
        }
    
    async def _fix_import_error(self, code: str, error_message: str) -> Dict[str, Any]:
        """Fix import-related errors"""
        fixed_code = code
        changes = []
        
        # Extract module name from error message
        import re
        match = re.search(r"No module named '(\w+)'", error_message)
        if match:
            module_name = match.group(1)
            
            # Suggest installation command
            install_command = f"pip install {module_name}"
            changes.append(f"Module '{module_name}' needs to be installed: {install_command}")
            
            # Try common alternative import patterns
            if module_name == "cv2":
                changes.append("Alternative: pip install opencv-python")
            elif module_name == "sklearn":
                fixed_code = code.replace("import sklearn", "import scikit-learn")
                changes.append("Corrected sklearn import to use scikit-learn")
        
        return {
            "fixed_code": fixed_code,
            "confidence": 0.6,
            "explanation": "Fixed ImportError by identifying missing module",
            "changes": changes,
            "solution_type": SolutionType.DEPENDENCY_UPDATE,
            "verification_steps": [
                "Install the missing module using pip",
                "Verify the import works after installation"
            ]
        }
    
    async def _fix_indentation_error(self, code: str, error_message: str) -> Dict[str, Any]:
        """Fix indentation errors"""
        lines = code.split('\n')
        fixed_lines = []
        changes = []
        
        # Standardize indentation to 4 spaces
        for i, line in enumerate(lines):
            if line.strip():  # Skip empty lines
                # Count leading whitespace
                leading_spaces = len(line) - len(line.lstrip())
                
                # Convert tabs to spaces
                if '\t' in line:
                    line = line.replace('\t', '    ')
                    changes.append(f"Converted tabs to spaces at line {i+1}")
                
                # Fix inconsistent indentation
                if leading_spaces % 4 != 0 and leading_spaces > 0:
                    correct_indent = (leading_spaces // 4) * 4
                    line = ' ' * correct_indent + line.lstrip()
                    changes.append(f"Fixed indentation at line {i+1}")
            
            fixed_lines.append(line)
        
        return {
            "fixed_code": '\n'.join(fixed_lines),
            "confidence": 0.9,
            "explanation": "Fixed indentation errors by standardizing to 4-space indentation",
            "changes": changes,
            "solution_type": SolutionType.CODE_FIX,
            "verification_steps": ["Check Python syntax with proper indentation"]
        }
    
    async def _fix_type_error(self, code: str, error_message: str) -> Dict[str, Any]:
        """Fix type-related errors"""
        fixed_code = code
        changes = []
        
        # Common type error patterns
        if "can't multiply sequence by non-int" in error_message:
            changes.append("Type error suggests multiplying string by non-integer")
            changes.append("Consider converting to int() or float() if numeric operation intended")
        elif "unsupported operand type" in error_message:
            changes.append("Type mismatch in operation - check operand types")
            changes.append("Consider type conversion or validation before operation")
        elif "list indices must be integers" in error_message:
            changes.append("Using non-integer as list index")
            changes.append("Convert index to int() or check index type")
        
        # Generic type checking addition
        lines = code.split('\n')
        # Add basic type checking where appropriate
        for i, line in enumerate(lines):
            if "=" in line and not line.strip().startswith("#"):
                var_name = line.split('=')[0].strip()
                if any(op in line for op in ['+', '-', '*', '/']):
                    check_line = f"    # Type check: ensure {var_name} is numeric"
                    lines.insert(i, check_line)
                    changes.append(f"Added type checking suggestion for {var_name}")
                    break
        
        fixed_code = '\n'.join(lines)
        
        return {
            "fixed_code": fixed_code,
            "confidence": 0.5,
            "explanation": "Added type checking guidance for TypeError",
            "changes": changes,
            "solution_type": SolutionType.CODE_FIX,
            "verification_steps": [
                "Add explicit type checking before operations",
                "Use isinstance() to verify types",
                "Consider type hints for better code clarity"
            ]
        }
    
    async def _generate_generic_fix(
        self, code: str, error_message: str, context: str
    ) -> Dict[str, Any]:
        """Generate generic fix when specific patterns don't match"""
        
        changes = [
            "Generic error detected - manual review recommended",
            f"Error message: {error_message[:100]}...",
            "Consider debugging with print statements or debugger"
        ]
        
        # Add debugging helper
        debug_code = f"""
# Auto-generated debugging helper
print("DEBUG: Error occurred - {error_message[:50]}...")
print("DEBUG: Check variables and flow at this point")

{code}
"""
        
        return {
            "fixed_code": debug_code,
            "confidence": 0.3,
            "explanation": "Added debugging assistance for manual error resolution",
            "changes": changes,
            "solution_type": "manual_review",
            "verification_steps": [
                "Review error message carefully",
                "Use debugging tools or print statements",
                "Check variable types and values",
                "Verify logic flow and conditions"
            ]
        }
    
    async def _implement_solution_as_fix(
        self, solution: Solution, original_code: str, error_message: str
    ) -> Dict[str, Any]:
        """Implement a Solution object as a code fix"""
        
        if not self.llm_manager:
            # Fallback to basic implementation
            return {
                "fixed_code": original_code,
                "confidence": solution.confidence,
                "explanation": solution.description,
                "changes": ["Solution generated but LLM not available for implementation"],
                "solution_type": solution.solution_type,
                "verification_steps": solution.verification_steps
            }
        
        implementation_prompt = f"""
        Implement the following solution to fix the code error:

        ORIGINAL CODE:
        ```
        {original_code}
        ```

        ERROR MESSAGE:
        {error_message}

        SOLUTION TO IMPLEMENT:
        {solution.description}

        IMPLEMENTATION STEPS:
        {json.dumps(solution.implementation_steps, indent=2)}

        Please provide:
        1. The fixed code with the solution applied
        2. Explanation of what was changed
        3. List of specific changes made
        4. Confidence level in the fix (0.0-1.0)

        Return as JSON with fields: fixed_code, explanation, changes, confidence
        """
        
        try:
            result = await self.llm_manager.generate_completion(
                prompt=implementation_prompt,
                model="claude-3-sonnet",
                temperature=0.1,
                max_tokens=3000,
                metadata={
                    "operation": "solution_implementation",
                    "solution_type": solution.solution_type,
                    "correlation_id": self.correlation_id
                }
            )
            
            implementation_result = json.loads(result.content)
            
            return {
                "fixed_code": implementation_result.get("fixed_code", original_code),
                "confidence": min(solution.confidence, implementation_result.get("confidence", 0.7)),
                "explanation": implementation_result.get("explanation", solution.description),
                "changes": implementation_result.get("changes", []),
                "solution_type": solution.solution_type,
                "verification_steps": solution.verification_steps,
                "rollback_instructions": f"Restore original code to revert changes"
            }
            
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(
                "solution_implementation_failed",
                error=str(e),
                solution_id=solution.solution_id,
                correlation_id=self.correlation_id
            )
            
            # Fallback implementation
            return {
                "fixed_code": original_code,
                "confidence": solution.confidence * 0.5,  # Reduce confidence due to implementation failure
                "explanation": f"Solution identified but implementation failed: {solution.description}",
                "changes": ["Automatic implementation failed - manual review required"],
                "solution_type": solution.solution_type,
                "verification_steps": solution.verification_steps
            }

    def get_generation_stats(self) -> Dict[str, Any]:
        """Get solution generation statistics"""
        return {
            "generation_config": self.generation_config,
            "available_solution_types": [
                SolutionType.CODE_FIX,
                SolutionType.CONFIGURATION_CHANGE,
                SolutionType.DEPENDENCY_UPDATE,
                SolutionType.ARCHITECTURAL_CHANGE,
                SolutionType.SECURITY_PATCH,
                SolutionType.PERFORMANCE_OPTIMIZATION
            ],
            "correlation_id": self.correlation_id,
            "fix_generation_enabled": True,
            "supported_error_types": [
                "SyntaxError",
                "NameError", 
                "ImportError",
                "IndentationError",
                "TypeError",
                "Generic errors"
            ]
        }