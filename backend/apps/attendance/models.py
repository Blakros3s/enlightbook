"""
Attendance Management Models for EnlightBook.
Tracks daily and period-wise attendance with leave management.
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from apps.users.models import CustomUser
from apps.academic.models import Class, Section, Subject


class AttendancePeriod(models.Model):
    """
    Defines school periods/sessions for period-wise attendance.
    """
    name = models.CharField(max_length=50, help_text="e.g., Period 1, Morning Session")
    start_time = models.TimeField()
    end_time = models.TimeField()
    order = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Attendance Period'
        verbose_name_plural = 'Attendance Periods'
    
    def __str__(self):
        return f"{self.name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"
    
    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")


class DailyAttendance(models.Model):
    """
    Daily attendance tracking for students.
    """
    ATTENDANCE_STATUS = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused/Leave'),
        ('half_day', 'Half Day'),
        ('early_departure', 'Early Departure'),
    ]
    
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='daily_attendance',
        limit_choices_to={'is_student': True}
    )
    date = models.DateField()
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS)
    
    # Who recorded the attendance
    recorded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_recorded',
        limit_choices_to={'is_teacher': True}
    )
    
    # Check-in/out times
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    
    # Leave integration
    leave_application = models.ForeignKey(
        'LeaveApplication',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_records'
    )
    
    # Remarks
    remarks = models.TextField(blank=True, help_text="Any additional notes")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date', 'student']
        verbose_name = 'Daily Attendance'
        verbose_name_plural = 'Daily Attendance Records'
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.date} - {self.get_status_display()}"
    
    def clean(self):
        # Validate check-out is after check-in
        if self.check_in_time and self.check_out_time:
            if self.check_out_time <= self.check_in_time:
                raise ValidationError("Check-out time must be after check-in time.")
    
    @property
    def is_present(self):
        """Check if student is considered present."""
        return self.status in ['present', 'late', 'excused']
    
    @property
    def is_absent(self):
        """Check if student is considered absent."""
        return self.status in ['absent']


class PeriodAttendance(models.Model):
    """
    Period-wise attendance tracking.
    """
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]
    
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='period_attendance',
        limit_choices_to={'is_student': True}
    )
    date = models.DateField()
    period = models.ForeignKey(
        AttendancePeriod,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='period_attendance'
    )
    school_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='period_attendance'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='period_attendance'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Who recorded
    recorded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='period_attendance_recorded',
        limit_choices_to={'is_teacher': True}
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'date', 'period']
        ordering = ['-date', 'period__order', 'student']
        verbose_name = 'Period Attendance'
        verbose_name_plural = 'Period Attendance Records'
        indexes = [
            models.Index(fields=['student', 'date', 'period']),
            models.Index(fields=['school_class', 'section', 'date']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.date} - {self.period} - {self.get_status_display()}"
    
    def clean(self):
        # Validate section belongs to class
        if self.section.school_class != self.school_class:
            raise ValidationError("Section must belong to the selected class.")


class LeaveApplication(models.Model):
    """
    Leave applications for students and staff.
    """
    LEAVE_TYPES = [
        ('sick', 'Sick Leave'),
        ('personal', 'Personal Leave'),
        ('family', 'Family Emergency'),
        ('medical', 'Medical Appointment'),
        ('sports', 'Sports Event'),
        ('academic', 'Academic Event'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    applicant = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='leave_applications'
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    
    # Date range
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.IntegerField(default=1)
    
    # Reason
    reason = models.TextField()
    supporting_documents = models.FileField(
        upload_to='leave_documents/',
        blank=True,
        null=True
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Approval
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leave_approved',
        limit_choices_to={'is_principal': True}
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_remarks = models.TextField(blank=True)
    
    # Auto-mark attendance on approval
    auto_mark_attendance = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Leave Application'
        verbose_name_plural = 'Leave Applications'
    
    def __str__(self):
        return f"{self.applicant.get_full_name()} - {self.leave_type} ({self.start_date} to {self.end_date})"
    
    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError("End date must be after start date.")
            
            # Calculate days
            self.days = (self.end_date - self.start_date).days + 1
    
    def approve(self, approved_by, remarks=''):
        """Approve leave and auto-mark attendance."""
        from django.utils import timezone
        
        self.status = 'approved'
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.approval_remarks = remarks
        self.save()
        
        if self.auto_mark_attendance:
            self._mark_attendance_excused()
    
    def _mark_attendance_excused(self):
        """Mark attendance as excused for leave period."""
        current_date = self.start_date
        
        while current_date <= self.end_date:
            # Check if applicant is a student
            if self.applicant.is_student:
                DailyAttendance.objects.update_or_create(
                    student=self.applicant,
                    date=current_date,
                    defaults={
                        'status': 'excused',
                        'leave_application': self,
                        'recorded_by': None,
                        'remarks': f'Leave: {self.reason}'
                    }
                )
            
            current_date += timedelta(days=1)
    
    def reject(self, rejected_by, remarks=''):
        """Reject leave application."""
        self.status = 'rejected'
        self.approved_by = rejected_by
        self.approval_remarks = remarks
        self.save()


class AttendanceSummary(models.Model):
    """
    Cached attendance statistics for performance.
    """
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='attendance_summaries',
        limit_choices_to={'is_student': True}
    )
    month = models.DateField(help_text="First day of month")
    
    # Working days
    total_working_days = models.IntegerField(default=0)
    
    # Attendance counts
    present_days = models.IntegerField(default=0)
    absent_days = models.IntegerField(default=0)
    late_days = models.IntegerField(default=0)
    excused_days = models.IntegerField(default=0)
    half_day_days = models.IntegerField(default=0)
    
    # Calculated
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Metadata
    last_calculated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'month']
        ordering = ['-month', 'student']
        verbose_name = 'Attendance Summary'
        verbose_name_plural = 'Attendance Summaries'
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.month.strftime('%B %Y')}"
    
    def calculate_percentage(self):
        """Calculate attendance percentage."""
        if self.total_working_days > 0:
            present_count = self.present_days + self.excused_days
            self.attendance_percentage = (present_count / self.total_working_days) * 100
        else:
            self.attendance_percentage = 0
        return self.attendance_percentage
    
    def recalculate(self):
        """Recalculate summary from attendance records."""
        from django.db.models import Count, Q
        
        start_date = self.month
        end_date = (self.month.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        attendance_counts = DailyAttendance.objects.filter(
            student=self.student,
            date__range=[start_date, end_date]
        ).values('status').annotate(count=Count('id'))
        
        # Reset counts
        self.present_days = 0
        self.absent_days = 0
        self.late_days = 0
        self.excused_days = 0
        self.half_day_days = 0
        
        # Update from query
        for item in attendance_counts:
            status = item['status']
            count = item['count']
            
            if status == 'present':
                self.present_days = count
            elif status == 'absent':
                self.absent_days = count
            elif status == 'late':
                self.late_days = count
            elif status == 'excused':
                self.excused_days = count
            elif status == 'half_day':
                self.half_day_days = count
        
        self.calculate_percentage()
        self.save()


class AttendancePolicy(models.Model):
    """
    Attendance policies for classes.
    """
    school_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='attendance_policies',
        unique=True
    )
    
    minimum_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=75.00,
        help_text="Minimum attendance percentage required"
    )
    
    grace_days = models.IntegerField(
        default=5,
        help_text="Additional grace days allowed"
    )
    
    consecutive_absence_alert = models.IntegerField(
        default=3,
        help_text="Alert after this many consecutive absences"
    )
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Attendance Policy'
        verbose_name_plural = 'Attendance Policies'
    
    def __str__(self):
        return f"{self.school_class.class_name} - Min {self.minimum_percentage}%"
    
    def check_compliance(self, student):
        """Check if student meets attendance requirements."""
        latest_summary = AttendanceSummary.objects.filter(
            student=student
        ).order_by('-month').first()
        
        if not latest_summary:
            return True  # No data yet
        
        return latest_summary.attendance_percentage >= self.minimum_percentage
    
    def get_required_attendance(self, total_days):
        """Calculate required attendance days."""
        required = (total_days * self.minimum_percentage) / 100
        return required - self.grace_days


class AttendanceNotification(models.Model):
    """
    Notifications for attendance events.
    """
    NOTIFICATION_TYPES = [
        ('absence', 'Absence Alert'),
        ('low_attendance', 'Low Attendance Warning'),
        ('consecutive_absence', 'Consecutive Absence Alert'),
        ('late_arrival', 'Late Arrival'),
        ('leave_approved', 'Leave Approved'),
    ]
    
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='attendance_notifications',
        limit_choices_to={'is_student': True}
    )
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    
    # Recipients
    sent_to_student = models.BooleanField(default=False)
    sent_to_parent = models.BooleanField(default=False)
    sent_to_teacher = models.BooleanField(default=False)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Attendance Notification'
        verbose_name_plural = 'Attendance Notifications'
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.get_notification_type_display()}"
    
    def mark_read(self):
        """Mark notification as read."""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save()


class HolidayCalendar(models.Model):
    """
    School holidays and events.
    """
    HOLIDAY_TYPES = [
        ('national', 'National Holiday'),
        ('school', 'School Holiday'),
        ('exam', 'Examination'),
        ('event', 'School Event'),
        ('vacation', 'Vacation'),
    ]
    
    name = models.CharField(max_length=200)
    date = models.DateField()
    holiday_type = models.CharField(max_length=20, choices=HOLIDAY_TYPES)
    
    # For multi-day holidays
    is_multi_day = models.BooleanField(default=False)
    end_date = models.DateField(null=True, blank=True)
    
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Holiday Calendar'
        verbose_name_plural = 'Holiday Calendar'
    
    def __str__(self):
        return f"{self.name} - {self.date}"
    
    def clean(self):
        if self.is_multi_day and self.end_date:
            if self.end_date < self.date:
                raise ValidationError("End date must be after start date.")
        elif self.is_multi_day and not self.end_date:
            raise ValidationError("End date is required for multi-day holidays.")