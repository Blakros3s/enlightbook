# Attendance Management Service

## Service Overview
Comprehensive attendance tracking system with daily and period-wise attendance, leave management, reporting, and parent notifications.

## Database Models

### 1. Core Attendance
```python
class AttendancePeriod(models.Model):
    """Define school periods/sessions"""
    name = models.CharField(max_length=50)  # "Period 1", "Morning Session"
    start_time = models.TimeField()
    end_time = models.TimeField()
    order = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']

class DailyAttendance(models.Model):
    """Daily attendance tracking"""
    ATTENDANCE_STATUS = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused/Leave'),
        ('half_day', 'Half Day'),
        ('early_departure', 'Early Departure'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS)
    recorded_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    
    # Check-in/out times
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    
    # Leave integration
    leave_application = models.ForeignKey('LeaveApplication', on_delete=models.SET_NULL, null=True)
    
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date']

class PeriodAttendance(models.Model):
    """Period-wise attendance"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    period = models.ForeignKey(AttendancePeriod, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ])
    
    recorded_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'date', 'period')
```

### 2. Leave Management
```python
class LeaveApplication(models.Model):
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    leave_date = models.DateField()
    days = models.IntegerField(default=1)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')
    
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='approved_leaves')
    approved_at = models.DateTimeField(null=True)
    
    auto_mark_attendance = models.BooleanField(default=True)
    
    def approve(self, approved_by):
        \"\"\"Approve leave and auto-mark attendance\"\"\"
        self.status = 'approved'
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.save()
        
        if self.auto_mark_attendance:
            student = Student.objects.get(user=self.applicant)
            current_date = self.leave_date
            
            for i in range(self.days):
                DailyAttendance.objects.update_or_create(
                    student=student,
                    date=current_date,
                    defaults={
                        'status': 'excused',
                        'leave_application': self,
                        'recorded_by': None
                    }
                )
                current_date += timedelta(days=1)
```

### 3. Attendance Summary
```python
class StudentAttendanceSummary(models.Model):
    \"\"\"Cached attendance statistics\"\"\"
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    month = models.DateField()  # First day of month
    
    total_days = models.IntegerField(default=0)
    present_days = models.IntegerField(default=0)
    absent_days = models.IntegerField(default=0)
    late_days = models.IntegerField(default=0)
    excused_days = models.IntegerField(default=0)
    
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    
    class Meta:
        unique_together = ('student', 'month')
    
    def calculate_percentage(self):
        if self.total_days > 0:
            self.attendance_percentage = (self.present_days / self.total_days) * 100
        else:
            self.attendance_percentage = 0
        return self.attendance_percentage
```

## API Endpoints

```
# Daily Attendance
GET    /api/attendance/daily                    # List daily attendance
POST   /api/attendance/daily                    # Mark attendance
POST   /api/attendance/daily/bulk               # Bulk mark attendance
GET    /api/attendance/students/:id/daily       # Get student's attendance

# Period Attendance
GET    /api/attendance/periods                  # List period attendance
POST   /api/attendance/periods                  # Mark period attendance
POST   /api/attendance/periods/bulk             # Bulk mark period attendance

# Leave Applications
GET    /api/attendance/leaves                   # List leave applications
POST   /api/attendance/leaves                   # Apply for leave
GET    /api/attendance/leaves/:id               # Get leave details
POST   /api/attendance/leaves/:id/approve       # Approve leave
POST   /api/attendance/leaves/:id/reject        # Reject leave

# Reports
GET    /api/attendance/reports/summary          # Attendance summary
GET    /api/attendance/reports/defaulters       # Low attendance students
GET    /api/attendance/reports/class-wise       # Class-wise attendance
GET    /api/attendance/students/:id/percentage  # Student's attendance %
```

## Business Rules

### 1. Attendance Policies
```python
class AttendancePolicy(models.Model):
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)
    minimum_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=75.00)
    grace_days = models.IntegerField(default=5)
    consecutive_absence_alert = models.IntegerField(default=3)
    
    def check_compliance(self, student):
        summary = StudentAttendanceSummary.objects.filter(
            student=student
        ).latest('month')
        return summary.attendance_percentage >= self.minimum_percentage
```

### 2. Bulk Attendance Entry
```python
def mark_bulk_attendance(class_id, section_id, date, marked_by, exceptions=None):
    \"\"\"Mark all students present, then apply exceptions\"\"\"
    students = Student.objects.filter(
        class_code_id=class_id,
        class_code_section_id=section_id,
        is_active=True
    )
    
    attendance_records = []
    for student in students:
        status = exceptions.get(student.id, 'present') if exceptions else 'present'
        attendance_records.append(
            DailyAttendance(
                student=student,
                date=date,
                status=status,
                recorded_by=marked_by
            )
        )
    
    DailyAttendance.objects.bulk_create(
        attendance_records,
        update_conflicts=True,
        unique_fields=['student', 'date'],
        update_fields=['status', 'recorded_by']
    )
```

## Frontend Features

### 1. Attendance Marking Interface
- Grid view of all students
- One-click "Mark All Present"
- Quick status toggles
- Section filtering
- Date selector

### 2. Attendance Dashboard
- Monthly attendance calendar
- Percentage indicators
- Low attendance alerts
- Trend graphs

### 3. Leave Management Portal
- Application submission form
- Approval workflow
- Leave balance tracking
- History view

## Implementation Priority

**Week 9**: Daily attendance models and APIs
**Week 10**: Bulk entry and period attendance
**Week 11**: Leave management integration
**Week 12**: Reports and notifications
