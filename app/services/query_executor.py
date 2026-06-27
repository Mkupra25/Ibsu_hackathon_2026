"""
Query Executor — ვალიდირებული SQL-ის უსაფრთხო შესრულება.

📌 პრეზენტაციისთვის:
ეს კომპონენტი LLM-ის მიერ გენერირებულ (და ვალიდირებულ) SQL-ს
ასრულებს მონაცემთა ბაზაზე. მნიშვნელოვანი უსაფრთხოების ზომები:
- Read-only რეჟიმი (მხოლოდ SELECT)
- Query timeout (10 წამი)
- შედეგის ზომის ლიმიტი (1000 მწკრივი)
"""

from sqlalchemy import text
from app.db.session import AsyncSessionFactory
from app.config import get_settings

settings = get_settings()


class QueryExecutor:
    """SQL მოთხოვნების უსაფრთხო შემსრულებელი."""

    async def execute(self, sql_query: str) -> dict:
        """
        SQL მოთხოვნის შესრულება და შედეგის დაბრუნება.
        
        Args:
            sql_query: ვალიდირებული SELECT მოთხოვნა
            
        Returns:
            dict: {
                "columns": [...],
                "rows": [{...}, ...],
                "row_count": int
            }
        """
        async with AsyncSessionFactory() as session:
            try:
                # Timeout-ის დაყენება — თუ query 10 წამზე მეტი გაგრძელდა, გაუქმდება
                await session.execute(
                    text(f"SET statement_timeout = '{settings.query_timeout_seconds}s'")
                )

                # Read-only ტრანზაქცია
                await session.execute(text("SET TRANSACTION READ ONLY"))

                # SQL-ის შესრულება
                result = await session.execute(text(sql_query))

                # შედეგის წაკითხვა (ლიმიტით)
                rows = result.fetchmany(settings.max_result_rows)
                columns = list(result.keys())

                # მონაცემების სერიალიზაცია
                serialized_rows = []
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        # Decimal, datetime და სხვა ტიპების JSON-ში გარდაქმნა
                        if hasattr(value, '__float__'):
                            row_dict[col] = float(value)
                        elif hasattr(value, 'isoformat'):
                            row_dict[col] = value.isoformat()
                        else:
                            row_dict[col] = value
                    serialized_rows.append(row_dict)

                return {
                    "columns": columns,
                    "rows": serialized_rows,
                    "row_count": len(serialized_rows),
                }

            except Exception as e:
                error_msg = str(e)
                # PostgreSQL timeout error
                if "canceling statement due to statement timeout" in error_msg:
                    raise TimeoutError(
                        f"მოთხოვნის დრო ამოიწურა ({settings.query_timeout_seconds} წამი). "
                        "გთხოვ, გამოიყენეთ უფრო კონკრეტული ფილტრები."
                    )
                raise

            finally:
                await session.rollback()  # ყოველთვის rollback (read-only)


# Singleton instance
query_executor = QueryExecutor()
