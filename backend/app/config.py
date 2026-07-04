import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    🔒 Enterprise Operations Configuration Registry
    Handles runtime validation of database strings, Groq AI infrastructure,
    cryptographic secrets, Firebase buckets, and cross-origin resource permissions.
    """
    PROJECT_NAME: str = "Amity University Helpdesk Core API Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"  # Matches the multi-prefix target routing layout safely

    # 🗃️ Relational Database Connection Matrix
    # Overridden automatically by your local .env configuration parameters
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/amity_helpdesk",
        validation_alias="DATABASE_URL"
    )

    # 🧠 Groq LLaMA 3.3 70B AI Integration Pipeline
    GROQ_API_KEY: str = Field(
        default="YOUR_GROQ_API_KEY_PLACEHOLDER",
        validation_alias="GROQ_API_KEY"
    )
    LLM_MODEL: str = "llama3-70b-8192"  # Standard high-capacity token execution target

    # 📁 Firebase Admin Cloud Storage Bucket Configuration Registry
    # 🟢 FIXED: Updated hardcoded fallback string default value to match your verified console signature (.appspot.com)
    FIREBASE_STORAGE_BUCKET: str = Field(
        default="amity-campus-helpdesk.appspot.com",
        validation_alias="FIREBASE_STORAGE_BUCKET"
    )

    # 🔐 System Access Control Security Parameters
    SECRET_KEY: str = Field(
        default="AMITY_COMPLEX_CAMPUS_SECURE_HASHING_TOKEN_CORE_KEY_2026",
        validation_alias="SECRET_KEY"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # Session active for exactly 7 days

    # 🌐 Cross-Origin Resource Sharing (CORS) Security Domains
    CORS_ORIGINS: list[str] = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",  # Vite default execution ports
    ]

    # 📁 Reads settings from an isolated local environment mapping file (.env)
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

# Instantiated settings context molecule initialized for immediate dependency injection
settings = Settings()