'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import { authApi } from '@/lib/api';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  roles: string[];
  primary_role: string;
  two_factor_enabled: boolean;
  phone_number?: string;
  address?: string;
  date_of_birth?: string;
  profile_picture?: string;
  last_login?: string;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<boolean>;
  updateUser: (userData: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Check if user is already logged in on mount
  useEffect(() => {
    const initAuth = async () => {
      const accessToken = Cookies.get('access_token');
      
      if (accessToken) {
        try {
          const userData = await authApi.getCurrentUser();
          setUser(userData);
        } catch (error) {
          // Token might be expired, try to refresh
          const refreshed = await refreshToken();
          if (!refreshed) {
            // Clear tokens if refresh failed
            Cookies.remove('access_token');
            Cookies.remove('refresh_token');
          }
        }
      }
      
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    
    try {
      const response = await authApi.login({ username, password });
      
      // Store tokens in cookies
      Cookies.set('access_token', response.access, { 
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        expires: 1 / 96 // 15 minutes
      });
      
      Cookies.set('refresh_token', response.refresh, { 
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        expires: 7 // 7 days
      });
      
      setUser(response.user);
      
      // Redirect based on role
      const role = response.user.primary_role;
      if (role === 'student') {
        router.push('/student/dashboard');
      } else if (role === 'teacher') {
        router.push('/teacher/dashboard');
      } else {
        router.push('/dashboard');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    
    try {
      const refreshToken = Cookies.get('refresh_token');
      if (refreshToken) {
        await authApi.logout(refreshToken);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear tokens regardless of API success
      Cookies.remove('access_token');
      Cookies.remove('refresh_token');
      setUser(null);
      setIsLoading(false);
      router.push('/login');
    }
  };

  const refreshToken = async (): Promise<boolean> => {
    const refresh = Cookies.get('refresh_token');
    
    if (!refresh) {
      return false;
    }
    
    try {
      const response = await authApi.refreshToken(refresh);
      
      Cookies.set('access_token', response.access, { 
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        expires: 1 / 96 // 15 minutes
      });
      
      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      return false;
    }
  };

  const updateUser = (userData: Partial<User>) => {
    setUser(prev => prev ? { ...prev, ...userData } : null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        logout,
        refreshToken,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}
