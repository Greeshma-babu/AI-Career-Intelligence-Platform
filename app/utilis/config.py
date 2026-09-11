from pydantic_settings import BaseSettings
class Settings(BaseSettings):
 DATABASE_URL: str = "postgresql://user:password@localhost/talentpulse"
 NEWS_API_KEY: str = ""
 OLLAMA_BASE_URL: str = "http://localhost:11434"
 OLLAMA_MODEL: str = "llama3.2:3b"

 class Config:
    env_file = ".env"
settings = Settings()
