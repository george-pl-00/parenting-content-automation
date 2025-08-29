import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App settings
    app_name: str = "Magical Parenting Content Automation"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/parenting_automation"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # API Keys
    openai_api_key: Optional[str] = None
    instagram_access_token: Optional[str] = None
    midjourney_api_key: Optional[str] = None
    
    # Instagram API
    instagram_business_account_id: Optional[str] = None
    instagram_api_version: str = "v18.0"
    
    # Content Generation
    max_daily_posts: int = 3
    content_generation_interval: int = 12  # hours
    carousel_slide_count: int = 5
    
    # AI Settings
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 1500
    
    # Rate Limiting
    openai_rate_limit: int = 60  # requests per minute
    instagram_rate_limit: int = 200  # requests per hour
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "production":
    settings.debug = False
elif os.getenv("ENVIRONMENT") == "staging":
    settings.debug = True
else:
    settings.debug = True
