"""Application settings loaded from environment / .env."""
from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # Seed admin
    admin_name: str = "Admin"
    admin_email: str = "admin@example.com"
    admin_password: str = "change-me"

    # CORS — NoDecode: skip pydantic-settings JSON parsing so the validator
    # below can accept a plain comma-separated string from the env.
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]

    # App
    app_env: str = "development"

    # Google Sheets sync (off until explicitly enabled)
    sheet_sync_enabled: bool = False
    # service-account key file contents: raw JSON or base64 of it
    google_service_account_json: str = ""
    google_sheet_id: str = ""
    google_sheet_tab: str = ""
    sheet_sync_max_attempts: int = 5
    # shared with the frontend cron route; guards POST /sheet-sync/sweep
    cron_secret: str = ""

    # AI that reads the sheet's layout
    ai_provider: Literal["gemini", "grok"] = "gemini"
    ai_api_key: str = ""
    ai_model: str = ""

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, v: object) -> object:
        """Accept a comma-separated string or a JSON/list value."""
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return []
            if s.startswith("["):
                return v  # let pydantic parse JSON list
            return [o.strip() for o in s.split(",") if o.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
