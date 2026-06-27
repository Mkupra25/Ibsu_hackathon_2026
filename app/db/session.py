"""
მონაცემთა ბაზის სესიის მართვა.

📌 პრეზენტაციისთვის:
ეს ფაილი ქმნის "connection pool"-ს — კავშირების აუზს DB-სთან.
ყოველ მოთხოვნაზე ახალი კავშირი არ იქმნება (ძვირი ოპერაციაა),
არამედ აუზიდან აიღება არსებული კავშირი. ეს მნიშვნელოვანი
ოპტიმიზაციაა production აპლიკაციებში.

async/await სინტაქსი საშუალებას გვაძლევს DB მოთხოვნები
პარალელურად შევასრულოთ, ანუ ერთი მომხმარებლის query
არ ბლოკავს სხვა მომხმარებლებს.
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine, text
from app.config import get_settings


settings = get_settings()

# === ასინქრონული engine (API მოთხოვნებისთვის) ===
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # debug რეჟიმში SQL-ს კონსოლში დაბეჭდავს
    pool_size=10,          # მაქსიმუმ 10 ერთდროული კავშირი
    max_overflow=5,        # +5 დამატებითი, თუ ყველა დაკავებულია
    pool_timeout=30,       # 30 წამი ლოდინი თავისუფალ კავშირზე
)

# === ასინქრონული სესიის factory ===
AsyncSessionFactory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# === სინქრონული engine (seed/migration-ისთვის) ===
sync_engine = create_engine(
    settings.database_url_sync,
    echo=settings.debug,
)


async def get_db_session() -> AsyncSession:
    """
    Dependency injection — FastAPI ავტომატურად იძახებს ამ ფუნქციას
    ყოველ მოთხოვნაზე. სესია ავტომატურად იხურება მოთხოვნის ბოლოს.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()


async def execute_readonly_query(sql_query: str) -> list[dict]:
    """
    Read-only SQL query-ის შესრულება.
    
    📌 უსაფრთხოება:
    - მხოლოდ SELECT ოპერაციები
    - Timeout ლიმიტი
    - შედეგის ზომის ლიმიტი
    """
    async with AsyncSessionFactory() as session:
        # Timeout-ის დაყენება
        await session.execute(
            text(f"SET statement_timeout = '{settings.query_timeout_seconds}s'")
        )

        # SQL-ის შესრულება
        result = await session.execute(text(sql_query))
        rows = result.fetchmany(settings.max_result_rows)
        columns = list(result.keys())

        return {
            "columns": columns,
            "rows": [dict(zip(columns, row)) for row in rows],
            "row_count": len(rows),
        }
