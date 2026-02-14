# Architectural Patterns

## Full-Stack Integration Patterns

### 1. BFF (Backend for Frontend) Pattern
```
Next.js App
    ↓
BFF API (Next.js Route Handlers)
    ↓
Microservices / Django API
    ↓
Database
```

Use when:
- Multiple frontend apps (web, mobile, desktop)
- Different data needs per frontend
- Frontend teams need API control

### 2. API Gateway Pattern
```
Clients → API Gateway → Services
            ↓
    ┌───────┼───────┐
    ↓       ↓       ↓
  Auth    Core    Notifications
```

Benefits:
- Single entry point
- Authentication at gateway
- Rate limiting
- Request routing
- Protocol translation

### 3. Event-Driven Architecture
```
User Action → Event Bus → Multiple Consumers
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
Analytics   Notifications   Audit Log
```

Good for:
- Decoupled services
- Async processing
- Event sourcing
- Audit trails

## Component Communication

### Django → Next.js Data Flow
```
1. User Request
   ↓
2. Next.js Server Component
   ↓
3. API Call (Server-side)
   ↓
4. Django DRF Endpoint
   ↓
5. Database Query
   ↓
6. JSON Response
   ↓
7. Server Component Render
   ↓
8. HTML + Hydration
   ↓
9. Interactive Client App
```

### Authentication Flow
```
Login Request
    ↓
Next.js API Route
    ↓
Django /auth/login
    ↓
Validate Credentials
    ↓
Generate JWT Tokens
    ↓
Set HTTP-only Cookies
    ↓
Return User Data
    ↓
Store in Zustand (client)
```

## Data Synchronization Patterns

### Optimistic UI Updates
```typescript
// Update UI immediately, sync with server
const useUpdateProduct = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: updateProduct,
    onMutate: async (newProduct) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['product', newProduct.id] })
      
      // Snapshot previous value
      const previousProduct = queryClient.getQueryData(['product', newProduct.id])
      
      // Optimistically update
      queryClient.setQueryData(['product', newProduct.id], newProduct)
      
      return { previousProduct }
    },
    onError: (err, newProduct, context) => {
      // Rollback on error
      queryClient.setQueryData(
        ['product', newProduct.id],
        context?.previousProduct
      )
    },
    onSettled: (newProduct) => {
      // Refetch after error or success
      queryClient.invalidateQueries({ queryKey: ['product', newProduct?.id] })
    },
  })
}
```

### Real-time Synchronization
```python
# Django Signal
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=Product)
def notify_product_update(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        'product_updates',
        {
            'type': 'product_update',
            'data': {
                'id': str(instance.id),
                'name': instance.name,
                'price': str(instance.price),
                'updated_at': instance.updated_at.isoformat(),
            }
        }
    )

# Next.js WebSocket Hook
export function useProductUpdates() {
  const queryClient = useQueryClient()
  
  useEffect(() => {
    const ws = new WebSocket('wss://api.example.com/ws/products/')
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      // Update React Query cache
      queryClient.setQueryData(
        ['product', data.id],
        data
      )
    }
    
    return () => ws.close()
  }, [queryClient])
}
```

## Error Handling Strategy

### Layered Error Handling
```
Layer 1: Database (IntegrityError, DoesNotExist)
    ↓
Layer 2: Django (ValidationError, PermissionDenied)
    ↓
Layer 3: DRF (APIException)
    ↓
Layer 4: Next.js API Route (APIError)
    ↓
Layer 5: Client (Error Boundary, Toast notifications)
```

### Global Error Boundary
```typescript
// app/error.tsx
'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log to error tracking service
    console.error('Application error:', error)
  }, [error])

  return (
    <div className="flex flex-col items-center justify-center min-h-[400px]">
      <h2 className="text-2xl font-bold mb-4">Something went wrong!</h2>
      <p className="text-gray-600 mb-6">{error.message}</p>
      <Button onClick={reset}>Try again</Button>
    </div>
  )
}
```

## Performance Patterns

### Incremental Static Regeneration (ISR)
```typescript
// app/products/[id]/page.tsx
export const revalidate = 60 // Regenerate every 60 seconds

export async function generateStaticParams() {
  const products = await getFeaturedProducts()
  
  return products.map((product) => ({
    id: product.id,
  }))
}

export default async function ProductPage({ params }: { params: { id: string } }) {
  const product = await getProduct(params.id)
  
  if (!product) {
    notFound()
  }
  
  return <ProductDetail product={product} />
}
```

### Streaming & Suspense
```typescript
// app/dashboard/page.tsx
import { Suspense } from 'react'
import { DashboardSkeleton, ChartsSkeleton } from '@/components/skeletons'

export default function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>
      
      <Suspense fallback={<DashboardSkeleton />}>
        <DashboardStats />
      </Suspense>
      
      <Suspense fallback={<ChartsSkeleton />}>
        <RevenueCharts />
      </Suspense>
      
      <Suspense fallback={<ChartsSkeleton />}>
        <UserAnalytics />
      </Suspense>
    </div>
  )
}
```
