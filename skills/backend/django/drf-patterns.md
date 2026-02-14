# Django REST Framework (DRF) Best Practices

## Serializer Patterns

### Base Serializer Class
```python
from rest_framework import serializers

class BaseSerializer(serializers.ModelSerializer):
    """Base serializer with common functionality"""
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    def get_field_names(self, declared_fields, info):
        fields = super().get_field_names(declared_fields, info)
        return list(fields) + ['created_at', 'updated_at']
```

### ViewSet Patterns
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

class BaseViewSet(viewsets.ModelViewSet):
    """Base ViewSet with common functionality"""
    
    def get_serializer_class(self):
        if self.action == 'list':
            return self.list_serializer_class
        elif self.action in ['create', 'update', 'partial_update']:
            return self.write_serializer_class
        return self.serializer_class
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle is_active status"""
        instance = self.get_object()
        instance.is_active = not instance.is_active
        instance.save(update_fields=['is_active'])
        return Response({'status': 'updated'})
```

## Authentication & Permissions

### JWT Authentication
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### Custom Permissions
```python
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Only allow owners to edit objects"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    """Only admins can write, others read-only"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
```

## Pagination & Filtering

### Custom Pagination
```python
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
class CursorPagination(pagination.CursorPagination):
    page_size = 20
    ordering = '-created_at'
```

### Filtering
```python
from django_filters import rest_framework as filters

class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    category = filters.CharFilter(field_name="category__slug")
    
    class Meta:
        model = Product
        fields = ['category', 'is_available']
```

## API Documentation

### OpenAPI with drf-spectacular
```python
# settings.py
INSTALLED_APPS = [
    # ...
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Your API',
    'DESCRIPTION': 'API description',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```
