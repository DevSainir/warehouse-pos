from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "warehouse"
    ENV: str = "local"

    DATABASE_URL: str
    REDIS_URL: str

    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRES_MIN: int = 30

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_S3_BUCKET: str
    AWS_S3_BASE_URL: str
    AWS_PRESIGN_EXPIRES_SECONDS: int

settings = Settings()
