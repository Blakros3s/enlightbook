'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { ArrowDown, ArrowUp, Minus, LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon: LucideIcon;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  className?: string;
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info';
}

const variantStyles = {
  default: 'bg-card',
  primary: 'bg-gradient-to-br from-blue-500/10 to-indigo-500/10 border-blue-200/50 dark:border-blue-800/50',
  success: 'bg-gradient-to-br from-emerald-500/10 to-teal-500/10 border-emerald-200/50 dark:border-emerald-800/50',
  warning: 'bg-gradient-to-br from-amber-500/10 to-orange-500/10 border-amber-200/50 dark:border-amber-800/50',
  danger: 'bg-gradient-to-br from-rose-500/10 to-red-500/10 border-rose-200/50 dark:border-rose-800/50',
  info: 'bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border-cyan-200/50 dark:border-cyan-800/50',
};

const iconVariantStyles = {
  default: 'bg-muted text-muted-foreground',
  primary: 'bg-blue-500 text-white shadow-lg shadow-blue-500/30',
  success: 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/30',
  warning: 'bg-amber-500 text-white shadow-lg shadow-amber-500/30',
  danger: 'bg-rose-500 text-white shadow-lg shadow-rose-500/30',
  info: 'bg-cyan-500 text-white shadow-lg shadow-cyan-500/30',
};

export function StatCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
  trendValue,
  className,
  variant = 'default',
}: StatCardProps) {
  const TrendIcon = trend === 'up' ? ArrowUp : trend === 'down' ? ArrowDown : Minus;
  const trendColor = trend === 'up' ? 'text-emerald-600' : trend === 'down' ? 'text-rose-600' : 'text-muted-foreground';

  return (
    <Card className={cn('card-hover', variantStyles[variant], className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <div className={cn('p-2 rounded-lg', iconVariantStyles[variant])}>
          <Icon className="h-4 w-4" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold tracking-tight">{value}</div>
        {(description || trend) && (
          <div className="flex items-center gap-2 mt-1">
            {trend && (
              <div className={cn('flex items-center text-xs font-medium', trendColor)}>
                <TrendIcon className="h-3 w-3 mr-0.5" />
                {trendValue}
              </div>
            )}
            {description && (
              <p className="text-xs text-muted-foreground">{description}</p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
