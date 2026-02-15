'use client';

import React from 'react';
import { Sidebar } from './sidebar';
import { Header } from './header';
import { cn } from '@/lib/utils';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  return (
    <div className="min-h-screen bg-background">
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      
      <div
        className={cn(
          'transition-all duration-300 ease-in-out',
          sidebarOpen ? 'lg:ml-72' : 'lg:ml-20'
        )}
      >
        <Header 
          onMenuClick={() => setSidebarOpen(!sidebarOpen)} 
          isSidebarOpen={sidebarOpen}
        />
        
        <main className="p-4 lg:p-8 animate-fade-in">
          <div className="mx-auto max-w-7xl">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
