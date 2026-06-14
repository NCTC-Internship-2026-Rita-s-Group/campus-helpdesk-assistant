import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "AI-Powered Campus Helpdesk & Notice Assistant"
    
    # Database Settings
    DATABASE_URL: str
    
    # Security Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    
    # AI Vendor Credentials (Claude)
    # The default value allows the system to boot even before the API key is active
    ANTHROPIC_API_KEY: str = "mock-key" 

    # Configuration to read the root-level .env file
    # We navigate up two directories from backend/app/ to find the root folder
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate settings to be imported across your application modules
settings = Settings()