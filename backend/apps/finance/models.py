from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

from apps.users.models import CustomUser
from apps.academic.models import Class, AcademicYear


class FeeCategoryName(models.Model):
    """
    Master list of fee types (e.g., Tuition, Lab Fee, Sports Fee).
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=True, help_text="Must be paid by all students")
    is_recurring = models.BooleanField(default=True, help_text="Recurs monthly/annually")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Fee Category Name'
        verbose_name_plural = 'Fee Category Names'
    
    def __str__(self):
        return self.name


class FeeStructure(models.Model):
    """
    Class-specific fee amounts for each fee category.
    """
    school_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='fee_structures'
    )
    fee_category_name = models.ForeignKey(
        FeeCategoryName,
        on_delete=models.PROTECT,
        related_name='fee_structures'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='fee_structures'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school_class', 'fee_category_name', 'academic_year']
        ordering = ['school_class', 'fee_category_name']
        verbose_name = 'Fee Structure'
        verbose_name_plural = 'Fee Structures'
    
    def __str__(self):
        return f"{self.school_class.class_name} - {self.fee_category_name}: {self.amount}"


class StudentBill(models.Model):
    """
    Bills generated for students.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('partially_paid', 'Partially Paid'),
        ('fully_paid', 'Fully Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
        ('waived', 'Waived'),
    ]
    
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='bills',
        limit_choices_to={'is_student': True}
    )
    
    # Billing identification
    bill_number = models.CharField(max_length=20, unique=True)
    bill_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    
    # Billing period
    billing_month = models.DateField(help_text="First day of billing month")
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='bills'
    )
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Late fee
    late_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('2.00'))
    late_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Metadata
    notes = models.TextField(blank=True)
    issued_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bills_issued'
    )
    issued_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-bill_date', '-bill_number']
        verbose_name = 'Student Bill'
        verbose_name_plural = 'Student Bills'
    
    def __str__(self):
        return f"{self.bill_number} - {self.student.get_full_name()}"
    
    @property
    def amount_paid(self):
        """Calculate total amount paid."""
        total = self.allocations.aggregate(
            total=models.Sum('amount_applied')
        )['total'] or Decimal('0.00')
        return total
    
    @property
    def outstanding_amount(self):
        """Calculate outstanding amount."""
        return self.total_amount - self.amount_paid
    
    @property
    def is_fully_paid(self):
        """Check if bill is fully paid."""
        return self.outstanding_amount <= Decimal('0.00')
    
    @property
    def is_overdue(self):
        """Check if bill is overdue."""
        if self.status in ['fully_paid', 'cancelled', 'waived']:
            return False
        return timezone.now().date() > self.due_date
    
    def calculate_late_fee(self):
        """Calculate late fee if overdue."""
        if self.is_overdue and self.status not in ['fully_paid', 'cancelled']:
            days_overdue = (timezone.now().date() - self.due_date).days
            daily_rate = self.outstanding_amount * (self.late_fee_percentage / 100)
            self.late_fee_amount = daily_rate * days_overdue
            self.save(update_fields=['late_fee_amount'])
    
    def generate_bill_number(self):
        """Generate unique bill number."""
        year = timezone.now().year
        prefix = f"{year}B"
        
        # Get last bill number for this year
        last_bill = StudentBill.objects.filter(
            bill_number__startswith=prefix
        ).order_by('-bill_number').first()
        
        if last_bill:
            # Extract number and increment
            try:
                last_num = int(last_bill.bill_number.replace(prefix, ''))
                new_num = last_num + 1
            except ValueError:
                new_num = 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:04d}"
    
    def save(self, *args, **kwargs):
        # Generate bill number if not set
        if not self.bill_number:
            self.bill_number = self.generate_bill_number()
        
        # Calculate total
        self.total_amount = (
            self.subtotal - self.discount_amount + 
            self.tax_amount + self.late_fee_amount
        )
        
        # Update status based on payment (only if instance already has a pk)
        if self.pk:
            if self.is_fully_paid:
                self.status = 'fully_paid'
            elif self.amount_paid > 0:
                self.status = 'partially_paid'
            elif self.is_overdue and self.status == 'issued':
                self.status = 'overdue'
        
        super().save(*args, **kwargs)


class BillItem(models.Model):
    """
    Individual line items in a bill.
    """
    bill = models.ForeignKey(
        StudentBill,
        on_delete=models.CASCADE,
        related_name='items'
    )
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.PROTECT,
        related_name='bill_items',
        null=True,
        blank=True
    )
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['id']
        verbose_name = 'Bill Item'
        verbose_name_plural = 'Bill Items'
    
    def __str__(self):
        return f"{self.description}: {self.amount}"


class PaymentMethod(models.Model):
    """
    Available payment methods.
    """
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=20, unique=True)
    requires_reference = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class StudentPayment(models.Model):
    """
    Payments made by students.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('refunded', 'Refunded'),
    ]
    
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='payments',
        limit_choices_to={'is_student': True}
    )
    
    # Payment identification
    payment_number = models.CharField(max_length=20, unique=True)
    payment_date = models.DateField()
    
    # Amount
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment method
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    reference_number = models.CharField(max_length=100, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    
    # Verification
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments_verified',
        limit_choices_to={'is_accountant': True}
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date', '-payment_number']
        verbose_name = 'Student Payment'
        verbose_name_plural = 'Student Payments'
    
    def __str__(self):
        return f"{self.payment_number} - {self.student.get_full_name()} - {self.amount_paid}"
    
    def generate_payment_number(self):
        """Generate unique payment number."""
        year = timezone.now().year
        prefix = f"{year}P"
        
        last_payment = StudentPayment.objects.filter(
            payment_number__startswith=prefix
        ).order_by('-payment_number').first()
        
        if last_payment:
            try:
                last_num = int(last_payment.payment_number.replace(prefix, ''))
                new_num = last_num + 1
            except ValueError:
                new_num = 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:04d}"
    
    def save(self, *args, **kwargs):
        if not self.payment_number:
            self.payment_number = self.generate_payment_number()
        super().save(*args, **kwargs)
    
    @property
    def allocated_amount(self):
        """Get total allocated amount."""
        return self.allocations.aggregate(
            total=models.Sum('amount_applied')
        )['total'] or Decimal('0.00')
    
    @property
    def unallocated_amount(self):
        """Get unallocated amount."""
        return self.amount_paid - self.allocated_amount


class PaymentAllocation(models.Model):
    """
    Links payments to specific bills.
    """
    payment = models.ForeignKey(
        StudentPayment,
        on_delete=models.CASCADE,
        related_name='allocations'
    )
    bill = models.ForeignKey(
        StudentBill,
        on_delete=models.CASCADE,
        related_name='allocations'
    )
    amount_applied = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['payment', 'bill']
        ordering = ['-created_at']
        verbose_name = 'Payment Allocation'
        verbose_name_plural = 'Payment Allocations'
    
    def __str__(self):
        return f"{self.payment.payment_number} → {self.bill.bill_number}: {self.amount_applied}"
    
    def clean(self):
        # Validate amount doesn't exceed bill outstanding
        if self.amount_applied > self.bill.outstanding_amount:
            raise ValidationError(
                f"Amount exceeds outstanding balance ({self.bill.outstanding_amount})"
            )
        
        # Validate amount doesn't exceed unallocated payment
        if self.amount_applied > self.payment.unallocated_amount:
            raise ValidationError(
                f"Amount exceeds unallocated payment ({self.payment.unallocated_amount})"
            )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        # Update bill status
        self.bill.save()


class Scholarship(models.Model):
    """
    Scholarships and discounts for students.
    """
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('full_waiver', 'Full Waiver'),
    ]
    
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='scholarships',
        limit_choices_to={'is_student': True}
    )
    
    # Scholarship details
    scholarship_name = models.CharField(max_length=100)
    scholarship_type = models.CharField(max_length=100, blank=True, help_text="e.g., Merit, Need-based, Sports")
    
    # Discount configuration
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Applicability
    applicable_to_all_fees = models.BooleanField(default=True)
    applicable_fee_categories = models.ManyToManyField(
        FeeCategoryName,
        blank=True,
        related_name='scholarships'
    )
    
    # Validity
    valid_from = models.DateField()
    valid_until = models.DateField()
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='scholarships'
    )
    
    # Approval
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scholarships_approved',
        limit_choices_to={'is_principal': True}
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Scholarship'
        verbose_name_plural = 'Scholarships'
    
    def __str__(self):
        return f"{self.scholarship_name} - {self.student.get_full_name()}"
    
    def calculate_discount(self, amount):
        """Calculate discount amount for a given fee."""
        if self.discount_type == 'full_waiver':
            return amount
        elif self.discount_type == 'percentage':
            return amount * (self.discount_value / 100)
        else:  # fixed
            return min(self.discount_value, amount)
    
    def is_valid_for_date(self, date):
        """Check if scholarship is valid for a specific date."""
        return self.valid_from <= date <= self.valid_until and self.is_active


class FeeInstallmentPlan(models.Model):
    """
    Installment plans for fee payment.
    """
    name = models.CharField(max_length=100)
    school_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='installment_plans'
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='installment_plans'
    )
    number_of_installments = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['name', 'school_class', 'academic_year']
        ordering = ['school_class', 'name']
        verbose_name = 'Fee Installment Plan'
        verbose_name_plural = 'Fee Installment Plans'
    
    def __str__(self):
        return f"{self.name} - {self.school_class.class_name}"


class FeeInstallment(models.Model):
    """
    Individual installments within a plan.
    """
    plan = models.ForeignKey(
        FeeInstallmentPlan,
        on_delete=models.CASCADE,
        related_name='installments'
    )
    installment_number = models.PositiveIntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    due_day = models.PositiveIntegerField(help_text="Day of month when due")
    due_month_offset = models.IntegerField(default=0, help_text="Months from start of academic year")
    description = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['plan', 'installment_number']
        unique_together = ['plan', 'installment_number']
        verbose_name = 'Fee Installment'
        verbose_name_plural = 'Fee Installments'
    
    def __str__(self):
        return f"{self.plan.name} - Installment {self.installment_number}"


class StudentInstallmentAssignment(models.Model):
    """
    Assigns installment plans to students.
    """
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='installment_assignments',
        limit_choices_to={'is_student': True}
    )
    installment_plan = models.ForeignKey(
        FeeInstallmentPlan,
        on_delete=models.CASCADE,
        related_name='student_assignments'
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='installment_assignments'
    )
    assigned_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['student', 'academic_year']
        verbose_name = 'Student Installment Assignment'
        verbose_name_plural = 'Student Installment Assignments'
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.installment_plan.name}"


class FeeRefund(models.Model):
    """
    Refunds issued to students.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('processed', 'Processed'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='refunds',
        limit_choices_to={'is_student': True}
    )
    refund_number = models.CharField(max_length=20, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    
    # Link to original payment
    original_payment = models.ForeignKey(
        StudentPayment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='refunds'
    )
    
    # Refund method
    refund_method = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
    ])
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Approval
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='refunds_approved',
        limit_choices_to={'is_principal': True}
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Processing
    processed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='refunds_processed',
        limit_choices_to={'is_accountant': True}
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Fee Refund'
        verbose_name_plural = 'Fee Refunds'
    
    def __str__(self):
        return f"{self.refund_number} - {self.student.get_full_name()} - {self.amount}"
    
    def generate_refund_number(self):
        """Generate unique refund number."""
        year = timezone.now().year
        prefix = f"{year}R"
        
        last_refund = FeeRefund.objects.filter(
            refund_number__startswith=prefix
        ).order_by('-refund_number').first()
        
        if last_refund:
            try:
                last_num = int(last_refund.refund_number.replace(prefix, ''))
                new_num = last_num + 1
            except ValueError:
                new_num = 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:04d}"
    
    def save(self, *args, **kwargs):
        if not self.refund_number:
            self.refund_number = self.generate_refund_number()
        super().save(*args, **kwargs)


class FinancialTransactionLog(models.Model):
    """
    Audit log for all financial transactions.
    """
    TRANSACTION_TYPES = [
        ('bill_created', 'Bill Created'),
        ('bill_updated', 'Bill Updated'),
        ('bill_cancelled', 'Bill Cancelled'),
        ('payment_received', 'Payment Received'),
        ('payment_allocated', 'Payment Allocated'),
        ('payment_refunded', 'Payment Refunded'),
        ('scholarship_applied', 'Scholarship Applied'),
        ('refund_processed', 'Refund Processed'),
    ]
    
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='financial_logs',
        limit_choices_to={'is_student': True}
    )
    
    # Related objects
    bill = models.ForeignKey(
        StudentBill,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='transaction_logs'
    )
    payment = models.ForeignKey(
        StudentPayment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='transaction_logs'
    )
    
    # Transaction details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    
    # Metadata
    performed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='financial_transactions'
    )
    performed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-performed_at']
        verbose_name = 'Financial Transaction Log'
        verbose_name_plural = 'Financial Transaction Logs'
    
    def __str__(self):
        return f"{self.transaction_type} - {self.student.get_full_name()} - {self.amount}"
