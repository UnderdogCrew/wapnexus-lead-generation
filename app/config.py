from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "app/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    google_places_api_key: str = ""
    openai_api_key: str = ""
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "wapnexus_leads"
    openai_model: str = "gpt-4o-mini"
    wapnexus_api_token: str = ""
    wapnexus_send_url: str = "https://api.wapnexus.com/send/message"
    wapnexus_template_name: str = "grow_business_with_wapnexus"


@lru_cache
def get_settings() -> Settings:
    return Settings()
