"""
Configuration management for the MCP server
"""
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Server configuration
    server_host: str = Field(default="0.0.0.0", description="Server host")
    server_port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Enhanced Descope Authentication
    descope_project_id: str = Field(default="test_project", description="Descope project ID")
    descope_management_key: Optional[str] = Field(None, description="Descope management key for dynamic client registration")
    descope_client_id: Optional[str] = Field(None, description="Descope client ID for machine-to-machine authentication")
    descope_client_secret: Optional[str] = Field(None, description="Descope client secret for machine-to-machine authentication")
    descope_demo_mode: bool = Field(default=True, description="Enable demo mode for authentication (for development/testing)")
    
    # JWT Configuration
    jwt_algorithm: str = Field(default="RS256", description="JWT algorithm for token validation")
    jwt_verify_expiration: bool = Field(default=True, description="Verify JWT token expiration")
    jwt_require_claims: List[str] = Field(default=["exp", "iat", "sub", "aud"], description="Required JWT claims")
    
    # Security Settings
    token_cache_ttl: int = Field(default=3600, description="Token cache TTL in seconds")
    max_token_age_hours: int = Field(default=24, description="Maximum token age in hours")
    enable_token_refresh: bool = Field(default=True, description="Enable automatic token refresh")
    
    # Authentication Middleware
    auth_exclude_paths: List[str] = Field(
        default=["/health", "/docs", "/openapi.json", "/favicon.ico"],
        description="Paths excluded from authentication"
    )
    
    # LLM Configuration
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(None, description="Anthropic API key")
    default_llm_provider: str = Field(default="openai", description="Default LLM provider")
    
    # File management
    output_base_path: str = Field(default="./outputs", description="Base path for outputs")
    max_project_size_mb: int = Field(default=100, description="Maximum project size in MB")
    
    # Security
    allowed_file_extensions: List[str] = Field(
        default=[".py", ".js", ".ts", ".html", ".css", ".json", ".md", ".yml", ".yaml"],
        description="Allowed file extensions for generation"
    )
    max_generation_time_seconds: int = Field(default=300, description="Max time for generation")
    
    # Cequence AI Gateway Integration
    cequence_gateway_id: Optional[str] = Field(None, description="Cequence Gateway ID")
    cequence_api_key: Optional[str] = Field(None, description="Cequence API Key")
    cequence_gateway_url: Optional[str] = Field(None, description="Cequence Gateway URL")
    
    # Analytics Configuration
    enable_analytics: bool = Field(default=True, description="Enable analytics collection")
    analytics_buffer_size: int = Field(default=100, description="Analytics buffer size")
    analytics_flush_interval: int = Field(default=60, description="Analytics flush interval (seconds)")
    
    # Security Monitoring
    enable_security_monitoring: bool = Field(default=True, description="Enable security monitoring")
    max_request_size_mb: int = Field(default=10, description="Maximum request size in MB")
    rate_limit_per_minute: int = Field(default=100, description="Rate limit per minute per user")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # =============== LEGENDARY FEATURES CONFIGURATION ===============
    
    # Legendary Features Master Control
    legendary_feature_flag: bool = Field(default=True, description="Master switch for all legendary features")
    legendary_mode: str = Field(default="autonomous", description="Legendary mode: autonomous, assisted, or disabled")
    
    # Autonomous Architect Agent Configuration
    autonomous_architect_enabled: bool = Field(default=True, description="Enable Autonomous Architect Agent")
    autonomous_learning_enabled: bool = Field(default=True, description="Enable autonomous learning capabilities")
    autonomous_dag_max_depth: int = Field(default=10, description="Maximum DAG execution depth")
    autonomous_adaptation_threshold: float = Field(default=0.7, description="Threshold for autonomous adaptations")
    autonomous_strategy_cache_ttl: int = Field(default=3600, description="Strategy cache TTL in seconds")
    
    # Proactive Quality Agent Configuration  
    proactive_quality_enabled: bool = Field(default=True, description="Enable Proactive Quality Agent")
    quality_auto_remediation: bool = Field(default=True, description="Enable automatic quality remediation")
    quality_policy_enforcement: bool = Field(default=True, description="Enable policy-as-code enforcement")
    quality_threshold_score: float = Field(default=0.8, description="Minimum quality score threshold")
    quality_violation_auto_fix: bool = Field(default=True, description="Auto-fix quality violations")
    quality_learning_enabled: bool = Field(default=True, description="Enable quality learning from feedback")
    
    # Evolutionary Prompt Engine Configuration
    evolutionary_prompt_enabled: bool = Field(default=True, description="Enable Evolutionary Prompt Engine")
    prompt_evolution_enabled: bool = Field(default=True, description="Enable prompt self-evolution")
    prompt_performance_tracking: bool = Field(default=True, description="Track prompt performance metrics")
    prompt_optimization_iterations: int = Field(default=5, description="Maximum prompt optimization iterations")
    prompt_success_threshold: float = Field(default=0.85, description="Success threshold for prompt evolution")
    prompt_learning_rate: float = Field(default=0.1, description="Learning rate for prompt evolution")
    
    # Last Mile Cloud Agent Configuration
    last_mile_cloud_enabled: bool = Field(default=True, description="Enable Last Mile Cloud Agent")
    cloud_auto_deployment: bool = Field(default=False, description="Enable automatic deployment (USE WITH CAUTION)")
    cloud_verification_enabled: bool = Field(default=True, description="Enable deployment verification")
    cloud_rollback_enabled: bool = Field(default=True, description="Enable automatic rollback")
    cloud_monitoring_setup: bool = Field(default=True, description="Setup monitoring during deployment")
    cloud_optimization_enabled: bool = Field(default=True, description="Enable cloud resource optimization")
    
    # Revolutionary AI Capabilities
    self_improving_ai: bool = Field(default=True, description="Enable self-improving AI capabilities")
    predictive_automation: bool = Field(default=True, description="Enable predictive automation")
    autonomous_decision_making: bool = Field(default=False, description="Enable autonomous decision making (EXPERIMENTAL)")
    continuous_learning: bool = Field(default=True, description="Enable continuous learning across all agents")
    
    # Enhanced Analytics for Legendary Features
    legendary_analytics_enabled: bool = Field(default=True, description="Enable detailed analytics for legendary features")
    innovation_scoring_enabled: bool = Field(default=True, description="Enable innovation scoring")
    performance_benchmarking: bool = Field(default=True, description="Enable performance benchmarking")
    learning_metrics_tracking: bool = Field(default=True, description="Track learning and improvement metrics")
    
    # Security Settings for Legendary Features
    legendary_security_mode: str = Field(default="enhanced", description="Security mode for legendary features: basic, enhanced, paranoid")
    require_legendary_scopes: bool = Field(default=True, description="Require specific scopes for legendary tools")
    legendary_audit_logging: bool = Field(default=True, description="Enable comprehensive audit logging for legendary operations")
    
    # Performance Tuning
    legendary_max_concurrent_operations: int = Field(default=3, description="Maximum concurrent legendary operations")
    legendary_timeout_seconds: int = Field(default=600, description="Timeout for legendary operations")
    legendary_memory_limit_mb: int = Field(default=2048, description="Memory limit for legendary operations")
    
    # Integration Settings
    cequence_secret: Optional[str] = Field(None, description="Cequence secret for enhanced integration")
    descope_legendary_scopes: List[str] = Field(
        default=[
            "tools:legendary",
            "tools:autonomous", 
            "tools:evolutionary",
            "tools:proactive",
            "tools:cloud",
            "admin:legendary"
        ],
        description="Required Descope scopes for legendary features"
    )
    
    # Development and Testing
    legendary_dev_mode: bool = Field(default=False, description="Enable legendary development mode")
    legendary_testing_enabled: bool = Field(default=True, description="Enable legendary testing capabilities")
    legendary_mock_mode: bool = Field(default=False, description="Use mock implementations for testing")
    
    # Future Features (Experimental)
    quantum_ai_enabled: bool = Field(default=False, description="Enable quantum AI capabilities (EXPERIMENTAL)")
    neural_evolution_enabled: bool = Field(default=False, description="Enable neural evolution (EXPERIMENTAL)")
    swarm_intelligence_enabled: bool = Field(default=False, description="Enable swarm intelligence (EXPERIMENTAL)")


# Global settings instance
settings = Settings()
