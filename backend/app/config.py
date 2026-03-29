from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Scripts Control Service"
    database_url: str = "postgresql+asyncpg://app:app@db:5432/scripts_control"
    scripts_dir: str = "/app/scripts"
    monitor_domains: str = "https://example.com,https://python.org,https://github.com"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
