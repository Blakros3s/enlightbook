'use client';

import React from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { StatCard } from '@/components/ui/stat-card';
import { QuickActionsGrid } from '@/components/ui/quick-action-card';
import { useAuth } from '@/components/auth/auth-provider';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  Users,
  GraduationCap,
  Wallet,
  Calendar,
  FileText,
  Settings,
  UserPlus,
  BookOpen,
  TrendingUp,
  DollarSign,
  CheckCircle,
  Clock,
  AlertCircle,
  ArrowUpRight,
  ArrowDownRight,
  School,
  Award,
  Bell,
  Activity,
} from 'lucide-react';
import Link from 'next/link';

function AdminDashboard() {
  const { user } = useAuth();

  const quickActions = [
    {
      title: 'Add User',
      description: 'Create new user accounts',
      icon: UserPlus,
      href: '/users/new',
      variant: 'primary' as const,
    },
    {
      title: 'Manage Classes',
      description: 'Organize classes and sections',
      icon: School,
      href: '/academic/classes',
      variant: 'success' as const,
    },
    {
      title: 'Fee Structure',
      description: 'Configure fee categories',
      icon: DollarSign,
      href: '/finance/fees',
      variant: 'warning' as const,
    },
    {
      title: 'Exam Schedule',
      description: 'Create and manage exams',
      icon: Calendar,
      href: '/exams/list',
      variant: 'info' as const,
    },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Welcome back, {user?.first_name}!</h1>
          <p className="text-muted-foreground mt-1">
            Here&apos;s what&apos;s happening in your school today.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20">
            <Activity className="h-3 w-3 mr-1" />
            System Online
          </Badge>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Students"
          value="1,248"
          description="Across all classes"
          icon={GraduationCap}
          trend="up"
          trendValue="+12%"
          variant="primary"
        />
        <StatCard
          title="Total Teachers"
          value="64"
          description="Active staff"
          icon={Users}
          trend="up"
          trendValue="+3"
          variant="success"
        />
        <StatCard
          title="Fee Collection"
          value="₹8.4L"
          description="This month"
          icon={Wallet}
          trend="up"
          trendValue="+18%"
          variant="warning"
        />
        <StatCard
          title="Attendance Rate"
          value="94.2%"
          description="Average today"
          icon={CheckCircle}
          trend="neutral"
          trendValue="0%"
          variant="info"
        />
      </div>

      {/* Quick Actions */}
      <QuickActionsGrid title="Quick Actions" actions={quickActions} />

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-7">
        {/* Recent Activity */}
        <Card className="lg:col-span-4">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Latest updates across the system</CardDescription>
              </div>
              <Button variant="outline" size="sm">View All</Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { action: 'New student registered', user: 'Rahul Sharma', time: '2 min ago', type: 'success' },
                { action: 'Fee payment received', user: 'Priya Patel', time: '15 min ago', type: 'info' },
                { action: 'Attendance marked', user: 'Class 10-A', time: '1 hour ago', type: 'default' },
                { action: 'Exam scheduled', user: 'Mathematics Final', time: '3 hours ago', type: 'warning' },
              ].map((item, index) => (
                <div key={index} className="flex items-start gap-4 p-3 rounded-lg hover:bg-muted/50 transition-colors">
                  <div className={`h-2 w-2 mt-2 rounded-full ${
                    item.type === 'success' ? 'bg-emerald-500' :
                    item.type === 'info' ? 'bg-blue-500' :
                    item.type === 'warning' ? 'bg-amber-500' :
                    'bg-slate-500'
                  }`} />
                  <div className="flex-1">
                    <p className="text-sm font-medium">{item.action}</p>
                    <p className="text-xs text-muted-foreground">{item.user}</p>
                  </div>
                  <span className="text-xs text-muted-foreground">{item.time}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Upcoming Events */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Upcoming Events</CardTitle>
                <CardDescription>Next 7 days</CardDescription>
              </div>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { title: 'Parent-Teacher Meeting', date: 'Tomorrow', time: '10:00 AM', type: 'meeting' },
                { title: 'Annual Sports Day', date: 'Dec 15', time: '9:00 AM', type: 'event' },
                { title: 'Mid-term Exam Starts', date: 'Dec 18', time: 'All Day', type: 'exam' },
              ].map((event, index) => (
                <div key={index} className="flex items-center gap-4 p-3 rounded-lg border hover:border-primary/50 transition-colors">
                  <div className={`h-12 w-12 rounded-lg flex items-center justify-center ${
                    event.type === 'exam' ? 'bg-rose-100 text-rose-600' :
                    event.type === 'meeting' ? 'bg-blue-100 text-blue-600' :
                    'bg-amber-100 text-amber-600'
                  }`}>
                    {event.type === 'exam' ? <FileText className="h-5 w-5" /> :
                     event.type === 'meeting' ? <Users className="h-5 w-5" /> :
                     <Award className="h-5 w-5" />}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{event.title}</p>
                    <p className="text-xs text-muted-foreground">{event.date} at {event.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Fee Overview */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Fee Collection Overview</CardTitle>
            <CardDescription>Monthly collection statistics</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Collected</span>
                <span className="font-medium">₹8.4L / ₹12L</span>
              </div>
              <Progress value={70} className="h-2" />
            </div>
            <div className="grid grid-cols-3 gap-4 pt-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-emerald-600">₹8.4L</p>
                <p className="text-xs text-muted-foreground">Collected</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-amber-600">₹2.8L</p>
                <p className="text-xs text-muted-foreground">Pending</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-rose-600">₹0.8L</p>
                <p className="text-xs text-muted-foreground">Overdue</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Examination Status</CardTitle>
            <CardDescription>Current term progress</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {[
              { subject: 'Mathematics', progress: 85, status: 'on-track' },
              { subject: 'Science', progress: 72, status: 'on-track' },
              { subject: 'English', progress: 90, status: 'completed' },
              { subject: 'Social Studies', progress: 45, status: 'behind' },
            ].map((item, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2">
                    {item.subject}
                    {item.status === 'completed' && <CheckCircle className="h-3 w-3 text-emerald-500" />}
                    {item.status === 'behind' && <AlertCircle className="h-3 w-3 text-amber-500" />}
                  </span>
                  <span className="font-medium">{item.progress}%</span>
                </div>
                <Progress 
                  value={item.progress} 
                  className="h-1.5"
                />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function TeacherDashboard() {
  const { user } = useAuth();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Welcome, {user?.first_name}!</h1>
        <p className="text-muted-foreground mt-1">Manage your classes and students.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="My Classes"
          value="4"
          description="Sections assigned"
          icon={School}
          variant="primary"
        />
        <StatCard
          title="Total Students"
          value="156"
          description="In my sections"
          icon={Users}
          variant="success"
        />
        <StatCard
          title="Pending Attendance"
          value="2"
          description="Classes today"
          icon={CheckCircle}
          variant="warning"
        />
        <StatCard
          title="Upcoming Exams"
          value="3"
          description="This week"
          icon={FileText}
          variant="info"
        />
      </div>

      <QuickActionsGrid
        title="Quick Actions"
        actions={[
          { title: 'Mark Attendance', description: 'Take attendance for your classes', icon: CheckCircle, href: '/attendance/daily', variant: 'primary' },
          { title: 'Enter Marks', description: 'Record student marks', icon: FileText, href: '/exams/results', variant: 'success' },
          { title: 'View Schedule', description: 'Check your timetable', icon: Calendar, href: '/schedule', variant: 'info' },
          { title: 'Messages', description: 'Communicate with parents', icon: Bell, href: '/messages', variant: 'warning' },
        ]}
      />
    </div>
  );
}

function StudentDashboard() {
  const { user } = useAuth();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Hello, {user?.first_name}!</h1>
        <p className="text-muted-foreground mt-1">Here&apos;s your academic overview.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Attendance"
          value="94%"
          description="This semester"
          icon={CheckCircle}
          variant="success"
        />
        <StatCard
          title="GPA"
          value="3.8"
          description="Current term"
          icon={Award}
          variant="primary"
        />
        <StatCard
          title="Assignments"
          value="5"
          description="Pending"
          icon={BookOpen}
          variant="warning"
        />
        <StatCard
          title="Fee Status"
          value="Paid"
          description="Up to date"
          icon={Wallet}
          variant="info"
        />
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();

  const renderDashboard = () => {
    if (user?.roles.includes('master') || user?.roles.includes('principal') || user?.roles.includes('coordinator')) {
      return <AdminDashboard />;
    } else if (user?.roles.includes('teacher')) {
      return <TeacherDashboard />;
    } else if (user?.roles.includes('student')) {
      return <StudentDashboard />;
    }
    return <AdminDashboard />;
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        {renderDashboard()}
      </DashboardLayout>
    </ProtectedRoute>
  );
}
