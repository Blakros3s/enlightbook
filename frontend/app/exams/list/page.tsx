'use client';

import React, { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { examApi, academicYearApi } from '@/lib/api-exams';
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
import { Plus, Calendar, FileText, MoreHorizontal, Edit, Trash2, Eye, Upload, CheckCircle, AlertCircle } from 'lucide-react';
import Link from 'next/link';

export default function ExamsPage() {
  const [exams, setExams] = useState<any[]>([]);
  const [academicYears, setAcademicYears] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    name: '',
    exam_type: 'mid_term',
    academic_year: '',
    start_date: '',
    end_date: '',
    description: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [examsData, yearsData] = await Promise.all([
        examApi.getAll(),
        academicYearApi.getAll(),
      ]);
      setExams(examsData.results || examsData);
      setAcademicYears(yearsData.results || yearsData);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to fetch exams',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateExam = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await examApi.create({
        ...formData,
        academic_year: parseInt(formData.academic_year),
      });
      toast({ title: 'Success', description: 'Exam created' });
      setDialogOpen(false);
      fetchData();
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to create exam', variant: 'destructive' });
    }
  };

  const handlePublishTimetable = async (id: number) => {
    try {
      await examApi.publishTimetable(id);
      toast({ title: 'Success', description: 'Timetable published' });
      fetchData();
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to publish timetable', variant: 'destructive' });
    }
  };

  const handlePublishResults = async (id: number) => {
    try {
      await examApi.publishResults(id);
      toast({ title: 'Success', description: 'Results published' });
      fetchData();
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to publish results', variant: 'destructive' });
    }
  };

  const getStatusBadge = (exam: any) => {
    if (exam.is_result_published) {
      return <Badge className="bg-emerald-500">Results Published</Badge>;
    } else if (exam.is_timetable_published) {
      return <Badge className="bg-blue-500">Timetable Published</Badge>;
    }
    return <Badge variant="outline">Draft</Badge>;
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Examinations</h1>
              <p className="text-muted-foreground">Manage exams and schedules</p>
            </div>
            <Button onClick={() => setDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Create Exam
            </Button>
          </div>

          {/* Exams Grid */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {loading ? (
              <p className="col-span-full text-center py-8">Loading...</p>
            ) : exams.length === 0 ? (
              <p className="col-span-full text-center py-8 text-muted-foreground">No exams found</p>
            ) : (
              exams.map((exam) => (
                <Card key={exam.id} className="card-hover">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                          <FileText className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <CardTitle className="text-base">{exam.name}</CardTitle>
                          <p className="text-xs text-muted-foreground capitalize">{exam.exam_type.replace('_', ' ')}</p>
                        </div>
                      </div>
                      {getStatusBadge(exam)}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Academic Year</span>
                        <span className="font-medium">{exam.academic_year_name}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Start Date</span>
                        <span>{new Date(exam.start_date).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">End Date</span>
                        <span>{new Date(exam.end_date).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Subjects</span>
                        <span className="font-medium">{exam.details_count || 0}</span>
                      </div>
                    </div>

                    <div className="flex gap-2 mt-4 pt-4 border-t">
                      <Button variant="outline" size="sm" className="flex-1" asChild>
                        <Link href={`/exams/list/${exam.id}`}>
                          <Eye className="mr-1 h-3 w-3" />
                          View
                        </Link>
                      </Button>
                      {!exam.is_timetable_published && (
                        <Button
                          size="sm"
                          className="flex-1"
                          onClick={() => handlePublishTimetable(exam.id)}
                        >
                          <Calendar className="mr-1 h-3 w-3" />
                          Publish
                        </Button>
                      )}
                      {exam.is_timetable_published && !exam.is_result_published && (
                        <Button
                          size="sm"
                          variant="secondary"
                          className="flex-1"
                          onClick={() => handlePublishResults(exam.id)}
                        >
                          <CheckCircle className="mr-1 h-3 w-3" />
                          Results
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>

          {/* Create Exam Dialog */}
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle>Create Exam</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreateExam}>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Exam Name *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="e.g., Mid-Term Examination 2024"
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="exam_type">Exam Type *</Label>
                      <Select
                        value={formData.exam_type}
                        onValueChange={(value) => setFormData({ ...formData, exam_type: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="unit_test">Unit Test</SelectItem>
                          <SelectItem value="mid_term">Mid Term</SelectItem>
                          <SelectItem value="final">Final</SelectItem>
                          <SelectItem value="quiz">Quiz</SelectItem>
                        </SelectContent>
                      </Select>
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
                              {year.year}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
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
                </div>
                <DialogFooter>
                  <Button type="submit">Create Exam</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
