'use client';

import React from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Construction } from 'lucide-react';

export default function AttendanceReportsPage() {
  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Attendance Reports</h1>
            <p className="text-muted-foreground">View and analyze attendance data</p>
          </div>
          
          <div className="flex items-center justify-center min-h-[50vh]">
            <Card className="max-w-md w-full text-center">
              <CardHeader>
                <div className="mx-auto h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <Construction className="h-10 w-10 text-primary" />
                </div>
                <CardTitle className="text-2xl">Coming Soon</CardTitle>
                <CardDescription>
                  Detailed attendance reports with analytics and insights are under development.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  This feature will include monthly summaries, defaulter lists, and trend analysis.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
