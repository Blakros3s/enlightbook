# Scalability Patterns

## Horizontal Scaling Strategies

### Stateless Application Design
```python
# Good: Stateless function
def process_order(order_data: dict) -> dict:
    """No dependency on local state"""
    result = validate_order(order_data)
    return transform_order(result)

# Bad: Stateful dependency
class OrderProcessor:
    def __init__(self):
        self.cache = {}  # DON'T: Shared state per instance
    
    def process(self, order_data):
        if order_data['id'] in self.cache:
            return self.cache[order_data['id']]
```

### Session Management
```python
# settings.py - Use Redis for session storage
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
```

## Database Scaling

### Read Replicas
```python
# routers.py
class PrimaryReplicaRouter:
    def db_for_read(self, model, **hints):
        # Round-robin between replicas
        return random.choice(['replica1', 'replica2'])
    
    def db_for_write(self, model, **hints):
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == 'default'

# settings.py
DATABASE_ROUTERS = ['myapp.routers.PrimaryReplicaRouter']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'HOST': 'primary.db.internal',
    },
    'replica1': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'HOST': 'replica1.db.internal',
    },
    'replica2': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'HOST': 'replica2.db.internal',
    }
}
```

### Database Sharding
```python
# Sharding by user_id
class UserShardRouter:
    def db_for_read(self, model, **hints):
        if hasattr(model, 'user_id'):
            shard = self.get_shard_for_user(hints['user_id'])
            return f'shard{shard}'
        return 'default'
    
    def get_shard_for_user(self, user_id: int) -> int:
        """Consistent hashing for shard selection"""
        return user_id % 4  # 4 shards
    
    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)
```

## Caching Strategies

### Multi-Layer Caching
```
┌─────────────────────────────────────┐
│         Client Browser              │
│    (Service Worker + LocalStorage)  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         CDN Edge                    │
│    (Static Assets, API Responses)   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Application Cache           │
│    (Redis - Query Results)          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Database Cache              │
│    (PostgreSQL Buffer Pool)         │
└─────────────────────────────────────┘
```

### Cache Patterns

#### Cache-Aside (Lazy Loading)
```python
from django.core.cache import cache
from django.db import models

class ProductManager(models.Manager):
    def get_cached(self, product_id: int) -> 'Product':
        cache_key = f"product:{product_id}"
        
        # Try cache first
        product = cache.get(cache_key)
        if product:
            return product
        
        # Cache miss - fetch from DB
        try:
            product = self.get(pk=product_id)
            cache.set(cache_key, product, timeout=3600)
            return product
        except self.model.DoesNotExist:
            return None
```

#### Write-Through
```python
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update cache on write
        cache_key = f"product:{self.id}"
        cache.set(cache_key, self, timeout=3600)
```

#### Cache Warming
```python
from celery import shared_task

@shared_task
def warm_product_cache():
    """Pre-populate cache with hot products"""
    hot_products = Product.objects.filter(
        view_count__gte=1000
    ).select_related('category')
    
    for product in hot_products:
        cache_key = f"product:{product.id}"
        cache.set(cache_key, product, timeout=7200)
```

## Rate Limiting

### Token Bucket Algorithm
```python
import time
import redis
from django.conf import settings

class TokenBucketRateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def is_allowed(self, key: str, rate: int, capacity: int) -> bool:
        """
        Check if request is allowed under rate limit.
        
        Args:
            key: Unique identifier (user_id, IP, etc.)
            rate: Tokens added per second
            capacity: Maximum bucket capacity
        """
        lua_script = """
            local key = KEYS[1]
            local rate = tonumber(ARGV[1])
            local capacity = tonumber(ARGV[2])
            local now = tonumber(ARGV[3])
            
            local last_update = redis.call('hget', key, 'last_update') or now
            local tokens = tonumber(redis.call('hget', key, 'tokens') or capacity)
            
            local time_passed = now - last_update
            local new_tokens = math.min(capacity, tokens + (time_passed * rate))
            
            if new_tokens >= 1 then
                new_tokens = new_tokens - 1
                redis.call('hset', key, 'tokens', new_tokens)
                redis.call('hset', key, 'last_update', now)
                redis.call('expire', key, 3600)
                return 1
            else
                redis.call('hset', key, 'tokens', new_tokens)
                redis.call('hset', key, 'last_update', now)
                return 0
            end
        """
        
        now = time.time()
        result = self.redis.eval(
            lua_script, 1, key, rate, capacity, now
        )
        return bool(result)
```

### Django Middleware
```python
from django.http import JsonResponse
from django.core.cache import cache

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limiter = TokenBucketRateLimiter(cache.client.get_client())
    
    def __call__(self, request):
        # Get identifier (authenticated user or IP)
        if request.user.is_authenticated:
            key = f"rate_limit:user:{request.user.id}"
            rate = 100  # 100 req/s for authenticated
        else:
            key = f"rate_limit:ip:{request.META.get('REMOTE_ADDR')}"
            rate = 10   # 10 req/s for anonymous
        
        if not self.rate_limiter.is_allowed(key, rate=rate, capacity=rate*2):
            return JsonResponse(
                {'error': 'Rate limit exceeded'},
                status=429
            )
        
        return self.get_response(request)
```

## Load Balancing

### Algorithm Selection
```python
from enum import Enum
from typing import List
import random

class LoadBalanceStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"
    WEIGHTED = "weighted"

class LoadBalancer:
    def __init__(self, servers: List[str], strategy: LoadBalanceStrategy):
        self.servers = servers
        self.strategy = strategy
        self.current_index = 0
        self.connections = {server: 0 for server in servers}
    
    def get_server(self, client_ip: str = None) -> str:
        if self.strategy == LoadBalanceStrategy.ROUND_ROBIN:
            server = self.servers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.servers)
            return server
        
        elif self.strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return min(self.connections, key=self.connections.get)
        
        elif self.strategy == LoadBalanceStrategy.IP_HASH:
            hash_val = hash(client_ip) % len(self.servers)
            return self.servers[hash_val]
        
        elif self.strategy == LoadBalanceStrategy.WEIGHTED:
            # Weighted round-robin
            weighted_list = []
            for i, server in enumerate(self.servers):
                weight = self.get_server_weight(server)
                weighted_list.extend([i] * weight)
            
            idx = random.choice(weighted_list)
            return self.servers[idx]
    
    def get_server_weight(self, server: str) -> int:
        """Return weight based on server capacity"""
        # Could be based on CPU, memory, etc.
        return 1
```

## Auto-Scaling

### Metrics for Scaling
```python
class ScalingMetrics:
    """Key metrics to monitor for auto-scaling"""
    
    CPU_UTILIZATION = "cpu_utilization"          # Target: 70%
    MEMORY_UTILIZATION = "memory_utilization"    # Target: 80%
    REQUEST_QUEUE_DEPTH = "request_queue_depth"  # Target: <100
    RESPONSE_TIME_P95 = "response_time_p95"      # Target: <500ms
    ERROR_RATE = "error_rate"                    # Target: <1%
```

### Kubernetes HPA Configuration
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: django-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: django-app
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max
```
