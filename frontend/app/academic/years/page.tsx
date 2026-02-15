'use client';

import React, { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { academicYearApi } from '@/lib/api-academic';
import { useToast } from '@/components/ui/use-toast';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Plus, Calendar, MoreHorizontal, Edit, Trash2, CheckCircle, Star, CalendarDays } from 'lucide-react';

export default function AcademicYearsPage() {
  const [years, setYears] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingYear, setEditingYear] = useState<any>(null);
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    year: '',
    start_date: '',
    end_date: '',
    description: '',
  });

  useEffect(() => {
    fetchYears();
  }, []);

  const fetchYears = async () => {
    try {
      const data = await academicYearApi.getAll();
      setYears(data.results || data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to fetch academic years',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingYear) {
        await academicYearApi.update(editingYear.id, formData);
        toast({ title: 'Success', description: 'Academic year updated' });
      } else {
        await academicYearApi.create(formData);
        toast({ title: 'Success', description: 'Academic year created' });
      }
      setDialogOpen(false);
      setEditingYear(null);
      setFormData({ year: '', start_date: '', end_date: '', description: '' });
      fetchYears();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to save academic year',
        variant: 'destructive',
      });
    }
  };

  const handleSetCurrent = async (id: number) => {
    try {
      await academicYearApi.setCurrent(id);
      toast({ title: 'Success', description: 'Current year updated' });
      fetchYears();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update current year',
        variant: 'destructive',
      });
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure?')) return;
    try {
      await academicYearApi.delete(id);
      toast({ title: 'Success', description: 'Academic year deleted' });
      fetchYears();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete academic year',
        variant: 'destructive',
      });
    }
  };

  const openEditDialog = (year: any) => {
    setEditingYear(year);
    setFormData({
      year: year.year,
      start_date: year.start_date,
      end_date: year.end_date,
      description: year.description || '',
    });
    setDialogOpen(true);
  };

  const openCreateDialog = () => {
    setEditingYear(null);
    setFormData({ year: '', start_date: '', end_date: '', description: '' });
    setDialogOpen(true);
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Academic Years</h1>
              <p className="text-muted-foreground">Manage academic years and terms</p>
            </div>
            <Button onClick={openCreateDialog}>
              <Plus className="mr-2 h-4 w-4" />
              Add Year
            </Button>
          </div>

          {/* Current Year Card */}
          {years.find(y => y.is_current) && (
            <Card className="border-blue-500/30 bg-gradient-to-r from-blue-500/5 to-indigo-500/5">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="h-12 w-12 rounded-xl bg-blue-500 flex items-center justify-center">
                      <Star className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Current Academic Year</p>
                      <p className="text-2xl font-bold">{years.find(y => y.is_current)?.year}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">
                      {new Date(years.find(y => y.is_current)?.start_date).toLocaleDateString()} - 
                      {new Date(years.find(y => y.is_current)?.end_date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Years Table */}
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Year</TableHead>
                    <TableHead>Start Date</TableHead>
                    <TableHead>End Date</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="w-12"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8">Loading...</TableCell>
                    </TableRow>
                  ) : years.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                        No academic years found
                      </TableCell>
                    </TableRow>
                  ) : (
                    years.map((year) => (
                      <TableRow key={year.id}>
                        <TableCell className="font-medium">{year.year}</TableCell>
                        <TableCell>{new Date(year.start_date).toLocaleDateString()}</TableCell>
                        <TableCell>{new Date(year.end_date).toLocaleDateString()}</TableCell>
                        <TableCell>
                          {year.is_current ? (
                            <Badge className="bg-blue-500">Current</Badge>
                          ) : year.is_active ? (
                            <Badge variant="secondary">Active</Badge>
                          ) : (
                            <Badge variant="outline">Inactive</Badge>
                          )}
                        </TableCell>
                        <TableCell>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="icon">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem onClick={() => openEditDialog(year)}>
                                <Edit className="mr-2 h-4 w-4" />
                                Edit
                              </DropdownMenuItem>
                              {!year.is_current && (
                                <DropdownMenuItem onClick={() => handleSetCurrent(year.id)}>
                                  <CheckCircle className="mr-2 h-4 w-4" />
                                  Set as Current
                                </DropdownMenuItem>
                              )}
                              <DropdownMenuItem 
                                onClick={() => handleDelete(year.id)}
                                className="text-red-600"
                              >
                                <Trash2 className="mr-2 h-4 w-4" />
                                Delete
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Create/Edit Dialog */}
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{editingYear ? 'Edit Academic Year' : 'Add Academic Year'}</DialogTitle>
                <DialogDescription>
                  {editingYear ? 'Update academic year details' : 'Create a new academic year'}
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit}>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="year">Year Name *</Label>
                    <Input
                      id="year"
                      placeholder="e.g., 2024-2025"
                      value={formData.year}
                      onChange={(e) => setFormData({ ...formData, year: e.target.value })}
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="start_date">Start Date *</Label>
                      <Input
                        id="start_date"
                        type="date"
                        value={formData.start_date}
                        onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="end_date">End Date *</Label>
                      <Input
                        id="end_date"
                        type="date"
                        value={formData.end_date}
                        onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                        required
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Input
                      id="description"
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit">
                    {editingYear ? 'Update' : 'Create'}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
