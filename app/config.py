"""
კონფიგურაცია — გარემოს ცვლადების მართვა.

📌 პრეზენტაციისთვის:
ეს ფაილი იყენებს pydantic-settings ბიბლიოთეკას, რომელიც .env ფაილიდან
ავტომატურად კითხულობს კონფიგურაციას. ეს არის "12-Factor App" პრინციპი —
კონფიგურაცია კოდში არ ინახება, არამედ გარემოს ცვლადებში.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """აპლიკაციის კონფიგურაცია."""

    # === აპლიკაცია ===
    app_name: str = "სასაუბრო BI"
    app_env: str = "development"
    debug: bool = True

    # === მონაცემთა ბაზა ===
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/conversational_bi"
    database_url_sync: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/conversational_bi"
    database_url_readonly: str = "postgresql+asyncpg://readonly_user:readonly_pass@localhost:5432/conversational_bi"

    # === Google Gemini LLM ===
    google_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # === უსაფრთხოება ===
    query_timeout_seconds: int = 10
    max_result_rows: int = 1000

    # === CORS (React frontend) ===
    frontend_url: str = "http://localhost:3000"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Singleton pattern — Settings ობიექტი მხოლოდ ერთხელ იქმნება
    და შემდეგ cache-დან ბრუნდება. ეს ოპტიმიზაციაა.
    """
    return Settings()
