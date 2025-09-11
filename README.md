EventEase 

EventEase is a full-stack web application for discovering tech events and tech news.

It is built with:

⚡ FastAPI (Python) → backend REST API

🐘 PostgreSQL → database

⚛️ Next.js + TailwindCSS → frontend UI

🐳 Docker → containerized environment

📂 Project Structure
eventease/
├── backend/                 # FastAPI backend
│   ├── app/                 # Application code
│   │   ├── api/             # Routers (auth, users, events, news, etc.)
│   │   ├── db/              # Database setup
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # External API integrations
│   │   └── utils/           # Helpers (security, pagination, etc.)
│   ├── migrations/          # Alembic migrations
│   ├── seeder/              # Seeder scripts (admin user, etc.)
│   ├── tests/               # Pytest unit tests
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── init_db.py
│   ├── requirements.txt
│   └── pytest.ini
│
├── frontend/                # Next.js frontend
│   ├── public/              # Static assets (logos, placeholders, icons)
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # Reusable UI components
│   │   ├── context/         # React context providers
│   │   └── lib/             # API helpers (fetchEvents, fetchNews)
│   ├── Dockerfile
│   ├── package.json
│   └── tsconfig.json
│
├── docker-compose.yml       # Multi-service setup
├── LICENSE
└── README.md

🚀 Getting Started
1️⃣ Clone the repository
git clone <your-repo-url>
cd eventease

2️⃣ Environment Variables

Create .env.dev in the project root:

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=eventease
DATABASE_URL=postgresql://postgres:postgres@db:5432/eventease

# JWT secrets (for auth)
SECRET_KEY=supersecret       # 🔒 change in production!
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External API keys
SEARCHAPI_KEY=your_api_key_here   # 🔑 required for SearchApi.io
TICKETMASTER_KEY=your_api_key_here


Create .env.local in frontend/:

NEXT_PUBLIC_BACKEND_URL=http://backend:8000


👉 Replace API keys with your own. Never commit .env.* files to GitHub.

3️⃣ Start services with Docker
docker compose up --build


Services:

Backend (FastAPI) → http://localhost:8000

Swagger docs at /docs

Frontend (Next.js) → http://localhost:3000

PostgreSQL → port 5432

🗄 Database Setup

Apply migrations + initialize schema:

docker compose exec backend alembic upgrade head
docker compose exec backend python -m init_db


Create an admin user:

docker compose exec backend python -m seeder.seed_admin

🌐 Frontend

Built with Next.js 14 and React 18

Styled with TailwindCSS v4

Dark mode toggle via next-themes

API helpers (fetchEvents, fetchNews) normalize backend responses

Example usage:

"use client"
import { useEffect, useState } from "react"
import { fetchNews } from "@/lib/api"

export default function Home() {
  const [news, setNews] = useState([])

  useEffect(() => {
    fetchNews().then(setNews).catch(console.error)
  }, [])

  return (
    <ul>
      {news.map((n, i) => (
        <li key={i}>{n.title}</li>
      ))}
    </ul>
  )
}

🔗 API Endpoints
Auth

POST /auth/login

Users

GET /users/

Events

GET /events/ → paginated

POST /events/ → admin only

News

GET /news/ → paginated

POST /news/ → admin only

⚠️ Common Issues & Fixes

relation "events" does not exist
→ Run migrations + init_db.

Frontend “Failed to fetch”
→ Ensure .env.local has:

NEXT_PUBLIC_BACKEND_URL=http://backend:8000


Dark mode not toggling
→ Wrap <body> with ThemeProvider from next-themes.

500 errors on GET endpoints
→ Inspect logs:

docker compose logs backend -f

📜 License

This project is licensed under the MIT License
