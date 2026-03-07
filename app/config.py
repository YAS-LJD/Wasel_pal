from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "Wasel Palestine API"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # Database — PostgreSQL
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "wasel_db"
    POSTGRES_USER: str = "wasel_user"
    POSTGRES_PASSWORD: str = "wasel_pass_2026"

    # JWT
    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()