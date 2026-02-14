# Testing Strategy

## Django Testing

### Test Structure
```
apps/
└── users/
    └── tests/
        ├── __init__.py
        ├── conftest.py           # pytest fixtures
        ├── factories.py          # Model factories
        ├── test_models.py
        ├── test_services.py      # Business logic tests
        ├── test_views.py         # API tests
        └── test_integration.py   # Integration tests
```

### Model Testing
```python
# tests/test_models.py
import pytest
from django.core.exceptions import ValidationError
from apps.users.models import User

@pytest.mark.django_db
class TestUserModel:
    def test_user_creation(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        assert user.email == 'test@example.com'
        assert user.is_active is True
        assert user.is_staff is False
    
    def test_user_email_normalization(self):
        user = User.objects.create_user(
            email='TEST@EXAMPLE.COM',
            password='testpass123'
        )
        assert user.email == 'test@example.com'
    
    def test_user_without_email_raises_error(self):
        with pytest.raises(ValueError, match='Email is required'):
            User.objects.create_user(email='', password='testpass123')
```

### Service Testing
```python
# tests/test_services.py
import pytest
from unittest.mock import Mock, patch
from apps.orders.services import OrderService
from apps.orders.models import Order

@pytest.mark.django_db
class TestOrderService:
    @pytest.fixture
    def order_service(self, user):
        return OrderService(user=user)
    
    @pytest.fixture
    def valid_order_data(self):
        return {
            'items': [
                {'product_id': '1', 'quantity': 2},
                {'product_id': '2', 'quantity': 1}
            ],
            'shipping_address': {
                'street': '123 Main St',
                'city': 'New York',
                'zip': '10001'
            }
        }
    
    def test_create_order_success(self, order_service, valid_order_data):
        order = order_service.create_order(**valid_order_data)
        
        assert order.status == 'pending'
        assert order.items.count() == 2
    
    def test_create_order_insufficient_stock(self, order_service):
        data = {
            'items': [{'product_id': '1', 'quantity': 9999}],
            'shipping_address': {}
        }
        
        with pytest.raises(ValidationError, match='Insufficient stock'):
            order_service.create_order(**data)
    
    @patch('apps.orders.tasks.send_order_confirmation_email.delay')
    def test_order_confirmation_email_sent(self, mock_task, order_service, valid_order_data):
        order = order_service.create_order(**valid_order_data)
        
        mock_task.assert_called_once_with(order.id)
```

### API Testing
```python
# tests/test_views.py
import pytest
from rest_framework.test import APIClient
from rest_framework import status

@pytest.mark.django_db
class TestProductAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def authenticated_client(self, api_client, user):
        api_client.force_authenticate(user=user)
        return api_client
    
    def test_list_products(self, api_client, products):
        response = api_client.get('/api/v1/products/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == len(products)
    
    def test_create_product_requires_auth(self, api_client):
        response = api_client.post('/api/v1/products/', {
            'name': 'New Product',
            'price': 99.99
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_product_success(self, authenticated_client):
        response = authenticated_client.post('/api/v1/products/', {
            'name': 'New Product',
            'description': 'Product description',
            'price': 99.99,
            'stock_quantity': 100
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Product'
```

### Fixtures and Factories
```python
# tests/factories.py
import factory
from apps.users.models import User
from apps.products.models import Product, Category

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
    
    name = factory.Faker('word')
    slug = factory.Sequence(lambda n: f'category-{n}')

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
    
    name = factory.Faker('product_name')
    slug = factory.Sequence(lambda n: f'product-{n}')
    description = factory.Faker('text')
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    stock_quantity = factory.Faker('random_int', min=0, max=1000)
    category = factory.SubFactory(CategoryFactory)
    is_active = True

# conftest.py
import pytest
from .factories import UserFactory, ProductFactory

@pytest.fixture
def user(db):
    return UserFactory()

@pytest.fixture
def admin_user(db):
    return UserFactory(is_staff=True, is_superuser=True)

@pytest.fixture
def products(db):
    return ProductFactory.create_batch(10)
```

## Next.js Testing

### Component Testing with Vitest
```typescript
// components/__tests__/button.test.tsx
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from '../button'

describe('Button', () => {
  it('renders correctly', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })
  
  it('handles click events', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    
    fireEvent.click(screen.getByText('Click me'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
  
  it('shows loading state', () => {
    render(<Button isLoading>Loading</Button>)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })
  
  it('is disabled when loading', () => {
    render(<Button isLoading>Loading</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
```

### Hook Testing
```typescript
// hooks/__tests__/use-auth.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useLogin } from '../use-auth'
import { server } from '@/mocks/server'
import { http, HttpResponse } from 'msw'

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  })
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

describe('useLogin', () => {
  it('logs in successfully', async () => {
    server.use(
      http.post('/api/auth/login', () => {
        return HttpResponse.json({
          user: { id: '1', email: 'test@example.com' }
        })
      })
    )
    
    const { result } = renderHook(() => useLogin(), {
      wrapper: createWrapper()
    })
    
    act(() => {
      result.current.mutate({
        email: 'test@example.com',
        password: 'password'
      })
    })
    
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    
    expect(result.current.data).toEqual({
      user: { id: '1', email: 'test@example.com' }
    })
  })
  
  it('handles login error', async () => {
    server.use(
      http.post('/api/auth/login', () => {
        return new HttpResponse(
          JSON.stringify({ error: 'Invalid credentials' }),
          { status: 401 }
        )
      })
    )
    
    const { result } = renderHook(() => useLogin(), {
      wrapper: createWrapper()
    })
    
    act(() => {
      result.current.mutate({
        email: 'test@example.com',
        password: 'wrong'
      })
    })
    
    await waitFor(() => expect(result.current.isError).toBe(true))
    
    expect(result.current.error?.message).toBe('Invalid credentials')
  })
})
```

### E2E Testing with Playwright
```typescript
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test('user can log in', async ({ page }) => {
    await page.goto('/login')
    
    await page.fill('[name="email"]', 'user@example.com')
    await page.fill('[name="password"]', 'password')
    await page.click('button[type="submit"]')
    
    await expect(page).toHaveURL('/dashboard')
    await expect(page.locator('text=Welcome back')).toBeVisible()
  })
  
  test('shows error on invalid credentials', async ({ page }) => {
    await page.goto('/login')
    
    await page.fill('[name="email"]', 'user@example.com')
    await page.fill('[name="password"]', 'wrong')
    await page.click('button[type="submit"]')
    
    await expect(page.locator('text=Invalid credentials')).toBeVisible()
  })
  
  test('user can log out', async ({ page, context }) => {
    // Login first
    await page.goto('/login')
    await page.fill('[name="email"]', 'user@example.com')
    await page.fill('[name="password"]', 'password')
    await page.click('button[type="submit"]')
    
    // Logout
    await page.click('[data-testid="user-menu"]')
    await page.click('text=Log out')
    
    await expect(page).toHaveURL('/login')
  })
})
```

## Test Configuration

### pytest Configuration
```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
python_files = tests.py test_*.py *_tests.py
addopts = 
    --verbose
    --tb=short
    --cov=apps
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
```

### Vitest Configuration
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
      ]
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})
```

## CI Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test
        run: pytest --cov=apps --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run unit tests
        run: npm run test:unit -- --coverage
      
      - name: Run E2E tests
        run: |
          npx playwright install
          npm run test:e2e
```
