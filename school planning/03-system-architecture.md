# System Architecture & Technology Stack

## Architecture Overview

This is a comprehensive documentation of the complete system architecture for the **School Management System** built with **Django (Backend)** and **Next.js (Frontend)**.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT TIER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Web Browser │  │  Mobile App  │  │  Admin Panel │          │
│  │  (Next.js)   │  │  (React      │  │  (Next.js)   │          │
│  │              │  │   Native)    │  │              │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                  │
└─────────┼─────────────────┼─────────────────┼──────────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
          ┌─────────────────▼────────────────────┐
          │         API GATEWAY / CDN            │
          │  (Cloudflare / AWS CloudFront)       │
          └─────────────────┬────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                    APPLICATION TIER                            │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              NEXT.JS FRONTEND                           │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │  │
│  │  │  Pages   │ │  API     │ │  Server  │ │  Static  │  │  │
│  │  │  (SSR)   │ │  Routes  │ │  Actions │ │  Assets  │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │  │
│  └────────────────────────┬────────────────────────────────┘  │
│                           │                                   │
│  ┌────────────────────────▼────────────────────────────────┐  │
│  │           DJANGO REST FRAMEWORK API                     │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │  │
│  │  │  Auth    │ │  Student │ │  Academic│ │  Finance │  │  │
│  │  │  Service │ │  Service │ │  Service │ │  Service │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │  │
│  │  │  Exam    │ │  Attend  │ │  Comm.   │ │  Report  │  │  │
│  │  │  Service │ │  Service │ │  Service │ │  Service │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │  │
│  └────────────────────────┬────────────────────────────────┘  │
└───────────────────────────┼───────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                      DATA TIER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  PostgreSQL  │  │    Redis     │  │   AWS S3     │        │
│  │  (Primary)   │  │  (Cache)     │  │  (Storage)   │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│                 SUPPORTING SERVICES                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Celery     │  │  WebSocket   │  │   Email      │        │
│  │   (Tasks)    │  │  (Channels)  │  │   (SES/SMTP) │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└───────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend Stack

#### Core Framework
```json
{
  "framework": "Next.js 14+",
  "features": [
    "App Router (Server Components)",
    "Server Actions",
    "API Routes",
    "Static Site Generation (SSG)",
    "Server-Side Rendering (SSR)",
    "Incremental Static Regeneration (ISR)"
  ]
}
```

#### State Management
- **Global State**: Zustand (lightweight, no boilerplate)
- **Server State**: TanStack Query (React Query v5)
- **Form State**: React Hook Form
- **URL State**: Next.js built-in router params

#### UI Framework
```javascript
{
  "components": "Shadcn UI + Radix UI primitives",
  "styling": "Tailwind CSS",
  "animations": "Framer Motion",
  "icons": "Lucide React",
  "charts": "Recharts / Chart.js"
}
```

#### Data Fetching
- **HTTP Client**: Axios with interceptors
- **Cache Management**: TanStack Query
- **Real-time**: Socket.IO client
- **File Upload**: react-dropzone + axios

#### Form Handling & Validation
- **Forms**: React Hook Form
- **Validation**: Zod schemas
- **Date Handling**: date-fns
- **Rich Text**: TipTap / Quill

#### Authentication Client
```typescript
// Auth Context
- JWT token management
- Automatic token refresh
- Role-based route guards
- Session persistence (httpOnly cookies)
```

### Backend Stack

#### Core Framework
```python
{
  "framework": "Django 4.2 LTS",
  "api_framework": "Django REST Framework 3.14+",
  "python_version": "3.11+",
  "asgi_server": "Uvicorn",
  "wsgi_server": "Gunicorn"
}
```

#### Database
```python
{
  "primary_db": "PostgreSQL 15+",
  "features": [
    "JSONB fields for flexible data",
    "Full-text search",
    "Triggers and stored procedures",
    "Connection pooling (pgBouncer)"
  ]
}
```

#### Authentication & Authorization
- **JWT**: djangorestframework-simplejwt
- **2FA**: django-otp
- **Social Auth**: django-allauth (optional)
- **Permissions**: Built-in Django permissions + custom

#### API Documentation
- **Schema**: drf-spectacular (OpenAPI 3.0)
- **Interactive Docs**: Swagger UI / ReDoc
- **Versioning**: URL path versioning (/api/v1/)

#### File Storage
- **Development**: Local filesystem
- **Production**: AWS S3 / Google Cloud Storage
- **Library**: django-storages
- **Media Processing**: Pillow (images), python-magic (file type detection)

#### Caching & Session
```python
{
  "cache_backend": "Redis 7+",
  "session_backend": "Redis (django-redis)",
  "use_cases": [
    "API response caching",
    "Session storage",
    "Token blacklisting",
    "Rate limiting counters",
    "Real-time data (bus locations)"
  ]
}
```

#### Background Tasks
```python
{
  "task_queue": "Celery 5+",
  "message_broker": "Redis",
  "result_backend": "Redis",
  "scheduler": "Celery Beat",
  "monitoring": "Flower"
}
```

**Celery Tasks**:
- Email sending (async)
- Report generation (PDF/Excel)
- Data imports/exports
- Attendance reminders
- Result publishing notifications
- Database backups

#### Real-Time Communication
```python
{
  "websockets": "Django Channels 4+",
  "channel_layer": "channels_redis",
  "use_cases": [
    "Live bus tracking",
    "Chat/messaging",
    "Notifications",
    "Real-time dashboards"
  ]
}
```

### Database Architecture

#### Primary Database: PostgreSQL

**Schema Design Principles**:
1. Normalized to 3NF (Third Normal Form)
2. Denormalize only for performance (cached summaries)
3. Use JSONB for flexible metadata
4. Proper indexing strategy

**Key Tables**:
```sql
-- Core User Management
users (CustomUser)
teachers, students, principals, accountants, drivers

-- Academic Structure
academic_years, semesters, classes, sections, subjects

-- Student Academic
student_subject_enrollments, student_results, student_attendance

-- Financial
fee_categories, student_bills, student_payments, payment_allocations

-- Examination
exams, exam_details, student_results, student_overall_results

-- Communication
messages, communications, posts, discussion_posts

-- Audit & History
security_audit_logs, result_modification_logs, transaction_histories
```

**Database Optimizations**:
```sql
-- Indexes for common queries
CREATE INDEX idx_student_class ON students(class_code_id);
CREATE INDEX idx_attendance_date ON daily_attendance(date, student_id);
CREATE INDEX idx_results_exam ON student_results(exam_detail_id, student_id);
CREATE INDEX idx_payments_student_date ON student_payments(student_id, date DESC);

-- Composite indexes
CREATE INDEX idx_teacher_assignments 
  ON teacher_class_assignments(teacher_id, semester_id, class_assigned_id);

-- Partial indexes for active records
CREATE INDEX idx_active_students 
  ON students(class_code_id) WHERE is_active = TRUE;
```

#### Cache Layer: Redis

**Data Structures**:
```redis
# Session storage
session:<session_key> → JSON serialized session data

# Token blacklist
blacklist:token:<jti> → timestamp

# Rate limiting
ratelimit:login:<ip_address> → counter (expires in 5 minutes)

# Cached queries
cache:subjects:all → List of subjects (expires 1 hour)
cache:class:<class_id>:students → Student list (expires 5 minutes)

# Real-time data
buslocation:<driver_id> → {lat, lon, timestamp} (expires 5 minutes)
```

### Infrastructure & Deployment

#### Development Environment
```yaml
docker-compose.yml:
  services:
    - django: Backend API
    - nextjs: Frontend app
    - postgres: Database
    - redis: Cache & Celery broker
    - celery: Background worker
    - flower: Celery monitoring
```

#### Production Environment

**Hosting Options**:
1. **AWS**
   - EC2: Django + Gunicorn
   - RDS PostgreSQL
   - ElastiCache Redis
   - S3: Static files
   - CloudFront: CDN
   - SES: Email

2. **Vercel + Railway** (Alternative)
   - Vercel: Next.js hosting
   - Railway: Django API + PostgreSQL + Redis

3. **DigitalOcean** (Cost-effective)
   - Droplets: Django + Next.js
   - Managed PostgreSQL
   - Managed Redis
   - Spaces: Object storage

**Production Architecture**:
```
Internet
   │
   ▼
[Load Balancer]
   │
   ├─► [Next.js Server 1] ──┐
   ├─► [Next.js Server 2] ──┼─► [Redis Cache]
   │                         │
   ├─► [Django API 1] ───────┤
   ├─► [Django API 2] ───────┼─► [PostgreSQL Master]
   │                         │         │
   ├─► [Celery Worker 1] ────┤         ├─► [Read Replica 1]
   └─► [Celery Worker 2] ────┘         └─► [Read Replica 2]
```

### Security Architecture

#### Network Security
- **HTTPS Only**: Enforce SSL/TLS
- **CORS**: Whitelist frontend domains only
- **Firewall**: Only expose ports 80, 443
- **VPN**: Database accessible only via VPN
- **DDoS Protection**: Cloudflare / AWS Shield

#### Application Security
```python
# Django Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

#### Data Security
- **Encryption at Rest**: Database encryption (AWS RDS)
- **Encryption in Transit**: TLS 1.3
- **Sensitive Fields**: Encrypted using django-cryptography
- **PII Handling**: Anonymization for analytics
- **Backups**: Daily encrypted backups to S3

### Monitoring & Logging

#### Application Monitoring
```python
{
  "error_tracking": "Sentry",
  "performance_monitoring": "New Relic / DataDog",
  "uptime_monitoring": "UptimeRobot / Pingdom"
}
```

#### Logging Stack
```python
{
  "log_aggregation": "ELK Stack (Elasticsearch, Logstash, Kibana)",
  "alternative": "AWS CloudWatch Logs",
  "log_levels": {
    "development": "DEBUG",
    "staging": "INFO",
    "production": "WARNING"
  }
}
```

**Log Structure**:
```json
{
  "timestamp": "2024-02-14T10:30:00Z",
  "level": "ERROR",
  "service": "django-api",
  "user_id": 12345,
  "request_id": "abc-123-def",
  "ip_address": "192.168.1.1",
  "endpoint": "/api/students/",
  "method": "POST",
  "status_code": 500,
  "error": "Database connection timeout",
  "stack_trace": "..."
}
```

### API Design Principles

#### RESTful API Standards
```
GET    /api/v1/students          # List students
POST   /api/v1/students          # Create student
GET    /api/v1/students/:id      # Get student details
PUT    /api/v1/students/:id      # Full update
PATCH  /api/v1/students/:id      # Partial update
DELETE /api/v1/students/:id      # Delete student
```

#### Response Format
```json
{
  "success": true,
  "data": {
    "id": 123,
    "name": "John Doe",
    ...
  },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 150
  },
  "message": "Student retrieved successfully"
}
```

#### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["Enter a valid email address"],
      "age": ["Must be at least 5 years old"]
    }
  },
  "request_id": "abc-123-def"
}
```

#### API Versioning
- **Strategy**: URL path versioning
- **Current**: /api/v1/
- **Deprecation**: 6 months notice, maintain 2 versions

### Performance Optimization

#### Frontend Optimization
1. **Code Splitting**: Automatic with Next.js
2. **Image Optimization**: next/image component
3. **Lazy Loading**: React.lazy() for heavy components
4. **Prefetching**: Next.js link prefetching
5. **Bundle Analysis**: @next/bundle-analyzer

#### Backend Optimization
1. **Database Query Optimization**
   - Use select_related() and prefetch_related()
   - Avoid N+1 queries
   - Database indexing strategy

2. **Caching Strategy**
   ```python
   # View-level caching
   @cache_page(60 * 15)  # 15 minutes
   
   # Template fragment caching
   {% cache 500 sidebar %}
   
   # Low-level cache API
   cache.set('key', 'value', timeout=300)
   ```

3. **API Response Compression**: gzip middleware

4. **Connection Pooling**: pgBouncer for PostgreSQL

#### CDN Strategy
- Static assets (JS, CSS, images) served via CDN
- Cloudflare or CloudFront
- Edge caching for API responses (GET requests)

### Scalability Considerations

#### Horizontal Scaling
```
# Django API
- Stateless design (JWT, no server-side sessions)
- Load balancer distributes requests
- Scale to N instances

# Next.js Frontend
- Deploy to multiple regions (Vercel Edge)
- Auto-scaling based on traffic

# Database
- Read replicas for SELECT queries
- Master-slave replication
- Sharding for multi-tenant (by school)
```

#### Vertical Scaling
- Upgrade server resources (CPU, RAM)
- Database parameter tuning
- Connection pool sizing

### Development Workflow

#### Version Control
```
main (production)
  └── develop (staging)
      ├── feature/authentication
      ├── feature/fee-management
      └── bugfix/attendance-issue
```

#### CI/CD Pipeline
```yaml
# .github/workflows/ci-cd.yml
1. Code Push → GitHub
2. Run Tests (pytest, jest)
3. Lint Check (flake8, eslint)
4. Build Docker Images
5. Push to Registry (DockerHub / ECR)
6. Deploy to Staging
7. Run E2E Tests
8. Manual Approval
9. Deploy to Production
```

#### Testing Strategy
```python
# Backend Tests
- Unit Tests: pytest (80% coverage target)
- Integration Tests: Django TestCase
- API Tests: DRF APITestCase
- Load Tests: Locust

# Frontend Tests
- Unit Tests: Jest + React Testing Library
- Integration Tests: Cypress / Playwright
- Visual Regression: Percy / Chromatic
```

## Technology Comparison & Decisions

### Why Django?
✅ Mature ecosystem with ORM
✅ Built-in admin panel
✅ Strong security features
✅ Excellent documentation
✅ Perfect for complex business logic

### Why Next.js?
✅ Server-side rendering (SEO + performance)
✅ API routes (BFF pattern)
✅ File-based routing
✅ Built-in optimization
✅ Great developer experience

### Why PostgreSQL?
✅ ACID compliance
✅ Advanced features (JSONB, full-text search)
✅ Strong community
✅ Reliable and performant
✅ Great for relational data

### Why Redis?
✅ Fast in-memory operations
✅ Multiple data structures
✅ Pub/Sub for real-time
✅ Perfect for caching
✅ Session storage

## Estimated Infrastructure Costs

### Small School (500 students)
```
AWS:
- EC2 t3.medium × 2: $60/month
- RDS PostgreSQL db.t3.medium: $60/month
- ElastiCache Redis: $40/month
- S3 + CloudFront: $20/month
- SES: $5/month
Total: ~$185/month
```

### Medium School (1500 students)
```
AWS:
- EC2 t3.large × 3: $180/month
- RDS PostgreSQL db.m5.large: $140/month
- ElastiCache Redis m5.large: $90/month
- S3 + CloudFront: $50/month
- SES: $10/month
Total: ~$470/month
```
