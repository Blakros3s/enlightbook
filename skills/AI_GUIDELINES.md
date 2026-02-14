# AI Assistant Guidelines

## How to Use This Skills Library

### For Project Planning
1. **Start with**: `system-design/fundamentals.md`
2. **Review**: `templates/django-nextjs-project.md`
3. **Reference**: `architecture/fullstack-patterns.md`

### For Backend Development
- **Architecture**: `backend/django/architecture.md`
- **API Design**: `backend/django/drf-patterns.md`
- **Models**: Reference service layer and repository patterns

### For Frontend Development
- **Architecture**: `frontend/nextjs/architecture.md`
- **State Management**: Zustand patterns in architecture file
- **Data Fetching**: TanStack Query patterns

### For DevOps
- **Docker**: `devops/docker/containerization.md`
- **CI/CD**: `devops/ci-cd/pipeline.md`
- **Database**: `database/postgresql/schema-design.md` & `database/redis/caching-patterns.md`

### For Security
- **Security**: `security/best-practices.md`
- **API Security**: JWT and rate limiting patterns

## Code Generation Rules

### When Generating Django Code
1. Always use the project structure from `templates/`
2. Follow service layer pattern for business logic
3. Use proper type hints
4. Include docstrings with Args/Returns/Raises
5. Add appropriate database indexes
6. Implement proper error handling

### When Generating Next.js Code
1. Use App Router (Next.js 14+)
2. Separate Server and Client Components
3. Use proper TypeScript types
4. Implement TanStack Query for data fetching
5. Use Zustand for client state
6. Implement proper loading and error states

### When Generating Docker/Config Files
1. Use multi-stage builds for production
2. Include health checks
3. Use non-root users where possible
4. Optimize for layer caching
5. Include proper .dockerignore

## Common Prompts

### "Create a new Django app for [feature]"
```
Reference:
- backend/django/architecture.md (Service Layer, Repository Pattern)
- backend/django/drf-patterns.md (ViewSets, Serializers)
- api-design/rest-principles.md (URL structure, Response format)

Generate:
1. models.py with proper field types and indexes
2. serializers.py (List, Detail, Create/Update)
3. views.py or viewsets.py
4. services.py for business logic
5. urls.py
6. tests.py
```

### "Create a Next.js page for [feature]"
```
Reference:
- frontend/nextjs/architecture.md (App Router patterns)
- architecture/fullstack-patterns.md (Data flow)

Generate:
1. page.tsx (Server Component with data fetching)
2. components/[feature]-list.tsx (Client Component)
3. hooks/use-[feature].ts (TanStack Query)
4. types/[feature].ts (TypeScript interfaces)
```

### "Set up CI/CD pipeline"
```
Reference:
- devops/ci-cd/pipeline.md
- devops/docker/containerization.md

Generate:
1. .github/workflows/ci-cd.yml
2. Dockerfile optimizations
3. docker-compose configuration
4. Deployment scripts
```

## Quality Checklist

Before completing any task, verify:

### Backend
- [ ] Proper error handling with custom exceptions
- [ ] Input validation and sanitization
- [ ] Authentication and authorization checks
- [ ] Database query optimization (select_related, prefetch_related)
- [ ] API response format consistency
- [ ] Comprehensive test coverage

### Frontend
- [ ] TypeScript strict mode compliance
- [ ] Proper error boundaries
- [ ] Loading states for async operations
- [ ] Responsive design considerations
- [ ] Accessibility (ARIA labels, keyboard navigation)
- [ ] Form validation with user-friendly messages

### DevOps
- [ ] Environment variables documented
- [ ] Health checks implemented
- [ ] Logging configuration
- [ ] Security headers configured
- [ ] Backup strategies defined

## Anti-Patterns to Avoid

### Backend
- Business logic in views/serializers
- N+1 query problems
- Hardcoded secrets
- Raw SQL without parameterization
- Synchronous calls in async contexts

### Frontend
- Client-side data fetching for static content
- Prop drilling (use context/store instead)
- Large bundle sizes (no code splitting)
- No error handling for API calls
- Mutating state directly

### Database
- Missing indexes on foreign keys
- Storing passwords in plain text
- No connection pooling
- Long-running transactions
- SELECT * in production queries

## Testing Strategy

### Unit Tests
- Test business logic in services
- Test utility functions
- Mock external dependencies

### Integration Tests
- Test API endpoints
- Test database queries
- Test authentication flows

### E2E Tests
- Critical user journeys
- Cross-browser testing
- Mobile responsiveness

### Performance Tests
- Load testing with k6/Artillery
- Database query performance
- Frontend bundle analysis
