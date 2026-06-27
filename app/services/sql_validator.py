"""
SQL ვალიდატორი — LLM-ის მიერ გენერირებული SQL-ის უსაფრთხოების შემოწმება.

📌 პრეზენტაციისთვის:
ეს არის "Guardrails" კომპონენტი. LLM-ს არასდროს ენდობი 100%-ით.
ყოველ გენერირებულ SQL-ს ამოწმებ ავტომატურად:
1. სინტაქსის შემოწმება (sqlglot parser)
2. საშიში ოპერაციების ბლოკირება (DROP, DELETE, INSERT...)
3. ცხრილების ვალიდაცია (მხოლოდ ნებადართული ცხრილები)

ეს არის AST (Abstract Syntax Tree) parsing — SQL-ს "ხის" სტრუქტურად
გარდაქმნი და ანალიზი გაკეთე, ტექსტური შემოწმების ნაცვლად.
"""

import sqlglot
from sqlglot import errors as sqlglot_errors
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """SQL ვალიდაციის შედეგი."""
    is_valid: bool
    error_message: str | None = None
    sanitized_sql: str | None = None


# საშიში SQL ოპერაციები — ეს არასდროს უნდა გაიაროს
BLOCKED_OPERATIONS = {
    "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE",
    "TRUNCATE", "GRANT", "REVOKE", "EXECUTE", "EXEC",
    "MERGE", "CALL", "COPY",
}

# დამატებითი საშიში პატერნები (SQL injection ცდები)
BLOCKED_PATTERNS = [
    "--",           # კომენტარი (injection ტექნიკა)
    ";",            # მრავალი statement
    "xp_",          # SQL Server system procedures
    "sp_",          # SQL Server stored procedures
    "INFORMATION_SCHEMA",  # მეტადატის წვდომა (ეს ჩვენ თვითონ ვიყენებთ, არა LLM)
    "pg_catalog",   # PostgreSQL სისტემური ცხრილები
]


class SQLValidator:
    """SQL მოთხოვნების უსაფრთხოების ვალიდატორი."""

    def __init__(self, allowed_tables: list[str] | None = None):
        """
        Args:
            allowed_tables: ნებადართული ცხრილების სია.
                           თუ None, ყველა ცხრილი ნებადართულია.
        """
        self.allowed_tables = allowed_tables

    def validate(self, sql: str) -> ValidationResult:
        """
        SQL მოთხოვნის სრული ვალიდაცია.
        
        აბრუნებს ValidationResult-ს:
        - is_valid=True + sanitized_sql — უსაფრთხო SQL
        - is_valid=False + error_message — რა პრობლემაა
        """
        if not sql or not sql.strip():
            return ValidationResult(
                is_valid=False,
                error_message="ცარიელი SQL მოთხოვნა"
            )

        sql = sql.strip()

        # 1. საშიში პატერნების შემოწმება
        pattern_check = self._check_blocked_patterns(sql)
        if not pattern_check.is_valid:
            return pattern_check

        # 2. საშიში ოპერაციების შემოწმება
        operation_check = self._check_blocked_operations(sql)
        if not operation_check.is_valid:
            return operation_check

        # 3. სინტაქსის შემოწმება (sqlglot parser)
        syntax_check = self._check_syntax(sql)
        if not syntax_check.is_valid:
            return syntax_check

        # 4. ცხრილების ვალიდაცია (თუ კონფიგურირებულია)
        if self.allowed_tables:
            table_check = self._check_tables(sql)
            if not table_check.is_valid:
                return table_check

        return ValidationResult(
            is_valid=True,
            sanitized_sql=sql
        )

    def _check_blocked_patterns(self, sql: str) -> ValidationResult:
        """საშიში ტექსტური პატერნების შემოწმება."""
        sql_upper = sql.upper()
        for pattern in BLOCKED_PATTERNS:
            if pattern.upper() in sql_upper:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"დაბლოკილი პატერნი აღმოჩენილია: {pattern}"
                )
        return ValidationResult(is_valid=True)

    def _check_blocked_operations(self, sql: str) -> ValidationResult:
        """საშიში SQL ოპერაციების შემოწმება."""
        # SQL-ის პირველი სიტყვა
        first_word = sql.strip().split()[0].upper()

        if first_word in BLOCKED_OPERATIONS:
            return ValidationResult(
                is_valid=False,
                error_message=f"დაბლოკილი ოპერაცია: {first_word}. მხოლოდ SELECT ნებადართულია."
            )

        # ქვე-მოთხოვნებშიც შემოწმება
        sql_upper = sql.upper()
        for op in BLOCKED_OPERATIONS:
            # ვეძებთ ოპერაციას, რომელიც სიტყვის საზღვარზეა
            if f" {op} " in f" {sql_upper} ":
                return ValidationResult(
                    is_valid=False,
                    error_message=f"დაბლოკილი ოპერაცია ქვე-მოთხოვნაში: {op}"
                )

        return ValidationResult(is_valid=True)

    def _check_syntax(self, sql: str) -> ValidationResult:
        """SQL სინტაქსის შემოწმება sqlglot-ით."""
        try:
            parsed = sqlglot.parse(sql, dialect="postgres")
            if not parsed:
                return ValidationResult(
                    is_valid=False,
                    error_message="SQL ვერ დაიპარსა"
                )
            return ValidationResult(is_valid=True, sanitized_sql=sql)
        except sqlglot_errors.ParseError as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"SQL სინტაქსის შეცდომა: {str(e)}"
            )

    def _check_tables(self, sql: str) -> ValidationResult:
        """გამოყენებული ცხრილების ვალიდაცია."""
        try:
            parsed = sqlglot.parse(sql, dialect="postgres")
            for statement in parsed:
                # ამოიღე ყველა ცხრილის სახელი
                for table in statement.find_all(sqlglot.exp.Table):
                    table_name = table.name.lower()
                    if table_name not in [t.lower() for t in self.allowed_tables]:
                        return ValidationResult(
                            is_valid=False,
                            error_message=f"ცხრილი '{table_name}' არ არის ნებადართული"
                        )
        except Exception:
            pass  # Parse error already caught above

        return ValidationResult(is_valid=True)


# Singleton instance
sql_validator = SQLValidator(
    allowed_tables=["products", "customers", "orders", "order_items",
                     "monthly_revenue", "sales_summary"]
)
