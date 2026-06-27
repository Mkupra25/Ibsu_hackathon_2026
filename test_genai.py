import asyncio
from google import genai
from app.config import get_settings

async def test_genai():
    settings = get_settings()
    client = genai.Client(api_key=settings.google_api_key)
    response = await client.aio.models.generate_content(
        model=settings.gemini_model,
        contents="Say hello"
    )
    print("response:", response)
    print("response.text:", response.text)

if __name__ == "__main__":
    asyncio.run(test_genai())
