# PostgreSQL Database Design

## Schema Design Principles

### Normalization vs Denormalization
- **3NF (Third Normal Form)**: Start here for OLTP systems
- **Denormalize**: When read performance critical, use materialized views

### Django Model Best Practices
```python
from django.db import models

class Product(models.Model):
    """Example well-designed model"""
    
    # Use appropriate field types
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(blank=True)
    
    # Use Decimal for money, not Float
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        db_index=True
    )
    
    # Foreign keys with related_name
    category = models.ForeignKey(
        'Category',
        on_delete=models.PROTECT,
        related_name='products'
    )
    
    # Boolean with db_index for filtering
    is_active = models.BooleanField(default=True, db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['price', 'is_active']),
        ]
        ordering = ['-created_at']
```

## Indexing Strategies

### When to Index
- **Always**: Primary keys, foreign keys
- **Frequently queried**: Fields in WHERE, JOIN, ORDER BY
- **Range queries**: Date fields, numeric ranges
- **Search**: Full-text search fields

### Index Types
```sql
-- B-tree (default) - good for equality and range
CREATE INDEX idx_user_email ON users(email);

-- Partial index - only active users
CREATE INDEX idx_active_users ON users(email) WHERE is_active = true;

-- Composite index - order matters
CREATE INDEX idx_order_status_date ON orders(status, created_at);

-- GIN index - for JSONB and arrays
CREATE INDEX idx_product_metadata ON products USING GIN (metadata);
```

## Query Optimization

### N+1 Problem Solution
```python
# BAD: N+1 queries
for product in Product.objects.all():
    print(product.category.name)  # Query per product

# GOOD: select_related (single JOIN)
products = Product.objects.select_related('category')

# GOOD: prefetch_related (separate query + Python join)
products = Product.objects.prefetch_related('tags', 'reviews')

# For Many-to-Many with filter
products = Product.objects.prefetch_related(
    Prefetch('reviews', queryset=Review.objects.filter(rating__gte=4))
)
```

### QuerySet Optimization
```python
# Only fetch needed fields
Product.objects.only('id', 'name', 'price')

# Defer heavy fields
Product.objects.defer('description', 'large_json_field')

# Use values/values_list for simple data
Product.objects.values('id', 'name')
Product.objects.values_list('id', flat=True)

# Annotate instead of calculating in Python
from django.db.models import Count, Avg
products = Product.objects.annotate(
    review_count=Count('reviews'),
    avg_rating=Avg('reviews__rating')
)
```

## Connection Pooling

### PgBouncer Configuration
```ini
; pgbouncer.ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
listen_port = 6432
listen_addr = 127.0.0.1
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

; Pool settings
pool_mode = transaction
max_client_conn = 10000
default_pool_size = 25
min_pool_size = 10
reserve_pool_size = 5
reserve_pool_timeout = 3

; Timeouts
server_idle_timeout = 600
server_lifetime = 3600
client_idle_timeout = 0
client_login_timeout = 60
```

## Django Database Settings
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost',
        'PORT': '5432',
        
        # Connection pooling
        'CONN_MAX_AGE': 60,
        
        # Connection options
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',
        }
    }
}
```
