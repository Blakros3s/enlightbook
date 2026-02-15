'use client';

import React, { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { subjectApi, subjectCategoryApi } from '@/lib/api-academic';
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
import { Checkbox } from '@/components/ui/checkbox';
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
import { Plus, BookOpen, Clock, MoreHorizontal, Edit, Trash2, Search } from 'lucide-react';

export default function SubjectsPage() {
  const [subjects, setSubjects] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingSubject, setEditingSubject] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    subject_code: '',
    subject_name: '',
    category: '',
    credit_hours: '',
    is_optional: false,
    subject_type: 'theory',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [subjectsData, categoriesData] = await Promise.all([
        subjectApi.getAll(),
        subjectCategoryApi.getAll(),
      ]);
      setSubjects(subjectsData.results || subjectsData);
      setCategories(categoriesData.results || categoriesData);
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
      const data = {
        ...formData,
        credit_hours: parseFloat(formData.credit_hours),
        category: formData.category ? parseInt(formData.category) : null,
      };
      
      if (editingSubject) {
        await subjectApi.update(editingSubject.id, data);
        toast({ title: 'Success', description: 'Subject updated' });
      } else {
        await subjectApi.create(data);
        toast({ title: 'Success', description: 'Subject created' });
      }
      setDialogOpen(false);
      setEditingSubject(null);
      fetchData();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to save subject',
        variant: 'destructive',
      });
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure?')) return;
    try {
      await subjectApi.delete(id);
      toast({ title: 'Success', description: 'Subject deleted' });
      fetchData();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete subject',
        variant: 'destructive',
      });
    }
  };

  const openEditDialog = (subject: any) => {
    setEditingSubject(subject);
    setFormData({
      subject_code: subject.subject_code,
      subject_name: subject.subject_name,
      category: subject.category?.toString() || '',
      credit_hours: subject.credit_hours.toString(),
      is_optional: subject.is_optional,
      subject_type: subject.subject_type,
    });
    setDialogOpen(true);
  };

  const openCreateDialog = () => {
    setEditingSubject(null);
    setFormData({
      subject_code: '',
      subject_name: '',
      category: '',
      credit_hours: '',
      is_optional: false,
      subject_type: 'theory',
    });
    setDialogOpen(true);
  };

  const filteredSubjects = subjects.filter(subject =>
    subject.subject_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    subject.subject_code?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Subjects</h1>
              <p className="text-muted-foreground">Manage subjects and curriculum</p>
            </div>
            <Button onClick={openCreateDialog}>
              <Plus className="mr-2 h-4 w-4" />
              Add Subject
            </Button>
          </div>

          {/* Search */}
          <div className="flex items-center gap-4">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search subjects..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>

          {/* Subjects Table */}
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Code</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Credits</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="w-12"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8">Loading...</TableCell>
                    </TableRow>
                  ) : filteredSubjects.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                        No subjects found
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredSubjects.map((subject) => (
                      <TableRow key={subject.id}>
                        <TableCell className="font-medium">{subject.subject_code}</TableCell>
                        <TableCell>{subject.subject_name}</TableCell>
                        <TableCell>
                          {subject.category_name ? (
                            <Badge variant="outline">{subject.category_name}</Badge>
                          ) : (
                            <span className="text-muted-foreground">-</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            <Clock className="h-3 w-3 text-muted-foreground" />
                            {subject.credit_hours}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant={subject.subject_type === 'practical' ? 'secondary' : 'default'}>
                            {subject.subject_type}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {subject.is_optional ? (
                            <Badge variant="outline">Optional</Badge>
                          ) : (
                            <Badge>Core</Badge>
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
                              <DropdownMenuItem onClick={() => openEditDialog(subject)}>
                                <Edit className="mr-2 h-4 w-4" />
                                Edit
                              </DropdownMenuItem>
                              <DropdownMenuItem 
                                onClick={() => handleDelete(subject.id)}
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
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle>{editingSubject ? 'Edit Subject' : 'Add Subject'}</DialogTitle>
                <DialogDescription>
                  {editingSubject ? 'Update subject details' : 'Create a new subject'}
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit}>
                <div className="space-y-4 py-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="subject_code">Subject Code *</Label>
                      <Input
                        id="subject_code"
                        value={formData.subject_code}
                        onChange={(e) => setFormData({ ...formData, subject_code: e.target.value })}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="subject_name">Subject Name *</Label>
                      <Input
                        id="subject_name"
                        value={formData.subject_name}
                        onChange={(e) => setFormData({ ...formData, subject_name: e.target.value })}
                        required
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="category">Category</Label>
                      <Select
                        value={formData.category}
                        onValueChange={(value) => setFormData({ ...formData, category: value })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select category" />
                        </SelectTrigger>
                        <SelectContent>
                          {categories.map((cat) => (
                            <SelectItem key={cat.id} value={cat.id.toString()}>
                              {cat.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="credit_hours">Credit Hours *</Label>
                      <Input
                        id="credit_hours"
                        type="number"
                        step="0.5"
                        value={formData.credit_hours}
                        onChange={(e) => setFormData({ ...formData, credit_hours: e.target.value })}
                        required
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="subject_type">Subject Type *</Label>
                      <Select
                        value={formData.subject_type}
                        onValueChange={(value) => setFormData({ ...formData, subject_type: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="theory">Theory</SelectItem>
                          <SelectItem value="practical">Practical</SelectItem>
                          <SelectItem value="hybrid">Hybrid</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="flex items-center space-x-2 pt-6">
                      <Checkbox
                        id="is_optional"
                        checked={formData.is_optional}
                        onCheckedChange={(checked) => 
                          setFormData({ ...formData, is_optional: checked === true })
                        }
                      />
                      <Label htmlFor="is_optional">Optional Subject</Label>
                    </div>
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit">{editingSubject ? 'Update' : 'Create'}</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
