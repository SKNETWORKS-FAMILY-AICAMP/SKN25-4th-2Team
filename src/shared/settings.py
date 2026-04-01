from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_runtime_mode: str = Field(default="development", alias="APP_RUNTIME_MODE")
    langsmith_api_key: Optional[str] = Field(default=None, alias="LANGSMITH_API_KEY")
    langsmith_project: str = Field(default="Newspedia", alias="LANGSMITH_PROJECT")
    langsmith_workspace_id: Optional[str] = Field(default=None, alias="LANGSMITH_WORKSPACE_ID")
    langsmith_tracing: bool = Field(default=True, alias="LANGSMITH_TRACING")
    langsmith_trace_user: Optional[str] = Field(default=None, alias="LANGSMITH_TRACE_USER")

    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")
    openai_embedding_model: str = Field(default="text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL")


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()
