from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    port: int = 8000
    database_url: str = "postgresql://postgres:137_Cmspelo@localhost:5432/mind"
    database_echo: bool = False
    api_title: str = "M.I.N.D - Mental Intelligence & Network Data"
    api_version: str = "0.1.0"
    debug: bool = True
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    human_in_loop_required: bool = True
    min_confidence_threshold: float = 0.5
    data_retention_days: int = 1825
    encryption_key: str = "change-me-32-char-key-here!"


settings = Settings()
