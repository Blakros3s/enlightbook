from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

from apps.users.models import CustomUser
from apps.academic.models import (
    Class, Section, Subject, Semester, AcademicYear,
    StudentSubjectEnrollment
)


class GradingScale(models.Model):
    """
    Defines grading rules for classes/boards.
    """
    name = models.CharField(max_length=100, help_text="e.g., CBSE Scale, IB Scale")
    school_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='grading_scales',
        null=True,
        blank=True
    )
    is_default = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Grading Scale'
        verbose_name_plural = 'Grading Scales'
    
    def __str__(self):
        return f"{self.name} ({'Default' if self.is_default else 'Custom'})"
    
    def save(self, *args, **kwargs):
        # If this is marked as default, unset other defaults for this class
        if self.is_default and self.school_class:
            GradingScale.objects.filter(
                school_class=self.school_class,
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)
    
    def get_grade_for_percentage(self, percentage):
        """Get grade for a given percentage."""
        grade_range = self.ranges.filter(
            min_percentage__lte=percentage,
            max_percentage__gte=percentage
        ).first()
        return grade_range


class GradeRange(models.Model):
    """
    Individual grade ranges within a grading scale.
    """
    grading_scale = models.ForeignKey(
        GradingScale,
        on_delete=models.CASCADE,
        related_name='ranges'
    )
    grade = models.CharField(max_length=5, help_text="e.g., A+, A, B+")
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=4, decimal_places=2, help_text="For GPA calculation")
    description = models.CharField(max_length=50, blank=True, help_text="e.g., Outstanding, Excellent")
    
    class Meta:
        ordering = ['-min_percentage']
        verbose_name = 'Grade Range'
        verbose_name_plural = 'Grade Ranges'
        unique_together = ['grading_scale', 'grade']
    
    def __str__(self):
        return f"{self.grade} ({self.min_percentage}-{self.max_percentage}%)"
    
    def clean(self):
        if self.min_percentage >= self.max_percentage:
            raise ValidationError("Min percentage must be less than max percentage.")
        
        # Check for overlapping ranges
        overlapping = GradeRange.objects.filter(
            grading_scale=self.grading_scale,
            min_percentage__lt=self.max_percentage,
            max_percentage__gt=self.min_percentage
        ).exclude(id=self.id)
        
        if overlapping.exists():
            raise ValidationError("This range overlaps with existing grade ranges.")


class Exam(models.Model):
    """
    Major exams like mid-term, final, unit tests.
    """
    EXAM_TYPES = [
        ('mid_term', 'Mid-Term Examination'),
        ('final', 'Final Examination'),
        ('unit_test', 'Unit Test'),
        ('practical', 'Practical Examination'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('project', 'Project'),
    ]
    
    name = models.CharField(max_length=200)
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='exams'
    )
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='exams',
        null=True,
        blank=True
    )
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    
    # Weightage for overall result calculation
    weightage_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('100.00'),
        help_text="Weightage in overall result calculation"
    )
    
    # Publication status
    is_timetable_published = models.BooleanField(default=False)
    timetable_published_date = models.DateTimeField(null=True, blank=True)
    timetable_published_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timetables_published'
    )
    
    is_result_published = models.BooleanField(default=False)
    result_published_date = models.DateTimeField(null=True, blank=True)
    result_published_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='results_published'
    )
    
    allow_students_to_view_results = models.BooleanField(default=False)
    
    # Configuration
    max_marks = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('100.00'))
    passing_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('40.00'))
    
    # Dates
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='exams_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'
    
    def __str__(self):
        return f"{self.name} ({self.academic_year.year_name})"
    
    def publish_timetable(self, user):
        """Publish the exam timetable."""
        self.is_timetable_published = True
        self.timetable_published_date = timezone.now()
        self.timetable_published_by = user
        self.save()
    
    def publish_results(self, user):
        """Publish exam results."""
        self.is_result_published = True
        self.result_published_date = timezone.now()
        self.result_published_by = user
        self.allow_students_to_view_results = True
        self.save()
    
    def calculate_overall_results(self):
        """Calculate overall results for all students."""
        for overall_result in self.overall_results.all():
            overall_result.calculate_aggregate()


class ExamDetail(models.Model):
    """
    Specific exam details for each subject in each class/section.
    """
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='details'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='exam_details'
    )
    school_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='exam_details'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='exam_details',
        null=True,
        blank=True
    )
    
    # Marks distribution
    full_marks = models.DecimalField(max_digits=6, decimal_places=2)
    theory_full_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    practical_full_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    passing_marks = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Exam schedule
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.IntegerField()
    
    # Venue
    venue = models.CharField(max_length=100, blank=True)
    
    # Invigilators
    invigilators = models.ManyToManyField(
        CustomUser,
        blank=True,
        related_name='invigilated_exams',
        limit_choices_to={'is_teacher': True}
    )
    
    # Status
    is_marks_entered = models.BooleanField(default=False)
    marks_entered_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marks_entered'
    )
    marks_entered_at = models.DateTimeField(null=True, blank=True)
    
    is_marks_verified = models.BooleanField(default=False)
    marks_verified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marks_verified'
    )
    marks_verified_at = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='exam_details_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['exam', 'subject', 'school_class', 'section']
        ordering = ['exam_date', 'start_time']
        verbose_name = 'Exam Detail'
        verbose_name_plural = 'Exam Details'
    
    def __str__(self):
        section_str = f" - Sec {self.section.section_name}" if self.section else ""
        return f"{self.exam.name} - {self.subject}{section_str}"
    
    def clean(self):
        # Validate section belongs to class
        if self.section and self.section.school_class != self.school_class:
            raise ValidationError("Section must belong to the selected class.")
        
        # Validate time
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")
        
        # Validate marks distribution
        if self.subject.subject_type == 'theory':
            if self.theory_full_marks is None:
                raise ValidationError("Theory marks required for theory subjects.")
            if self.full_marks != self.theory_full_marks:
                raise ValidationError("Full marks must equal theory marks for theory subjects.")
        elif self.subject.subject_type == 'practical':
            if self.practical_full_marks is None:
                raise ValidationError("Practical marks required for practical subjects.")
            if self.full_marks != self.practical_full_marks:
                raise ValidationError("Full marks must equal practical marks for practical subjects.")
        elif self.subject.subject_type == 'hybrid':
            if self.theory_full_marks is None or self.practical_full_marks is None:
                raise ValidationError("Both theory and practical marks required for hybrid subjects.")
            if self.full_marks != self.theory_full_marks + self.practical_full_marks:
                raise ValidationError("Full marks must equal theory + practical for hybrid subjects.")
    
    def get_student_result(self, student):
        """Get result for a specific student."""
        return self.student_results.filter(student=student).first()
    
    def get_class_statistics(self):
        """Get statistics for this exam detail."""
        results = self.student_results.all()
        total_students = results.count()
        
        if total_students == 0:
            return {
                'total_students': 0,
                'students_appeared': 0,
                'students_passed': 0,
                'students_failed': 0,
                'pass_percentage': 0,
                'highest_marks': 0,
                'lowest_marks': 0,
                'average_marks': 0
            }
        
        appeared = results.exclude(status='absent')
        passed = results.filter(has_passed=True)
        
        marks = [r.total_marks for r in appeared if r.total_marks is not None]
        
        return {
            'total_students': total_students,
            'students_appeared': appeared.count(),
            'students_passed': passed.count(),
            'students_failed': appeared.count() - passed.count(),
            'pass_percentage': (passed.count() / appeared.count() * 100) if appeared.count() > 0 else 0,
            'highest_marks': max(marks) if marks else 0,
            'lowest_marks': min(marks) if marks else 0,
            'average_marks': sum(marks) / len(marks) if marks else 0
        }


class StudentExamStatus(models.Model):
    """
    Tracks student participation status in an exam.
    """
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('medical', 'Medical Leave'),
        ('disqualified', 'Disqualified'),
        ('exempted', 'Exempted'),
    ]
    
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='exam_statuses',
        limit_choices_to={'is_student': True}
    )
    exam_detail = models.ForeignKey(
        ExamDetail,
        on_delete=models.CASCADE,
        related_name='student_statuses'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    remarks = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    recorded_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'exam_detail']
        ordering = ['-recorded_at']
        verbose_name = 'Student Exam Status'
        verbose_name_plural = 'Student Exam Statuses'
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.exam_detail} - {self.get_status_display()}"


class StudentResult(models.Model):
    """
    Individual subject result for a student.
    """
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='exam_results',
        limit_choices_to={'is_student': True}
    )
    exam_detail = models.ForeignKey(
        ExamDetail,
        on_delete=models.CASCADE,
        related_name='student_results'
    )
    exam_status = models.ForeignKey(
        StudentExamStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Marks obtained
    theory_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    practical_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    total_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Calculated fields
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grade = models.CharField(max_length=5, blank=True)
    grade_point = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    # Separate grades
    theory_grade = models.CharField(max_length=5, blank=True)
    practical_grade = models.CharField(max_length=5, blank=True)
    
    # Pass/Fail
    has_passed = models.BooleanField(default=False)
    
    # Metadata
    entered_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='results_entered'
    )
    entered_at = models.DateTimeField(null=True, blank=True)
    
    verified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='results_verified'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'exam_detail']
        ordering = ['-created_at']
        verbose_name = 'Student Result'
        verbose_name_plural = 'Student Results'
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.exam_detail} - {self.total_marks}/{self.exam_detail.full_marks}"
    
    def clean(self):
        # Validate marks don't exceed full marks
        if self.theory_marks and self.exam_detail.theory_full_marks:
            if self.theory_marks > self.exam_detail.theory_full_marks:
                raise ValidationError("Theory marks exceed full marks.")
        
        if self.practical_marks and self.exam_detail.practical_full_marks:
            if self.practical_marks > self.exam_detail.practical_full_marks:
                raise ValidationError("Practical marks exceed full marks.")
        
        if self.total_marks and self.exam_detail.full_marks:
            if self.total_marks > self.exam_detail.full_marks:
                raise ValidationError("Total marks exceed full marks.")
    
    def calculate_result(self):
        """Calculate total, percentage, grade, and pass status."""
        # Calculate total marks
        self.total_marks = Decimal('0.00')
        
        if self.theory_marks:
            self.total_marks += self.theory_marks
        
        if self.practical_marks:
            self.total_marks += self.practical_marks
        
        # Calculate percentage
        if self.total_marks and self.exam_detail.full_marks:
            self.percentage = (self.total_marks / self.exam_detail.full_marks) * 100
        
        # Get grading scale
        grading_scale = self.exam_detail.school_class.grading_scales.filter(
            is_default=True,
            is_active=True
        ).first()
        
        if not grading_scale:
            # Use school's default or create a basic one
            grading_scale = GradingScale.objects.filter(
                is_default=True,
                is_active=True
            ).first()
        
        # Assign grades
        if self.percentage and grading_scale:
            grade_obj = grading_scale.get_grade_for_percentage(self.percentage)
            
            if grade_obj:
                self.grade = grade_obj.grade
                self.grade_point = grade_obj.grade_point
            
            # Theory grade
            if self.theory_marks and self.exam_detail.theory_full_marks:
                theory_percentage = (self.theory_marks / self.exam_detail.theory_full_marks) * 100
                theory_grade_obj = grading_scale.get_grade_for_percentage(theory_percentage)
                if theory_grade_obj:
                    self.theory_grade = theory_grade_obj.grade
            
            # Practical grade
            if self.practical_marks and self.exam_detail.practical_full_marks:
                practical_percentage = (self.practical_marks / self.exam_detail.practical_full_marks) * 100
                practical_grade_obj = grading_scale.get_grade_for_percentage(practical_percentage)
                if practical_grade_obj:
                    self.practical_grade = practical_grade_obj.grade
        
        # Check if passed
        if self.total_marks is not None:
            self.has_passed = self.total_marks >= self.exam_detail.passing_marks
        
        # Save without calling full save to avoid recursion
        self.save(update_fields=[
            'total_marks', 'percentage', 'grade', 'grade_point',
            'theory_grade', 'practical_grade', 'has_passed'
        ])
    
    def save(self, *args, **kwargs):
        self.clean()
        
        # Auto-calculate on save if marks are provided
        if (self.theory_marks is not None or self.practical_marks is not None) and not kwargs.pop('skip_calculation', False):
            self.calculate_result()
        
        super().save(*args, **kwargs)


class StudentOverallResult(models.Model):
    """
    Aggregated exam results for a student across all subjects.
    """
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='overall_results',
        limit_choices_to={'is_student': True}
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='overall_results'
    )
    
    # Aggregates
    total_marks_obtained = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    total_full_marks = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grade = models.CharField(max_length=5, blank=True)
    grade_point_average = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    # Rankings
    class_rank = models.IntegerField(null=True, blank=True)
    section_rank = models.IntegerField(null=True, blank=True)
    
    # Pass status
    subjects_appeared = models.IntegerField(default=0)
    subjects_passed = models.IntegerField(default=0)
    subjects_failed = models.IntegerField(default=0)
    overall_result = models.CharField(
        max_length=20,
        choices=[
            ('passed', 'Passed'),
            ('failed', 'Failed'),
            ('compartment', 'Compartment'),
        ],
        blank=True
    )
    
    # Metadata
    remarks = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'exam']
        ordering = ['-percentage']
        verbose_name = 'Student Overall Result'
        verbose_name_plural = 'Student Overall Results'
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.exam} - {self.percentage}%"
    
    def calculate_aggregate(self):
        """Calculate aggregate from individual subject results."""
        results = self.student.exam_results.filter(exam_detail__exam=self.exam)
        
        self.total_marks_obtained = Decimal('0.00')
        self.total_full_marks = Decimal('0.00')
        total_grade_points = Decimal('0.00')
        credit_hours = Decimal('0.00')
        
        self.subjects_appeared = 0
        self.subjects_passed = 0
        self.subjects_failed = 0
        
        for result in results:
            if result.exam_status and result.exam_status.status == 'absent':
                continue
            
            if result.total_marks is not None:
                self.subjects_appeared += 1
                self.total_marks_obtained += result.total_marks
                self.total_full_marks += result.exam_detail.full_marks
                
                if result.has_passed:
                    self.subjects_passed += 1
                else:
                    self.subjects_failed += 1
                
                # Calculate weighted GPA
                if result.grade_point is not None:
                    subject_credit = result.exam_detail.subject.credit_hours
                    total_grade_points += result.grade_point * subject_credit
                    credit_hours += subject_credit
        
        # Calculate percentage
        if self.total_full_marks > 0:
            self.percentage = (self.total_marks_obtained / self.total_full_marks) * 100
        
        # Calculate GPA
        if credit_hours > 0:
            self.grade_point_average = total_grade_points / credit_hours
        
        # Get overall grade
        if self.percentage:
            grading_scale = self.student.class_enrollments.filter(
                status='active'
            ).first().school_class.grading_scales.filter(is_default=True).first()
            
            if grading_scale:
                grade_obj = grading_scale.get_grade_for_percentage(self.percentage)
                if grade_obj:
                    self.grade = grade_obj.grade
        
        # Determine overall result
        if self.subjects_failed == 0:
            self.overall_result = 'passed'
        elif self.subjects_failed <= 2:  # Allow up to 2 compartment subjects
            self.overall_result = 'compartment'
        else:
            self.overall_result = 'failed'
        
        self.save(update_fields=[
            'total_marks_obtained', 'total_full_marks', 'percentage',
            'grade', 'grade_point_average', 'subjects_appeared',
            'subjects_passed', 'subjects_failed', 'overall_result'
        ])


class ResultModificationLog(models.Model):
    """
    Audit trail for all changes to student results.
    """
    student_result = models.ForeignKey(
        StudentResult,
        on_delete=models.CASCADE,
        related_name='modification_logs'
    )
    modified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='result_modifications'
    )
    modified_at = models.DateTimeField(auto_now_add=True)
    
    field_changed = models.CharField(max_length=50)
    old_value = models.CharField(max_length=100, blank=True)
    new_value = models.CharField(max_length=100, blank=True)
    reason = models.TextField(blank=True)
    
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_modifications',
        limit_choices_to={'is_principal': True}
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-modified_at']
        verbose_name = 'Result Modification Log'
        verbose_name_plural = 'Result Modification Logs'
    
    def __str__(self):
        return f"{self.student_result} - {self.field_changed} - {self.modified_at}"


class ReportCardTemplate(models.Model):
    """
    Customizable report card templates.
    """
    name = models.CharField(max_length=100)
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='report_card_templates'
    )
    
    # Template configuration
    header_image = models.ImageField(upload_to='report_cards/headers/', blank=True, null=True)
    footer_text = models.TextField(blank=True)
    show_signature = models.BooleanField(default=True)
    show_photo = models.BooleanField(default=True)
    show_attendance = models.BooleanField(default=True)
    show_remarks = models.BooleanField(default=True)
    
    # Custom fields
    custom_fields = models.JSONField(default=dict, blank=True, help_text="Custom fields for report card")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Report Card Template'
        verbose_name_plural = 'Report Card Templates'
    
    def __str__(self):
        return f"{self.name} ({self.academic_year.year_name})"


class GeneratedReportCard(models.Model):
    """
    Generated report cards for students.
    """
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='report_cards',
        limit_choices_to={'is_student': True}
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='report_cards'
    )
    template = models.ForeignKey(
        ReportCardTemplate,
        on_delete=models.CASCADE,
        related_name='generated_cards'
    )
    
    # Generated file
    pdf_file = models.FileField(upload_to='report_cards/generated/', blank=True, null=True)
    
    # Generation metadata
    generated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='report_cards_generated'
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    
    # Distribution
    is_distributed = models.BooleanField(default=False)
    distributed_at = models.DateTimeField(null=True, blank=True)
    distributed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='report_cards_distributed'
    )
    
    class Meta:
        unique_together = ['student', 'exam']
        ordering = ['-generated_at']
        verbose_name = 'Generated Report Card'
        verbose_name_plural = 'Generated Report Cards'
    
    def __str__(self):
        return f"Report Card - {self.student.get_full_name()} - {self.exam}"