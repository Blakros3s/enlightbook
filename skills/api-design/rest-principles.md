# API Design Principles

## REST API Best Practices

### URL Structure
```
GET    /api/v1/users           # List users
POST   /api/v1/users           # Create user
GET    /api/v1/users/{id}      # Get user
PUT    /api/v1/users/{id}      # Update user (full)
PATCH  /api/v1/users/{id}      # Update user (partial)
DELETE /api/v1/users/{id}      # Delete user

# Nested resources
GET    /api/v1/users/{id}/orders     # List user's orders
POST   /api/v1/users/{id}/orders     # Create order for user
GET    /api/v1/users/{id}/orders/{orderId}  # Get specific order
```

### HTTP Status Codes
```
200 OK              # Success
201 Created         # Resource created
204 No Content      # Success, no body (DELETE)
400 Bad Request     # Validation error
401 Unauthorized    # Not authenticated
403 Forbidden       # No permission
404 Not Found       # Resource doesn't exist
409 Conflict        # Resource conflict
422 Unprocessable   # Validation failed
429 Too Many Requests # Rate limited
500 Server Error    # Unexpected error
```

### Request/Response Format
```json
// Request - Create user
POST /api/v1/users
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe"
}

// Success Response - 201 Created
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}

// Error Response - 400 Bad Request
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["This field is required."],
      "first_name": ["Must be at least 2 characters."]
    }
  }
}
```

### Pagination
```json
// Request
GET /api/v1/products?page=2&page_size=20

// Response
{
  "data": [
    { "id": "1", "name": "Product 1" },
    { "id": "2", "name": "Product 2" }
  ],
  "pagination": {
    "current_page": 2,
    "total_pages": 10,
    "total_items": 200,
    "page_size": 20,
    "has_next": true,
    "has_previous": true
  },
  "links": {
    "self": "/api/v1/products?page=2&page_size=20",
    "first": "/api/v1/products?page=1&page_size=20",
    "prev": "/api/v1/products?page=1&page_size=20",
    "next": "/api/v1/products?page=3&page_size=20",
    "last": "/api/v1/products?page=10&page_size=20"
  }
}
```

## Django REST Framework Implementation

```python
# api/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'data': data,
            'pagination': {
                'current_page': self.page.number,
                'total_pages': self.page.paginator.num_pages,
                'total_items': self.page.paginator.count,
                'page_size': self.get_page_size(self.request),
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
            },
            'links': {
                'self': self.request.build_absolute_uri(),
                'first': self.get_first_link(),
                'prev': self.get_previous_link(),
                'next': self.get_next_link(),
                'last': self.get_last_link(),
            }
        })

# api/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_active', 'price']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'price', 'name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateSerializer
        return ProductDetailSerializer
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        product = self.get_object()
        product.is_active = True
        product.save(update_fields=['is_active'])
        return Response({'status': 'product activated'})
    
    @action(detail=False)
    def featured(self, request):
        featured = Product.objects.filter(is_featured=True)[:10]
        serializer = ProductListSerializer(featured, many=True)
        return Response(serializer.data)
```
