"""
Configuration management for the CLI tool.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv


class Config(BaseModel):
    """Configuration model for the CLI tool."""
    
    # Application settings
    app_name: str = Field(default="CLI Tool", description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    # Output settings
    output_format: str = Field(default="text", description="Output format")
    color_output: bool = Field(default=True, description="Enable colored output")
    
    # Custom settings
    settings: Dict[str, Any] = Field(default_factory=dict, description="Custom settings")
    
    @classmethod
    def from_file(cls, config_path: str) -> "Config":
        """Load configuration from a file."""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        # Load environment variables from .env file if it exists
        env_file = config_file.parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        
        # For now, return default config
        # In a real application, you would parse the config file
        return cls()
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            app_name=os.getenv("APP_NAME", "CLI Tool"),
            version=os.getenv("APP_VERSION", "1.0.0"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE"),
            output_format=os.getenv("OUTPUT_FORMAT", "text"),
            color_output=os.getenv("COLOR_OUTPUT", "true").lower() == "true",
        )
    
    def save(self, config_path: str) -> None:
        """Save configuration to a file."""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # In a real application, you would serialize the config
        # For now, this is a placeholder
        pass 