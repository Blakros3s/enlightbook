'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { AdminRoute } from '@/components/auth/protected-route';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Separator } from '@/components/ui/separator';
import { usersApi, UserCreateData } from '@/lib/api';
import { useToast } from '@/components/ui/use-toast';
import { ArrowLeft, Loader2, UserPlus } from 'lucide-react';
import Link from 'next/link';

const roles = [
  { id: 'is_master', label: 'Master Admin', description: 'Full system access' },
  { id: 'is_principal', label: 'Principal', description: 'School administration' },
  { id: 'is_coordinator', label: 'Coordinator', description: 'Academic coordination' },
  { id: 'is_teacher', label: 'Teacher', description: 'Teaching staff' },
  { id: 'is_student', label: 'Student', description: 'Student access' },
  { id: 'is_accountant', label: 'Accountant', description: 'Finance management' },
  { id: 'is_driver', label: 'Driver', description: 'Transportation' },
];

export default function NewUserPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<UserCreateData & { password_confirm: string }>({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    phone_number: '',
    is_master: false,
    is_principal: false,
    is_coordinator: false,
    is_teacher: false,
    is_student: false,
    is_accountant: false,
    is_driver: false,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.password !== formData.password_confirm) {
      toast({
        title: 'Error',
        description: 'Passwords do not match',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);
    try {
      const { password_confirm, ...data } = formData;
      await usersApi.createUser(data as UserCreateData);
      toast({
        title: 'Success',
        description: 'User created successfully',
      });
      router.push('/users');
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create user',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <AdminRoute>
      <DashboardLayout>
        <div className="space-y-6 max-w-4xl mx-auto">
          {/* Header */}
          <div className="flex items-center gap-4">
            <Button variant="outline" size="icon" asChild>
              <Link href="/users">
                <ArrowLeft className="h-4 w-4" />
              </Link>
            </Button>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Add New User</h1>
              <p className="text-muted-foreground">Create a new user account</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Account Information */}
            <Card>
              <CardHeader>
                <CardTitle>Account Information</CardTitle>
                <CardDescription>Basic account details</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="username">Username *</Label>
                    <Input
                      id="username"
                      value={formData.username}
                      onChange={(e) => handleChange('username', e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email *</Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => handleChange('email', e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="password">Password *</Label>
                    <Input
                      id="password"
                      type="password"
                      value={formData.password}
                      onChange={(e) => handleChange('password', e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password_confirm">Confirm Password *</Label>
                    <Input
                      id="password_confirm"
                      type="password"
                      value={formData.password_confirm}
                      onChange={(e) => handleChange('password_confirm', e.target.value)}
                      required
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Personal Information */}
            <Card>
              <CardHeader>
                <CardTitle>Personal Information</CardTitle>
                <CardDescription>User profile details</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="first_name">First Name</Label>
                    <Input
                      id="first_name"
                      value={formData.first_name}
                      onChange={(e) => handleChange('first_name', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="last_name">Last Name</Label>
                    <Input
                      id="last_name"
                      value={formData.last_name}
                      onChange={(e) => handleChange('last_name', e.target.value)}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone_number">Phone Number</Label>
                  <Input
                    id="phone_number"
                    value={formData.phone_number}
                    onChange={(e) => handleChange('phone_number', e.target.value)}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Roles */}
            <Card>
              <CardHeader>
                <CardTitle>User Roles</CardTitle>
                <CardDescription>Select roles for this user</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  {roles.map((role) => (
                    <div key={role.id} className="flex items-start space-x-3 p-3 rounded-lg border hover:bg-accent transition-colors">
                      <Checkbox
                        id={role.id}
                        checked={formData[role.id as keyof typeof formData] as boolean}
                        onCheckedChange={(checked) => 
                          handleChange(role.id, checked === true)
                        }
                      />
                      <div className="space-y-1">
                        <Label htmlFor={role.id} className="font-medium cursor-pointer">
                          {role.label}
                        </Label>
                        <p className="text-xs text-muted-foreground">{role.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Actions */}
            <div className="flex items-center justify-end gap-4">
              <Button variant="outline" asChild>
                <Link href="/users">Cancel</Link>
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <UserPlus className="mr-2 h-4 w-4" />
                    Create User
                  </>
                )}
              </Button>
            </div>
          </form>
        </div>
      </DashboardLayout>
    </AdminRoute>
  );
}
