# Redis Caching & Message Queue

## Redis Configuration

### Django Redis Cache
```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        }
    },
    "sessions": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Session configuration
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "sessions"

# Cache time to live
CACHE_TTL = 60 * 15  # 15 minutes
```

## Caching Patterns

### View Caching
```python
from django.views.decorators.cache import cache_page
from django.core.cache import cache

# Method 1: Decorator (time-based)
@cache_page(60 * 15)  # 15 minutes
def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/list.html', {'products': products})

# Method 2: Template fragment caching
{% load cache %}
{% cache 500 sidebar %}
    .. sidebar ..
{% endcache %}

# Method 3: Low-level caching
def get_product(product_id):
    cache_key = f'product:{product_id}'
    product = cache.get(cache_key)
    
    if product is None:
        product = Product.objects.get(id=product_id)
        cache.set(cache_key, product, timeout=3600)
    
    return product
```

### Cache Invalidation Strategies
```python
# Pattern 1: Cache-aside with explicit invalidation
class ProductService:
    def update_product(self, product_id, data):
        product = Product.objects.get(id=product_id)
        
        for key, value in data.items():
            setattr(product, key, value)
        product.save()
        
        # Invalidate caches
        cache.delete(f'product:{product_id}')
        cache.delete('product_list')
        cache.delete(f'category_products:{product.category_id}')
    
    def delete_product(self, product_id):
        Product.objects.filter(id=product_id).delete()
        
        # Pattern 2: Wildcard deletion
        keys_to_delete = cache.keys(f'*product:{product_id}*')
        cache.delete_many(keys_to_delete)
```

## Message Queue with Celery

### Celery Configuration
```python
# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Task settings
CELERY_TASK_ALWAYS_EAGER = False  # Set True for testing
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# Result expiration
CELERY_RESULT_EXPIRES = 3600

# Beat schedule for periodic tasks
CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-sessions': {
        'task': 'apps.users.tasks.cleanup_sessions',
        'schedule': 3600.0,  # Every hour
    },
}
```

### Task Patterns
```python
# apps/notifications/tasks.py
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.core.mail import send_mail

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
)
def send_email_task(self, to_email, subject, body):
    """Send email with retry logic"""
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email='noreply@example.com',
            recipient_list=[to_email],
            fail_silently=False,
        )
    except Exception as exc:
        # Retry with exponential backoff
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            # Log failure after max retries
            logger.error(f"Failed to send email to {to_email} after 3 retries")
            raise

@shared_task
def process_bulk_operation(user_ids, operation):
    """Process bulk operations in chunks"""
    chunk_size = 100
    
    for i in range(0, len(user_ids), chunk_size):
        chunk = user_ids[i:i + chunk_size]
        
        # Process chunk
        for user_id in chunk:
            process_user_operation.delay(user_id, operation)

@shared_task
def generate_report(report_type, filters):
    """Generate reports asynchronously"""
    # Long-running task
    report_data = generate_report_data(report_type, filters)
    
    # Store result
    cache.set(f'report:{report_type}', report_data, timeout=86400)
    
    # Notify user
    notify_user.delay(
        user_id=filters['user_id'],
        message=f'Your {report_type} report is ready'
    )
```

## Real-time Features with WebSockets

### Django Channels Setup
```python
# settings.py
ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}

# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.user_group_name = f'user_{self.user.id}'
        
        # Join user group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave user group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'mark_read':
            await self.mark_notification_read(data['notification_id'])
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        Notification.objects.filter(
            id=notification_id,
            user=self.user
        ).update(is_read=True)
    
    async def notification_message(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': event['data']
        }))

# Send notification from anywhere
def send_user_notification(user_id, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{user_id}',
        {
            'type': 'notification_message',
            'data': {
                'message': message,
                'timestamp': timezone.now().isoformat()
            }
        }
    )
```
