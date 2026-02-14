# System Design Fundamentals

## Core Principles

### 1. Scalability
- **Horizontal Scaling**: Add more machines (preferred)
- **Vertical Scaling**: Add more power to existing machines
- **Trade-offs**: Cost, complexity, single point of failure

### 2. Reliability
- **Redundancy**: Multiple instances, data replication
- **Failover**: Automatic switching to backup
- **Graceful Degradation**: Partial functionality during failures

### 3. Availability
- **SLA Targets**: 99.9% (8.76h downtime/year), 99.99% (52m/year)
- **Load Balancing**: Distribute traffic evenly
- **Health Checks**: Automated instance monitoring

### 4. Performance
- **Latency**: Time for single request (target: <200ms)
- **Throughput**: Requests per second (target: 10K+ RPS)
- **Caching Strategy**: Multi-layer caching approach

## Design Methodology

### 4S Approach
1. **Scope**: Define functional requirements (features)
2. **Sketch**: High-level design diagram
3. **Scale**: Estimate traffic, storage, bandwidth
4. **Solidify**: Deep dive into components

### Key Questions to Ask
- What's the read-to-write ratio?
- What's the expected QPS (queries per second)?
- What's the data volume over 5 years?
- Is real-time required or eventual consistency OK?
- What's the geographic distribution?

## Common Components

### Load Balancer
- **Types**: Layer 4 (transport), Layer 7 (application)
- **Algorithms**: Round-robin, least connections, IP hash
- **Tools**: Nginx, HAProxy, AWS ALB, CloudFlare

### CDN (Content Delivery Network)
- **Purpose**: Static asset delivery, DDoS protection
- **Cache Rules**: Time-based, query string variations
- **Providers**: CloudFlare, AWS CloudFront, Fastly

### Message Queue
- **Use Cases**: Async processing, decoupling, load leveling
- **Patterns**: Pub/Sub, Work Queue, Request/Reply
- **Tools**: RabbitMQ, Apache Kafka, AWS SQS, Redis

### Database Scaling
- **Read Replicas**: Offload read traffic
- **Sharding**: Horizontal partitioning by key
- **Partitioning**: Vertical splitting by feature

## Django + Next.js Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Web App    │  │  Mobile App  │  │  Third Party │       │
│  │   (Next.js)  │  │   (React)    │  │    APIs      │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
└─────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    CDN (CloudFlare)                         │
│         Static Assets + DDoS Protection + SSL               │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                 Load Balancer (Nginx)                       │
│            SSL Termination + Rate Limiting                  │
└───────────────┬───────────────────────────┬─────────────────┘
                │                           │
    ┌───────────▼──────────┐   ┌───────────▼──────────┐
    │   Next.js Servers    │   │   Next.js Servers    │
    │   (SSR + Static)     │   │   (SSR + Static)     │
    │   ┌──────────────┐   │   │   ┌──────────────┐   │
    │   │  App Router  │   │   │   │  App Router  │   │
    │   │  Server Comps│   │   │   │  Server Comps│   │
    │   └──────────────┘   │   │   └──────────────┘   │
    └───────────┬──────────┘   └───────────┬──────────┘
                │                           │
                └───────────┬───────────────┘
                            │
                ┌───────────▼──────────┐
                │    Django API GW     │
                │   (DRF + Channels)   │
                └───────────┬──────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌───────▼────────┐  ┌───────▼────────┐
│  Django App 1  │  │  Django App 2  │  │  Django App 3  │
│  (Auth/Users)  │  │ (Core Business)│  │ (Notifications)│
└───────┬────────┘  └───────┬────────┘  └───────┬────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
    ┌───────────────────────┼───────────────────────┐
    │                       │                       │
┌───▼──────────┐   ┌───────▼────────┐   ┌──────────▼──────┐
│ PostgreSQL   │   │     Redis      │   │ Elasticsearch   │
│ (Primary DB) │   │(Cache + Queue) │   │  (Search + Logs)│
└──────────────┘   └────────────────┘   └─────────────────┘
```

## Capacity Planning

### Traffic Estimates
- **Daily Active Users (DAU)**: 100,000
- **Requests per User per Day**: 50
- **Total Requests per Day**: 5,000,000
- **Peak RPS**: 5,000,000 / 86,400 * 3 (peak factor) ≈ 175 RPS
- **Average RPS**: 5,000,000 / 86,400 ≈ 58 RPS

### Storage Estimates
- **User Data**: 10KB per user × 1M users = 10GB
- **Media Files**: 100MB per day × 365 = 36.5GB/year
- **Logs**: 1GB per day × 365 = 365GB/year
- **Backup Strategy**: 3x production data = ~1.2TB

### Bandwidth Estimates
- **API Traffic**: 1KB per request × 5M requests = 5GB/day
- **Static Assets**: 2MB per session × 100K sessions = 200GB/day
- **Total Outbound**: ~205GB/day = 6.15TB/month

## Common Patterns

### Microservices vs Monolith

**Start with Monolith when:**
- Team size < 10 developers
- Time to market is critical
- Uncertain about domain boundaries

**Move to Microservices when:**
- Different scaling requirements per service
- Multiple teams with independent deployments
- Need for diverse technology stacks

### Event-Driven Architecture
```
User Action → Event Bus → Multiple Consumers
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
Analytics   Notifications   Cache Update
```

### CQRS (Command Query Responsibility Segregation)
- **Commands**: Write operations (Django ORM)
- **Queries**: Read operations (Optimized views, Elasticsearch)
- **Benefits**: Independent scaling, specialized optimization

## Django + Next.js Specific Patterns

### Server-Side Rendering (SSR) Flow
```
User Request → Next.js Server → Django API → Database
                    ↓
              Render HTML
                    ↓
              Send to Client
                    ↓
              Hydrate React
```

### API-First Design
1. Design API contracts (OpenAPI/Swagger)
2. Implement Django DRF endpoints
3. Generate TypeScript types from API spec
4. Build Next.js frontend with type safety

### Real-time Communication
```
Client ← WebSocket → Django Channels ← Redis
  ↓                                       ↓
React Query                         Celery Workers
```
