from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  
    DATABASE_URL: str = "postgres://postgres:cyberify_dev_123@127.0.0.1:5432/cyberify_kb"
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    LOG_LEVEL: str = "INFO"
    FASTEMBED_MODEL: str = "BAAI/bge-small-en-v1.5"
    HUGGINGFACE_API_TOKEN: str = ""
    HUGGINGFACE_CHAT_MODEL: str = "microsoft/Phi-3-mini-4k-instruct"
    HUGGINGFACE_MAX_NEW_TOKENS: int = 512
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

TORTOISE_ORM = {
    "timezone": "UTC",
    "connections": {
        "default": settings.DATABASE_URL,
    },
    "apps": {
        "models": {
            "models": [
                "app.models.user",
                "app.models.document",
                "aerich.models",
            ],
            "default_connection": "default",
        }
    },
}
