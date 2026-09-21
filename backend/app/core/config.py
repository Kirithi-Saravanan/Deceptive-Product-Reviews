from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

_backend_dir = Path(__file__).resolve().parent.parent.parent
_root_dir = _backend_dir.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "ReviewGuard AI API"
    API_V1_STR: str = "/api"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/reviewguard"
    
    # Auth
    JWT_SECRET_KEY: str = "change_this_to_a_secure_random_string_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    model_config = SettingsConfigDict(
        env_file=[str(_backend_dir / ".env"), str(_root_dir / ".env"), ".env"],
        env_ignore_empty=True,
        extra="ignore"
    )

settings = Settings()
