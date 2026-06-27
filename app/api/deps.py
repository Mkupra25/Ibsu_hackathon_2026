"""
Dependency Injection — საერთო dependency-ების მართვა.

📌 პრეზენტაციისთვის:
FastAPI-ის Depends() სისტემა ავტომატურად "აწვდის" საჭირო
ობიექტებს (DB სესია, LLM კლიენტი) ყველა endpoint-ს.
ეს არის Dependency Injection pattern — კოდის მოდულარობისთვის.
"""

from app.db.session import get_db_session
from app.config import get_settings

# Re-export for easy import in routes
__all__ = ["get_db_session", "get_settings"]
