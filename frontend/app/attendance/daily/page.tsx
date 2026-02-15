'use client';

import React, { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { dailyAttendanceApi, classApi, sectionApi } from '@/lib/api-attendance';
import { useToast } from '@/components/ui/use-toast';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Calendar, CheckCircle, Users, Clock, XCircle, AlertCircle, Save, Loader2 } from 'lucide-react';
import { format } from 'date-fns';

const attendanceStatuses = [
  { value: 'present', label: 'Present', color: 'bg-emerald-500', icon: CheckCircle },
  { value: 'absent', label: 'Absent', color: 'bg-rose-500', icon: XCircle },
  { value: 'late', label: 'Late', color: 'bg-amber-500', icon: Clock },
  { value: 'excused', label: 'Excused', color: 'bg-blue-500', icon: AlertCircle },
  { value: 'half_day', label: 'Half Day', color: 'bg-purple-500', icon: Clock },
];

export default function DailyAttendancePage() {
  const [classes, setClasses] = useState<any[]>([]);
  const [sections, setSections] = useState<any[]>([]);
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  const [filters, setFilters] = useState({
    classId: '',
    sectionId: '',
    date: format(new Date(), 'yyyy-MM-dd'),
  });

  const [attendance, setAttendance] = useState<Record<number, string>>({});

  useEffect(() => {
    fetchClasses();
  }, []);

  useEffect(() => {
    if (filters.classId) {
      fetchSections(parseInt(filters.classId));
    }
  }, [filters.classId]);

  useEffect(() => {
    if (filters.classId && filters.date) {
      fetchAttendance();
    }
  }, [filters.classId, filters.sectionId, filters.date]);

  const fetchClasses = async () => {
    try {
      const data = await classApi.getAll();
      setClasses(data.results || data);
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to fetch classes', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  const fetchSections = async (classId: number) => {
    try {
      const data = await sectionApi.getAll({ school_class: classId });
      setSections(data.results || data);
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to fetch sections', variant: 'destructive' });
    }
  };

  const fetchAttendance = async () => {
    setLoading(true);
    try {
      const data = await dailyAttendanceApi.getByClass(
        parseInt(filters.classId),
        filters.date,
        filters.sectionId ? parseInt(filters.sectionId) : undefined
      );
      
      const attendanceMap: Record<number, string> = {};
      data.students?.forEach((student: any) => {
        attendanceMap[student.id] = student.attendance_status || 'present';
      });
      setStudents(data.students || []);
      setAttendance(attendanceMap);
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to fetch attendance', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAll = (status: string) => {
    const newAttendance: Record<number, string> = {};
    students.forEach((student) => {
      newAttendance[student.id] = status;
    });
    setAttendance(newAttendance);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const attendanceData = Object.entries(attendance).map(([studentId, status]) => ({
        student_id: parseInt(studentId),
        status,
      }));

      await dailyAttendanceApi.bulkMark({
        school_class_id: parseInt(filters.classId),
        section_id: filters.sectionId ? parseInt(filters.sectionId) : undefined,
        date: filters.date,
        attendance_data: attendanceData,
      });

      toast({ title: 'Success', description: 'Attendance saved successfully' });
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to save attendance', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  };

  const getStatusIcon = (status: string) => {
    const statusConfig = attendanceStatuses.find(s => s.value === status);
    if (!statusConfig) return null;
    const Icon = statusConfig.icon;
    return <Icon className="h-4 w-4" />;
  };

  const getStatusColor = (status: string) => {
    const statusConfig = attendanceStatuses.find(s => s.value === status);
    return statusConfig?.color || 'bg-slate-500';
  };

  const stats = {
    present: Object.values(attendance).filter(s => s === 'present').length,
    absent: Object.values(attendance).filter(s => s === 'absent').length,
    late: Object.values(attendance).filter(s => s === 'late').length,
    excused: Object.values(attendance).filter(s => s === 'excused').length,
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Daily Attendance</h1>
              <p className="text-muted-foreground">Mark student attendance</p>
            </div>
            <Button onClick={handleSave} disabled={saving || students.length === 0}>
              {saving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Save Attendance
                </>
              )}
            </Button>
          </div>

          {/* Filters */}
          <Card>
            <CardContent className="p-6">
              <div className="grid gap-4 md:grid-cols-4">
                <div className="space-y-2">
                  <Label>Class</Label>
                  <Select
                    value={filters.classId}
                    onValueChange={(value) => setFilters({ ...filters, classId: value, sectionId: '' })}
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
                  <Label>Section</Label>
                  <Select
                    value={filters.sectionId}
                    onValueChange={(value) => setFilters({ ...filters, sectionId: value })}
                    disabled={!filters.classId || sections.length === 0}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select section" />
                    </SelectTrigger>
                    <SelectContent>
                      {sections.map((section) => (
                        <SelectItem key={section.id} value={section.id.toString()}>
                          {section.section_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Date</Label>
                  <Input
                    type="date"
                    value={filters.date}
                    onChange={(e) => setFilters({ ...filters, date: e.target.value })}
                  />
                </div>
                <div className="flex items-end gap-2">
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={() => handleMarkAll('present')}
                    disabled={students.length === 0}
                  >
                    <CheckCircle className="mr-2 h-4 w-4" />
                    Mark All Present
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Stats */}
          {students.length > 0 && (
            <div className="grid gap-4 md:grid-cols-4">
              <Card className="bg-emerald-50 border-emerald-200">
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-emerald-600" />
                    <span className="font-medium text-emerald-900">Present</span>
                  </div>
                  <p className="text-2xl font-bold text-emerald-700 mt-1">{stats.present}</p>
                </CardContent>
              </Card>
              <Card className="bg-rose-50 border-rose-200">
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <XCircle className="h-5 w-5 text-rose-600" />
                    <span className="font-medium text-rose-900">Absent</span>
                  </div>
                  <p className="text-2xl font-bold text-rose-700 mt-1">{stats.absent}</p>
                </CardContent>
              </Card>
              <Card className="bg-amber-50 border-amber-200">
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <Clock className="h-5 w-5 text-amber-600" />
                    <span className="font-medium text-amber-900">Late</span>
                  </div>
                  <p className="text-2xl font-bold text-amber-700 mt-1">{stats.late}</p>
                </CardContent>
              </Card>
              <Card className="bg-blue-50 border-blue-200">
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-blue-600" />
                    <span className="font-medium text-blue-900">Excused</span>
                  </div>
                  <p className="text-2xl font-bold text-blue-700 mt-1">{stats.excused}</p>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Attendance Table */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Student Attendance</span>
                <span className="text-sm font-normal text-muted-foreground">
                  {students.length} students
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Roll No</TableHead>
                    <TableHead>Student Name</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center py-8">Loading...</TableCell>
                    </TableRow>
                  ) : students.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center py-8 text-muted-foreground">
                        {filters.classId ? 'No students found in this class' : 'Select a class to view students'}
                      </TableCell>
                    </TableRow>
                  ) : (
                    students.map((student) => (
                      <TableRow key={student.id}>
                        <TableCell className="font-medium">{student.roll_number || '-'}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                              <span className="text-sm font-semibold text-primary">
                                {student.full_name?.charAt(0).toUpperCase()}
                              </span>
                            </div>
                            {student.full_name}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(attendance[student.id] || 'present')}>
                            {getStatusIcon(attendance[student.id] || 'present')}
                            <span className="ml-1 capitalize">{attendance[student.id] || 'Present'}</span>
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-1">
                            {attendanceStatuses.map((status) => (
                              <Button
                                key={status.value}
                                variant={attendance[student.id] === status.value ? 'default' : 'ghost'}
                                size="icon"
                                className={`h-8 w-8 ${
                                  attendance[student.id] === status.value ? status.color : ''
                                }`}
                                onClick={() => setAttendance({ ...attendance, [student.id]: status.value })}
                              >
                                <status.icon className="h-4 w-4" />
                              </Button>
                            ))}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
