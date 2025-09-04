"""
Frontend agent specialized for React/Vue/Angular UI development
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from src.agents.base_agent import BaseAgent


class FrontendAgent(BaseAgent):
    """Specialized agent for frontend development"""
    
    def __init__(self, correlation_id: Optional[str] = None):
        super().__init__(agent_type="frontend", correlation_id=correlation_id)
    
    def _get_model_preferences(self) -> Dict[str, str]:
        """Frontend-optimized model preferences"""
        return {
            "code_generation": "claude-3-sonnet",  # Good for UI/UX reasoning
            "component_design": "gpt-4",           # Excellent for component architecture
            "styling": "claude-3-haiku",           # Fast for CSS/styling tasks
            "optimization": "claude-3-sonnet"      # Good for performance optimization
        }
    
    def _initialize_prompt_templates(self) -> Dict[str, str]:
        """Initialize frontend-specific prompt templates"""
        return {
            "component": """
You are an expert React/Frontend developer. Create reusable, accessible, and performant components.

Focus on:
- Modern React patterns (hooks, functional components)
- TypeScript for type safety
- Responsive design principles
- Accessibility (ARIA labels, semantic HTML)
- Performance optimization
- Clean, maintainable code structure
            """,
            
            "page": """
You are an expert Frontend developer creating full page layouts.

Focus on:
- Complete page structure with routing
- State management (Redux/Zustand/Context)
- Data fetching and error handling
- Loading states and user feedback
- Mobile-first responsive design
- SEO optimization
            """,
            
            "styling": """
You are an expert CSS/Styling developer.

Focus on:
- Modern CSS (Grid, Flexbox, Custom Properties)
- Responsive design with mobile-first approach
- Design system consistency
- Performance (minimal CSS, efficient selectors)
- Browser compatibility
- Accessibility in styling
            """,
            
            "integration": """
You are an expert Frontend developer integrating with APIs.

Focus on:
- Async data fetching with proper error handling
- State management for API data
- Loading and error states
- Caching strategies
- Authentication integration
- Real-time updates (WebSockets/SSE)
            """,
            
            "default": """
You are an expert Frontend developer with deep knowledge of modern web technologies.
Create high-quality, maintainable, and performant frontend code.
            """
        }
    
    def _get_agent_capabilities(self) -> List[str]:
        """Frontend agent capabilities"""
        return [
            "React/Vue/Angular component development",
            "Responsive UI design and implementation",
            "State management (Redux, Zustand, Context)",
            "API integration and data fetching",
            "CSS/SCSS/Styled Components",
            "TypeScript implementation",
            "Performance optimization",
            "Accessibility (WCAG) compliance",
            "Testing (Jest, React Testing Library)",
            "Build optimization (Webpack, Vite)"
        ]
    
    async def create_component(
        self,
        component_name: str,
        requirements: str,
        props_schema: Optional[Dict[str, Any]] = None,
        styling_framework: str = "css-modules"
    ) -> Dict[str, Any]:
        """
        Create a reusable React component
        """
        self.logger.info(
            "creating_component",
            component_name=component_name,
            styling_framework=styling_framework
        )
        
        context = {
            "component_name": component_name,
            "props_schema": props_schema,
            "styling_framework": styling_framework,
            "requirements": requirements
        }
        
        prompt = f"""
Create a React component named {component_name}.

Requirements: {requirements}

Props Schema: {props_schema if props_schema else "Define appropriate props based on requirements"}

Styling Framework: {styling_framework}

Generate:
1. TypeScript React component with proper typing
2. Corresponding stylesheet ({styling_framework})
3. Unit tests using React Testing Library
4. Storybook story for component showcase
"""
        
        result = await self.generate_code(
            prompt=prompt,
            context=context,
            code_type="component"
        )
        
        # Add component-specific metadata
        if result.get("success"):
            result["component_metadata"] = {
                "name": component_name,
                "type": "functional_component",
                "styling_framework": styling_framework,
                "has_props": props_schema is not None,
                "files_generated": [
                    f"{component_name}.tsx",
                    f"{component_name}.module.css",
                    f"{component_name}.test.tsx",
                    f"{component_name}.stories.tsx"
                ]
            }
        
        return result
    
    async def create_page(
        self,
        page_name: str,
        route_path: str,
        requirements: str,
        layout_type: str = "standard"
    ) -> Dict[str, Any]:
        """
        Create a complete page with routing and layout
        """
        self.logger.info(
            "creating_page",
            page_name=page_name,
            route_path=route_path,
            layout_type=layout_type
        )
        
        context = {
            "page_name": page_name,
            "route_path": route_path,
            "layout_type": layout_type,
            "requirements": requirements
        }
        
        prompt = f"""
Create a complete page component named {page_name}.

Route Path: {route_path}
Layout Type: {layout_type}
Requirements: {requirements}

Generate:
1. Page component with proper routing setup
2. State management for page data
3. API integration for data fetching
4. Loading and error states
5. Responsive layout implementation
6. SEO meta tags and optimization
"""
        
        result = await self.generate_code(
            prompt=prompt,
            context=context,
            code_type="page"
        )
        
        # Add page-specific metadata
        if result.get("success"):
            result["page_metadata"] = {
                "name": page_name,
                "route": route_path,
                "layout": layout_type,
                "has_routing": True,
                "has_state_management": True,
                "files_generated": [
                    f"{page_name}Page.tsx",
                    f"{page_name}Page.module.css",
                    f"use{page_name}.ts",  # Custom hook
                    f"{page_name}Page.test.tsx"
                ]
            }
        
        return result
    
    async def integrate_api(
        self,
        api_endpoints: List[Dict[str, Any]],
        authentication_type: str = "jwt",
        state_management: str = "context"
    ) -> Dict[str, Any]:
        """
        Create API integration layer for frontend
        """
        self.logger.info(
            "integrating_api",
            endpoints_count=len(api_endpoints),
            auth_type=authentication_type,
            state_mgmt=state_management
        )
        
        context = {
            "api_endpoints": api_endpoints,
            "authentication_type": authentication_type,
            "state_management": state_management
        }
        
        prompt = f"""
Create API integration layer for frontend application.

API Endpoints: {api_endpoints}
Authentication: {authentication_type}
State Management: {state_management}

Generate:
1. API client with proper error handling
2. Authentication service
3. State management setup ({state_management})
4. Custom hooks for API calls
5. Type definitions for API responses
6. Error boundary components
"""
        
        result = await self.generate_code(
            prompt=prompt,
            context=context,
            code_type="integration"
        )
        
        # Add integration-specific metadata
        if result.get("success"):
            result["integration_metadata"] = {
                "endpoints_count": len(api_endpoints),
                "authentication": authentication_type,
                "state_management": state_management,
                "files_generated": [
                    "api/client.ts",
                    "api/auth.ts",
                    "hooks/useApi.ts",
                    "types/api.ts",
                    "components/ErrorBoundary.tsx"
                ]
            }
        
        return result
    
    async def optimize_performance(
        self,
        project_id: str,
        optimization_targets: List[str]
    ) -> Dict[str, Any]:
        """
        Optimize frontend performance
        """
        self.logger.info(
            "optimizing_performance",
            project_id=project_id,
            targets=optimization_targets
        )
        
        # Simulate performance analysis
        await asyncio.sleep(2)
        
        optimizations = []
        
        for target in optimization_targets:
            if target == "bundle_size":
                optimizations.append({
                    "type": "bundle_optimization",
                    "actions": [
                        "Code splitting implementation",
                        "Tree shaking configuration",
                        "Dynamic imports for routes",
                        "Bundle analyzer setup"
                    ],
                    "expected_improvement": "25-40% bundle size reduction"
                })
            elif target == "render_performance":
                optimizations.append({
                    "type": "render_optimization",
                    "actions": [
                        "React.memo implementation",
                        "useMemo and useCallback optimization",
                        "Virtual scrolling for large lists",
                        "Lazy loading for images"
                    ],
                    "expected_improvement": "30-50% faster renders"
                })
            elif target == "loading_speed":
                optimizations.append({
                    "type": "loading_optimization",
                    "actions": [
                        "Service worker caching",
                        "Resource preloading",
                        "Image optimization",
                        "CDN integration"
                    ],
                    "expected_improvement": "40-60% faster page loads"
                })
        
        return {
            "project_id": project_id,
            "optimization_plan": optimizations,
            "total_optimizations": len(optimizations),
            "estimated_performance_gain": "35-55% overall improvement",
            "implementation_time": "2-4 hours",
            "priority_order": [opt["type"] for opt in optimizations]
        }
    
    async def audit_accessibility(
        self,
        project_id: str,
        components: List[str]
    ) -> Dict[str, Any]:
        """
        Audit accessibility compliance
        """
        self.logger.info(
            "auditing_accessibility",
            project_id=project_id,
            components_count=len(components)
        )
        
        # Simulate accessibility audit
        await asyncio.sleep(1.5)
        
        audit_results = []
        
        for component in components:
            # Simulate component audit
            issues_found = []
            score = 85  # Mock score
            
            # Common accessibility issues simulation
            if "button" in component.lower():
                issues_found.append({
                    "severity": "medium",
                    "issue": "Missing aria-label for icon button",
                    "solution": "Add descriptive aria-label attribute"
                })
            
            if "form" in component.lower():
                issues_found.append({
                    "severity": "high",
                    "issue": "Form inputs missing labels",
                    "solution": "Associate labels with form controls"
                })
            
            audit_results.append({
                "component": component,
                "accessibility_score": score,
                "issues": issues_found,
                "wcag_compliance": "AA" if score > 80 else "Partial",
                "recommendations": [
                    "Add ARIA landmarks",
                    "Improve keyboard navigation",
                    "Enhance color contrast"
                ]
            })
        
        overall_score = sum(result["accessibility_score"] for result in audit_results) / len(audit_results)
        
        return {
            "project_id": project_id,
            "overall_accessibility_score": overall_score,
            "wcag_compliance_level": "AA" if overall_score > 80 else "Partial",
            "component_audits": audit_results,
            "total_issues": sum(len(result["issues"]) for result in audit_results),
            "priority_fixes": [
                issue for result in audit_results 
                for issue in result["issues"] 
                if issue["severity"] == "high"
            ]
        }