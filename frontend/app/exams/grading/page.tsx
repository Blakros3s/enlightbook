'use client';

import React, { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { gradingScaleApi } from '@/lib/api-exams';
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
import { Plus, Award, MoreHorizontal, Edit, Trash2, Star, CheckCircle } from 'lucide-react';

export default function GradingScalesPage() {
  const [scales, setScales] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [gradeRangeDialogOpen, setGradeRangeDialogOpen] = useState(false);
  const [selectedScale, setSelectedScale] = useState<any>(null);
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    name: '',
    description: '',
  });

  const [gradeRangeForm, setGradeRangeForm] = useState({
    grade: '',
    min_percentage: '',
    max_percentage: '',
    grade_point: '',
    description: '',
  });

  useEffect(() => {
    fetchScales();
  }, []);

  const fetchScales = async () => {
    try {
      const data = await gradingScaleApi.getAll();
      setScales(data.results || data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to fetch grading scales',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateScale = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await gradingScaleApi.create(formData);
      toast({ title: 'Success', description: 'Grading scale created' });
      setDialogOpen(false);
      setFormData({ name: '', description: '' });
      fetchScales();
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to create scale', variant: 'destructive' });
    }
  };

  const handleAddGradeRange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedScale) return;
    
    try {
      await gradingScaleApi.addGradeRange(selectedScale.id, {
        ...gradeRangeForm,
        min_percentage: parseFloat(gradeRangeForm.min_percentage),
        max_percentage: parseFloat(gradeRangeForm.max_percentage),
        grade_point: parseFloat(gradeRangeForm.grade_point),
      });
      toast({ title: 'Success', description: 'Grade range added' });
      setGradeRangeDialogOpen(false);
      setGradeRangeForm({ grade: '', min_percentage: '', max_percentage: '', grade_point: '', description: '' });
      fetchScales();
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to add grade range', variant: 'destructive' });
    }
  };

  const handleSetDefault = async (id: number) => {
    try {
      await gradingScaleApi.setDefault(id);
      toast({ title: 'Success', description: 'Default grading scale updated' });
      fetchScales();
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to update default', variant: 'destructive' });
    }
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Grading Scales</h1>
              <p className="text-muted-foreground">Manage grade ranges and evaluation criteria</p>
            </div>
            <Button onClick={() => setDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Add Scale
            </Button>
          </div>

          {/* Scales List */}
          <div className="grid gap-6">
            {loading ? (
              <p className="text-center py-8">Loading...</p>
            ) : scales.length === 0 ? (
              <p className="text-center py-8 text-muted-foreground">No grading scales found</p>
            ) : (
              scales.map((scale) => (
                <Card key={scale.id} className={scale.is_default ? 'border-primary' : ''}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`h-10 w-10 rounded-lg flex items-center justify-center ${
                          scale.is_default ? 'bg-primary text-primary-foreground' : 'bg-muted'
                        }`}>
                          <Award className="h-5 w-5" />
                        </div>
                        <div>
                          <CardTitle className="text-lg flex items-center gap-2">
                            {scale.name}
                            {scale.is_default && (
                              <Badge variant="default" className="bg-primary">Default</Badge>
                            )}
                          </CardTitle>
                          {scale.description && (
                            <p className="text-sm text-muted-foreground">{scale.description}</p>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => { setSelectedScale(scale); setGradeRangeDialogOpen(true); }}
                        >
                          <Plus className="mr-1 h-3 w-3" />
                          Add Range
                        </Button>
                        {!scale.is_default && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleSetDefault(scale.id)}
                          >
                            <Star className="mr-1 h-3 w-3" />
                            Set Default
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {scale.ranges && scale.ranges.length > 0 ? (
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Grade</TableHead>
                            <TableHead>Range (%)</TableHead>
                            <TableHead>Grade Point</TableHead>
                            <TableHead>Description</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {scale.ranges.map((range: any) => (
                            <TableRow key={range.id}>
                              <TableCell className="font-bold">{range.grade}</TableCell>
                              <TableCell>{range.min_percentage}% - {range.max_percentage}%</TableCell>
                              <TableCell>{range.grade_point}</TableCell>
                              <TableCell className="text-muted-foreground">{range.description || '-'}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    ) : (
                      <p className="text-sm text-muted-foreground text-center py-4">
                        No grade ranges defined yet
                      </p>
                    )}
                  </CardContent>
                </Card>
              ))
            )}
          </div>

          {/* Create Scale Dialog */}
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Grading Scale</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreateScale}>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Scale Name *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="e.g., Standard Grading Scale"
                      required
                    />
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
                  <Button type="submit">Create Scale</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>

          {/* Add Grade Range Dialog */}
          <Dialog open={gradeRangeDialogOpen} onOpenChange={setGradeRangeDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Grade Range</DialogTitle>
                <DialogDescription>For {selectedScale?.name}</DialogDescription>
              </DialogHeader>
              <form onSubmit={handleAddGradeRange}>
                <div className="space-y-4 py-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="grade">Grade *</Label>
                      <Input
                        id="grade"
                        value={gradeRangeForm.grade}
                        onChange={(e) => setGradeRangeForm({ ...gradeRangeForm, grade: e.target.value })}
                        placeholder="e.g., A+"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="grade_point">Grade Point *</Label>
                      <Input
                        id="grade_point"
                        type="number"
                        step="0.1"
                        value={gradeRangeForm.grade_point}
                        onChange={(e) => setGradeRangeForm({ ...gradeRangeForm, grade_point: e.target.value })}
                        placeholder="e.g., 4.0"
                        required
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="min_percentage">Min % *</Label>
                      <Input
                        id="min_percentage"
                        type="number"
                        value={gradeRangeForm.min_percentage}
                        onChange={(e) => setGradeRangeForm({ ...gradeRangeForm, min_percentage: e.target.value })}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="max_percentage">Max % *</Label>
                      <Input
                        id="max_percentage"
                        type="number"
                        value={gradeRangeForm.max_percentage}
                        onChange={(e) => setGradeRangeForm({ ...gradeRangeForm, max_percentage: e.target.value })}
                        required
                      />
                    </div>
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit">Add Range</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
