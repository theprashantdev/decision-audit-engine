from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openrouter_api_key: str
    database_url: str
    escalation_threshold: float = 0.75
    app_env: str = "development"
    secret_key: str = "change_in_production"
    openrouter_model: str = "openai/gpt-4o-mini"

    class Config:
        env_file = ".env"

settings = Settings()
