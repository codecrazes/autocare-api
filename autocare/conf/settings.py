from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    SECRET_KEY: str = ""
    CONFIRMATION_SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SENDER_EMAIL: str = ""
    SENDER_PASSWORD: str = ""
    BASE_URL: str = "https://www.autocare.app.br/"
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "https://www.autocare.app.br/auth/token"


settings = Settings()
