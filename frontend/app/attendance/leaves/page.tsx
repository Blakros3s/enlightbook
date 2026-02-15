'use client';

import React, { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { leaveApplicationApi } from '@/lib/api-attendance';
import { useAuth } from '@/components/auth/auth-provider';
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
import { Textarea } from '@/components/ui/textarea';
import { Plus, FileText, Calendar, CheckCircle, XCircle, Clock, AlertCircle, Loader2 } from 'lucide-react';
import { format } from 'date-fns';

export default function LeavesPage() {
  const [leaves, setLeaves] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [approveDialogOpen, setApproveDialogOpen] = useState(false);
  const [selectedLeave, setSelectedLeave] = useState<any>(null);
  const { user } = useAuth();
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    leave_type: 'sick',
    leave_date: format(new Date(), 'yyyy-MM-dd'),
    days: '1',
    reason: '',
  });

  const [approveData, setApproveData] = useState({
    action: 'approve',
    remarks: '',
  });

  useEffect(() => {
    fetchLeaves();
  }, []);

  const fetchLeaves = async () => {
    try {
      const data = await leaveApplicationApi.getAll();
      setLeaves(data.results || data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to fetch leave applications',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await leaveApplicationApi.create({
        ...formData,
        days: parseInt(formData.days),
      });
      toast({ title: 'Success', description: 'Leave application submitted' });
      setDialogOpen(false);
      setFormData({ leave_type: 'sick', leave_date: format(new Date(), 'yyyy-MM-dd'), days: '1', reason: '' });
      fetchLeaves();
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to submit application', variant: 'destructive' });
    }
  };

  const handleApproveReject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedLeave) return;

    try {
      if (approveData.action === 'approve') {
        await leaveApplicationApi.approve(selectedLeave.id, approveData.remarks);
      } else {
        await leaveApplicationApi.reject(selectedLeave.id, approveData.remarks);
      }
      toast({ title: 'Success', description: `Leave ${approveData.action}d` });
      setApproveDialogOpen(false);
      setSelectedLeave(null);
      fetchLeaves();
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to process request', variant: 'destructive' });
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { color: string; icon: any }> = {
      pending: { color: 'bg-amber-500', icon: Clock },
      approved: { color: 'bg-emerald-500', icon: CheckCircle },
      rejected: { color: 'bg-rose-500', icon: XCircle },
    };
    const config = variants[status] || variants.pending;
    const Icon = config.icon;
    return (
      <Badge className={config.color}>
        <Icon className="h-3 w-3 mr-1" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const canApprove = user?.roles.some(r => ['master', 'principal', 'coordinator'].includes(r));

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Leave Applications</h1>
              <p className="text-muted-foreground">Manage leave requests</p>
            </div>
            <Button onClick={() => setDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Apply for Leave
            </Button>
          </div>

          {/* Leaves Table */}
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Applicant</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Days</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="w-24"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center py-8">Loading...</TableCell>
                    </TableRow>
                  ) : leaves.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                        No leave applications found
                      </TableCell>
                    </TableRow>
                  ) : (
                    leaves.map((leave) => (
                      <TableRow key={leave.id}>
                        <TableCell className="font-medium">{leave.applicant_name}</TableCell>
                        <TableCell className="capitalize">{leave.leave_type}</TableCell>
                        <TableCell>{format(new Date(leave.leave_date), 'MMM dd, yyyy')}</TableCell>
                        <TableCell>{leave.days} day(s)</TableCell>
                        <TableCell>{getStatusBadge(leave.status)}</TableCell>
                        <TableCell>
                          {canApprove && leave.status === 'pending' && (
                            <Button
                              size="sm"
                              onClick={() => { setSelectedLeave(leave); setApproveDialogOpen(true); }}
                            >
                              Review
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Apply Dialog */}
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Apply for Leave</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit}>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="leave_type">Leave Type *</Label>
                    <Select
                      value={formData.leave_type}
                      onValueChange={(value) => setFormData({ ...formData, leave_type: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="sick">Sick Leave</SelectItem>
                        <SelectItem value="casual">Casual Leave</SelectItem>
                        <SelectItem value="emergency">Emergency</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="leave_date">Date *</Label>
                      <Input
                        id="leave_date"
                        type="date"
                        value={formData.leave_date}
                        onChange={(e) => setFormData({ ...formData, leave_date: e.target.value })}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="days">Days *</Label>
                      <Input
                        id="days"
                        type="number"
                        min="1"
                        value={formData.days}
                        onChange={(e) => setFormData({ ...formData, days: e.target.value })}
                        required
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="reason">Reason *</Label>
                    <Textarea
                      id="reason"
                      value={formData.reason}
                      onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                      placeholder="Please provide a reason for your leave..."
                      required
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit">Submit Application</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>

          {/* Approve/Reject Dialog */}
          <Dialog open={approveDialogOpen} onOpenChange={setApproveDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Review Leave Application</DialogTitle>
                <DialogDescription>
                  {selectedLeave?.applicant_name} - {selectedLeave?.leave_type} leave
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleApproveReject}>
                <div className="space-y-4 py-4">
                  <div className="p-4 bg-muted rounded-lg">
                    <p className="text-sm font-medium">Reason:</p>
                    <p className="text-sm text-muted-foreground">{selectedLeave?.reason}</p>
                  </div>
                  <div className="space-y-2">
                    <Label>Action</Label>
                    <Select
                      value={approveData.action}
                      onValueChange={(value) => setApproveData({ ...approveData, action: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="approve">Approve</SelectItem>
                        <SelectItem value="reject">Reject</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="remarks">Remarks</Label>
                    <Textarea
                      id="remarks"
                      value={approveData.remarks}
                      onChange={(e) => setApproveData({ ...approveData, remarks: e.target.value })}
                      placeholder="Optional remarks..."
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit">
                    {approveData.action === 'approve' ? 'Approve' : 'Reject'}
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
