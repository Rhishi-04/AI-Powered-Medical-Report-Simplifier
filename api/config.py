"""
Application configuration settings.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Ollama Configuration
    OLLAMA_URL: str = "http://localhost:11434"
    LLM_MODEL_NAME: str = "llama3.2:latest"
    LLM_MAX_TOKENS: int = 2048
    LLM_TEMPERATURE: float = 0.1
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    
    # Processing Configuration
    OCR_CONFIDENCE_THRESHOLD: float = 0.6
    VALIDATION_CONFIDENCE_THRESHOLD: float = 0.7
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    
    # LLM Timeout Configuration
    LLM_TIMEOUT: int = 300  # 5 minutes for large reports
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
