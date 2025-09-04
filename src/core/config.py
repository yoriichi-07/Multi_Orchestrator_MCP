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


# Global settings instance
settings = Settings()
