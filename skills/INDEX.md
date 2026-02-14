# Skills Library Index

Complete documentation index for Django + Next.js full-stack development.

## Quick Reference

### Getting Started
1. **New Project?** → `templates/django-nextjs-project.md`
2. **Architecture Overview** → `architecture/fullstack-patterns.md`
3. **AI Guidelines** → `AI_GUIDELINES.md`

### By Technology Stack

#### Backend (Django)
- **Architecture** → `backend/django/architecture.md`
- **DRF/API** → `backend/django/drf-patterns.md`
- **Configuration** → `system-design/fundamentals.md` (Django + Next.js Architecture section)

#### Frontend (Next.js)
- **Architecture** → `frontend/nextjs/architecture.md`
- **Data Fetching** → State management and TanStack Query patterns
- **Forms** → React Hook Form + Zod patterns

#### Database
- **PostgreSQL** → `database/postgresql/schema-design.md`
- **Redis/Caching** → `database/redis/caching-patterns.md`
- **Scaling** → `system-design/scalability-patterns.md`

#### DevOps
- **Docker** → `devops/docker/containerization.md`
- **CI/CD** → `devops/ci-cd/pipeline.md`
- **System Design** → `system-design/fundamentals.md`

#### Security & Testing
- **Security** → `security/best-practices.md`
- **Testing** → `testing/strategies.md`
- **API Design** → `api-design/rest-principles.md`

## Usage Patterns

### For LLM/AI Code Generation

When prompting an AI assistant, reference these files:

**Example Prompt:**
```
Create a new Django app for order management following:
- Backend patterns from: skills/backend/django/architecture.md
- API standards from: skills/api-design/rest-principles.md
- Include: models, serializers, viewsets, services, and tests
```

**Example Prompt:**
```
Build a Next.js product listing page using:
- Server Components pattern from: skills/frontend/nextjs/architecture.md
- Data fetching with TanStack Query
- Include: loading states, error handling, and pagination
```

### For Human Reference

Each file contains:
- **Code examples** - Production-ready patterns
- **Best practices** - Industry standards
- **Anti-patterns** - What to avoid
- **Configuration** - Setup instructions

## File Structure Overview

```
skills/
├── README.md                          # Overview
├── AI_GUIDELINES.md                   # AI assistant instructions
├── INDEX.md                           # This file
│
├── system-design/
│   ├── fundamentals.md                # Core design principles
│   └── scalability-patterns.md        # Scaling strategies
│
├── backend/
│   └── django/
│       ├── architecture.md            # Django patterns
│       └── drf-patterns.md            # DRF best practices
│
├── frontend/
│   └── nextjs/
│       └── architecture.md            # Next.js 14+ patterns
│
├── database/
│   ├── postgresql/
│   │   └── schema-design.md           # Database design
│   └── redis/
│       └── caching-patterns.md        # Caching & queues
│
├── devops/
│   ├── docker/
│   │   └── containerization.md        # Docker setup
│   └── ci-cd/
│       └── pipeline.md                # GitHub Actions
│
├── api-design/
│   └── rest-principles.md             # API standards
│
├── architecture/
│   └── fullstack-patterns.md          # Integration patterns
│
├── testing/
│   └── strategies.md                  # Testing approach
│
├── security/
│   └── best-practices.md              # Security guide
│
└── templates/
    └── django-nextjs-project.md       # Project template
```

## Key Principles

1. **Modularity** - Each file focuses on one concern
2. **Copy-Paste Ready** - Code examples are production-ready
3. **Stack-Specific** - Tailored for Django + Next.js
4. **Best Practices** - Follows industry standards
5. **Comprehensive** - Covers full development lifecycle

## Updates & Maintenance

This library should be:
- Updated with new framework versions
- Extended with new patterns as discovered
- Refined based on project experience
- Shared across team members

## License

Use freely for any project. Adapt patterns as needed.
