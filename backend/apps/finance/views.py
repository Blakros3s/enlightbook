from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    FeeCategoryName, FeeStructure, StudentBill, BillItem, PaymentMethod,
    StudentPayment, PaymentAllocation, Scholarship, FeeInstallmentPlan,
    FeeInstallment, StudentInstallmentAssignment, FeeRefund,
    FinancialTransactionLog
)
from .serializers import (
    FeeCategoryNameSerializer, FeeStructureListSerializer, FeeStructureDetailSerializer,
    StudentBillListSerializer, StudentBillDetailSerializer, StudentBillCreateSerializer,
    BillItemSerializer, PaymentMethodSerializer,
    StudentPaymentListSerializer, StudentPaymentDetailSerializer, StudentPaymentCreateSerializer,
    PaymentAllocationSerializer, PaymentAllocationCreateSerializer,
    ScholarshipListSerializer, ScholarshipDetailSerializer, ScholarshipCreateSerializer,
    FeeInstallmentPlanSerializer, FeeInstallmentPlanCreateSerializer,
    StudentInstallmentAssignmentSerializer,
    FeeRefundSerializer, FinancialTransactionLogSerializer,
    StudentLedgerSerializer, BulkBillGenerationSerializer, FinancialReportSerializer
)
from apps.academic.models import ClassEnrollment


class FeeCategoryNameViewSet(viewsets.ModelViewSet):
    """ViewSet for fee category names (master list)."""
    queryset = FeeCategoryName.objects.all()
    serializer_class = FeeCategoryNameSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class FeeStructureViewSet(viewsets.ModelViewSet):
    """ViewSet for fee structures."""
    queryset = FeeStructure.objects.select_related('school_class', 'fee_category_name', 'academic_year')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['school_class', 'fee_category_name', 'academic_year', 'is_active']
    search_fields = ['school_class__class_name', 'fee_category_name__name']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FeeStructureDetailSerializer
        return FeeStructureListSerializer


class StudentBillViewSet(viewsets.ModelViewSet):
    """ViewSet for student bills."""
    queryset = StudentBill.objects.select_related('student', 'academic_year').prefetch_related('items', 'allocations')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'academic_year', 'status', 'billing_month']
    search_fields = ['bill_number', 'student__first_name', 'student__last_name', 'student__username']
    ordering_fields = ['bill_date', 'due_date', 'total_amount', 'created_at']
    ordering = ['-bill_date']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StudentBillCreateSerializer
        elif self.action == 'list':
            return StudentBillListSerializer
        return StudentBillDetailSerializer
    
    @action(detail=True, methods=['post'])
    def issue(self, request, pk=None):
        """Issue a draft bill."""
        bill = self.get_object()
        if bill.status != 'draft':
            return Response(
                {'error': 'Only draft bills can be issued'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bill.status = 'issued'
        bill.issued_by = request.user
        bill.issued_at = timezone.now()
        bill.save()
        
        # Log transaction
        FinancialTransactionLog.objects.create(
            transaction_type='bill_created',
            student=bill.student,
            bill=bill,
            amount=bill.total_amount,
            balance_after=bill.outstanding_amount,
            description=f'Bill {bill.bill_number} issued',
            performed_by=request.user,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({'status': 'Bill issued successfully'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a bill."""
        bill = self.get_object()
        if bill.status in ['fully_paid']:
            return Response(
                {'error': 'Cannot cancel a fully paid bill'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bill.status = 'cancelled'
        bill.save()
        
        # Log transaction
        FinancialTransactionLog.objects.create(
            transaction_type='bill_cancelled',
            student=bill.student,
            bill=bill,
            amount=Decimal('0.00'),
            balance_after=Decimal('0.00'),
            description=f'Bill {bill.bill_number} cancelled',
            performed_by=request.user,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({'status': 'Bill cancelled successfully'})
    
    @action(detail=True, methods=['post'])
    def apply_scholarship(self, request, pk=None):
        """Apply scholarship discount to bill."""
        bill = self.get_object()
        scholarship_id = request.data.get('scholarship_id')
        
        if not scholarship_id:
            return Response(
                {'error': 'scholarship_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            scholarship = Scholarship.objects.get(id=scholarship_id, student=bill.student)
        except Scholarship.DoesNotExist:
            return Response(
                {'error': 'Scholarship not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calculate discount
        discount = scholarship.calculate_discount(bill.subtotal)
        bill.discount_amount = discount
        bill.save()
        
        # Log transaction
        FinancialTransactionLog.objects.create(
            transaction_type='scholarship_applied',
            student=bill.student,
            bill=bill,
            amount=discount,
            balance_after=bill.outstanding_amount,
            description=f'Scholarship {scholarship.scholarship_name} applied',
            performed_by=request.user,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({
            'status': 'Scholarship applied successfully',
            'discount_amount': str(discount),
            'new_total': str(bill.total_amount)
        })
    
    @action(detail=False, methods=['post'])
    def bulk_generate(self, request):
        """Generate bills for all students in a class."""
        serializer = BulkBillGenerationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Get all active students in class
        enrollments = ClassEnrollment.objects.filter(
            school_class_id=data['school_class_id'],
            status='active'
        ).select_related('student')
        
        bills_created = 0
        for enrollment in enrollments:
            # Create bill
            bill = StudentBill.objects.create(
                student=enrollment.student,
                due_date=data['due_date'],
                billing_month=data['billing_month'],
                academic_year_id=data['academic_year_id'],
                notes=data.get('notes', ''),
                status='draft'
            )
            
            # Add bill items
            for fee_structure in FeeStructure.objects.filter(
                id__in=data['fee_category_ids'],
                school_class_id=data['school_class_id'],
                academic_year_id=data['academic_year_id'],
                is_active=True
            ):
                BillItem.objects.create(
                    bill=bill,
                    fee_structure=fee_structure,
                    description=fee_structure.fee_category_name.name,
                    amount=fee_structure.amount
                )
            
            # Apply applicable scholarships
            scholarships = Scholarship.objects.filter(
                student=enrollment.student,
                academic_year_id=data['academic_year_id'],
                is_active=True,
                valid_from__lte=data['billing_month'],
                valid_until__gte=data['billing_month']
            )
            
            total_discount = Decimal('0.00')
            for scholarship in scholarships:
                discount = scholarship.calculate_discount(bill.subtotal)
                total_discount += discount
            
            if total_discount > 0:
                bill.discount_amount = total_discount
                bill.save()
            
            bills_created += 1
        
        return Response({
            'status': f'{bills_created} bills generated successfully',
            'bills_created': bills_created
        })
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue bills."""
        bills = StudentBill.objects.filter(
            due_date__lt=timezone.now().date(),
            status__in=['issued', 'partially_paid']
        ).select_related('student')
        
        serializer = StudentBillListSerializer(bills, many=True)
        return Response(serializer.data)


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """ViewSet for payment methods."""
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]


class StudentPaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for student payments."""
    queryset = StudentPayment.objects.select_related('student', 'payment_method').prefetch_related('allocations')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'payment_method', 'status', 'payment_date']
    search_fields = ['payment_number', 'student__first_name', 'student__last_name', 'reference_number']
    ordering_fields = ['payment_date', 'amount_paid', 'created_at']
    ordering = ['-payment_date']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StudentPaymentCreateSerializer
        elif self.action == 'list':
            return StudentPaymentListSerializer
        return StudentPaymentDetailSerializer
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a payment."""
        payment = self.get_object()
        
        if payment.status != 'pending':
            return Response(
                {'error': 'Only pending payments can be verified'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = 'verified'
        payment.verified_by = request.user
        payment.verified_at = timezone.now()
        payment.save()
        
        # Log transaction
        FinancialTransactionLog.objects.create(
            transaction_type='payment_received',
            student=payment.student,
            payment=payment,
            amount=payment.amount_paid,
            balance_after=self._get_student_balance(payment.student),
            description=f'Payment {payment.payment_number} verified',
            performed_by=request.user,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({'status': 'Payment verified successfully'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a payment."""
        payment = self.get_object()
        
        if payment.status != 'pending':
            return Response(
                {'error': 'Only pending payments can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = 'rejected'
        payment.save()
        
        return Response({'status': 'Payment rejected'})
    
    @action(detail=True, methods=['post'])
    def allocate(self, request, pk=None):
        """Allocate payment to bills."""
        payment = self.get_object()
        
        allocations_data = request.data.get('allocations', [])
        
        if not allocations_data:
            return Response(
                {'error': 'allocations are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_allocations = []
        for alloc_data in allocations_data:
            serializer = PaymentAllocationCreateSerializer(data=alloc_data)
            if serializer.is_valid():
                allocation = PaymentAllocation.objects.create(
                    payment=payment,
                    bill_id=serializer.validated_data['bill_id'],
                    amount_applied=serializer.validated_data['amount_applied']
                )
                created_allocations.append(allocation)
                
                # Log transaction
                FinancialTransactionLog.objects.create(
                    transaction_type='payment_allocated',
                    student=payment.student,
                    bill=allocation.bill,
                    payment=payment,
                    amount=allocation.amount_applied,
                    balance_after=self._get_student_balance(payment.student),
                    description=f'Payment allocated to bill {allocation.bill.bill_number}',
                    performed_by=request.user,
                    ip_address=request.META.get('REMOTE_ADDR')
                )
        
        return Response({
            'status': f'{len(created_allocations)} allocations created',
            'allocations': PaymentAllocationSerializer(created_allocations, many=True).data
        })
    
    def _get_student_balance(self, student):
        """Get current balance for a student."""
        total_billed = StudentBill.objects.filter(
            student=student,
            status__in=['issued', 'partially_paid', 'overdue', 'fully_paid']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        total_paid = StudentPayment.objects.filter(
            student=student,
            status='verified'
        ).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
        
        return total_billed - total_paid


class ScholarshipViewSet(viewsets.ModelViewSet):
    """ViewSet for scholarships."""
    queryset = Scholarship.objects.select_related('student', 'academic_year', 'approved_by').prefetch_related('applicable_fee_categories')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['student', 'academic_year', 'discount_type', 'is_active']
    search_fields = ['student__first_name', 'student__last_name', 'scholarship_name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ScholarshipCreateSerializer
        elif self.action == 'list':
            return ScholarshipListSerializer
        return ScholarshipDetailSerializer
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a scholarship."""
        scholarship = self.get_object()
        
        if scholarship.approved_by:
            return Response(
                {'error': 'Scholarship is already approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        scholarship.approved_by = request.user
        scholarship.approved_at = timezone.now()
        scholarship.save()
        
        return Response({'status': 'Scholarship approved successfully'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a scholarship."""
        scholarship = self.get_object()
        scholarship.is_active = False
        scholarship.save()
        
        return Response({'status': 'Scholarship deactivated'})
    
    @action(detail=False, methods=['get'])
    def by_student(self, request):
        """Get scholarships for a specific student."""
        student_id = request.query_params.get('student_id')
        
        if not student_id:
            return Response(
                {'error': 'student_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        scholarships = self.get_queryset().filter(student_id=student_id)
        serializer = ScholarshipListSerializer(scholarships, many=True)
        return Response(serializer.data)


class FeeInstallmentPlanViewSet(viewsets.ModelViewSet):
    """ViewSet for installment plans."""
    queryset = FeeInstallmentPlan.objects.select_related('school_class', 'academic_year').prefetch_related('installments')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['school_class', 'academic_year', 'is_active']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FeeInstallmentPlanCreateSerializer
        return FeeInstallmentPlanSerializer


class StudentInstallmentAssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for student installment assignments."""
    queryset = StudentInstallmentAssignment.objects.select_related('student', 'installment_plan', 'academic_year')
    serializer_class = StudentInstallmentAssignmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'installment_plan', 'academic_year', 'is_active']


class FeeRefundViewSet(viewsets.ModelViewSet):
    """ViewSet for fee refunds."""
    queryset = FeeRefund.objects.select_related('student', 'original_payment', 'approved_by', 'processed_by')
    serializer_class = FeeRefundSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['student', 'status', 'refund_method']
    search_fields = ['refund_number', 'student__first_name', 'student__last_name']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a refund request."""
        refund = self.get_object()
        
        if refund.status != 'pending':
            return Response(
                {'error': 'Only pending refunds can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        refund.status = 'approved'
        refund.approved_by = request.user
        refund.approved_at = timezone.now()
        refund.save()
        
        return Response({'status': 'Refund approved'})
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process an approved refund."""
        refund = self.get_object()
        
        if refund.status != 'approved':
            return Response(
                {'error': 'Only approved refunds can be processed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        refund.status = 'processed'
        refund.processed_by = request.user
        refund.processed_at = timezone.now()
        refund.save()
        
        # Log transaction
        FinancialTransactionLog.objects.create(
            transaction_type='refund_processed',
            student=refund.student,
            amount=refund.amount,
            balance_after=self._get_student_balance(refund.student),
            description=f'Refund {refund.refund_number} processed',
            performed_by=request.user,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({'status': 'Refund processed'})
    
    def _get_student_balance(self, student):
        """Get current balance for a student."""
        total_billed = StudentBill.objects.filter(
            student=student,
            status__in=['issued', 'partially_paid', 'overdue', 'fully_paid']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        total_paid = StudentPayment.objects.filter(
            student=student,
            status='verified'
        ).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
        
        return total_billed - total_paid


class FinancialTransactionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for financial transaction logs (read-only)."""
    queryset = FinancialTransactionLog.objects.select_related('student', 'bill', 'payment', 'performed_by')
    serializer_class = FinancialTransactionLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['transaction_type', 'student', 'performed_by', 'performed_at']
    search_fields = ['student__first_name', 'student__last_name', 'description']
    ordering = ['-performed_at']


class FinancialReportViewSet(viewsets.ViewSet):
    """ViewSet for financial reports."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate financial report."""
        serializer = FinancialReportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        report_type = data['report_type']
        start_date = data['start_date']
        end_date = data['end_date']
        
        if report_type == 'daily_collection':
            return self._daily_collection_report(start_date, end_date)
        elif report_type == 'monthly_summary':
            return self._monthly_summary_report(start_date, end_date)
        elif report_type == 'outstanding_fees':
            return self._outstanding_fees_report(data.get('class_id'))
        elif report_type == 'class_wise':
            return self._class_wise_report(start_date, end_date)
        else:
            return Response(
                {'error': 'Invalid report type'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _daily_collection_report(self, start_date, end_date):
        """Generate daily collection report."""
        payments = StudentPayment.objects.filter(
            payment_date__range=[start_date, end_date],
            status='verified'
        ).values('payment_date').annotate(
            total_amount=Sum('amount_paid'),
            count=Count('id')
        ).order_by('payment_date')
        
        total = payments.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        return Response({
            'report_type': 'Daily Collection',
            'start_date': start_date,
            'end_date': end_date,
            'total_collection': str(total),
            'total_transactions': sum(p['count'] for p in payments),
            'daily_breakdown': list(payments)
        })
    
    def _monthly_summary_report(self, start_date, end_date):
        """Generate monthly summary report."""
        # Bills issued
        bills = StudentBill.objects.filter(
            bill_date__range=[start_date, end_date],
            status__in=['issued', 'partially_paid', 'fully_paid', 'overdue']
        ).aggregate(
            total_billed=Sum('total_amount'),
            total_discounts=Sum('discount_amount'),
            count=Count('id')
        )
        
        # Payments received
        payments = StudentPayment.objects.filter(
            payment_date__range=[start_date, end_date],
            status='verified'
        ).aggregate(
            total_collected=Sum('amount_paid'),
            count=Count('id')
        )
        
        # Outstanding
        outstanding = StudentBill.objects.filter(
            status__in=['issued', 'partially_paid', 'overdue']
        ).aggregate(
            total_outstanding=Sum('total_amount') - Sum('allocations__amount_applied')
        )
        
        return Response({
            'report_type': 'Monthly Summary',
            'start_date': start_date,
            'end_date': end_date,
            'bills_issued': {
                'count': bills['count'] or 0,
                'total_billed': str(bills['total_billed'] or Decimal('0.00')),
                'total_discounts': str(bills['total_discounts'] or Decimal('0.00'))
            },
            'payments_received': {
                'count': payments['count'] or 0,
                'total_collected': str(payments['total_collected'] or Decimal('0.00'))
            },
            'outstanding': str(outstanding['total_outstanding'] or Decimal('0.00'))
        })
    
    def _outstanding_fees_report(self, class_id=None):
        """Generate outstanding fees report."""
        queryset = StudentBill.objects.filter(
            status__in=['issued', 'partially_paid', 'overdue']
        ).select_related('student', 'school_class')
        
        if class_id:
            queryset = queryset.filter(school_class_id=class_id)
        
        outstanding_by_student = queryset.values(
            'student__id',
            'student__first_name',
            'student__last_name',
            'student__username'
        ).annotate(
            total_outstanding=Sum('total_amount') - Sum('allocations__amount_applied')
        ).filter(total_outstanding__gt=0).order_by('-total_outstanding')
        
        total_outstanding = sum(item['total_outstanding'] for item in outstanding_by_student)
        
        return Response({
            'report_type': 'Outstanding Fees',
            'total_outstanding': str(total_outstanding),
            'total_students': len(outstanding_by_student),
            'students': list(outstanding_by_student)
        })
    
    def _class_wise_report(self, start_date, end_date):
        """Generate class-wise collection report."""
        payments = StudentPayment.objects.filter(
            payment_date__range=[start_date, end_date],
            status='verified'
        ).values(
            'student__class_enrollments__school_class__class_name'
        ).annotate(
            total_collected=Sum('amount_paid'),
            count=Count('id')
        ).order_by('-total_collected')
        
        return Response({
            'report_type': 'Class-wise Collection',
            'start_date': start_date,
            'end_date': end_date,
            'class_breakdown': list(payments)
        })
    
    @action(detail=False, methods=['get'])
    def student_ledger(self, request):
        """Get student ledger statement."""
        student_id = request.query_params.get('student_id')
        
        if not student_id:
            return Response(
                {'error': 'student_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get bills
        bills = StudentBill.objects.filter(student_id=student_id).order_by('bill_date')
        
        # Get payments
        payments = StudentPayment.objects.filter(student_id=student_id).order_by('payment_date')
        
        # Combine and sort transactions
        transactions = []
        
        for bill in bills:
            transactions.append({
                'date': bill.bill_date,
                'type': 'bill',
                'description': f'Bill #{bill.bill_number}',
                'debit': str(bill.total_amount),
                'credit': '0.00',
                'balance': str(bill.outstanding_amount)
            })
        
        for payment in payments:
            if payment.status == 'verified':
                transactions.append({
                    'date': payment.payment_date,
                    'type': 'payment',
                    'description': f'Payment #{payment.payment_number}',
                    'debit': '0.00',
                    'credit': str(payment.amount_paid),
                    'balance': '0.00'  # Will be calculated
                })
        
        # Sort by date
        transactions.sort(key=lambda x: x['date'])
        
        # Calculate running balance
        balance = Decimal('0.00')
        for trans in transactions:
            balance += Decimal(trans['debit']) - Decimal(trans['credit'])
            trans['balance'] = str(balance)
        
        # Calculate totals
        total_billed = sum(Decimal(t['debit']) for t in transactions)
        total_paid = sum(Decimal(t['credit']) for t in transactions)
        
        return Response({
            'student_id': student_id,
            'total_billed': str(total_billed),
            'total_paid': str(total_paid),
            'current_balance': str(balance),
            'transactions': transactions
        })
