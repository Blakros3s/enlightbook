from django.contrib import admin
from .models import (
    FeeCategoryName, FeeStructure, StudentBill, BillItem, PaymentMethod,
    StudentPayment, PaymentAllocation, Scholarship, FeeInstallmentPlan,
    FeeInstallment, StudentInstallmentAssignment, FeeRefund,
    FinancialTransactionLog
)


class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 1


class FeeInstallmentInline(admin.TabularInline):
    model = FeeInstallment
    extra = 1


@admin.register(FeeCategoryName)
class FeeCategoryNameAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_mandatory', 'is_recurring', 'is_active']
    list_filter = ['is_mandatory', 'is_recurring', 'is_active']
    search_fields = ['name', 'description']


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['school_class', 'fee_category_name', 'amount', 'academic_year', 'is_active']
    list_filter = ['school_class', 'academic_year', 'is_active']
    search_fields = ['school_class__class_name', 'fee_category_name__name']


@admin.register(StudentBill)
class StudentBillAdmin(admin.ModelAdmin):
    list_display = ['bill_number', 'student', 'total_amount', 'outstanding_amount', 'status', 'due_date']
    list_filter = ['status', 'academic_year', 'billing_month']
    search_fields = ['bill_number', 'student__first_name', 'student__last_name']
    readonly_fields = ['bill_number', 'amount_paid', 'outstanding_amount', 'is_overdue', 'is_fully_paid']
    inlines = [BillItemInline]
    date_hierarchy = 'bill_date'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'requires_reference', 'is_active']
    list_filter = ['requires_reference', 'is_active']


@admin.register(StudentPayment)
class StudentPaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_number', 'student', 'amount_paid', 'payment_method', 'status', 'payment_date']
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = ['payment_number', 'student__first_name', 'student__last_name', 'reference_number']
    readonly_fields = ['payment_number', 'allocated_amount', 'unallocated_amount']
    date_hierarchy = 'payment_date'


@admin.register(PaymentAllocation)
class PaymentAllocationAdmin(admin.ModelAdmin):
    list_display = ['payment', 'bill', 'amount_applied', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at']


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ['scholarship_name', 'student', 'discount_type', 'discount_value', 'is_active']
    list_filter = ['discount_type', 'is_active', 'academic_year']
    search_fields = ['scholarship_name', 'student__first_name', 'student__last_name']
    filter_horizontal = ['applicable_fee_categories']


@admin.register(FeeInstallmentPlan)
class FeeInstallmentPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'school_class', 'number_of_installments', 'academic_year', 'is_active']
    list_filter = ['school_class', 'academic_year', 'is_active']
    inlines = [FeeInstallmentInline]


@admin.register(StudentInstallmentAssignment)
class StudentInstallmentAssignmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'installment_plan', 'academic_year', 'is_active']
    list_filter = ['academic_year', 'is_active']
    search_fields = ['student__first_name', 'student__last_name']


@admin.register(FeeRefund)
class FeeRefundAdmin(admin.ModelAdmin):
    list_display = ['refund_number', 'student', 'amount', 'status', 'created_at']
    list_filter = ['status', 'refund_method', 'created_at']
    search_fields = ['refund_number', 'student__first_name', 'student__last_name']
    readonly_fields = ['refund_number']


@admin.register(FinancialTransactionLog)
class FinancialTransactionLogAdmin(admin.ModelAdmin):
    list_display = ['transaction_type', 'student', 'amount', 'performed_by', 'performed_at']
    list_filter = ['transaction_type', 'performed_at']
    search_fields = ['student__first_name', 'student__last_name', 'description']
    readonly_fields = ['performed_at', 'ip_address']
    date_hierarchy = 'performed_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
