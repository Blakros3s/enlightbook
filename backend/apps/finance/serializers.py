from rest_framework import serializers
from django.db import transaction
from decimal import Decimal

from .models import (
    FeeCategoryName, FeeStructure, StudentBill, BillItem, PaymentMethod,
    StudentPayment, PaymentAllocation, Scholarship, FeeInstallmentPlan,
    FeeInstallment, StudentInstallmentAssignment, FeeRefund,
    FinancialTransactionLog
)
from apps.academic.models import Class, AcademicYear


class FeeCategoryNameSerializer(serializers.ModelSerializer):
    """Serializer for fee category names (master list)."""
    
    class Meta:
        model = FeeCategoryName
        fields = ['id', 'name', 'description', 'is_mandatory', 'is_recurring', 'is_active', 'created_at']
        read_only_fields = ['created_at']


class FeeStructureListSerializer(serializers.ModelSerializer):
    """List serializer for fee structures."""
    school_class_name = serializers.CharField(source='school_class.class_name', read_only=True)
    fee_category_name_str = serializers.CharField(source='fee_category_name.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.year_name', read_only=True)
    
    class Meta:
        model = FeeStructure
        fields = [
            'id', 'school_class', 'school_class_name', 'fee_category_name',
            'fee_category_name_str', 'amount', 'academic_year', 'academic_year_name',
            'is_active', 'created_at'
        ]
        read_only_fields = ['created_at']


class FeeStructureDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for fee structures."""
    
    class Meta:
        model = FeeStructure
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class BillItemSerializer(serializers.ModelSerializer):
    """Serializer for bill items."""
    fee_category_name = serializers.CharField(source='fee_structure.fee_category_name.name', read_only=True)
    
    class Meta:
        model = BillItem
        fields = ['id', 'fee_structure', 'fee_category_name', 'description', 'amount']


class StudentBillListSerializer(serializers.ModelSerializer):
    """List serializer for student bills."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_username = serializers.CharField(source='student.username', read_only=True)
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    outstanding_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = StudentBill
        fields = [
            'id', 'bill_number', 'student', 'student_name', 'student_username',
            'bill_date', 'due_date', 'total_amount', 'amount_paid',
            'outstanding_amount', 'status', 'is_overdue', 'billing_month'
        ]


class StudentBillDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for student bills."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    items = BillItemSerializer(many=True, read_only=True)
    allocations = serializers.SerializerMethodField()
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    outstanding_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    is_fully_paid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = StudentBill
        fields = [
            'id', 'bill_number', 'student', 'student_name', 'bill_date', 'due_date',
            'billing_month', 'academic_year', 'subtotal', 'discount_amount',
            'tax_amount', 'late_fee_amount', 'total_amount', 'amount_paid',
            'outstanding_amount', 'status', 'is_overdue', 'is_fully_paid',
            'late_fee_percentage', 'notes', 'items', 'allocations',
            'issued_by', 'issued_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'bill_number', 'amount_paid', 'outstanding_amount', 'is_overdue',
            'is_fully_paid', 'issued_at', 'created_at', 'updated_at'
        ]
    
    def get_allocations(self, obj):
        """Get payment allocations for this bill."""
        allocations = obj.allocations.select_related('payment')
        return [
            {
                'id': alloc.id,
                'payment_number': alloc.payment.payment_number,
                'payment_date': alloc.payment.payment_date,
                'amount_applied': alloc.amount_applied,
                'created_at': alloc.created_at
            }
            for alloc in allocations
        ]


class StudentBillCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bills with items."""
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    
    class Meta:
        model = StudentBill
        fields = [
            'student', 'due_date', 'billing_month', 'academic_year',
            'discount_amount', 'tax_amount', 'notes', 'items'
        ]
    
    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        
        # Calculate subtotal from items
        subtotal = sum(Decimal(str(item.get('amount', 0))) for item in items_data)
        validated_data['subtotal'] = subtotal
        
        # Create bill
        bill = StudentBill.objects.create(**validated_data)
        
        # Create bill items
        for item_data in items_data:
            BillItem.objects.create(
                bill=bill,
                fee_structure_id=item_data.get('fee_structure_id'),
                description=item_data.get('description', ''),
                amount=Decimal(str(item_data.get('amount', 0)))
            )
        
        # Recalculate total
        bill.save()
        
        return bill


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for payment methods."""
    
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'code', 'requires_reference', 'is_active']


class PaymentAllocationSerializer(serializers.ModelSerializer):
    """Serializer for payment allocations."""
    bill_number = serializers.CharField(source='bill.bill_number', read_only=True)
    
    class Meta:
        model = PaymentAllocation
        fields = ['id', 'bill', 'bill_number', 'amount_applied', 'created_at']
        read_only_fields = ['created_at']


class StudentPaymentListSerializer(serializers.ModelSerializer):
    """List serializer for student payments."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)
    allocated_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    unallocated_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = StudentPayment
        fields = [
            'id', 'payment_number', 'student', 'student_name', 'payment_date',
            'amount_paid', 'allocated_amount', 'unallocated_amount',
            'payment_method', 'payment_method_name', 'status', 'created_at'
        ]


class StudentPaymentDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for student payments."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)
    allocations = PaymentAllocationSerializer(many=True, read_only=True)
    allocated_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    unallocated_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = StudentPayment
        fields = [
            'id', 'payment_number', 'student', 'student_name', 'payment_date',
            'amount_paid', 'payment_method', 'payment_method_name',
            'reference_number', 'bank_name', 'status', 'notes',
            'allocated_amount', 'unallocated_amount', 'allocations',
            'verified_by', 'verified_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'payment_number', 'allocated_amount', 'unallocated_amount',
            'verified_at', 'created_at', 'updated_at'
        ]


class StudentPaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments with allocations."""
    allocations = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = StudentPayment
        fields = [
            'student', 'payment_date', 'amount_paid', 'payment_method',
            'reference_number', 'bank_name', 'notes', 'allocations'
        ]
    
    @transaction.atomic
    def create(self, validated_data):
        allocations_data = validated_data.pop('allocations', [])
        
        # Create payment
        payment = StudentPayment.objects.create(**validated_data)
        
        # Create allocations
        for alloc_data in allocations_data:
            PaymentAllocation.objects.create(
                payment=payment,
                bill_id=alloc_data.get('bill_id'),
                amount_applied=Decimal(str(alloc_data.get('amount_applied', 0)))
            )
        
        return payment


class PaymentAllocationCreateSerializer(serializers.Serializer):
    """Serializer for creating payment allocations."""
    bill_id = serializers.IntegerField()
    amount_applied = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate(self, data):
        # Validate bill exists and has outstanding balance
        try:
            bill = StudentBill.objects.get(id=data['bill_id'])
            if data['amount_applied'] > bill.outstanding_amount:
                raise serializers.ValidationError(
                    f"Amount exceeds outstanding balance ({bill.outstanding_amount})"
                )
        except StudentBill.DoesNotExist:
            raise serializers.ValidationError("Bill not found")
        
        return data


class ScholarshipListSerializer(serializers.ModelSerializer):
    """List serializer for scholarships."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    discount_type_display = serializers.CharField(source='get_discount_type_display', read_only=True)
    
    class Meta:
        model = Scholarship
        fields = [
            'id', 'student', 'student_name', 'scholarship_name',
            'scholarship_type', 'discount_type', 'discount_type_display',
            'discount_value', 'valid_from', 'valid_until', 'is_active'
        ]


class ScholarshipDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for scholarships."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    applicable_fee_categories_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Scholarship
        fields = [
            'id', 'student', 'student_name', 'scholarship_name', 'scholarship_type',
            'discount_type', 'discount_value', 'applicable_to_all_fees',
            'applicable_fee_categories', 'applicable_fee_categories_display',
            'valid_from', 'valid_until', 'academic_year', 'approved_by',
            'approved_by_name', 'approved_at', 'is_active', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['approved_at', 'created_at', 'updated_at']
    
    def get_applicable_fee_categories_display(self, obj):
        return [cat.name for cat in obj.applicable_fee_categories.all()]


class ScholarshipCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating scholarships."""
    applicable_fee_category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Scholarship
        fields = [
            'student', 'scholarship_name', 'scholarship_type', 'discount_type',
            'discount_value', 'applicable_to_all_fees', 'applicable_fee_category_ids',
            'valid_from', 'valid_until', 'academic_year', 'notes'
        ]
    
    @transaction.atomic
    def create(self, validated_data):
        category_ids = validated_data.pop('applicable_fee_category_ids', [])
        
        scholarship = super().create(validated_data)
        
        if category_ids:
            scholarship.applicable_fee_categories.set(category_ids)
        
        return scholarship


class FeeInstallmentSerializer(serializers.ModelSerializer):
    """Serializer for fee installments."""
    
    class Meta:
        model = FeeInstallment
        fields = ['id', 'installment_number', 'percentage', 'due_day', 'due_month_offset', 'description']


class FeeInstallmentPlanSerializer(serializers.ModelSerializer):
    """Serializer for installment plans."""
    school_class_name = serializers.CharField(source='school_class.class_name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.year_name', read_only=True)
    installments = FeeInstallmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = FeeInstallmentPlan
        fields = [
            'id', 'name', 'school_class', 'school_class_name',
            'academic_year', 'academic_year_name', 'number_of_installments',
            'installments', 'is_active', 'created_at'
        ]


class FeeInstallmentPlanCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating installment plans with installments."""
    installments = FeeInstallmentSerializer(many=True, write_only=True)
    
    class Meta:
        model = FeeInstallmentPlan
        fields = ['name', 'school_class', 'academic_year', 'number_of_installments', 'installments']
    
    @transaction.atomic
    def create(self, validated_data):
        installments_data = validated_data.pop('installments', [])
        
        plan = FeeInstallmentPlan.objects.create(**validated_data)
        
        for installment_data in installments_data:
            FeeInstallment.objects.create(plan=plan, **installment_data)
        
        return plan


class StudentInstallmentAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for student installment assignments."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    installment_plan_name = serializers.CharField(source='installment_plan.name', read_only=True)
    
    class Meta:
        model = StudentInstallmentAssignment
        fields = [
            'id', 'student', 'student_name', 'installment_plan',
            'installment_plan_name', 'academic_year', 'assigned_date', 'is_active'
        ]
        read_only_fields = ['assigned_date']


class FeeRefundSerializer(serializers.ModelSerializer):
    """Serializer for fee refunds."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)
    
    class Meta:
        model = FeeRefund
        fields = [
            'id', 'refund_number', 'student', 'student_name', 'amount',
            'reason', 'original_payment', 'refund_method', 'status',
            'approved_by', 'approved_by_name', 'approved_at',
            'processed_by', 'processed_by_name', 'processed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'refund_number', 'approved_by', 'approved_at',
            'processed_by', 'processed_at', 'created_at', 'updated_at'
        ]


class FinancialTransactionLogSerializer(serializers.ModelSerializer):
    """Serializer for financial transaction logs."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    
    class Meta:
        model = FinancialTransactionLog
        fields = [
            'id', 'transaction_type', 'transaction_type_display', 'student',
            'student_name', 'bill', 'payment', 'amount', 'balance_after',
            'description', 'performed_by', 'performed_by_name',
            'performed_at', 'ip_address'
        ]
        read_only_fields = ['performed_at']


class StudentLedgerSerializer(serializers.Serializer):
    """Serializer for student ledger."""
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    academic_year = serializers.CharField()
    
    # Summary
    total_billed = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_discounts = serializers.DecimalField(max_digits=10, decimal_places=2)
    current_balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Details
    transactions = serializers.ListField(child=serializers.DictField())


class BulkBillGenerationSerializer(serializers.Serializer):
    """Serializer for bulk bill generation."""
    school_class_id = serializers.IntegerField()
    fee_category_ids = serializers.ListField(child=serializers.IntegerField())
    billing_month = serializers.DateField()
    due_date = serializers.DateField()
    academic_year_id = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        # Validate class exists
        try:
            Class.objects.get(id=data['school_class_id'])
        except Class.DoesNotExist:
            raise serializers.ValidationError("Class not found")
        
        # Validate academic year exists
        try:
            AcademicYear.objects.get(id=data['academic_year_id'])
        except AcademicYear.DoesNotExist:
            raise serializers.ValidationError("Academic year not found")
        
        return data


class FinancialReportSerializer(serializers.Serializer):
    """Serializer for financial reports."""
    report_type = serializers.ChoiceField(choices=[
        ('daily_collection', 'Daily Collection'),
        ('monthly_summary', 'Monthly Summary'),
        ('outstanding_fees', 'Outstanding Fees'),
        ('class_wise', 'Class-wise Collection'),
    ])
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    class_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date must be before end date")
        return data
