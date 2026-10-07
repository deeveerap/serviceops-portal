from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "serviceops-portal"
    APP_VERSION: str = "1.0.0"

    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "serviceops"
    POSTGRES_PASSWORD: str = "serviceops"
    POSTGRES_DB: str = "serviceops"

    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    REDIS_URL: str = "redis://redis:6379/0"
    ENABLE_REDIS: bool = False

    class Config:
        env_file = ".env"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
