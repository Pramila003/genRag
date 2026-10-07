# apps/chatbot_service/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    LLM_MODEL: str = "openai/gpt-oss-120b"
    LLM_TEMPERATURE: float = 0.0
    ITSM_API_BASE_URL: str = "http://localhost:8000/api/v1"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()