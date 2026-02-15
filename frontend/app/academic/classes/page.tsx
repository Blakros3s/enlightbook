'use client';

import React, { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { classApi, academicYearApi, sectionApi } from '@/lib/api-academic';
import { useToast } from '@/components/ui/use-toast';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
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
import { Plus, School, Users, MoreHorizontal, Edit, Trash2, ChevronRight, PlusCircle } from 'lucide-react';
import Link from 'next/link';

export default function ClassesPage() {
  const [classes, setClasses] = useState<any[]>([]);
  const [academicYears, setAcademicYears] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [sectionDialogOpen, setSectionDialogOpen] = useState(false);
  const [selectedClass, setSelectedClass] = useState<any>(null);
  const [editingClass, setEditingClass] = useState<any>(null);
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    class_code: '',
    class_name: '',
    grade_level: '',
    academic_year: '',
    description: '',
  });

  const [sectionFormData, setSectionFormData] = useState({
    section_name: '',
    max_capacity: '40',
    class_teacher: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [classesData, yearsData] = await Promise.all([
        classApi.getAll(),
        academicYearApi.getAll({ is_current: true }),
      ]);
      setClasses(classesData.results || classesData);
      setAcademicYears(yearsData.results || yearsData);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to fetch data',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingClass) {
        await classApi.update(editingClass.id, formData);
        toast({ title: 'Success', description: 'Class updated' });
      } else {
        await classApi.create(formData);
        toast({ title: 'Success', description: 'Class created' });
      }
      setDialogOpen(false);
      setEditingClass(null);
      fetchData();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to save class',
        variant: 'destructive',
      });
    }
  };

  const handleCreateSection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedClass) return;
    
    try {
      await sectionApi.create({
        ...sectionFormData,
        school_class: selectedClass.id,
        max_capacity: parseInt(sectionFormData.max_capacity),
      });
      toast({ title: 'Success', description: 'Section created' });
      setSectionDialogOpen(false);
      setSectionFormData({ section_name: '', max_capacity: '40', class_teacher: '' });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to create section',
        variant: 'destructive',
      });
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure?')) return;
    try {
      await classApi.delete(id);
      toast({ title: 'Success', description: 'Class deleted' });
      fetchData();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete class',
        variant: 'destructive',
      });
    }
  };

  const openEditDialog = (cls: any) => {
    setEditingClass(cls);
    setFormData({
      class_code: cls.class_code,
      class_name: cls.class_name,
      grade_level: cls.grade_level.toString(),
      academic_year: cls.academic_year.toString(),
      description: cls.description || '',
    });
    setDialogOpen(true);
  };

  const openCreateDialog = () => {
    setEditingClass(null);
    setFormData({ class_code: '', class_name: '', grade_level: '', academic_year: '', description: '' });
    setDialogOpen(true);
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Classes</h1>
              <p className="text-muted-foreground">Manage classes and sections</p>
            </div>
            <Button onClick={openCreateDialog}>
              <Plus className="mr-2 h-4 w-4" />
              Add Class
            </Button>
          </div>

          {/* Classes Grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {loading ? (
              <p className="text-muted-foreground col-span-full">Loading...</p>
            ) : classes.length === 0 ? (
              <p className="text-muted-foreground col-span-full">No classes found</p>
            ) : (
              classes.map((cls) => (
                <Card key={cls.id} className="card-hover">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                          <School className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <CardTitle className="text-lg">{cls.class_name}</CardTitle>
                          <CardDescription>{cls.class_code}</CardDescription>
                        </div>
                      </div>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => openEditDialog(cls)}>
                            <Edit className="mr-2 h-4 w-4" />
                            Edit
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => { setSelectedClass(cls); setSectionDialogOpen(true); }}>
                            <PlusCircle className="mr-2 h-4 w-4" />
                            Add Section
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            onClick={() => handleDelete(cls.id)}
                            className="text-red-600"
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <p className="text-xs text-muted-foreground">Grade Level</p>
                        <p className="font-medium">Grade {cls.grade_level}</p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-xs text-muted-foreground">Sections</p>
                        <p className="font-medium">{cls.sections?.length || 0}</p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-xs text-muted-foreground">Students</p>
                        <div className="flex items-center gap-1">
                          <Users className="h-3 w-3 text-muted-foreground" />
                          <p className="font-medium">{cls.student_count || 0}</p>
                        </div>
                      </div>
                      <div className="space-y-1">
                        <p className="text-xs text-muted-foreground">Status</p>
                        <Badge variant={cls.is_active ? 'default' : 'secondary'}>
                          {cls.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </div>
                    </div>
                    
                    {cls.sections?.length > 0 && (
                      <div className="mt-4 pt-4 border-t">
                        <p className="text-xs text-muted-foreground mb-2">Sections</p>
                        <div className="flex flex-wrap gap-2">
                          {cls.sections.map((section: any) => (
                            <Badge key={section.id} variant="outline">
                              {section.section_name}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    <Button variant="ghost" className="w-full mt-4" asChild>
                      <Link href={`/academic/classes/${cls.id}`}>
                        View Details
                        <ChevronRight className="ml-1 h-4 w-4" />
                      </Link>
                    </Button>
                  </CardContent>
                </Card>
              ))
            )}
          </div>

          {/* Create/Edit Dialog */}
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle>{editingClass ? 'Edit Class' : 'Add Class'}</DialogTitle>
                <DialogDescription>
                  {editingClass ? 'Update class details' : 'Create a new class'}
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit}>
                <div className="space-y-4 py-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="class_code">Class Code *</Label>
                      <Input
                        id="class_code"
                        value={formData.class_code}
                        onChange={(e) => setFormData({ ...formData, class_code: e.target.value })}
                        placeholder="e.g., CLS-10"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="class_name">Class Name *</Label>
                      <Input
                        id="class_name"
                        value={formData.class_name}
                        onChange={(e) => setFormData({ ...formData, class_name: e.target.value })}
                        placeholder="e.g., Class 10"
                        required
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="grade_level">Grade Level *</Label>
                      <Input
                        id="grade_level"
                        type="number"
                        value={formData.grade_level}
                        onChange={(e) => setFormData({ ...formData, grade_level: e.target.value })}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="academic_year">Academic Year *</Label>
                      <Select
                        value={formData.academic_year}
                        onValueChange={(value) => setFormData({ ...formData, academic_year: value })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select year" />
                        </SelectTrigger>
                        <SelectContent>
                          {academicYears.map((year) => (
                            <SelectItem key={year.id} value={year.id.toString()}>
                              {year.year} {year.is_current && '(Current)'}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit">{editingClass ? 'Update' : 'Create'}</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>

          {/* Create Section Dialog */}
          <Dialog open={sectionDialogOpen} onOpenChange={setSectionDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Section</DialogTitle>
                <DialogDescription>
                  Create a new section for {selectedClass?.class_name}
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleCreateSection}>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="section_name">Section Name *</Label>
                    <Input
                      id="section_name"
                      value={sectionFormData.section_name}
                      onChange={(e) => setSectionFormData({ ...sectionFormData, section_name: e.target.value })}
                      placeholder="e.g., A, B, C"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="max_capacity">Max Capacity</Label>
                    <Input
                      id="max_capacity"
                      type="number"
                      value={sectionFormData.max_capacity}
                      onChange={(e) => setSectionFormData({ ...sectionFormData, max_capacity: e.target.value })}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit">Create Section</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
