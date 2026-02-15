"""
Attendance Management URLs for EnlightBook.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AttendancePeriodViewSet, DailyAttendanceViewSet,
    PeriodAttendanceViewSet, LeaveApplicationViewSet,
    AttendanceSummaryViewSet, AttendancePolicyViewSet,
    AttendanceNotificationViewSet, HolidayCalendarViewSet,
    AttendanceReportViewSet
)

app_name = 'attendance'

router = DefaultRouter()
router.register(r'periods', AttendancePeriodViewSet)
router.register(r'daily', DailyAttendanceViewSet)
router.register(r'period-wise', PeriodAttendanceViewSet)
router.register(r'leaves', LeaveApplicationViewSet)
router.register(r'summaries', AttendanceSummaryViewSet)
router.register(r'policies', AttendancePolicyViewSet)
router.register(r'notifications', AttendanceNotificationViewSet)
router.register(r'holidays', HolidayCalendarViewSet)
router.register(r'reports', AttendanceReportViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
]