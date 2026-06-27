import asyncio
from google import genai
from app.config import get_settings

async def list_models():
    settings = get_settings()
    client = genai.Client(api_key=settings.google_api_key)
    
    print("Available models:")
    # genai client list models
    models = client.models.list()
    for m in models:
        print(f"- {m.name}")

if __name__ == "__main__":
    asyncio.run(list_models())
