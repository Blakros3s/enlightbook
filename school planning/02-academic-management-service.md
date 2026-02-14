# Academic Management Service

## Service Overview
Manages the core academic structure including classes, subjects, sections, semesters, syllabus tracking, and teacher-subject-class assignments.

## Core Responsibilities
- Class and grade management
- Subject management (compulsory/optional, credit/non-credit)
- Section management and capacity tracking
- Academic year and semester management
- Teacher-subject-class assignments
- Student subject enrollment
- Syllabus and curriculum tracking
- Academic calendar management

## Key Features

### 1. Academic Year & Semester Management
```python
class AcademicYear(models.Model):
    year = models.CharField(max_length=20)  # "2024-2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
class Semester(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)  # "First Semester", "Q1"
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
```

**Purpose**: Organize academic activities by time periods

### 2. Class Management
```python
class Class(models.Model):
    class_code = models.CharField(max_length=20, unique=True)
    class_name = models.CharField(max_length=100)  # "Grade 10", "Form 4"
    grade_level = models.IntegerField()  # 1-12
    subjects = models.ManyToManyField(Subject, related_name='compulsory_for_classes')
    optional_subjects = models.ManyToManyField(Subject, related_name='optional_for_classes')
    grading_scale = models.ForeignKey(GradingScale, on_delete=models.PROTECT)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
```

**Features**:
- Define compulsory and optional subjects
- Link to grading scale
- Track class-specific policies

### 3. Section Management
```python
class Section(models.Model):
    school_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='sections')
    section_name = models.CharField(max_length=10)  # "A", "B", "C"
    max_capacity = models.IntegerField(default=40)
    class_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    room_number = models.CharField(max_length=20, blank=True)
    
    @property
    def current_enrollment(self):
        return self.students.count()
    
    @property
    def available_seats(self):
        return max(0, self.max_capacity - self.current_enrollment)
```

**Features**:
- Capacity management
- Auto-calculate available seats
- Assign class teachers

### 4. Subject Management
```python
class SubjectCategory(models.Model):
    name = models.CharField(max_length=100)  # "Science", "Mathematics", "Languages"
    department = models.CharField(max_length=100)
    head_of_department = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)

class Subject(models.Model):
    subject_code = models.CharField(max_length=20, unique=True)
    subject_name = models.CharField(max_length=100)
    category = models.ForeignKey(SubjectCategory, on_delete=models.SET_NULL, null=True)
    
    # Credit system
    is_credit = models.BooleanField(default=True)
    credit_hours = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Subject type
    is_optional = models.BooleanField(default=False)
    subject_type = models.CharField(max_length=20, choices=[
        ('theory', 'Theory'),
        ('practical', 'Practical'),
        ('hybrid', 'Theory + Practical')
    ])
    
    # Prerequisites
    prerequisites = models.ManyToManyField(
        'self',
        through='SubjectPrerequisite',
        symmetrical=False,
        related_name='prerequisite_for'
    )
```

**Features**:
- Categorize subjects by department
- Define credit-bearing vs non-credit
- Set subject prerequisites
- Specify theory/practical/hybrid types

### 5. Teacher Assignment
```python
class TeacherClassAssignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    weekly_hours = models.IntegerField()  # Teaching hours per week
    
    class Meta:
        unique_together = ('teacher', 'subject', 'class_assigned', 'section', 'semester')
```

**Purpose**: Track which teacher teaches what subject to which class/section

### 6. Student Subject Enrollment
```python
class StudentSubjectEnrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('enrolled', 'Enrolled'),
        ('dropped', 'Dropped'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ])
    
    class Meta:
        unique_together = ('student', 'subject', 'semester')
    
    def clean(self):
        # Validate prerequisites
        for prereq in self.subject.prerequisites.all():
            if not self.student.has_completed_subject(prereq):
                raise ValidationError(f"Must complete {prereq.subject_name} first")
```

### 7. Syllabus Tracking
```python
class Chapter(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    chapter_number = models.IntegerField()
    chapter_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
class Topic(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    topic_name = models.CharField(max_length=200)
    order = models.IntegerField()
    
class SyllabusProgress(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    completed_on = models.DateField()
    notes = models.TextField(blank=True)
```

## API Endpoints

### Academic Year Management
```
GET    /api/academic/years                    # List all academic years
POST   /api/academic/years                    # Create academic year
GET    /api/academic/years/:id                # Get academic year details
PUT    /api/academic/years/:id                # Update academic year
GET    /api/academic/years/current            # Get current academic year
POST   /api/academic/years/:id/set-current    # Set as current year
```

### Semester Management
```
GET    /api/academic/semesters                # List all semesters
POST   /api/academic/semesters                # Create semester
GET    /api/academic/semesters/:id            # Get semester details
PUT    /api/academic/semesters/:id            # Update semester
GET    /api/academic/semesters/active         # Get active semester
```

### Class Management
```
GET    /api/academic/classes                  # List all classes
POST   /api/academic/classes                  # Create class
GET    /api/academic/classes/:id              # Get class details
PUT    /api/academic/classes/:id              # Update class
DELETE /api/academic/classes/:id              # Delete class
GET    /api/academic/classes/:id/subjects     # Get class subjects
POST   /api/academic/classes/:id/subjects     # Add subject to class
```

### Section Management
```
GET    /api/academic/classes/:classId/sections           # List sections
POST   /api/academic/classes/:classId/sections           # Create section
GET    /api/academic/sections/:id                        # Get section details
PUT    /api/academic/sections/:id                        # Update section
GET    /api/academic/sections/:id/students               # Get students in section
GET    /api/academic/sections/:id/availability          # Check available seats
```

### Subject Management
```
GET    /api/academic/subjects                 # List all subjects
POST   /api/academic/subjects                 # Create subject
GET    /api/academic/subjects/:id             # Get subject details
PUT    /api/academic/subjects/:id             # Update subject
DELETE /api/academic/subjects/:id             # Delete subject
GET    /api/academic/subjects/:id/prerequisites  # Get prerequisites
POST   /api/academic/subjects/:id/prerequisites  # Add prerequisite
```

### Teacher Assignment
```
GET    /api/academic/teachers/:id/assignments        # Get teacher's assignments
POST   /api/academic/teachers/:id/assignments        # Create assignment
DELETE /api/academic/teachers/:id/assignments/:assignmentId  # Remove assignment
GET    /api/academic/teachers/:id/workload           # Calculate teacher workload
```

### Student Enrollment
```
GET    /api/academic/students/:id/enrollments        # Get student's enrolled subjects
POST   /api/academic/students/:id/enrollments        # Enroll in subject
DELETE /api/academic/students/:id/enrollments/:enrollmentId  # Drop subject
GET    /api/academic/students/:id/eligible-subjects  # Get subjects student can enroll in
```

### Syllabus Tracking
```
GET    /api/academic/syllabus/:classId/:subjectId      # Get syllabus for class-subject
POST   /api/academic/syllabus/progress                 # Mark topic as completed
GET    /api/academic/syllabus/progress/:teacherId      # Get teacher's syllabus progress
GET    /api/academic/syllabus/completion/:classId      # Syllabus completion percentage
```

## Business Rules

### 1. Credit Hour Limits
```python
class ClassCreditPolicy(models.Model):
    class_assigned = models.OneToOneField(Class, on_delete=models.CASCADE)
    min_credits = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 18.0
    max_credits = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 24.0
    min_optional_subjects = models.IntegerField(default=0)
    max_optional_subjects = models.IntegerField(default=2)
```

- Students must enroll in minimum required credits
- Cannot exceed maximum credit hours
- Optional subject selection within limits

### 2. Section Capacity
- Sections have maximum capacity
- Cannot enroll students beyond capacity
- Auto-warning when section is 90% full
- Section balancing recommendations

### 3. Teacher Workload
```python
class TeacherWorkloadPolicy(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE)
    max_weekly_hours = models.IntegerField(default=35)
    max_classes = models.IntegerField(default=6)
    max_sections = models.IntegerField(default=8)
```

- Teachers cannot exceed maximum weekly teaching hours
- System warns when approaching limits
- Load balancing across teachers

### 4. Subject Prerequisites
- Students must complete prerequisites before enrollment
- Minimum passing grade required for prerequisite
- Can define co-requisites (must be taken together)
- Mutual exclusivity (cannot take both)

## Frontend Components (Next.js)

### 1. Class Management Dashboard
```typescript
// app/academic/classes/page.tsx
- List all classes with grade levels
- Create/Edit class modal
- Assign subjects to class
- View sections under each class
- Capacity utilization charts
```

### 2. Subject Catalog
```typescript
// app/academic/subjects/page.tsx
- Searchable subject list
- Filter by category, type, credit status
- View prerequisites tree
- Subject enrollment statistics
```

### 3. Teacher Assignment Interface
```typescript
// app/academic/assignments/page.tsx
- Drag-and-drop teacher-subject-class assignment
- Visual workload indicator
- Conflict detection (time clashes)
- Weekly schedule view
```

### 4. Student Enrollment Portal
```typescript
// app/student/enrollment/page.tsx
- Available subjects based on class and semester
- Show prerequisites and eligibility
- Credit hour calculator
- Subject selection cart
- Enrollment confirmation
```

### 5. Syllabus Progress Tracker
```typescript
// app/teacher/syllabus/page.tsx
- Subject chapter/topic outline
- Mark topics as completed
- Progress percentage per class
- Comparison with other sections
- Behind schedule alerts
```

## Integration Points

### With Examination Service
- Subject enrollment determines eligible exams
- Exam scheduling considers subject type (theory/practical)
- Results linked to enrolled subjects

### With Attendance Service
- Attendance tracked per subject-class combination
- Period-wise attendance linked to subject schedule
- Minimum attendance required for exam eligibility

### With Fee Management
- Subject-based fees (lab fees for practical subjects)
- Optional subject fees
- Credit hour-based tuition calculation

### With Timetable Service
- Teacher availability from assignments
- Subject periods allocation
- Room assignment based on subject type

## Data Migration Strategy

### From Current System
1. Map existing Classes to new structure
2. Migrate Subject assignments
3. Create default Academic Year
4. Link students to new enrollment model
5. Preserve teacher assignments

### Historical Data
- Archive previous academic years
- Maintain class promotion history
- Track subject completion over years

## Technology Stack

### Backend
- **Django Models**: Class, Subject, Section, Teacher, Student
- **Validation**: django-model-utils for status transitions
- **Caching**: Redis for frequently accessed data (class lists, subject catalogs)
- **Background Jobs**: Celery for enrollment batch operations

### Frontend
- **Next.js Pages**: Server-side rendered class and subject pages
- **State Management**: Zustand for enrollment cart
- **Forms**: React Hook Form for assignment creation
- **UI Components**: Shadcn UI for modals, dropdowns, data tables
- **Charts**: Recharts for capacity visualization

## Performance Optimization

### Database
```sql
-- Indexes for common queries
CREATE INDEX idx_student_class_section ON students(class_code_id, class_code_section_id);
CREATE INDEX idx_teacher_assignments ON teacher_class_assignments(teacher_id, semester_id);
CREATE INDEX idx_subject_enrollment ON student_subject_enrollments(student_id, status);
```

### Caching Strategy
```python
# Cache subject catalog for 1 hour
@cache_page(60 * 60)
def get_subject_catalog(request):
    ...

# Cache class structure for current academic year
cache_key = f"class_structure_{academic_year_id}"
```

### Query Optimization
```python
# Use select_related for foreign keys
classes = Class.objects.select_related('grading_scale', 'academic_year')

# Use prefetch_related for many-to-many
classes = Class.objects.prefetch_related('subjects', 'optional_subjects', 'sections')
```

## Testing Strategy

### Unit Tests
- Class creation and validation
- Section capacity calculations
- Credit hour validation
- Prerequisite checking
- Teacher workload calculation

### Integration Tests
- Complete enrollment workflow
- Teacher assignment process
- Syllabus progress tracking
- Academic year transition

## Implementation Priority

### Phase 1: Core Structure (Week 1-2)
1. Create Academic Year and Semester models
2. Implement Class and Section management
3. Build Subject catalog
4. Add basic validation

### Phase 2: Assignments (Week 3-4)
1. Teacher-Subject-Class assignment system
2. Student subject enrollment
3. Credit hour validation
4. Prerequisite checking

### Phase 3: Advanced Features (Week 5-6)
1. Syllabus tracking
2. Section capacity management
3. Teacher workload optimization
4. Academic calendar integration
