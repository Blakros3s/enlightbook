from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    FeeCategoryNameViewSet, FeeStructureViewSet, StudentBillViewSet,
    PaymentMethodViewSet, StudentPaymentViewSet,
    ScholarshipViewSet, FeeInstallmentPlanViewSet,
    StudentInstallmentAssignmentViewSet, FeeRefundViewSet,
    FinancialTransactionLogViewSet, FinancialReportViewSet
)

app_name = 'finance'

router = DefaultRouter()
router.register(r'fee-categories', FeeCategoryNameViewSet)
router.register(r'fee-structures', FeeStructureViewSet)
router.register(r'bills', StudentBillViewSet)
router.register(r'payment-methods', PaymentMethodViewSet)
router.register(r'payments', StudentPaymentViewSet)
router.register(r'scholarships', ScholarshipViewSet)
router.register(r'installment-plans', FeeInstallmentPlanViewSet)
router.register(r'installment-assignments', StudentInstallmentAssignmentViewSet)
router.register(r'refunds', FeeRefundViewSet)
router.register(r'transaction-logs', FinancialTransactionLogViewSet)
router.register(r'reports', FinancialReportViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
]
