# Full-Stack Django + Next.js Project Template

## Project Structure

```
my-project/
├── backend/                      # Django backend
│   ├── apps/
│   │   ├── __init__.py
│   │   ├── users/
│   │   ├── core/
│   │   └── api/
│   ├── common/
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── local.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── local.txt
│   │   └── production.txt
│   ├── Dockerfile
│   ├── manage.py
│   └── pytest.ini
├── frontend/                     # Next.js frontend
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── hooks/
│   ├── stores/
│   ├── types/
│   ├── public/
│   ├── Dockerfile
│   ├── next.config.js
│   ├── package.json
│   └── tailwind.config.ts
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .github/
│   └── workflows/
│       └── ci-cd.yml
└── README.md
```

## Backend Setup

### requirements/base.txt
```
Django>=5.0,<6.0
djangorestframework>=3.14.0
django-cors-headers>=4.3.0
django-filter>=23.0
django-redis>=5.4.0
drf-spectacular>=0.27.0
celery>=5.3.0
redis>=5.0.0
psycopg2-binary>=2.9.0
Pillow>=10.0.0
python-dotenv>=1.0.0
gunicorn>=21.0.0
whitenoise>=6.6.0
dj-database-url>=2.1.0
```

### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements/production.txt .
RUN pip install --no-cache-dir -r production.txt

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "config.wsgi:application"]
```

## Frontend Setup

### package.json
```json
{
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.0.0",
    "zustand": "^4.4.0",
    "axios": "^1.6.0",
    "react-hook-form": "^7.48.0",
    "zod": "^3.22.0",
    "@hookform/resolvers": "^3.3.0",
    "tailwindcss": "^3.3.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "typescript": "^5.2.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "14.0.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

### Frontend Dockerfile
```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

## Docker Compose Development

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: >
      sh -c "python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    environment:
      - DEBUG=1
      - DJANGO_SETTINGS_MODULE=config.settings.local
      - DATABASE_URL=postgres://postgres:postgres@db:5432/myapp
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    command: npm run dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api

volumes:
  postgres_data:
```

## Environment Configuration

### .env.example
```bash
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=config.settings.local
DATABASE_URL=postgres://postgres:postgres@localhost:5432/myapp
REDIS_URL=redis://localhost:6379/0

# Next.js
NEXT_PUBLIC_API_URL=http://localhost:8000/api
API_URL=http://localhost:8000/api

# External Services
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=

STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=

SENDGRID_API_KEY=
```

## Quick Start Commands

```bash
# 1. Clone and setup
git clone <repo>
cd my-project

# 2. Create environment files
cp .env.example .env
cp backend/.env.example backend/.env

# 3. Start with Docker
docker-compose up --build

# 4. Run migrations
docker-compose exec backend python manage.py migrate

# 5. Create superuser
docker-compose exec backend python manage.py createsuperuser

# 6. Access applications
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/docs/
```
