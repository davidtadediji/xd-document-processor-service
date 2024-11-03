from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # AWS S3 Configuration
    S3_BUCKET: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_REGION: str
    S3_ENDPOINT: str

    # Database Configuration
    DATABASE_URL: str

    # Application Settings
    LOG_LEVEL: str = "INFO"

    class ConfigDict:
        env_file = ".env"


settings = Settings()
