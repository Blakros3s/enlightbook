# Phase 0: Project Infrastructure Setup

## Summary

Phase 0 establishes the complete foundation for the EnlightBook School Management System. This includes the Django backend structure, Next.js frontend setup, Docker containerization, and all necessary configuration files.

**Status**: ✅ **COMPLETE**

---

## What Was Built

### 1. Backend Structure (Django)

#### Directory Structure Created:
```
backend/
├── apps/                          # Django applications
│   ├── __init__.py
│   ├── users/                     # Authentication & User Management
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   └── urls.py
│   ├── core/                      # Core utilities
│   │   ├── __init__.py
│   │   └── apps.py
│   ├── academic/                  # Academic Management
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   └── urls.py
│   ├── finance/                   # Fee Management
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   └── urls.py
│   ├── exams/                     # Examination System
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   └── urls.py
│   ├── attendance/                # Attendance Tracking
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   └── urls.py
│   └── communication/             # Messaging System
│       ├── __init__.py
│       ├── apps.py
│       └── urls.py
├── common/                        # Shared utilities
│   └── __init__.py
├── config/                        # Django Configuration
│   ├── __init__.py               # Includes Celery app
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py               # 320 lines - Main settings
│   │   ├── local.py              # Development settings
│   │   └── production.py         # Production settings
│   ├── urls.py                   # Main URL routing
│   ├── wsgi.py                   # WSGI application
│   ├── asgi.py                   # ASGI application
│   └── celery.py                 # Celery configuration
├── requirements/                  # Python dependencies
│   ├── base.txt                  # Core dependencies (18 packages)
│   ├── local.txt                 # Dev dependencies (+7 packages)
│   └── production.txt            # Production deps (+1 package)
├── Dockerfile                     # Backend container definition
└── manage.py                      # Django management script
```

#### Key Backend Features:
- **Django 5.0** with Django REST Framework
- **JWT Authentication** (SimpleJWT) with 15min access / 7day refresh tokens
- **PostgreSQL** database with connection pooling
- **Redis** for caching and sessions
- **Celery** for background tasks
- **API Documentation** (drf-spectacular - OpenAPI/Swagger)
- **CORS** configured for frontend communication
- **Security headers** and HTTPS enforcement (production)
- **Password validation** (12+ chars, complexity requirements)
- **7 Django apps** initialized with proper AppConfig

---

### 2. Frontend Structure (Next.js)

#### Directory Structure Created:
```
frontend/
├── app/                          # Next.js 14+ App Router
│   ├── layout.tsx               # Root layout with Inter font
│   ├── page.tsx                 # Home page
│   └── globals.css              # Global styles & Tailwind
├── components/                   # React components (empty, ready)
├── hooks/                        # Custom React hooks (empty, ready)
├── stores/                       # Zustand stores (empty, ready)
├── types/                        # TypeScript types (empty, ready)
├── public/                       # Static assets (empty, ready)
├── lib/                          # Utility functions
│   └── utils.ts                 # cn(), formatDate(), formatCurrency()
├── package.json                 # 28 dependencies configured
├── tsconfig.json                # TypeScript configuration
├── tailwind.config.ts           # Tailwind CSS with custom theme
├── next.config.js               # Next.js with API proxy
├── postcss.config.js            # PostCSS configuration
├── next-env.d.ts                # Next.js types
└── Dockerfile                   # Frontend container definition
```

#### Key Frontend Features:
- **Next.js 14+** with App Router
- **TypeScript 5** with strict mode
- **Tailwind CSS** with custom CSS variables for theming
- **Shadcn UI** ready (Radix UI primitives)
- **TanStack Query** for server state management
- **Zustand** for client state management
- **React Hook Form + Zod** for forms and validation
- **Axios** configured with interceptors
- **Recharts** for data visualization
- **Lucide React** for icons

---

### 3. Docker & Infrastructure

#### Files Created:
- **docker-compose.yml** - Full stack orchestration with 6 services
- **backend/Dockerfile** - Python 3.11 container with all dependencies
- **frontend/Dockerfile** - Node.js 20 container
- **.env.example** - Environment variables template

#### Services Configured:
1. **db** - PostgreSQL 15 with health checks
2. **redis** - Redis 7 for cache/sessions
3. **backend** - Django development server
4. **celery** - Background task worker
5. **celery-beat** - Task scheduler
6. **frontend** - Next.js development server

---

### 4. Documentation & Utilities

#### Files Created:
- **README.md** - Complete project documentation with quick start
- **.gitignore** - Python, Node.js, and IDE ignore patterns
- **verify-setup.sh** - Bash script to verify setup completion
- **steps.md** (root) - Complete 18-week implementation guide

---

## What You Need To Do

### Step 1: Verify Prerequisites

Ensure you have the following installed:
- ✅ Docker Desktop (or Docker Engine + Compose)
- ✅ Git (for version control)

**Check installations:**
```bash
docker --version
docker-compose --version
git --version
```

---

### Step 2: Initial Setup

#### 2.1 Copy Environment File
```bash
cp .env.example .env
```

The `.env` file contains all necessary configuration. For development, the defaults should work.

#### 2.2 Review Project Structure (Optional)
Take a look at what was created:
```bash
# View backend structure
tree backend -L 3

# View frontend structure  
tree frontend -L 2

# View all files
find . -type f -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.json" -o -name "*.yml" | head -30
```

---

### Step 3: Start the Application

#### 3.1 Build and Start All Services
```bash
docker-compose up --build
```

**This will:**
- Download PostgreSQL, Redis, Python, and Node.js images
- Build the backend and frontend containers
- Start all 6 services
- Mount code for live reloading

**First build will take 3-5 minutes** depending on your internet speed.

#### 3.2 Verify Services Are Running
Open new terminal windows and check:

```bash
# View running containers
docker-compose ps

# View logs (in separate terminals)
docker-compose logs -f backend   # Django logs
docker-compose logs -f frontend  # Next.js logs
docker-compose logs -f db        # Database logs
```

You should see all containers with status "Up".

---

### Step 4: Initialize Database

#### 4.1 Run Migrations
In a new terminal:
```bash
docker-compose exec backend python manage.py migrate
```

You should see Django creating database tables.

#### 4.2 Create Superuser
```bash
docker-compose exec backend python manage.py createsuperuser
```

Follow the prompts to create an admin account:
- Username: (your choice)
- Email: (your email)
- Password: (12+ characters required)

---

### Step 5: Verify Everything Works

#### 5.1 Check Services
Open your browser and verify:

| Service | URL | Expected Result |
|---------|-----|-----------------|
| Frontend | http://localhost:3000 | "Welcome to EnlightBook" page |
| Backend API | http://localhost:8000/api/ | DRF browsable API root |
| API Docs | http://localhost:8000/api/docs/ | Swagger UI documentation |
| Django Admin | http://localhost:8000/admin/ | Login page (use superuser) |

#### 5.2 Test API Endpoints
```bash
# Test health endpoint
curl http://localhost:8000/api/

# You should see:
# {"detail":"Not found"} or API root response
```

---

### Step 6: Development Workflow

#### Making Changes

**Backend Changes:**
- Edit files in `backend/` directory
- Changes auto-reload (Django dev server)
- View logs: `docker-compose logs -f backend`

**Frontend Changes:**
- Edit files in `frontend/` directory
- Changes auto-reload (Next.js dev server)
- View logs: `docker-compose logs -f frontend`

#### Common Commands

```bash
# Restart specific service
docker-compose restart backend
docker-compose restart frontend

# Run Django shell
docker-compose exec backend python manage.py shell

# Run Django checks
docker-compose exec backend python manage.py check

# Install new Python package
docker-compose exec backend pip install <package>

# Install new Node package
docker-compose exec frontend npm install <package>

# View database
docker-compose exec db psql -U postgres -d enlightbook

# Stop all services
docker-compose down

# Stop and remove volumes (DELETES DATA!)
docker-compose down -v
```

---

### Step 7: Optional - Local Development (Without Docker)

If you prefer local development:

#### Backend (Local)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements/local.txt

# Start PostgreSQL and Redis locally first
# Then:
python manage.py migrate
python manage.py runserver
```

#### Frontend (Local)
```bash
cd frontend
npm install
npm run dev
```

---

## Troubleshooting

### Issue: Port already in use
**Error**: `bind: address already in use`

**Solution**: Stop services using these ports or change ports in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
  - "3001:3000"  # Change 3000 to 3001
```

### Issue: Permission denied (Windows)
**Error**: Cannot access files or volumes

**Solution**: Run Docker Desktop as Administrator or ensure file sharing is enabled in Docker settings.

### Issue: Database connection failed
**Error**: `could not connect to server: Connection refused`

**Solution**: Wait 10-20 seconds for PostgreSQL to fully start, then retry migrations.

### Issue: Frontend build fails
**Error**: Module not found or build errors

**Solution**: 
```bash
docker-compose exec frontend npm install
docker-compose restart frontend
```

---

## What's Next (Phase 1)

Once Phase 0 is verified working, proceed to **Phase 1: Authentication & User Management**:

### Phase 1 Will Build:
1. Custom User model with role fields
2. JWT login/logout endpoints
3. User registration API
4. Login page (frontend)
5. Protected routes
6. User profile management

### Skills Needed:
- Django models and migrations
- Django REST Framework serializers/viewsets
- JWT authentication flow
- Next.js authentication context
- Protected route components

---

## Verification Checklist

Before moving to Phase 1, verify:

- [ ] `docker-compose up --build` completes without errors
- [ ] All 6 containers are running (`docker-compose ps`)
- [ ] Migrations completed successfully
- [ ] Superuser created
- [ ] Frontend loads at http://localhost:3000
- [ ] Backend API responds at http://localhost:8000/api/
- [ ] API Docs accessible at http://localhost:8000/api/docs/
- [ ] Can log into Django Admin
- [ ] Can view logs for all services
- [ ] Changes to code auto-reload

---

## Support

If you encounter issues:

1. Check logs: `docker-compose logs <service-name>`
2. Restart services: `docker-compose restart`
3. Clean rebuild: `docker-compose down -v && docker-compose up --build`
4. Verify setup: `./verify-setup.sh` (Linux/Mac) or review file structure manually

---

**Ready to proceed?** Once you complete the steps above and verify everything works, we can begin **Phase 1: Authentication & User Management**!
