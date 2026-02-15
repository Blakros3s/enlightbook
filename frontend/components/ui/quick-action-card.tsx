'use client';

import React from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { LucideIcon, ArrowRight, MoreHorizontal } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface QuickActionCardProps {
  title: string;
  description?: string;
  icon: LucideIcon;
  href?: string;
  onClick?: () => void;
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info';
  badge?: string;
  className?: string;
}

const variantStyles = {
  default: 'hover:border-primary/50',
  primary: 'hover:border-blue-500/50 hover:bg-blue-50/50 dark:hover:bg-blue-950/20',
  success: 'hover:border-emerald-500/50 hover:bg-emerald-50/50 dark:hover:bg-emerald-950/20',
  warning: 'hover:border-amber-500/50 hover:bg-amber-50/50 dark:hover:bg-amber-950/20',
  danger: 'hover:border-rose-500/50 hover:bg-rose-50/50 dark:hover:bg-rose-950/20',
  info: 'hover:border-cyan-500/50 hover:bg-cyan-50/50 dark:hover:bg-cyan-950/20',
};

const iconVariantStyles = {
  default: 'bg-muted text-muted-foreground',
  primary: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
  success: 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400',
  warning: 'bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400',
  danger: 'bg-rose-100 text-rose-600 dark:bg-rose-900/30 dark:text-rose-400',
  info: 'bg-cyan-100 text-cyan-600 dark:bg-cyan-900/30 dark:text-cyan-400',
};

export function QuickActionCard({
  title,
  description,
  icon: Icon,
  href,
  onClick,
  variant = 'default',
  badge,
  className,
}: QuickActionCardProps) {
  const content = (
    <Card
      className={cn(
        'group cursor-pointer transition-all duration-300 hover:shadow-lg card-hover',
        variantStyles[variant],
        className
      )}
      onClick={onClick}
    >
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className={cn('p-3 rounded-xl transition-transform duration-300 group-hover:scale-110', iconVariantStyles[variant])}>
            <Icon className="h-6 w-6" />
          </div>
          
          {badge && (
            <Badge variant="secondary" className="text-xs">
              {badge}
            </Badge>
          )}
        </div>
        
        <div className="mt-4">
          <h3 className="font-semibold text-lg">{title}</h3>
          {description && (
            <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
              {description}
            </p>
          )}
        </div>

        <div className="mt-4 flex items-center text-sm font-medium text-primary opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          Get started
          <ArrowRight className="ml-1 h-4 w-4 transition-transform duration-300 group-hover:translate-x-1" />
        </div>
      </CardContent>
    </Card>
  );

  if (href) {
    return (
      <Link href={href} className="block">
        {content}
      </Link>
    );
  }

  return content;
}

interface QuickActionsGridProps {
  actions: QuickActionCardProps[];
  title?: string;
  className?: string;
}

export function QuickActionsGrid({ actions, title, className }: QuickActionsGridProps) {
  return (
    <div className={cn('space-y-4', className)}>
      {title && (
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">{title}</h2>
        </div>
      )}
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {actions.map((action, index) => (
          <QuickActionCard key={index} {...action} />
        ))}
      </div>
    </div>
  );
}
