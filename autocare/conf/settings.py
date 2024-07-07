from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="autocare/config/.env", env_file_encoding="utf-8")

    DATABASE_URL: str = ""
    SECRET_KEY: str = ""
    CONFIRMATION_SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SENDER_EMAIL: str = ""
    SENDER_PASSWORD: str = ""
    BASE_URL: str = "http://127.0.0.1:8000"


settings = Settings()
