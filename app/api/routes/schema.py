"""
Schema endpoint — მონაცემთა ბაზის სტრუქტურის API.

📌 პრეზენტაციისთვის:
ეს endpoint ფრონტენდს საშუალებას აძლევს აჩვენოს DB-ის სტრუქტურა
მომხმარებელს — რა ცხრილები არსებობს, რა სვეტები აქვთ.
ეს transparency-ისთვისაა — მომხმარებელმა იცოდეს, რა მონაცემებზე
შეუძლია კითხვა.
"""

from fastapi import APIRouter
from app.models.schemas import SchemaResponse, TableInfo
from app.services.schema_retriever import schema_retriever

router = APIRouter()


@router.get(
    "/schema",
    response_model=SchemaResponse,
    summary="მონაცემთა ბაზის სტრუქტურა",
    description="აბრუნებს ყველა ცხრილის ინფორმაციას: სახელი, სვეტები, ტიპები, მწკრივების რაოდენობა",
)
async def get_schema():
    """DB სქემის ინფორმაცია ფრონტენდისთვის."""
    tables_info = await schema_retriever.get_tables_info()

    tables = [
        TableInfo(
            table_name=t["table_name"],
            columns=t["columns"],
            row_count=t["row_count"],
            comment=t["comment"],
        )
        for t in tables_info
    ]

    return SchemaResponse(
        tables=tables,
        total_tables=len(tables),
    )
