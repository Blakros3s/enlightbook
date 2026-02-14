# Next.js 14+ Architecture & Patterns

## Project Structure

### Recommended Directory Layout
```
nextjs_project/
├── app/                          # App Router (Next.js 14+)
│   ├── (auth)/                   # Route groups
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── register/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   ├── page.tsx              # Dashboard home
│   │   ├── products/
│   │   │   ├── page.tsx          # Product list
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx      # Product detail
│   │   │   └── loading.tsx       # Loading UI
│   │   └── settings/
│   │       └── page.tsx
│   ├── api/                      # Route handlers
│   │   ├── auth/
│   │   │   └── [...nextauth]/
│   │   │       └── route.ts
│   │   └── webhooks/
│   │       └── stripe/
│   │           └── route.ts
│   ├── layout.tsx                # Root layout
│   ├── page.tsx                  # Home page
│   ├── loading.tsx               # Global loading
│   ├── error.tsx                 # Global error
│   ├── not-found.tsx             # 404 page
│   └── globals.css
├── components/
│   ├── ui/                       # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── input.tsx
│   ├── forms/                    # Form components
│   │   ├── login-form.tsx
│   │   └── product-form.tsx
│   ├── layout/                   # Layout components
│   │   ├── header.tsx
│   │   ├── sidebar.tsx
│   │   └── footer.tsx
│   └── shared/                   # Shared components
│       ├── data-table.tsx
│       ├── pagination.tsx
│       └── search-input.tsx
├── lib/
│   ├── utils.ts                  # Utility functions
│   ├── api.ts                    # API client
│   ├── auth.ts                   # Auth utilities
│   └── constants.ts              # App constants
├── hooks/
│   ├── use-auth.ts
│   ├── use-products.ts
│   └── use-local-storage.ts
├── types/
│   ├── index.ts
│   ├── user.ts
│   └── product.ts
├── stores/
│   └── auth-store.ts             # Zustand store
├── styles/
│   └── globals.css
├── public/
│   ├── images/
│   └── fonts/
├── middleware.ts
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

## App Router Patterns

### Layout Pattern
```typescript
// app/layout.tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Providers } from '@/components/providers'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'My App',
  description: 'Description',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}

// app/(dashboard)/layout.tsx
import { Sidebar } from '@/components/layout/sidebar'
import { Header } from '@/components/layout/header'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
```

### Server Components Pattern
```typescript
// app/products/page.tsx (Server Component)
import { Suspense } from 'react'
import { ProductList } from '@/components/products/product-list'
import { ProductListSkeleton } from '@/components/products/product-list-skeleton'
import { getProducts } from '@/lib/api'

export const dynamic = 'force-dynamic' // or 'auto', 'force-static'
export const revalidate = 60 // Revalidate every 60 seconds

interface ProductsPageProps {
  searchParams: {
    page?: string
    category?: string
    search?: string
  }
}

export default async function ProductsPage({ 
  searchParams 
}: ProductsPageProps) {
  const page = Number(searchParams.page) || 1
  const category = searchParams.category
  const search = searchParams.search
  
  // Fetch on server
  const productsPromise = getProducts({ page, category, search })
  
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Products</h1>
      <Suspense fallback={<ProductListSkeleton />}>
        <ProductList promise={productsPromise} />
      </Suspense>
    </div>
  )
}

// components/products/product-list.tsx
'use client'

import { use } from 'react'
import { ProductCard } from './product-card'
import type { Product } from '@/types/product'

interface ProductListProps {
  promise: Promise<{ products: Product[]; total: number }>
}

export function ProductList({ promise }: ProductListProps) {
  const { products, total } = use(promise)
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  )
}
```

### Client Components Pattern
```typescript
// components/products/product-card.tsx
'use client'

import { useState } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { useCart } from '@/hooks/use-cart'
import type { Product } from '@/types/product'

interface ProductCardProps {
  product: Product
}

export function ProductCard({ product }: ProductCardProps) {
  const [isAdding, setIsAdding] = useState(false)
  const { addItem } = useCart()
  
  const handleAddToCart = async () => {
    setIsAdding(true)
    try {
      await addItem(product)
    } finally {
      setIsAdding(false)
    }
  }
  
  return (
    <div className="border rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
      <Link href={`/products/${product.id}`}>
        <div className="relative aspect-square">
          <Image
            src={product.image}
            alt={product.name}
            fill
            className="object-cover"
          />
        </div>
        <div className="p-4">
          <h3 className="font-semibold truncate">{product.name}</h3>
          <p className="text-gray-600">${product.price}</p>
        </div>
      </Link>
      <div className="p-4 pt-0">
        <Button 
          onClick={handleAddToCart}
          disabled={isAdding}
          className="w-full"
        >
          {isAdding ? 'Adding...' : 'Add to Cart'}
        </Button>
      </div>
    </div>
  )
}
```

## Data Fetching Patterns

### API Client Setup
```typescript
// lib/api.ts
import { cookies } from 'next/headers'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

interface FetchOptions extends RequestInit {
  requireAuth?: boolean
}

export async function apiClient<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const { requireAuth = true, ...fetchOptions } = options
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...fetchOptions.headers,
  }
  
  if (requireAuth) {
    const cookieStore = cookies()
    const token = cookieStore.get('access_token')?.value
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new APIError(
      error.message || 'API request failed',
      response.status,
      error
    )
  }
  
  return response.json()
}

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public data: any
  ) {
    super(message)
    this.name = 'APIError'
  }
}

// API functions
export function getProducts(params?: {
  page?: number
  category?: string
  search?: string
}) {
  const query = new URLSearchParams()
  if (params?.page) query.set('page', String(params.page))
  if (params?.category) query.set('category', params.category)
  if (params?.search) query.set('search', params.search)
  
  return apiClient(`/products?${query}`)
}

export function getProduct(id: string) {
  return apiClient(`/products/${id}`)
}
```

### TanStack Query Integration
```typescript
// lib/query-client.ts
import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

// components/providers.tsx
'use client'

import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { queryClient } from '@/lib/query-client'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}

// hooks/use-products.ts
'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getProducts, createProduct, updateProduct, deleteProduct } from '@/lib/api'
import type { Product } from '@/types/product'

export function useProducts(params?: {
  page?: number
  category?: string
  search?: string
}) {
  return useQuery({
    queryKey: ['products', params],
    queryFn: () => getProducts(params),
  })
}

export function useCreateProduct() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: createProduct,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
    },
  })
}

export function useUpdateProduct() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Product> }) =>
      updateProduct(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
      queryClient.invalidateQueries({ queryKey: ['product', variables.id] })
    },
  })
}
```

## State Management

### Zustand Store Pattern
```typescript
// stores/auth-store.ts
import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { User } from '@/types/user'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  // Actions
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  setUser: (user: User | null) => void
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
          })
          
          if (!response.ok) {
            throw new Error('Login failed')
          }
          
          const data = await response.json()
          set({ 
            user: data.user, 
            isAuthenticated: true,
            isLoading: false 
          })
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Login failed',
            isLoading: false 
          })
        }
      },
      
      logout: () => {
        set({ 
          user: null, 
          isAuthenticated: false,
          error: null 
        })
        // Clear persisted storage
        localStorage.removeItem('auth-store')
      },
      
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      
      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-store',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)

// stores/cart-store.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Product } from '@/types/product'

interface CartItem extends Product {
  quantity: number
}

interface CartState {
  items: CartItem[]
  isOpen: boolean
  
  addItem: (product: Product) => void
  removeItem: (productId: string) => void
  updateQuantity: (productId: string, quantity: number) => void
  clearCart: () => void
  toggleCart: () => void
  totalItems: () => number
  totalPrice: () => number
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],
      isOpen: false,
      
      addItem: (product) => {
        const items = get().items
        const existingItem = items.find((item) => item.id === product.id)
        
        if (existingItem) {
          set({
            items: items.map((item) =>
              item.id === product.id
                ? { ...item, quantity: item.quantity + 1 }
                : item
            ),
          })
        } else {
          set({ items: [...items, { ...product, quantity: 1 }] })
        }
      },
      
      removeItem: (productId) => {
        set({ items: get().items.filter((item) => item.id !== productId) })
      },
      
      updateQuantity: (productId, quantity) => {
        if (quantity <= 0) {
          get().removeItem(productId)
          return
        }
        
        set({
          items: get().items.map((item) =>
            item.id === productId ? { ...item, quantity } : item
          ),
        })
      },
      
      clearCart: () => set({ items: [] }),
      
      toggleCart: () => set({ isOpen: !get().isOpen }),
      
      totalItems: () =>
        get().items.reduce((total, item) => total + item.quantity, 0),
      
      totalPrice: () =>
        get().items.reduce(
          (total, item) => total + item.price * item.quantity,
          0
        ),
    }),
    {
      name: 'cart-store',
    }
  )
)
```

## Form Handling

### React Hook Form + Zod
```typescript
// components/forms/product-form.tsx
'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { useCreateProduct } from '@/hooks/use-products'

const productSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  description: z.string().min(10, 'Description must be at least 10 characters'),
  price: z.number().min(0.01, 'Price must be greater than 0'),
  stockQuantity: z.number().int().min(0, 'Stock cannot be negative'),
  category: z.string().min(1, 'Category is required'),
})

type ProductFormData = z.infer<typeof productSchema>

export function ProductForm() {
  const createProduct = useCreateProduct()
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<ProductFormData>({
    resolver: zodResolver(productSchema),
  })
  
  const onSubmit = async (data: ProductFormData) => {
    try {
      await createProduct.mutateAsync(data)
      reset()
    } catch (error) {
      console.error('Failed to create product:', error)
    }
  }
  
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Label htmlFor="name">Product Name</Label>
        <Input
          id="name"
          {...register('name')}
          error={errors.name?.message}
        />
      </div>
      
      <div>
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          {...register('description')}
          error={errors.description?.message}
        />
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="price">Price</Label>
          <Input
            id="price"
            type="number"
            step="0.01"
            {...register('price', { valueAsNumber: true })}
            error={errors.price?.message}
          />
        </div>
        
        <div>
          <Label htmlFor="stockQuantity">Stock Quantity</Label>
          <Input
            id="stockQuantity"
            type="number"
            {...register('stockQuantity', { valueAsNumber: true })}
            error={errors.stockQuantity?.message}
          />
        </div>
      </div>
      
      <div>
        <Label htmlFor="category">Category</Label>
        <Input
          id="category"
          {...register('category')}
          error={errors.category?.message}
        />
      </div>
      
      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Creating...' : 'Create Product'}
      </Button>
    </form>
  )
}
```
