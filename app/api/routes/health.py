"""
Health Check endpoint.

📌 პრეზენტაციისთვის:
ეს endpoint ამოწმებს, მუშაობს თუ არა აპლიკაცია და მონაცემთა ბაზა.
Production-ში ამას load balancer-ები და monitoring სისტემები იყენებენ.
"""

from fastapi import APIRouter
from sqlalchemy import text
from datetime import datetime, timezone

from app.models.schemas import HealthResponse
from app.db.session import async_engine
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="სისტემის ჯანმრთელობის შემოწმება",
    description="ამოწმებს აპლიკაციის და მონაცემთა ბაზის მდგომარეობას",
)
async def health_check():
    """აპლიკაციის და DB-ის სტატუსის შემოწმება."""
    db_status = "გათიშულია"

    try:
        # ვცდილობთ DB-ს დაკავშირებას
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_status = "დაკავშირებულია ✅"
    except Exception as e:
        db_status = f"შეცდომა: {str(e)}"

    return HealthResponse(
        status="მუშაობს ✅",
        app_name=settings.app_name,
        database=db_status,
        timestamp=datetime.now(timezone.utc),
    )
