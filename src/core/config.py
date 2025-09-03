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
    
    # Authentication
    descope_project_id: str = Field(default="test_project", description="Descope project ID")
    descope_management_key: Optional[str] = Field(None, description="Descope management key")
    
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
    
    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    log_level: str = Field(default="INFO", description="Logging level")


# Global settings instance
settings = Settings()
