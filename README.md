EventEase 🎉

EventEase is a full-stack web application for discovering university and tech events, alongside curated news.
It uses FastAPI (Python) for the backend, PostgreSQL for persistence, and Next.js + TailwindCSS for the frontend.
Everything runs inside Docker for consistency across environments.

📦 Project Structure
eventease/
│── backend/        # FastAPI app, models, routers, migrations
│   ├── app/
│   │   ├── api/            # Auth, Users, Events, News, etc.
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # External APIs (news, events)
│   │   └── db/             # Database setup
│   └── migrations/         # Alembic migrations
│
│── frontend/       # Next.js 14 app with Tailwind v4
│   ├── src/app/    # App Router pages (home, about)
│   ├── src/components/     # Reusable components
│   └── src/lib/    # API helpers (fetchEvents, fetchNews)
│
│── docker-compose.yml
│── README.md

🚀 Getting Started
1. Clone repository
git clone <your-private-repo-url>
cd eventease



2. Environment Variables

Create a file .env.dev in the root of the project with:

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=eventease
DATABASE_URL=postgresql://postgres:postgres@db:5432/eventease

# JWT secrets (for auth)
SECRET_KEY=supersecret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

Create a file .env.local in the frontend directory with:

NEXT_PUBLIC_BACKEND_URL=http://backend:8000

3. Start Services with Docker
docker compose up --build


This starts:

backend → FastAPI on http://localhost:8000
 (Swagger at /docs)

frontend → Next.js on http://localhost:3000

db → PostgreSQL 15 on port 5432

🗄 Database Setup

We use Alembic for migrations + a helper script to create initial tables.

Recreate schema (⚠️ will drop old data):

docker compose down -v
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m init_db

🔑 Admin Seeder

To create an admin user:

docker compose exec backend python -m seeder.seed_admin

🌐 Frontend

Built with Next.js 14 + React 18

Styled with Tailwind v4

Dark mode toggle via next-themes

API helpers normalize responses (fetchEvents, fetchNews) so components can directly use .map

Example usage
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

Auth → POST /auth/login

Users → GET /users/

Events

GET /events/ (public, paginated)

POST /events/ (admin only)

News

GET /news/ (public, paginated)

POST /news/ (admin only)

⚠️ Common Issues & Fixes

relation "events" does not exist → Run migrations + init_db.

Failed to fetch in frontend → Make sure NEXT_PUBLIC_BACKEND_URL=http://backend:8000 in docker-compose.

Dark mode not toggling → Ensure Providers wraps <body> with ThemeProvider attribute="class".

500 on GET endpoints → Check backend logs with
docker compose logs backend -f.