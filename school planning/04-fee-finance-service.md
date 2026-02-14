# Fee Management & Finance Service

## Service Overview
Comprehensive financial management system handling billing, payments, scholarships, refunds, and financial reporting.

## Core Capabilities
- Fee category and structure management
- Bill generation with auto-numbering
- Payment recording and allocations
- Scholarship and discount management
- Refund processing
- Transaction history and audit trail
- Financial reporting and analytics
- Payment method tracking

## Database Models (Optimized)

### 1. Fee Structure
```python
class FeeCategoryName(models.Model):
    """Types of fees: Tuition, Lab Fee, Sports Fee, etc."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

class FeeCategory(models.Model):
    """Class-specific fee amounts"""
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)
    fee_category_name = models.ForeignKey(FeeCategoryName, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    is_mandatory = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('class_assigned', 'fee_category_name', 'academic_year')
```

### 2. Billing System
```python
class StudentBill(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    
    # Billing period
    billing_month = models.DateField()  # First day of month
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    
    # Bill identification
    bill_number = models.CharField(max_length=20, unique=True)  # Auto: 2024B001
    bill_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('partially_paid', 'Partially Paid'),
        ('fully_paid', 'Fully Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled')
    ], default='draft')
    
    # Metadata
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def amount_paid(self):
        allocations = self.allocations.aggregate(total=Sum('amount_applied'))
        return allocations['total'] or Decimal(0)
    
    @property
    def outstanding_amount(self):
        return self.total_amount - self.amount_paid
    
    @property
    def is_fully_paid(self):
        return self.outstanding_amount <= Decimal(0)
    
    @property
    def is_overdue(self):
        if self.status != 'fully_paid':
            return timezone.now().date() > self.due_date
        return False
```

### 3. Payment System
```python
class PaymentMethod(models.Model):
    name = models.CharField(max_length=50, unique=True)
    requires_reference = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

class StudentPayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    payment_number = models.CharField(max_length=20, unique=True)  # Auto: 2024P001
    payment_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment method
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    reference_number = models.CharField(max_length=100, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    
    # Verification
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    verified_at = models.DateTimeField(null=True)
    
    # Metadata
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='payments_created')
    created_at = models.DateTimeField(auto_now_add=True)

class PaymentAllocation(models.Model):
    """Link payments to specific bills"""
    payment = models.ForeignKey(StudentPayment, on_delete=models.CASCADE, related_name='allocations')
    bill = models.ForeignKey(StudentBill, on_delete=models.CASCADE, related_name='allocations')
    amount_applied = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('payment', 'bill')
```

### 4. Scholarship & Discounts
```python
class Scholarship(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scholarships')
    scholarship_name = models.CharField(max_length=100)
    scholarship_type = models.CharField(max_length=100)  # Merit, Need-based, Sports
    
    # Discount configuration
    discount_type = models.CharField(max_length=20, choices=[
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('full_waiver', 'Full Waiver')
    ])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Applicability
    applicable_to_all_fees = models.BooleanField(default=True)
    applicable_fee_categories = models.ManyToManyField(FeeCategoryName, blank=True)
    
    # Validity
    valid_from = models.DateField()
    valid_until = models.DateField()
    
    # Approval
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    approved_at = models.DateTimeField(null=True)
```

### 5. Installment Plans
```python
class FeeInstallmentPlan(models.Model):
    name = models.CharField(max_length=100)
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)
    number_of_installments = models.IntegerField()
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

class FeeInstallment(models.Model):
    plan = models.ForeignKey(FeeInstallmentPlan, on_delete=models.CASCADE, related_name='installments')
    installment_number = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    due_day_of_month = models.IntegerField()

class StudentInstallmentPlan(models.Model):
    """Assign installment plan to student"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    installment_plan = models.ForeignKey(FeeInstallmentPlan, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    assigned_on = models.DateField(auto_now_add=True)
```

### 6. Refunds
```python
class FeeRefund(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    refund_number = models.CharField(max_length=20, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    
    original_payment = models.ForeignKey(StudentPayment, on_delete=models.SET_NULL, null=True)
    
    refund_method = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer')
    ])
    
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('processed', 'Processed'),
        ('rejected', 'Rejected'),
    ], default='pending')
    
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='refunds_processed')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True)
```

## API Endpoints

### Fee Structure Management
```
GET    /api/finance/fee-categories                  # List all fee categories
POST   /api/finance/fee-categories                  # Create fee category
GET    /api/finance/fee-categories/:id              # Get category details
PUT    /api/finance/fee-categories/:id              # Update category
GET    /api/finance/classes/:classId/fee-structure  # Get class fee structure
POST   /api/finance/classes/:classId/fee-structure  # Set class fee structure
```

### Billing
```
GET    /api/finance/bills                           # List all bills (with filters)
POST   /api/finance/bills                           # Create bill
GET    /api/finance/bills/:id                       # Get bill details
PUT    /api/finance/bills/:id                       # Update bill
DELETE /api/finance/bills/:id                       # Cancel bill
POST   /api/finance/bills/bulk-generate             # Generate bills for class/month
GET    /api/finance/students/:id/bills              # Get student's bills
```

### Payments
```
GET    /api/finance/payments                        # List all payments
POST   /api/finance/payments                        # Record payment
GET    /api/finance/payments/:id                    # Get payment details
POST   /api/finance/payments/:id/verify             # Verify payment
GET    /api/finance/students/:id/payments           # Get student's payments
POST   /api/finance/payments/:id/allocate           # Allocate payment to bills
```

### Scholarships
```
GET    /api/finance/scholarships                    # List all scholarships
POST   /api/finance/scholarships                    # Create scholarship
GET    /api/finance/scholarships/:id                # Get scholarship details
PUT    /api/finance/scholarships/:id                # Update scholarship
POST   /api/finance/scholarships/:id/approve        # Approve scholarship
GET    /api/finance/students/:id/scholarships       # Get student's scholarships
```

### Refunds
```
GET    /api/finance/refunds                         # List all refunds
POST   /api/finance/refunds                         # Initiate refund
GET    /api/finance/refunds/:id                     # Get refund details
POST   /api/finance/refunds/:id/approve             # Approve refund
POST   /api/finance/refunds/:id/process             # Process refund
```

### Reports
```
GET    /api/finance/reports/outstanding-dues        # Outstanding dues report
GET    /api/finance/reports/collection-summary      # Daily/monthly collection
GET    /api/finance/reports/category-wise           # Fee category wise collection
GET    /api/finance/reports/defaulters              # List of defaulters
GET    /api/finance/reports/scholarship-impact      # Scholarship impact analysis
```

## Business Logic & Workflows

### 1. Bill Generation Workflow
```python
def generate_monthly_bills(class_id, month, academic_year):
    """
    Auto-generate bills for all students in a class
    """
    # 1. Get all active students in class
    students = Student.objects.filter(
        class_code_id=class_id,
        is_active=True
    )
    
    # 2. Get fee structure for the class
    fee_categories = FeeCategory.objects.filter(
        class_assigned_id=class_id,
        academic_year=academic_year
    )
    
    # 3. For each student
    for student in students:
        # Get student's scholarship
        scholarship = student.scholarships.filter(
            valid_from__lte=month,
            valid_until__gte=month
        ).first()
        
        # Calculate subtotal
        subtotal = sum(fc.amount for fc in fee_categories)
        
        # Apply scholarship discount
        discount = 0
        if scholarship:
            discount = scholarship.calculate_discount(subtotal)
        
        # Create bill
        bill = StudentBill.objects.create(
            student=student,
            billing_month=month,
            academic_year=academic_year,
            bill_number=generate_bill_number(),
            due_date=calculate_due_date(month),
            subtotal=subtotal,
            discount=discount,
            total_amount=subtotal - discount,
            status='issued'
        )
        
        # Link fee categories
        for fc in fee_categories:
            StudentBillFeeCategory.objects.create(
                student_bill=bill,
                fee_category=fc
            )
```

### 2. Payment Allocation Logic
```python
def allocate_payment(payment_id, allocation_data):
    """
    Allocate a payment to one or more bills
    
    allocation_data = [
        {'bill_id': 1, 'amount': 500},
        {'bill_id': 2, 'amount': 300}
    ]
    """
    payment = StudentPayment.objects.get(id=payment_id)
    total_allocated = sum(item['amount'] for item in allocation_data)
    
    # Validate
    if total_allocated > payment.amount_paid:
        raise ValidationError("Cannot allocate more than payment amount")
    
    # Create allocations
    for item in allocation_data:
        PaymentAllocation.objects.create(
            payment=payment,
            bill_id=item['bill_id'],
            amount_applied=item['amount']
        )
    
    # Update bill statuses
    for item in allocation_data:
        bill = StudentBill.objects.get(id=item['bill_id'])
        update_bill_status(bill)
```

### 3. Due Date & Late Fee Calculation
```python
class BillDueDate(models.Model):
    bill = models.ForeignKey(StudentBill, on_delete=models.CASCADE)
    due_date = models.DateField()
    late_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=2)
    
    @property
    def late_fee_amount(self):
        if self.is_overdue:
            days_late = (timezone.now().date() - self.due_date).days
            return (self.bill.outstanding_amount * self.late_fee_percentage / 100) * days_late
        return Decimal(0)
```

## Frontend Features (Next.js)

### 1. Billing Dashboard
```typescript
// app/finance/bills/page.tsx
Features:
- List all bills with filters (class, month, status)
- Bulk bill generation
- Quick search by student name/ID
- Export to Excel/PDF
- Outstanding dues summary
```

### 2. Payment Recording Interface
```typescript
// app/finance/payments/page.tsx
Features:
- Payment form with student lookup
- Show student's outstanding bills
- Auto-allocate to oldest bill first
- Support partial payments
- Generate receipt (PDF)
```

### 3. Student Ledger
```typescript
// app/finance/students/:id/ledger
Features:
- Complete transaction history
- Bills, payments, refunds timeline
- Current balance display
- Download statement
- Payment history graph
```

### 4. Financial Reports
```typescript
// app/finance/reports/page.tsx
Reports:
- Daily collection summary
- Outstanding dues by class
- Defaulters list (overdue > 30 days)
- Fee category wise collection
- Scholarship utilization
- Month-over-month comparison
```

### 5. Scholarship Management
```typescript
// app/finance/scholarships/page.tsx
Features:
- Create scholarship records
- Assign to students
- Set validity periods
- Approve/reject workflow
- Impact analysis dashboard
```

## Receipt Generation

### Payment Receipt
```python
from weasyprint import HTML

def generate_receipt_pdf(payment_id):
    payment = StudentPayment.objects.get(id=payment_id)
    
    context = {
        'payment': payment,
        'student': payment.student,
        'school': SchoolDetail.objects.first(),
        'allocations': payment.allocations.all()
    }
    
    html = render_to_string('receipts/payment_receipt.html', context)
    pdf = HTML(string=html).write_pdf()
    
    filename = f"receipt_{payment.payment_number}.pdf"
    # Save to S3 or local storage
    return pdf
```

## Notification Triggers

### Email/SMS Notifications
```python
# Bill generated
→ Email bill to parent with payment link

# Payment received
→ SMS confirmation + email receipt

# Bill overdue
→ Reminder email 3 days before due date
→ Reminder SMS on due date
→ Overdue notice 7 days after due date

# Low balance
→ Alert when account balance < 0
```

## Financial Analytics

### Key Metrics
```python
# Dashboard KPIs
- Total collection (today, this month, this year)
- Outstanding dues
- Collection rate (%)
- Average days to payment
- Scholarship impact on revenue
```

### Reports
1. **Collection Summary**: Total collected by payment method
2. **Outstanding Dues**: Amount owed by class/section
3. **Defaulters List**: Students with overdue payments
4. **Category Analysis**: Collection per fee category
5. **Trend Analysis**: Month-over-month growth

## Security & Compliance

### Audit Trail
```python
class FinancialAuditLog(models.Model):
    action = models.CharField(max_length=50)  # bill_created, payment_recorded, etc.
    performed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    entity_type = models.CharField(max_length=50)  # Bill, Payment, Refund
    entity_id = models.IntegerField()
    old_values = models.JSONField(null=True)
    new_values = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
```

### Permissions
- **Accountant**: Full access to billing and payments
- **Principal**: View-only access + approve large refunds
- **Teacher**: View assigned students' fee status
- **Parent/Student**: View own fee details only

## Integration with Other Services

### With Academic Service
- Calculate fees based on enrolled subjects
- Optional subject fees
- Lab/practical fees for science subjects

### With Attendance Service
- Fee clearance required for exam eligibility
- Attendance-based scholarships

### With Student Service
- Fee status affects student enrollment
- Transfer certificate requires fee clearance

## Implementation Priority

### Week 1-2: Core Billing
- Fee category management
- Bill generation
- Payment recording
- Basic reports

### Week 3-4: Advanced Features
- Payment allocation
- Scholarships
- Installment plans
- Receipt generation

### Week 5-6: Analytics & Optimization
- Financial dashboards
- Advanced reporting
- Notification system
- Refund workflow

## Technology Stack

### Backend
- Django models with transaction atomicity
- Celery for async bill generation
- Redis for caching financial summaries
- PostgreSQL for transaction integrity

### Frontend
- Next.js server components for reports
- TanStack Table for data grids
- Recharts for financial graphs
- React-PDF for receipt previews

### Third-party
- Stripe/Razorpay for online payments
- AWS SES for email receipts
- Twilio for SMS notifications
