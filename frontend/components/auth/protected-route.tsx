'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from './auth-provider';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: string[];
  fallback?: React.ReactNode;
}

export function ProtectedRoute({ 
  children, 
  allowedRoles, 
  fallback 
}: ProtectedRouteProps) {
  const { user, isLoading, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Not authenticated
  if (!isAuthenticated) {
    return fallback || null;
  }

  // Check role permissions
  if (allowedRoles && user) {
    const hasPermission = allowedRoles.some(role => user.roles.includes(role));
    
    if (!hasPermission) {
      return (
        <div className="flex flex-col items-center justify-center min-h-screen p-4">
          <h1 className="text-2xl font-bold text-destructive mb-4">Access Denied</h1>
          <p className="text-muted-foreground mb-4">
            You don&apos;t have permission to access this page.
          </p>
          <button 
            onClick={() => router.push('/dashboard')}
            className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
          >
            Go to Dashboard
          </button>
        </div>
      );
    }
  }

  return <>{children}</>;
}

// Role-specific route wrappers
export function AdminRoute({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute allowedRoles={['master', 'principal']}>
      {children}
    </ProtectedRoute>
  );
}

export function TeacherRoute({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute allowedRoles={['master', 'principal', 'coordinator', 'teacher']}>
      {children}
    </ProtectedRoute>
  );
}

export function StudentRoute({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute allowedRoles={['master', 'principal', 'coordinator', 'teacher', 'student']}>
      {children}
    </ProtectedRoute>
  );
}

export function AccountantRoute({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute allowedRoles={['master', 'principal', 'accountant']}>
      {children}
    </ProtectedRoute>
  );
}
