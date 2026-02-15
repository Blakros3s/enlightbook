'use client';

import React from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Construction } from 'lucide-react';

export default function PlaceholderPage({ 
  title = "Coming Soon",
  description = "This feature is under development"
}: { 
  title?: string;
  description?: string;
}) {
  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <Card className="max-w-md w-full text-center">
            <CardHeader>
              <div className="mx-auto h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <Construction className="h-10 w-10 text-primary" />
              </div>
              <CardTitle className="text-2xl">{title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">{description}</p>
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
