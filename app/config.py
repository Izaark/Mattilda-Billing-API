from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    DATABASE_URL: str
    API_V1_PREFIX: str = "/api/v1"
    API_KEY: str = "dev-secret-key"
    
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"


settings = Settings()