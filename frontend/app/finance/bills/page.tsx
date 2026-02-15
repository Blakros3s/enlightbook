'use client';

import React, { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { billApi, studentEnrollmentApi } from '@/lib/api-finance';
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
import { Plus, FileText, DollarSign, Search, MoreHorizontal, Eye, Download, CheckCircle, XCircle } from 'lucide-react';

export default function BillsPage() {
  const [bills, setBills] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    student: '',
    billing_month: '',
    due_date: '',
    items: [] as { fee_category: string; amount: string }[],
  });

  useEffect(() => {
    fetchBills();
  }, []);

  const fetchBills = async () => {
    try {
      const data = await billApi.getAll();
      setBills(data.results || data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to fetch bills',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (id: number, action: 'issue' | 'cancel') => {
    try {
      if (action === 'issue') {
        await billApi.issue(id);
      } else {
        await billApi.cancel(id);
      }
      toast({ title: 'Success', description: `Bill ${action}d successfully` });
      fetchBills();
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to update bill', variant: 'destructive' });
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      draft: 'bg-slate-100 text-slate-800',
      issued: 'bg-blue-100 text-blue-800',
      partially_paid: 'bg-amber-100 text-amber-800',
      paid: 'bg-emerald-100 text-emerald-800',
      cancelled: 'bg-rose-100 text-rose-800',
      overdue: 'bg-red-100 text-red-800',
    };
    return <Badge className={variants[status] || ''}>{status.replace('_', ' ').toUpperCase()}</Badge>;
  };

  const filteredBills = bills.filter(bill =>
    bill.student_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    bill.bill_number?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Bills</h1>
              <p className="text-muted-foreground">Manage student fee bills</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline">
                <Download className="mr-2 h-4 w-4" />
                Bulk Generate
              </Button>
              <Button onClick={() => setDialogOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Create Bill
              </Button>
            </div>
          </div>

          {/* Stats */}
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Total Outstanding</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-rose-600">
                  ₹{bills.filter(b => ['issued', 'partially_paid', 'overdue'].includes(b.status))
                    .reduce((sum, b) => sum + parseFloat(b.outstanding_amount || 0), 0).toLocaleString()}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Paid This Month</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-emerald-600">
                  ₹{bills.filter(b => b.status === 'paid')
                    .reduce((sum, b) => sum + parseFloat(b.total_amount || 0), 0).toLocaleString()}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Overdue Bills</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-amber-600">
                  {bills.filter(b => b.status === 'overdue').length}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Total Bills</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{bills.length}</div>
              </CardContent>
            </Card>
          </div>

          {/* Search */}
          <div className="flex items-center gap-4">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search bills..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>

          {/* Bills Table */}
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Bill #</TableHead>
                    <TableHead>Student</TableHead>
                    <TableHead>Billing Month</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Paid</TableHead>
                    <TableHead>Outstanding</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="w-12"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center py-8">Loading...</TableCell>
                    </TableRow>
                  ) : filteredBills.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                        No bills found
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredBills.map((bill) => (
                      <TableRow key={bill.id}>
                        <TableCell className="font-medium">{bill.bill_number}</TableCell>
                        <TableCell>{bill.student_name}</TableCell>
                        <TableCell>{new Date(bill.billing_month).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</TableCell>
                        <TableCell className="font-medium">₹{parseFloat(bill.total_amount).toLocaleString()}</TableCell>
                        <TableCell>₹{parseFloat(bill.amount_paid || 0).toLocaleString()}</TableCell>
                        <TableCell className={parseFloat(bill.outstanding_amount) > 0 ? 'text-rose-600 font-medium' : ''}>
                          ₹{parseFloat(bill.outstanding_amount || 0).toLocaleString()}
                        </TableCell>
                        <TableCell>{getStatusBadge(bill.status)}</TableCell>
                        <TableCell>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="icon">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem>
                                <Eye className="mr-2 h-4 w-4" />
                                View
                              </DropdownMenuItem>
                              {bill.status === 'draft' && (
                                <DropdownMenuItem onClick={() => handleStatusChange(bill.id, 'issue')}>
                                  <CheckCircle className="mr-2 h-4 w-4" />
                                  Issue Bill
                                </DropdownMenuItem>
                              )}
                              {bill.status !== 'paid' && bill.status !== 'cancelled' && (
                                <DropdownMenuItem onClick={() => handleStatusChange(bill.id, 'cancel')}>
                                  <XCircle className="mr-2 h-4 w-4" />
                                  Cancel
                                </DropdownMenuItem>
                              )}
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
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
