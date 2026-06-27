"""
სქემის ამომღები — მონაცემთა ბაზის სტრუქტურის ინტროსპექცია.

📌 პრეზენტაციისთვის:
ეს სერვისი DB-ის სტრუქტურას (ცხრილები, სვეტები, ტიპები, კომენტარები)
ავტომატურად ამოიღებს. LLM-ს ეს ინფორმაცია ეძლევა, რომ სწორი SQL
დაწეროს. ეს არის "Schema Introspection" — სისტემა თავად სწავლობს
DB-ის სტრუქტურას, ხელით აღწერა საჭირო არ არის.

ეს RAG (Retrieval-Augmented Generation) კომპონენტია — LLM-ს
მხოლოდ რელევანტურ კონტექსტს ვაწვდით.
"""

from sqlalchemy import text
from app.db.session import AsyncSessionFactory


class SchemaRetriever:
    """მონაცემთა ბაზის სქემის ამომღები."""

    def __init__(self):
        self._schema_cache: str | None = None

    async def get_full_schema(self) -> str:
        """
        ამოიღებს მთლიან DB სქემას ფორმატირებული ტექსტის სახით.
        
        Cache-ს იყენებს — სქემა ხშირად არ იცვლება, ამიტომ
        ყოველ მოთხოვნაზე DB-ში წასვლა არ არის საჭირო.
        """
        if self._schema_cache:
            return self._schema_cache

        schema_text = await self._introspect_schema()
        self._schema_cache = schema_text
        return schema_text

    def invalidate_cache(self):
        """Cache-ს გასუფთავება (სქემის ცვლილების შემთხვევაში)."""
        self._schema_cache = None

    async def _introspect_schema(self) -> str:
        """DB-ის სტრუქტურის ამოღება PostgreSQL information_schema-დან."""
        async with AsyncSessionFactory() as session:
            # === ცხრილების სია ===
            tables_result = await session.execute(text("""
                SELECT 
                    t.table_name,
                    obj_description(
                        (quote_ident(t.table_schema) || '.' || quote_ident(t.table_name))::regclass
                    ) AS table_comment
                FROM information_schema.tables t
                WHERE t.table_schema = 'public' 
                  AND t.table_type = 'BASE TABLE'
                ORDER BY t.table_name
            """))
            tables = tables_result.fetchall()

            schema_parts = []
            schema_parts.append("=== მონაცემთა ბაზის სქემა ===\n")

            for table_name, table_comment in tables:
                # === სვეტების ინფორმაცია ===
                columns_result = await session.execute(text("""
                    SELECT 
                        c.column_name,
                        c.data_type,
                        c.is_nullable,
                        c.column_default,
                        col_description(
                            (quote_ident(c.table_schema) || '.' || quote_ident(c.table_name))::regclass,
                            c.ordinal_position
                        ) AS column_comment
                    FROM information_schema.columns c
                    WHERE c.table_schema = 'public' 
                      AND c.table_name = :table_name
                    ORDER BY c.ordinal_position
                """), {"table_name": table_name})
                columns = columns_result.fetchall()

                # === Foreign Key-ები ===
                fk_result = await session.execute(text("""
                    SELECT
                        kcu.column_name,
                        ccu.table_name AS foreign_table,
                        ccu.column_name AS foreign_column
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage ccu
                        ON tc.constraint_name = ccu.constraint_name
                    WHERE tc.table_name = :table_name
                      AND tc.constraint_type = 'FOREIGN KEY'
                """), {"table_name": table_name})
                foreign_keys = fk_result.fetchall()

                # === მწკრივების რაოდენობა ===
                count_result = await session.execute(
                    text(f"SELECT COUNT(*) FROM {table_name}")
                )
                row_count = count_result.scalar()

                # === ფორმატირება ===
                comment_str = f" -- {table_comment}" if table_comment else ""
                schema_parts.append(
                    f"\nცხრილი: {table_name}{comment_str} ({row_count} მწკრივი)"
                )
                schema_parts.append("-" * 60)

                for col_name, data_type, nullable, default, col_comment in columns:
                    null_str = "NULL" if nullable == "YES" else "NOT NULL"
                    comment = f"  -- {col_comment}" if col_comment else ""
                    schema_parts.append(
                        f"  {col_name}: {data_type} ({null_str}){comment}"
                    )

                if foreign_keys:
                    schema_parts.append("  კავშირები (Foreign Keys):")
                    for fk_col, fk_table, fk_foreign_col in foreign_keys:
                        schema_parts.append(
                            f"    {fk_col} → {fk_table}.{fk_foreign_col}"
                        )

            # === Views ===
            views_result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.views 
                WHERE table_schema = 'public'
            """))
            views = views_result.fetchall()

            if views:
                schema_parts.append("\n=== ხედები (Views) ===")
                for (view_name,) in views:
                    cols_result = await session.execute(text("""
                        SELECT column_name, data_type
                        FROM information_schema.columns
                        WHERE table_schema = 'public' AND table_name = :view_name
                        ORDER BY ordinal_position
                    """), {"view_name": view_name})
                    view_cols = cols_result.fetchall()
                    schema_parts.append(f"\nხედი: {view_name}")
                    for col_name, data_type in view_cols:
                        schema_parts.append(f"  {col_name}: {data_type}")

            return "\n".join(schema_parts)

    async def get_tables_info(self) -> list[dict]:
        """ცხრილების ინფორმაცია API-სთვის (GET /api/schema)."""
        async with AsyncSessionFactory() as session:
            tables_result = await session.execute(text("""
                SELECT 
                    t.table_name,
                    obj_description(
                        (quote_ident(t.table_schema) || '.' || quote_ident(t.table_name))::regclass
                    ) AS table_comment
                FROM information_schema.tables t
                WHERE t.table_schema = 'public' 
                  AND t.table_type = 'BASE TABLE'
                ORDER BY t.table_name
            """))
            tables = tables_result.fetchall()

            result = []
            for table_name, table_comment in tables:
                columns_result = await session.execute(text("""
                    SELECT 
                        c.column_name,
                        c.data_type,
                        c.is_nullable,
                        col_description(
                            (quote_ident(c.table_schema) || '.' || quote_ident(c.table_name))::regclass,
                            c.ordinal_position
                        ) AS column_comment
                    FROM information_schema.columns c
                    WHERE c.table_schema = 'public' AND c.table_name = :table_name
                    ORDER BY c.ordinal_position
                """), {"table_name": table_name})
                columns = columns_result.fetchall()

                count_result = await session.execute(
                    text(f"SELECT COUNT(*) FROM {table_name}")
                )
                row_count = count_result.scalar()

                result.append({
                    "table_name": table_name,
                    "comment": table_comment,
                    "row_count": row_count,
                    "columns": [
                        {
                            "name": col_name,
                            "type": data_type,
                            "nullable": nullable == "YES",
                            "comment": col_comment,
                        }
                        for col_name, data_type, nullable, col_comment in columns
                    ],
                })

            return result


# Singleton instance
schema_retriever = SchemaRetriever()
