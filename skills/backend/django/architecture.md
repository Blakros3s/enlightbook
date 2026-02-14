# Django Architecture & Patterns

## Project Structure

### Recommended Directory Layout
```
django_project/
├── apps/                           # All Django applications
│   ├── __init__.py
│   ├── users/                      # User management app
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── managers.py             # Custom model managers
│   │   ├── models.py
│   │   ├── serializers.py          # DRF serializers
│   │   ├── services.py             # Business logic layer
│   │   ├── signals.py
│   │   ├── tasks.py                # Celery tasks
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       ├── test_services.py
│   │       └── test_views.py
│   ├── core/                       # Core business logic
│   ├── notifications/
│   ├── payments/
│   └── api/                        # API versioning & routing
│       ├── __init__.py
│       ├── v1/
│       │   ├── __init__.py
│       │   ├── urls.py
│       │   └── routers.py
│       └── v2/
├── config/                         # Project configuration
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                 # Base settings
│   │   ├── local.py                # Local development
│   │   ├── production.py           # Production settings
│   │   └── test.py                 # Test settings
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── common/                         # Shared utilities
│   ├── __init__.py
│   ├── exceptions.py
│   ├── models.py                   # Abstract base models
│   ├── pagination.py
│   ├── permissions.py
│   ├── throttling.py
│   └── utils.py
├── media/                          # User uploads
├── static/                         # Static files
├── templates/                      # Django templates
├── locale/                         # Translations
├── requirements/
│   ├── base.txt
│   ├── local.txt
│   └── production.txt
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── entrypoint.sh
├── manage.py
├── pytest.ini
├── setup.cfg
└── pyproject.toml
```

## Configuration Management

### Split Settings Pattern
```python
# config/settings/base.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    # Local apps
    'apps.users',
    'apps.core',
]

# ... base configuration

# config/settings/local.py
from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'myapp_local'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# config/settings/production.py
from .base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

## Model Architecture

### Abstract Base Models
```python
# common/models.py
from django.db import models
import uuid
from django.utils import timezone

class BaseModel(models.Model):
    """Abstract base model with common fields"""
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']

class SoftDeleteModel(BaseModel):
    """Model with soft delete capability"""
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def delete(self, soft=True, *args, **kwargs):
        if soft:
            self.is_active = False
            self.deleted_at = timezone.now()
            self.save(update_fields=['is_active', 'deleted_at'])
        else:
            super().delete(*args, **kwargs)
    
    def restore(self):
        self.is_active = True
        self.deleted_at = None
        self.save(update_fields=['is_active', 'deleted_at'])

class AuditableModel(BaseModel):
    """Model with audit tracking"""
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated'
    )
    
    class Meta:
        abstract = True
```

### Custom Model Manager Pattern
```python
# apps/users/managers.py
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)
    
    def active(self):
        """Return only active users"""
        return self.filter(is_active=True)
    
    def with_recent_activity(self, days=30):
        """Return users active in last N days"""
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(last_login__gte=cutoff)

class ActiveManager(models.Manager):
    """Manager that only returns active objects"""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
```

### Model Implementation
```python
# apps/users/models.py
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from common.models import BaseModel
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """Custom user model with email as username"""
    
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Status fields
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Use custom manager
    objects = UserManager()
    active_users = ActiveManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'user'
        verbose_name_plural = 'users'
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['is_verified', 'created_at']),
        ]
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def initials(self):
        """Return user initials for avatar"""
        first = self.first_name[0].upper() if self.first_name else ''
        last = self.last_name[0].upper() if self.last_name else ''
        return f"{first}{last}" or self.email[0].upper()
```

## Service Layer Pattern

### Business Logic Services
```python
# apps/core/services.py
from typing import Optional, List
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Order, Product
from .tasks import send_order_confirmation_email

class OrderService:
    """Service class for order business logic"""
    
    def __init__(self, user=None):
        self.user = user
    
    @transaction.atomic
    def create_order(self, items: List[dict], shipping_address: dict) -> Order:
        """
        Create a new order with validation and inventory check.
        
        Args:
            items: List of {'product_id': int, 'quantity': int}
            shipping_address: Dict with address details
        
        Returns:
            Created Order instance
        
        Raises:
            ValidationError: If validation fails
        """
        # Validate items
        if not items:
            raise ValidationError("Order must contain at least one item")
        
        # Calculate totals and validate inventory
        total_amount = 0
        order_items = []
        
        for item_data in items:
            product = self._get_product(item_data['product_id'])
            quantity = item_data['quantity']
            
            if quantity > product.stock_quantity:
                raise ValidationError(
                    f"Insufficient stock for {product.name}. "
                    f"Available: {product.stock_quantity}"
                )
            
            total_amount += product.price * quantity
            order_items.append({
                'product': product,
                'quantity': quantity,
                'price': product.price
            })
        
        # Create order
        order = Order.objects.create(
            user=self.user,
            total_amount=total_amount,
            shipping_address=shipping_address,
            status='pending'
        )
        
        # Create order items and update inventory
        for item in order_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )
            
            # Decrement stock
            item['product'].stock_quantity -= item['quantity']
            item['product'].save(update_fields=['stock_quantity'])
        
        # Send confirmation email asynchronously
        send_order_confirmation_email.delay(order.id)
        
        return order
    
    def _get_product(self, product_id: int) -> Product:
        """Fetch product or raise error"""
        try:
            return Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            raise ValidationError(f"Product {product_id} not found")
    
    @transaction.atomic
    def cancel_order(self, order_id: int, reason: str) -> Order:
        """Cancel order and restore inventory"""
        try:
            order = Order.objects.select_related().get(
                id=order_id, 
                user=self.user
            )
        except Order.DoesNotExist:
            raise ValidationError("Order not found")
        
        if order.status in ['shipped', 'delivered']:
            raise ValidationError("Cannot cancel shipped or delivered orders")
        
        # Restore inventory
        for item in order.items.all():
            item.product.stock_quantity += item.quantity
            item.product.save(update_fields=['stock_quantity'])
        
        order.status = 'cancelled'
        order.cancellation_reason = reason
        order.save(update_fields=['status', 'cancellation_reason'])
        
        return order
```

## Repository Pattern

### Abstract Repository
```python
# common/repositories.py
from typing import TypeVar, Generic, List, Optional
from django.db.models import Model, QuerySet

T = TypeVar('T', bound=Model)

class BaseRepository(Generic[T]):
    """Generic repository for database operations"""
    
    def __init__(self, model_class: type[T]):
        self.model_class = model_class
    
    def get_by_id(self, id: str) -> Optional[T]:
        """Get single entity by ID"""
        try:
            return self.model_class.objects.get(pk=id)
        except self.model_class.DoesNotExist:
            return None
    
    def get_all(self) -> QuerySet[T]:
        """Get all entities"""
        return self.model_class.objects.all()
    
    def filter(self, **kwargs) -> QuerySet[T]:
        """Filter entities"""
        return self.model_class.objects.filter(**kwargs)
    
    def create(self, **kwargs) -> T:
        """Create new entity"""
        return self.model_class.objects.create(**kwargs)
    
    def update(self, instance: T, **kwargs) -> T:
        """Update entity"""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save(update_fields=kwargs.keys())
        return instance
    
    def delete(self, instance: T) -> None:
        """Delete entity"""
        instance.delete()
    
    def exists(self, **kwargs) -> bool:
        """Check if entity exists"""
        return self.model_class.objects.filter(**kwargs).exists()

# Usage
class ProductRepository(BaseRepository[Product]):
    def __init__(self):
        super().__init__(Product)
    
    def get_in_stock(self) -> QuerySet[Product]:
        return self.filter(stock_quantity__gt=0)
    
    def get_by_category(self, category_id: str) -> QuerySet[Product]:
        return self.filter(category_id=category_id, is_active=True)
```
