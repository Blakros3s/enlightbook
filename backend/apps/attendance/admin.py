"""
Attendance Management Admin for EnlightBook.
"""
from django.contrib import admin
from .models import (
    AttendancePeriod, DailyAttendance, PeriodAttendance,
    LeaveApplication, AttendanceSummary, AttendancePolicy,
    AttendanceNotification, HolidayCalendar
)


@admin.register(AttendancePeriod)
class AttendancePeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'order', 'is_active']
    list_filter = ['is_active']
    ordering = ['order']


@admin.register(DailyAttendance)
class DailyAttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'check_in_time', 'check_out_time']
    list_filter = ['status', 'date']
    search_fields = ['student__first_name', 'student__last_name']
    date_hierarchy = 'date'


@admin.register(PeriodAttendance)
class PeriodAttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'period', 'subject', 'school_class', 'status']
    list_filter = ['status', 'date', 'school_class']
    search_fields = ['student__first_name', 'student__last_name']


@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'leave_type', 'start_date', 'end_date', 'days', 'status']
    list_filter = ['leave_type', 'status', 'created_at']
    search_fields = ['applicant__first_name', 'applicant__last_name', 'reason']
    date_hierarchy = 'start_date'


@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ['student', 'month', 'attendance_percentage', 'present_days', 'absent_days']
    list_filter = ['month']
    search_fields = ['student__first_name', 'student__last_name']


@admin.register(AttendancePolicy)
class AttendancePolicyAdmin(admin.ModelAdmin):
    list_display = ['school_class', 'minimum_percentage', 'grace_days', 'is_active']
    list_filter = ['is_active']


@admin.register(AttendanceNotification)
class AttendanceNotificationAdmin(admin.ModelAdmin):
    list_display = ['student', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['student__first_name', 'student__last_name']


@admin.register(HolidayCalendar)
class HolidayCalendarAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'holiday_type', 'is_active']
    list_filter = ['holiday_type', 'is_active']
    date_hierarchy = 'date'