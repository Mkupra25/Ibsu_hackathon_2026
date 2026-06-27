import asyncio
from app.services.sql_generator import sql_generator

async def test():
    intent = await sql_generator.classify_intent("გამარჯობა")
    print(f"Intent for 'გამარჯობა': '{intent}'")
    
    intent2 = await sql_generator.classify_intent("რა კითხვა შეიძლება დაგისვა?")
    print(f"Intent for 'რა კითხვა...': '{intent2}'")

if __name__ == "__main__":
    asyncio.run(test())
