# EnlightBook - School Management System

A comprehensive school management system built with Django and Next.js.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd enlightbook
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Start all services**
   ```bash
   docker-compose up --build
   ```

4. **Run migrations**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

6. **Access the applications**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/
   - API Documentation: http://localhost:8000/api/docs/
   - Django Admin: http://localhost:8000/admin/

### Manual Setup (Development)

#### Backend Setup

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements/local.txt
   ```

3. **Create local environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

#### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

## 📁 Project Structure

```
enlightbook/
├── backend/                    # Django Backend
│   ├── apps/                   # Django applications
│   │   ├── users/             # Authentication & User Management
│   │   ├── academic/          # Academic Structure
│   │   ├── finance/           # Fee Management
│   │   ├── exams/             # Examination & Results
│   │   ├── attendance/        # Attendance Tracking
│   │   └── communication/     # Messaging & Notifications
│   ├── common/                # Common utilities
│   ├── config/                # Django configuration
│   │   ├── settings/          # Settings (base, local, production)
│   │   ├── urls.py           # URL configuration
│   │   ├── wsgi.py           # WSGI application
│   │   ├── asgi.py           # ASGI application
│   │   └── celery.py         # Celery configuration
│   ├── requirements/          # Python dependencies
│   ├── Dockerfile            # Backend Docker image
│   └── manage.py             # Django management script
│
├── frontend/                   # Next.js Frontend
│   ├── app/                   # Next.js 14+ App Router
│   ├── components/            # React components
│   ├── lib/                   # Utility functions
│   ├── hooks/                 # Custom React hooks
│   ├── stores/                # Zustand stores
│   ├── types/                 # TypeScript types
│   ├── public/                # Static assets
│   ├── package.json           # Node dependencies
│   ├── tailwind.config.ts     # Tailwind CSS config
│   ├── tsconfig.json          # TypeScript config
│   └── Dockerfile            # Frontend Docker image
│
├── docker-compose.yml         # Docker Compose configuration
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🔧 Technology Stack

### Backend
- **Framework**: Django 5.0 + Django REST Framework
- **Authentication**: JWT (SimpleJWT) + 2FA (django-otp)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Task Queue**: Celery 5
- **Documentation**: drf-spectacular (OpenAPI/Swagger)

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS + Shadcn UI
- **State Management**: Zustand + TanStack Query
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx (production)
- **Monitoring**: Sentry (production)

## 📚 API Documentation

Once the backend is running, access the interactive API documentation at:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

## 🧪 Running Tests

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📝 Environment Variables

Key environment variables (see `.env.example` for full list):

### Backend
- `DEBUG` - Debug mode (True/False)
- `SECRET_KEY` - Django secret key
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `CORS_ALLOWED_ORIGINS` - Allowed CORS origins

### Frontend
- `NEXT_PUBLIC_API_URL` - Backend API URL (client-side)
- `API_URL` - Backend API URL (server-side)

## 🤝 Contributing

1. Create a feature branch from `develop`
2. Make your changes
3. Write tests for new functionality
4. Submit a pull request

## 📄 License

This project is proprietary software for EnlightBook School Management System.

## 🆘 Support

For support, please contact the development team or create an issue in the repository.
