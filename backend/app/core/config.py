from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    BACKEND_URL: str = "https://constructure-ai-backend.onrender.com"
    FRONTEND_URL: str = "https://constructure-ai-assistant.vercel.app"
    ENVIRONMENT: str = "production"
    
    # Google OAuth2
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days
    
    # AI Provider
    AI_PROVIDER: str = "anthropic"  # anthropic or openai
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
