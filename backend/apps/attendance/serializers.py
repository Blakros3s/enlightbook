"""
Attendance Management Serializers for EnlightBook.
"""
from rest_framework import serializers
from django.db import transaction
from datetime import timedelta

from .models import (
    AttendancePeriod, DailyAttendance, PeriodAttendance,
    LeaveApplication, AttendanceSummary, AttendancePolicy,
    AttendanceNotification, HolidayCalendar
)


class AttendancePeriodSerializer(serializers.ModelSerializer):
    """Serializer for attendance periods."""
    
    class Meta:
        model = AttendancePeriod
        fields = ['id', 'name', 'start_time', 'end_time', 'order', 'is_active']


class DailyAttendanceListSerializer(serializers.ModelSerializer):
    """List serializer for daily attendance."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_roll_number = serializers.CharField(source='student.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = DailyAttendance
        fields = [
            'id', 'student', 'student_name', 'student_roll_number',
            'date', 'status', 'status_display', 'check_in_time', 'check_out_time',
            'created_at'
        ]


class DailyAttendanceDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for daily attendance."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_present = serializers.BooleanField(read_only=True)
    is_absent = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = DailyAttendance
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class DailyAttendanceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating daily attendance."""
    
    class Meta:
        model = DailyAttendance
        fields = ['student', 'date', 'status', 'check_in_time', 'check_out_time', 'remarks']
    
    def validate(self, data):
        # Check if attendance already exists for this student and date
        existing = DailyAttendance.objects.filter(
            student=data['student'],
            date=data['date']
        ).first()
        
        if existing and self.instance is None:
            raise serializers.ValidationError(
                "Attendance already recorded for this student on this date. Use update instead."
            )
        
        return data


class BulkAttendanceSerializer(serializers.Serializer):
    """Serializer for bulk attendance entry."""
    school_class_id = serializers.IntegerField()
    section_id = serializers.IntegerField(required=False, allow_null=True)
    date = serializers.DateField()
    attendance_data = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate(self, data):
        # Validate class exists
        from apps.academic.models import Class
        try:
            Class.objects.get(id=data['school_class_id'])
        except Class.DoesNotExist:
            raise serializers.ValidationError("Class not found.")
        
        # Validate section if provided
        if data.get('section_id'):
            from apps.academic.models import Section
            try:
                section = Section.objects.get(id=data['section_id'])
                if section.school_class_id != data['school_class_id']:
                    raise serializers.ValidationError("Section does not belong to the specified class.")
            except Section.DoesNotExist:
                raise serializers.ValidationError("Section not found.")
        
        return data


class PeriodAttendanceSerializer(serializers.ModelSerializer):
    """Serializer for period attendance."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    period_name = serializers.CharField(source='period.name', read_only=True)
    subject_name = serializers.CharField(source='subject.subject_name', read_only=True)
    class_name = serializers.CharField(source='school_class.class_name', read_only=True)
    section_name = serializers.CharField(source='section.section_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)
    
    class Meta:
        model = PeriodAttendance
        fields = [
            'id', 'student', 'student_name', 'date', 'period', 'period_name',
            'subject', 'subject_name', 'school_class', 'class_name',
            'section', 'section_name', 'status', 'status_display',
            'recorded_by', 'recorded_by_name', 'recorded_at'
        ]
        read_only_fields = ['recorded_at']


class PeriodAttendanceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating period attendance."""
    
    class Meta:
        model = PeriodAttendance
        fields = ['student', 'date', 'period', 'subject', 'school_class', 'section', 'status']


class LeaveApplicationListSerializer(serializers.ModelSerializer):
    """List serializer for leave applications."""
    applicant_name = serializers.CharField(source='applicant.get_full_name', read_only=True)
    leave_type_display = serializers.CharField(source='get_leave_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = LeaveApplication
        fields = [
            'id', 'applicant', 'applicant_name', 'leave_type', 'leave_type_display',
            'start_date', 'end_date', 'days', 'status', 'status_display',
            'created_at'
        ]


class LeaveApplicationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for leave applications."""
    applicant_name = serializers.CharField(source='applicant.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    leave_type_display = serializers.CharField(source='get_leave_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = LeaveApplication
        fields = '__all__'
        read_only_fields = ['days', 'approved_at', 'created_at', 'updated_at']


class LeaveApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating leave applications."""
    
    class Meta:
        model = LeaveApplication
        fields = ['leave_type', 'start_date', 'end_date', 'reason', 'supporting_documents']
    
    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date must be after start date.")
        return data


class AttendanceSummarySerializer(serializers.ModelSerializer):
    """Serializer for attendance summaries."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    month_display = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceSummary
        fields = [
            'id', 'student', 'student_name', 'month', 'month_display',
            'total_working_days', 'present_days', 'absent_days', 'late_days',
            'excused_days', 'half_day_days', 'attendance_percentage',
            'last_calculated'
        ]
        read_only_fields = ['last_calculated']
    
    def get_month_display(self, obj):
        return obj.month.strftime('%B %Y')


class AttendancePolicySerializer(serializers.ModelSerializer):
    """Serializer for attendance policies."""
    school_class_name = serializers.CharField(source='school_class.class_name', read_only=True)
    
    class Meta:
        model = AttendancePolicy
        fields = [
            'id', 'school_class', 'school_class_name', 'minimum_percentage',
            'grace_days', 'consecutive_absence_alert', 'is_active'
        ]


class AttendanceNotificationSerializer(serializers.ModelSerializer):
    """Serializer for attendance notifications."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    
    class Meta:
        model = AttendanceNotification
        fields = [
            'id', 'student', 'student_name', 'notification_type', 'notification_type_display',
            'message', 'sent_to_student', 'sent_to_parent', 'sent_to_teacher',
            'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['created_at', 'read_at']


class HolidayCalendarSerializer(serializers.ModelSerializer):
    """Serializer for holiday calendar."""
    holiday_type_display = serializers.CharField(source='get_holiday_type_display', read_only=True)
    
    class Meta:
        model = HolidayCalendar
        fields = [
            'id', 'name', 'date', 'holiday_type', 'holiday_type_display',
            'is_multi_day', 'end_date', 'description', 'is_active'
        ]


class AttendanceStatisticsSerializer(serializers.Serializer):
    """Serializer for attendance statistics."""
    school_class_id = serializers.IntegerField(required=False, allow_null=True)
    section_id = serializers.IntegerField(required=False, allow_null=True)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    
    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date must be before end date.")
        return data


class StudentAttendanceDetailSerializer(serializers.Serializer):
    """Serializer for detailed student attendance."""
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    class_name = serializers.CharField()
    section_name = serializers.CharField()
    
    # Monthly breakdown
    monthly_data = serializers.ListField(child=serializers.DictField())
    
    # Overall statistics
    total_working_days = serializers.IntegerField()
    present_days = serializers.IntegerField()
    absent_days = serializers.IntegerField()
    late_days = serializers.IntegerField()
    excused_days = serializers.IntegerField()
    attendance_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Compliance
    is_compliant = serializers.BooleanField()
    required_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)


class DefaulterListSerializer(serializers.Serializer):
    """Serializer for defaulter (low attendance) list."""
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    class_name = serializers.CharField()
    section_name = serializers.CharField()
    attendance_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    absent_days = serializers.IntegerField()
    consecutive_absences = serializers.IntegerField()
    parent_contact = serializers.CharField(required=False)


class AttendanceTrendSerializer(serializers.Serializer):
    """Serializer for attendance trends."""
    date = serializers.DateField()
    total_students = serializers.IntegerField()
    present_count = serializers.IntegerField()
    absent_count = serializers.IntegerField()
    late_count = serializers.IntegerField()
    attendance_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)