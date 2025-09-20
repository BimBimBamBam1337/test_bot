from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn


class Settings(BaseSettings):
    token: str
    postgres_dsn: PostgresDsn
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
