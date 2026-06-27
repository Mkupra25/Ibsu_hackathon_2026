# 🤖 სასაუბრო BI — AI ასისტენტი SQL მონაცემთა ბაზისთვის

ქართულენოვანი AI ასისტენტი, რომელიც ბუნებრივ ენაზე დასმულ ბიზნეს-კითხვებს SQL მოთხოვნებად გარდაქმნის და მონაცემთა ბაზიდან პასუხს აბრუნებს.

## 🚀 სწრაფი დაწყება (Backend)

### წინაპირობები
- Python 3.12+
- Docker Desktop (PostgreSQL-ისთვის)
- Google Gemini API Key ([აქედან](https://aistudio.google.com/apikey))

### 1. გარემოს ცვლადების კონფიგურაცია
```bash
cp .env.example .env
# .env ფაილში ჩაწერეთ თქვენი GOOGLE_API_KEY
```

### 2. PostgreSQL-ის გაშვება (Docker)
```bash
docker-compose up -d db
```

### 3. Python გარემოს შექმნა
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 4. აპლიკაციის გაშვება
```bash
uvicorn app.main:app --reload --port 8000
```

## 🎨 Frontend (React + Vite)
Frontend განთავსებულია იმავე რეპოზიტორიაში. გაშვებისთვის დაგჭირდებათ Node.js (v18+).

### გაშვება:
```bash
npm install
npm run dev
```

## 📊 API Endpoints

| მეთოდი | URL | აღწერა |
|---|---|---|
| `GET` | `/api/health` | სისტემის სტატუსი |
| `POST` | `/api/chat` | ბიზნეს-კითხვის დასმა |
| `GET` | `/api/schema` | DB სტრუქტურა |

---
*GTU ტექნოლოგიური ჰაკათონი 2026*
