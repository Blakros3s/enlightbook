from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.users.models import CustomUser


class AcademicYear(models.Model):
    """
    Represents a school academic year (e.g., 2024-2025).
    """
    year_name = models.CharField(max_length=20, unique=True, help_text="e.g., 2024-2025")
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False, help_text="Mark as the current active academic year")
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Academic Year'
        verbose_name_plural = 'Academic Years'
    
    def __str__(self):
        return self.year_name
    
    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError("End date must be after start date.")
    
    def save(self, *args, **kwargs):
        self.clean()
        # If this is marked as current, unset other current years
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class Semester(models.Model):
    """
    Represents a semester/term within an academic year.
    """
    SEMESTER_CHOICES = [
        ('first', 'First Semester'),
        ('second', 'Second Semester'),
        ('third', 'Third Semester'),
        ('summer', 'Summer Term'),
        ('quarter_1', 'Quarter 1'),
        ('quarter_2', 'Quarter 2'),
        ('quarter_3', 'Quarter 3'),
        ('quarter_4', 'Quarter 4'),
    ]
    
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='semesters'
    )
    name = models.CharField(max_length=50, choices=SEMESTER_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False, help_text="Mark as the currently active semester")
    registration_open = models.BooleanField(default=False, help_text="Allow student registrations")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['academic_year', 'start_date']
        unique_together = ['academic_year', 'name']
        verbose_name = 'Semester'
        verbose_name_plural = 'Semesters'
    
    def __str__(self):
        return f"{self.academic_year.year_name} - {self.get_name_display()}"
    
    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError("End date must be after start date.")
        
        # Check semester dates are within academic year
        if self.academic_year:
            if self.start_date < self.academic_year.start_date:
                raise ValidationError("Semester start date must be within academic year.")
            if self.end_date > self.academic_year.end_date:
                raise ValidationError("Semester end date must be within academic year.")


class SubjectCategory(models.Model):
    """
    Categories for subjects (e.g., Science, Mathematics, Languages).
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#3B82F6", help_text="Hex color code for UI")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Subject Category'
        verbose_name_plural = 'Subject Categories'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.name.upper().replace(' ', '_')[:20]
        super().save(*args, **kwargs)


class Subject(models.Model):
    """
    Represents a subject/course in the curriculum.
    """
    SUBJECT_TYPES = [
        ('theory', 'Theory Only'),
        ('practical', 'Practical Only'),
        ('hybrid', 'Theory + Practical'),
    ]
    
    subject_code = models.CharField(max_length=20, unique=True)
    subject_name = models.CharField(max_length=200)
    category = models.ForeignKey(
        SubjectCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subjects'
    )
    
    # Credit system
    is_credit = models.BooleanField(default=True, help_text="Does this subject carry credits?")
    credit_hours = models.DecimalField(max_digits=5, decimal_places=2, default=3.00)
    
    # Subject type
    is_optional = models.BooleanField(default=False, help_text="Can students choose not to take this?")
    subject_type = models.CharField(max_length=20, choices=SUBJECT_TYPES, default='theory')
    
    # Marks distribution
    theory_full_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100.00)
    practical_full_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    passing_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=40.00)
    
    # Description
    description = models.TextField(blank=True)
    syllabus = models.TextField(blank=True, help_text="Detailed syllabus/outcome")
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['subject_code']
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
    
    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"
    
    @property
    def total_full_marks(self):
        """Calculate total full marks based on subject type."""
        if self.subject_type == 'theory':
            return self.theory_full_marks
        elif self.subject_type == 'practical':
            return self.practical_full_marks
        else:  # hybrid
            return self.theory_full_marks + self.practical_full_marks


class SubjectPrerequisite(models.Model):
    """
    Defines prerequisite relationships between subjects.
    """
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='prerequisites_details'
    )
    prerequisite_subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='is_prerequisite_for'
    )
    minimum_grade = models.CharField(max_length=5, blank=True, help_text="Minimum grade required (e.g., C, B)")
    is_mandatory = models.BooleanField(default=True, help_text="Is this prerequisite mandatory?")
    
    class Meta:
        unique_together = ['subject', 'prerequisite_subject']
        verbose_name = 'Subject Prerequisite'
        verbose_name_plural = 'Subject Prerequisites'
    
    def __str__(self):
        return f"{self.prerequisite_subject} → {self.subject}"
    
    def clean(self):
        if self.subject == self.prerequisite_subject:
            raise ValidationError("A subject cannot be a prerequisite for itself.")


class Class(models.Model):
    """
    Represents a class/grade level (e.g., Grade 10, Form 4).
    """
    class_code = models.CharField(max_length=20, unique=True)
    class_name = models.CharField(max_length=100)
    grade_level = models.IntegerField(help_text="Numeric grade level (e.g., 1-12)")
    
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='classes'
    )
    
    # Subjects
    compulsory_subjects = models.ManyToManyField(
        Subject,
        related_name='compulsory_for_classes',
        blank=True
    )
    optional_subjects = models.ManyToManyField(
        Subject,
        related_name='optional_for_classes',
        blank=True
    )
    
    # Credit policy
    min_credits = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)
    max_credits = models.DecimalField(max_digits=5, decimal_places=2, default=24.00)
    min_optional_subjects = models.IntegerField(default=0)
    max_optional_subjects = models.IntegerField(default=2)
    
    # Configuration
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['grade_level', 'class_code']
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
    
    def __str__(self):
        return f"{self.class_name} ({self.academic_year.year_name})"


class Section(models.Model):
    """
    Represents a section/division within a class (e.g., Class 10A, 10B).
    """
    school_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    section_name = models.CharField(max_length=10, help_text="e.g., A, B, C")
    max_capacity = models.PositiveIntegerField(default=40)
    
    # Class teacher
    class_teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sections_as_teacher',
        limit_choices_to={'is_teacher': True}
    )
    
    # Room assignment
    room_number = models.CharField(max_length=20, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['school_class', 'section_name']
        unique_together = ['school_class', 'section_name']
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
    
    def __str__(self):
        return f"{self.school_class.class_name} - Section {self.section_name}"
    
    @property
    def current_enrollment(self):
        """Get current number of enrolled students."""
        # This will be populated when Student model is created
        return 0  # Placeholder
    
    @property
    def available_seats(self):
        """Calculate available seats."""
        return max(0, self.max_capacity - self.current_enrollment)
    
    @property
    def is_full(self):
        """Check if section is at capacity."""
        return self.current_enrollment >= self.max_capacity


class TeacherClassAssignment(models.Model):
    """
    Assigns teachers to specific classes, sections, and subjects.
    """
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='class_assignments',
        limit_choices_to={'is_teacher': True}
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='teacher_assignments'
    )
    school_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='teacher_assignments'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='teacher_assignments',
        null=True,
        blank=True
    )
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='teacher_assignments'
    )
    
    # Workload
    weekly_periods = models.PositiveIntegerField(default=5, help_text="Number of periods per week")
    
    # Schedule
    schedule_notes = models.TextField(blank=True, help_text="Day/time schedule notes")
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['teacher', 'school_class', 'subject']
        unique_together = ['teacher', 'subject', 'school_class', 'section', 'semester']
        verbose_name = 'Teacher Class Assignment'
        verbose_name_plural = 'Teacher Class Assignments'
    
    def __str__(self):
        section_str = f" - Sec {self.section.section_name}" if self.section else ""
        return f"{self.teacher.get_full_name()} teaches {self.subject} to {self.school_class}{section_str}"
    
    def clean(self):
        # Validate teacher is actually a teacher
        if not self.teacher.is_teacher:
            raise ValidationError("Selected user is not a teacher.")
        
        # Validate section belongs to the class
        if self.section and self.section.school_class != self.school_class:
            raise ValidationError("Section must belong to the selected class.")
        
        # Validate semester belongs to the same academic year as class
        if self.semester.academic_year != self.school_class.academic_year:
            raise ValidationError("Semester must be from the same academic year as the class.")


class StudentSubjectEnrollment(models.Model):
    """
    Tracks student enrollment in subjects.
    """
    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('dropped', 'Dropped'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subject_enrollments',
        limit_choices_to={'is_student': True}
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='student_enrollments'
    )
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='student_enrollments'
    )
    
    # Enrollment details
    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')
    
    # Grade information (populated after completion)
    final_grade = models.CharField(max_length=5, blank=True)
    grade_points = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    # Metadata
    dropped_date = models.DateTimeField(null=True, blank=True)
    dropped_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-enrollment_date']
        unique_together = ['student', 'subject', 'semester']
        verbose_name = 'Student Subject Enrollment'
        verbose_name_plural = 'Student Subject Enrollments'
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.subject} ({self.semester})"
    
    def clean(self):
        # Validate student is actually a student
        if not self.student.is_student:
            raise ValidationError("Selected user is not a student.")
        
        # Check prerequisites
        if self.status == 'enrolled':
            self._check_prerequisites()
    
    def _check_prerequisites(self):
        """Check if student has completed required prerequisites."""
        prerequisites = self.subject.prerequisites_details.filter(is_mandatory=True)
        
        for prereq in prerequisites:
            # Check if student has completed the prerequisite subject
            completed = StudentSubjectEnrollment.objects.filter(
                student=self.student,
                subject=prereq.prerequisite_subject,
                status='completed'
            ).exists()
            
            if not completed:
                raise ValidationError(
                    f"Prerequisite not met: {prereq.prerequisite_subject}. "
                    f"Student must complete this subject first."
                )


class ClassEnrollment(models.Model):
    """
    Tracks student enrollment in a specific class and section.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('promoted', 'Promoted'),
        ('repeated', 'Repeated'),
        ('transferred', 'Transferred'),
        ('graduated', 'Graduated'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='class_enrollments',
        limit_choices_to={'is_student': True}
    )
    school_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='student_enrollments'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='student_enrollments'
    )
    
    # Enrollment details
    roll_number = models.CharField(max_length=20, blank=True, help_text="Student roll number in class")
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Completion
    completion_date = models.DateField(null=True, blank=True)
    final_grade = models.CharField(max_length=5, blank=True)
    remarks = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-enrollment_date']
        unique_together = ['student', 'school_class']
        verbose_name = 'Class Enrollment'
        verbose_name_plural = 'Class Enrollments'
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.school_class} ({self.status})"
    
    def clean(self):
        # Validate student is actually a student
        if not self.student.is_student:
            raise ValidationError("Selected user is not a student.")
        
        # Validate section belongs to the class
        if self.section.school_class != self.school_class:
            raise ValidationError("Section must belong to the selected class.")
        
        # Check section capacity
        if self._state.adding and self.section.is_full:
            raise ValidationError("This section is at full capacity.")
    
    def save(self, *args, **kwargs):
        self.clean()
        
        # Generate roll number if not provided
        if not self.roll_number:
            last_roll = ClassEnrollment.objects.filter(
                school_class=self.school_class,
                section=self.section
            ).order_by('-roll_number').first()
            
            if last_roll and last_roll.roll_number.isdigit():
                self.roll_number = str(int(last_roll.roll_number) + 1)
            else:
                self.roll_number = "1"
        
        super().save(*args, **kwargs)
