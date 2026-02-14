# Examination & Results Management Service

## Service Overview
Comprehensive examination management system handling exam creation, timetabling, mark entry, grading, result publication, and report card generation.

## Database Models

### 1. Grading System
```python
class GradingScale(models.Model):
    """Define grading rules for classes/boards"""
    name = models.CharField(max_length=100)  # "CBSE Scale", "IB Scale"
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)
    is_default = models.BooleanField(default=False)
    description = models.TextField(blank=True)

class GradeRange(models.Model):
    """Individual grade ranges in a scale"""
    grading_scale = models.ForeignKey(GradingScale, on_delete=models.CASCADE, related_name='ranges')
    grade = models.CharField(max_length=5)  # "A+", "A", "B+"
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=4, decimal_places=2)  # For GPA
    description = models.CharField(max_length=50)  # "Outstanding", "Excellent"
    
    class Meta:
        ordering = ['-min_percentage']
```

### 2. Exam Management
```python
class Exam(models.Model):
    """Major exams: mid-term, final, etc."""
    name = models.CharField(max_length=200)
    academic_year = models.ForeignKey(Academic Year, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    exam_type = models.CharField(max_length=50, choices=[
        ('mid_term', 'Mid-Term'),
        ('final', 'Final'),
        ('unit_test', 'Unit Test'),
        ('practical', 'Practical'),
    ])
    
    # Publication status
    is_timetable_published = models.BooleanField(default=False)
    timetable_published_date = models.DateTimeField(null=True)
    
    is_result_published = models.BooleanField(default=False)
    result_published_date = models.DateTimeField(null=True)
    
    allow_students_to_view_results = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ExamDetail(models.Model):
    """Specific exam details for each subject in each class"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='details')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True)
    
    # Marks distribution
    full_marks = models.DecimalField(max_digits=6, decimal_places=2)
    theory_full_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    practical_full_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    passing_marks = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Exam schedule
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.IntegerField()
    
    # Venue
    venue = models.CharField(max_length=100, blank=True)
    
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        unique_together = ('exam', 'subject', 'class_assigned', 'section')
```

### 3. Student Results
```python
class StudentExamStatus(models.Model):
    """Track student participation in exam"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam_detail = models.ForeignKey(ExamDetail, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('medical', 'Medical Leave'),
        ('disqualified', 'Disqualified'),
    ], default='scheduled')
    remarks = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('student', 'exam_detail')

class StudentResult(models.Model):
    """Individual subject result"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam_detail = models.ForeignKey(ExamDetail, on_delete=models.CASCADE)
    exam_status = models.ForeignKey(StudentExamStatus, on_delete=models.CASCADE)
    
    # Marks obtained
    practical_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    theory_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    total_marks = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Calculated fields
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5)
    gpa = models.DecimalField(max_digits=4, decimal_places=2)
    
    # Additional grades
    theory_grade = models.CharField(max_length=5, blank=True)
    practical_grade = models.CharField(max_length=5, blank=True)
    
    # Pass/Fail
    has_passed = models.BooleanField(default=False)
    
    # Metadata
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='results_entered')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'exam_detail')
    
    def clean(self):
        # Validate marks don't exceed full marks
        if self.theory_marks and self.exam_detail.theory_full_marks:
            if self.theory_marks > self.exam_detail.theory_full_marks:
                raise ValidationError("Theory marks exceed full marks")
        
        if self.practical_marks and self.exam_detail.practical_full_marks:
            if self.practical_marks > self.exam_detail.practical_full_marks:
                raise ValidationError("Practical marks exceed full marks")
    
    def save(self, *args, **kwargs):
        # Auto-calculate total and percentage
        self.total_marks = (self.theory_marks or 0) + (self.practical_marks or 0)
        self.percentage = (self.total_marks / self.exam_detail.full_marks) * 100
        
        # Assign grades
        grading_scale = self.exam_detail.class_assigned.grading_scale
        grade_obj = GradeRange.objects.filter(
            grading_scale=grading_scale,
            min_percentage__lte=self.percentage,
            max_percentage__gte=self.percentage
        ).first()
        
        if grade_obj:
            self.grade = grade_obj.grade
            self.gpa = grade_obj.grade_point
        
        # Check if passed
        self.has_passed = self.total_marks >= self.exam_detail.passing_marks
        
        super().save(*args, **kwargs)

class StudentOverallResult(models.Model):
    """Aggregated exam results"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    
    # Aggregates
    total_marks_obtained = models.DecimalField(max_digits=8, decimal_places=2)
    total_full_marks = models.DecimalField(max_digits=8, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    gpa = models.DecimalField(max_digits=4, decimal_places=2)
    grade = models.CharField(max_length=5)
    
    # Rankings
    class_rank = models.IntegerField(null=True)
    section_rank = models.IntegerField(null=True)
    
    # Pass status
    subjects_passed = models.IntegerField(default=0)
    subjects_failed = models.IntegerField(default=0)
    overall_result = models.CharField(max_length=20, choices=[
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('compartment', 'Compartment'),
    ])
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'exam')
```

### 4. Audit Trail
```python
class ResultModificationLog(models.Model):
    """Track all changes to student results"""
    student_result = models.ForeignKey(StudentResult, on_delete=models.CASCADE)
    modified_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    modified_at = models.DateTimeField(auto_now_add=True)
    
    field_changed = models.CharField(max_length=50)
    old_value = models.CharField(max_length=100)
    new_value = models.CharField(max_length=100)
    reason = models.TextField(blank=True)
    
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='approved_modifications')
```

## Business Logic

### 1. Automatic GPA Calculation
```python
def calculate_student_gpa(student_id, exam_id):
    \"\"\"Calculate weighted GPA based on credit hours\"\"\"
    results = StudentResult.objects.filter(
        student_id=student_id,
        exam_detail__exam_id=exam_id
    ).select_related('exam_detail__subject')
    
    total_credit_hours = 0
    weighted_grade_points = 0
    
    for result in results:
        subject = result.exam_detail.subject
        if subject.is_credit:
            total_credit_hours += subject.credit_hours
            weighted_grade_points += (result.gpa * subject.credit_hours)
    
    if total_credit_hours > 0:
        cgpa = weighted_grade_points / total_credit_hours
    else:
        cgpa = 0
    
    return round(cgpa, 2)
```

### 2. Rank Calculation
```python
def calculate_ranks(exam_id):
    \"\"\"Auto-calculate class and section ranks\"\"\"
    from django.db.models import Window, F
    from django.db.models.functions import Rank
    
    # Update class ranks
    StudentOverallResult.objects.filter(exam_id=exam_id).update(
        class_rank=Window(
            expression=Rank(),
            partition_by=[F('student__class_code')],
            order_by=[F('gpa').desc(), F('percentage').desc()]
        )
    )
    
    # Update section ranks
    StudentOverallResult.objects.filter(exam_id=exam_id).update(
        section_rank=Window(
            expression=Rank(),
            partition_by=[F('student__class_code_section')],
            order_by=[F('gpa').desc(), F('percentage').desc()]
        )
    )
```

### 3. Report Card Generation
```python
def generate_report_card(student_id, exam_id):
    \"\"\"Generate PDF report card\"\"\"
    from weasyprint import HTML
    
    student = Student.objects.get(id=student_id)
    overall = StudentOverallResult.objects.get(student_id=student_id, exam_id=exam_id)
    subject_results = StudentResult.objects.filter(
        student_id=student_id,
        exam_detail__exam_id=exam_id
    ).select_related('exam_detail__subject')
    
    context = {
        'student': student,
        'exam': overall.exam,
        'overall': overall,
        'subjects': subject_results,
        'school': SchoolDetail.objects.first(),
    }
    
    html = render_to_string('reports/report_card.html', context)
    pdf = HTML(string=html).write_pdf()
    
    return pdf
```

## API Endpoints

```
# Exam Management
GET    /api/exams                          # List all exams
POST   /api/exams                          # Create exam
GET    /api/exams/:id                      # Get exam details
PUT    /api/exams/:id                      # Update exam
DELETE /api/exams/:id                      # Delete exam
POST   /api/exams/:id/publish-timetable    # Publish timetable
POST   /api/exams/:id/publish-results      # Publish results

# Exam Details
GET    /api/exams/:examId/details          # List exam details
POST   /api/exams/:examId/details          # Create exam detail
PUT    /api/exam-details/:id               # Update exam detail
DELETE /api/exam-details/:id               # Delete exam detail

# Mark Entry
GET    /api/exam-details/:id/results       # Get all results for exam-detail
POST   /api/results                        # Enter marks
PUT    /api/results/:id                    # Update marks
POST   /api/results/bulk                   # Bulk mark entry

# Results
GET    /api/students/:id/results           # Get student's results
GET    /api/exams/:id/results              # Get all results for exam
GET    /api/results/:id/report-card        # Generate report card PDF
GET    /api/results/analytics              # Performance analytics
POST   /api/results/:id/calculate-ranks    # Recalculate ranks

# Grading Scales
GET    /api/grading-scales                 # List grading scales
POST   /api/grading-scales                 # Create grading scale
GET    /api/grading-scales/:id             # Get grading scale
PUT    /api/grading-scales/:id             # Update grading scale
```

## Frontend Components

### 1. Exam Creation Wizard
- Multi-step form for exam setup
- Subject selection per class
- Mark distribution configuration
- Timetable builder

### 2. Mark Entry Interface
- Excel-like grid for bulk entry
- Auto-save functionality
- Mark validation
- Quick navigation
- Offline support

### 3. Result Dashboard
- Class performance overview
- Subject-wise pass percentages
- Topper lists
- Grade distribution charts
- Comparison with previous exams

### 4. Report Card Designer
- Template customization
- School branding
- Signature placement
- Watermark support
- Batch generation

## Workflow

### Result Publication
```
1. Draft → Enter all marks
2. Review → Principal reviews marks
3. Approve → Marks locked
4. Publish → Results visible to students
5. Archive → Results archived at year end
```

## Implementation Priority

**Week 13-14**: Core exam and grading models
**Week 15-16**: Mark entry and result calculation
**Week 17**: Report card generation
**Week 18**: Analytics and dashboards
