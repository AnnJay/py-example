from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorythm: str
    access_token_expire_minutes: int = 30


    model_config = SettingsConfigDict(
        env_file=".env",          # Загрузка из .env файла
        env_file_encoding="utf-8"
    )


settings = Settings()
