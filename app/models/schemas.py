"""
Pydantic მოდელები — მოთხოვნა/პასუხის სქემები.

📌 პრეზენტაციისთვის:
Pydantic ავტომატურად ამოწმებს (ვალიდაცია) ყველა შემომავალ მონაცემს.
თუ React-იდან არასწორი JSON მოვა, FastAPI ავტომატურად 422 შეცდომას
დააბრუნებს დეტალური ახსნით. ეს არის "data validation layer".
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# === მოთხოვნის მოდელები ===

class ChatRequest(BaseModel):
    """მომხმარებლის შეტყობინების მოდელი."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="მომხმარებლის შეკითხვა ქართულ ან ინგლისურ ენაზე"
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="საუბრის ID — follow-up კითხვებისთვის"
    )


# === პასუხის მოდელები ===

class ChartSuggestion(BaseModel):
    """გრაფიკის შეთავაზება ფრონტენდისთვის."""
    chart_type: str = Field(description="გრაფიკის ტიპი: bar, line, pie, table")
    x_axis: Optional[str] = Field(default=None, description="X ღერძის სვეტი")
    y_axis: Optional[str] = Field(default=None, description="Y ღერძის სვეტი")
    title: Optional[str] = Field(default=None, description="გრაფიკის სათაური ქართულად")


class QueryResult(BaseModel):
    """SQL query-ის შედეგი."""
    columns: list[str] = Field(description="სვეტების სახელები")
    rows: list[dict] = Field(description="მონაცემთა მწკრივები")
    row_count: int = Field(description="მწკრივების რაოდენობა")


class ChatResponse(BaseModel):
    """სრული პასუხი მომხმარებლისთვის."""
    answer: str = Field(description="ტექსტური პასუხი ქართულ ენაზე")
    sql_query: Optional[str] = Field(default=None, description="გენერირებული SQL query")
    data: Optional[QueryResult] = Field(default=None, description="მოთხოვნის შედეგები")
    chart: Optional[ChartSuggestion] = Field(default=None, description="გრაფიკის შეთავაზება")
    conversation_id: str = Field(description="საუბრის ID")
    processing_time_ms: Optional[int] = Field(default=None, description="დამუშავების დრო (მილიწამი)")
    error: Optional[str] = Field(default=None, description="შეცდომის შეტყობინება, თუ არის")


# === სქემის მოდელი ===

class TableInfo(BaseModel):
    """ცხრილის ინფორმაცია."""
    table_name: str
    columns: list[dict]
    row_count: Optional[int] = None
    comment: Optional[str] = None


class SchemaResponse(BaseModel):
    """DB სქემის ინფორმაცია."""
    tables: list[TableInfo]
    total_tables: int


# === Health Check ===

class HealthResponse(BaseModel):
    """ჯანმრთელობის შემოწმების პასუხი."""
    status: str = "ok"
    app_name: str
    database: str = "disconnected"
    timestamp: datetime


# === სადემონსტრაციო კითხვები ===

class ExampleQuestion(BaseModel):
    """სადემონსტრაციო კითხვა."""
    question: str
    category: str
    description: str
