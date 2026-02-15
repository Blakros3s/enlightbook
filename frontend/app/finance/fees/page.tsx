'use client';

import React, { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { feeCategoryApi, feeStructureApi, classApi } from '@/lib/api-finance';
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
import { Plus, DollarSign, MoreHorizontal, Edit, Trash2, Tag, Building } from 'lucide-react';

export default function FeeStructurePage() {
  const [feeCategories, setFeeCategories] = useState<any[]>([]);
  const [feeStructures, setFeeStructures] = useState<any[]>([]);
  const [classes, setClasses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [categoryDialogOpen, setCategoryDialogOpen] = useState(false);
  const [structureDialogOpen, setStructureDialogOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState<any>(null);
  const { toast } = useToast();

  const [categoryForm, setCategoryForm] = useState({
    name: '',
    code: '',
    description: '',
    is_recurring: false,
  });

  const [structureForm, setStructureForm] = useState({
    school_class: '',
    fee_category_name: '',
    amount: '',
    academic_year: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [categoriesData, structuresData, classesData] = await Promise.all([
        feeCategoryApi.getAll(),
        feeStructureApi.getAll(),
        classApi.getAll(),
      ]);
      setFeeCategories(categoriesData.results || categoriesData);
      setFeeStructures(structuresData.results || structuresData);
      setClasses(classesData.results || classesData);
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

  const handleCreateCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await feeCategoryApi.create(categoryForm);
      toast({ title: 'Success', description: 'Fee category created' });
      setCategoryDialogOpen(false);
      setCategoryForm({ name: '', code: '', description: '', is_recurring: false });
      fetchData();
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to create category', variant: 'destructive' });
    }
  };

  const handleCreateStructure = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await feeStructureApi.create({
        ...structureForm,
        amount: parseFloat(structureForm.amount),
      });
      toast({ title: 'Success', description: 'Fee structure created' });
      setStructureDialogOpen(false);
      fetchData();
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to create fee structure', variant: 'destructive' });
    }
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Fee Structure</h1>
              <p className="text-muted-foreground">Manage fee categories and class-wise fees</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setCategoryDialogOpen(true)}>
                <Tag className="mr-2 h-4 w-4" />
                Add Category
              </Button>
              <Button onClick={() => setStructureDialogOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Set Class Fee
              </Button>
            </div>
          </div>

          {/* Fee Categories */}
          <Card>
            <CardHeader>
              <CardTitle>Fee Categories</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Code</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead className="w-12"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center py-8">Loading...</TableCell>
                    </TableRow>
                  ) : feeCategories.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center py-8 text-muted-foreground">
                        No fee categories found
                      </TableCell>
                    </TableRow>
                  ) : (
                    feeCategories.map((category) => (
                      <TableRow key={category.id}>
                        <TableCell className="font-medium">{category.code}</TableCell>
                        <TableCell>{category.name}</TableCell>
                        <TableCell>
                          <Badge variant={category.is_recurring ? 'default' : 'outline'}>
                            {category.is_recurring ? 'Recurring' : 'One-time'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="icon">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem>
                                <Edit className="mr-2 h-4 w-4" />
                                Edit
                              </DropdownMenuItem>
                              <DropdownMenuItem className="text-red-600">
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

          {/* Fee Structures by Class */}
          <Card>
            <CardHeader>
              <CardTitle>Class-wise Fee Structure</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Class</TableHead>
                    <TableHead>Fee Category</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Academic Year</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center py-8">Loading...</TableCell>
                    </TableRow>
                  ) : feeStructures.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center py-8 text-muted-foreground">
                        No fee structures found
                      </TableCell>
                    </TableRow>
                  ) : (
                    feeStructures.map((structure) => (
                      <TableRow key={structure.id}>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Building className="h-4 w-4 text-muted-foreground" />
                            {structure.school_class_name}
                          </div>
                        </TableCell>
                        <TableCell>{structure.fee_category_name}</TableCell>
                        <TableCell className="font-medium">
                          ₹{parseFloat(structure.amount).toLocaleString()}
                        </TableCell>
                        <TableCell>{structure.academic_year_name}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Add Category Dialog */}
          <Dialog open={categoryDialogOpen} onOpenChange={setCategoryDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Fee Category</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreateCategory}>
                <div className="space-y-4 py-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="code">Code *</Label>
                      <Input
                        id="code"
                        value={categoryForm.code}
                        onChange={(e) => setCategoryForm({ ...categoryForm, code: e.target.value })}
                        placeholder="e.g., TUITION"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="name">Name *</Label>
                      <Input
                        id="name"
                        value={categoryForm.name}
                        onChange={(e) => setCategoryForm({ ...categoryForm, name: e.target.value })}
                        placeholder="e.g., Tuition Fee"
                        required
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Input
                      id="description"
                      value={categoryForm.description}
                      onChange={(e) => setCategoryForm({ ...categoryForm, description: e.target.value })}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit">Create Category</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>

          {/* Add Fee Structure Dialog */}
          <Dialog open={structureDialogOpen} onOpenChange={setStructureDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Set Class Fee</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreateStructure}>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="school_class">Class *</Label>
                    <Select
                      value={structureForm.school_class}
                      onValueChange={(value) => setStructureForm({ ...structureForm, school_class: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select class" />
                      </SelectTrigger>
                      <SelectContent>
                        {classes.map((cls) => (
                          <SelectItem key={cls.id} value={cls.id.toString()}>
                            {cls.class_name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="fee_category_name">Fee Category *</Label>
                    <Select
                      value={structureForm.fee_category_name}
                      onValueChange={(value) => setStructureForm({ ...structureForm, fee_category_name: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        {feeCategories.map((cat) => (
                          <SelectItem key={cat.id} value={cat.id.toString()}>
                            {cat.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="amount">Amount (₹) *</Label>
                    <Input
                      id="amount"
                      type="number"
                      value={structureForm.amount}
                      onChange={(e) => setStructureForm({ ...structureForm, amount: e.target.value })}
                      required
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit">Set Fee</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
