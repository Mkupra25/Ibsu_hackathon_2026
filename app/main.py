"""
სასაუბრო BI — FastAPI აპლიკაციის შესვლის წერტილი.

📌 პრეზენტაციისთვის:
ეს ფაილი არის აპლიკაციის "გული". აქ ხდება:
1. FastAPI აპლიკაციის შექმნა
2. CORS-ის კონფიგურაცია (React ფრონტენდთან კომუნიკაცია)
3. ყველა route-ის დარეგისტრირება
4. Swagger UI-ის კონფიგურაცია (ავტომატური API დოკუმენტაცია)

გაშვება: uvicorn app.main:app --reload
Swagger UI: http://localhost:8000/docs
"""

import sys

# Windows-ის კონსოლში ქართული სიმბოლოებისა და ემოჯიების ბეჭდვისთვის
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.api.routes import health, chat, schema

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    აპლიკაციის lifecycle მართვა.
    startup: DB კავშირის შემოწმება
    shutdown: რესურსების გათავისუფლება
    """
    # === Startup ===
    print(f"🚀 {settings.app_name} ჩაირთო!")
    print(f"📊 გარემო: {settings.app_env}")
    print(f"🔗 DB: {settings.database_url[:50]}...")
    yield
    # === Shutdown ===
    print(f"👋 {settings.app_name} გაითიშა")


# === FastAPI აპლიკაციის შექმნა ===
app = FastAPI(
    title=settings.app_name,
    description=(
        "AI ასისტენტი, რომელიც ბუნებრივ ენაზე დასმულ კითხვებს "
        "SQL მოთხოვნებად გარდაქმნის და მონაცემთა ბაზიდან პასუხს აბრუნებს. "
        "მთლიანად ქართულ ენაზე."
    ),
    version="1.0.0",
    docs_url="/docs",          # Swagger UI
    redoc_url="/redoc",        # ReDoc (ალტერნატიული დოკუმენტაცია)
    lifespan=lifespan,
)


# === CORS კონფიგურაცია ===
# ეს საშუალებას აძლევს React ფრონტენდს (localhost:3000)
# გამოიძახოს ჩვენი API (localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,    # React dev server
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],       # GET, POST, PUT, DELETE...
    allow_headers=["*"],       # ყველა header
)


# === Route-ების რეგისტრაცია ===
app.include_router(health.router, prefix="/api", tags=["სისტემა"])
app.include_router(chat.router, prefix="/api", tags=["საუბარი"])
app.include_router(schema.router, prefix="/api", tags=["სქემა"])


# === Root endpoint ===
@app.get("/", tags=["სისტემა"])
async def root():
    """მთავარი გვერდი — აპლიკაციის ინფორმაცია."""
    return {
        "აპლიკაცია": settings.app_name,
        "ვერსია": "1.0.0",
        "აღწერა": "AI ასისტენტი SQL მონაცემთა ბაზისთვის",
        "დოკუმენტაცია": "/docs",
        "სტატუსი": "/api/health",
    }
