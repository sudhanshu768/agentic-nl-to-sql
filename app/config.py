from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    read_only_database_url: str

    gemini_api_key: str = ""
    llm_provider: str = "gemini"
    llm_model: str

    max_sql_retries: int = 3
    max_result_rows: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()