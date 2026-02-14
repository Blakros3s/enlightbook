# Phase 2: Academic Management System

## Summary

Phase 2 implements the complete academic management system for EnlightBook, including academic years, semesters, classes, sections, subjects, teacher assignments, and student enrollments.

**Status**: ✅ **COMPLETE**

---

## What Was Built

### 1. Backend (Django)

#### Models Created

**`apps/academic/models.py`** (9 models, ~700 lines)

1. **AcademicYear** - School academic year management
   - Year name (e.g., "2024-2025")
   - Start/end dates
   - Current year flag
   - Automatic unsetting of other current years

2. **Semester** - Terms/semesters within academic year
   - Multiple semester types (First, Second, Summer, Quarters)
   - Registration open/closed status
   - Active semester tracking
   - Date validation within academic year

3. **SubjectCategory** - Subject categorization
   - Name, code, department
   - Color coding for UI
   - Auto-generated code from name

4. **Subject** - Course/subject management
   - Subject code, name, category
   - Credit system (hours, optional/compulsory)
   - Subject types: Theory, Practical, Hybrid
   - Marks distribution (theory/practical)
   - Prerequisite support
   - Syllabus and description

5. **SubjectPrerequisite** - Prerequisite relationships
   - Mandatory/optional prerequisites
   - Minimum grade requirements
   - Prevents circular dependencies

6. **Class** - Grade level management
   - Class code, name, grade level
   - Links to academic year
   - Compulsory and optional subjects (ManyToMany)
   - Credit policy (min/max credits)
   - Optional subject limits
   - Monthly fee configuration

7. **Section** - Class divisions (A, B, C)
   - Max capacity management
   - Class teacher assignment
   - Room number tracking
   - Available seats calculation
   - Capacity warnings

8. **TeacherClassAssignment** - Teacher assignments
   - Teacher-subject-class-section-semester linking
   - Weekly periods workload tracking
   - Schedule notes
   - Prevents duplicate assignments

9. **StudentSubjectEnrollment** - Student course enrollment
   - Enrollment status tracking (enrolled, dropped, completed, failed, withdrawn)
   - Final grades and grade points
   - Prerequisite validation
   - Drop tracking with reasons

10. **ClassEnrollment** - Student class enrollment
    - Roll number generation
    - Section assignment
    - Status tracking (active, promoted, repeated, transferred, graduated, withdrawn)
    - Automatic capacity checking
    - Bulk enrollment support

#### Serializers Created

**`apps/academic/serializers.py`** (12 serializers, ~400 lines)

- **AcademicYearSerializer** - Year data with is_past flag
- **SemesterSerializer** - Semester with academic year info
- **SubjectCategorySerializer** - Category with subject count
- **SubjectListSerializer** - Minimal subject data for lists
- **SubjectDetailSerializer** - Full subject with prerequisites
- **SubjectCreateUpdateSerializer** - Create/update with prerequisites
- **SectionSerializer** - Section with enrollment stats
- **ClassListSerializer** - Class list with student counts
- **ClassDetailSerializer** - Full class with sections and subjects
- **ClassCreateUpdateSerializer** - Create/update with subject assignments
- **TeacherClassAssignmentSerializer** - Teacher assignments
- **TeacherWorkloadSerializer** - Workload summary
- **StudentSubjectEnrollmentSerializer** - Subject enrollments
- **ClassEnrollmentSerializer** - Class enrollments
- **ClassEnrollmentCreateSerializer** - Enrollment creation with validation

#### Views Created

**`apps/academic/views.py`** (7 ViewSets, ~500 lines)

- **AcademicYearViewSet**
  - CRUD operations
  - `set_current` action
  - Filtering by current/active status

- **SemesterViewSet**
  - CRUD operations
  - `set_active` action
  - `toggle_registration` action
  - Filtering by academic year

- **SubjectCategoryViewSet**
  - Full CRUD
  - Subject count annotation

- **SubjectViewSet**
  - Full CRUD
  - `add_prerequisite` action
  - `remove_prerequisite` action
  - Prerequisite validation

- **ClassViewSet**
  - Full CRUD
  - `students` action - List class students
  - `statistics` action - Class stats
  - Filtering by academic year and grade level

- **SectionViewSet**
  - Full CRUD
  - `students` action - List section students
  - Capacity filtering

- **TeacherClassAssignmentViewSet**
  - Full CRUD
  - `by_teacher` action - Filter by teacher
  - `workload` action - Teacher workload summary

- **StudentSubjectEnrollmentViewSet**
  - Full CRUD
  - `by_student` action - Student's enrollments
  - `eligible_subjects` action - Available subjects with prereq check
  - `drop` action - Drop enrolled subject

- **ClassEnrollmentViewSet**
  - Full CRUD
  - `by_class` action - Class roster
  - `promote` action - Promote student
  - `transfer` action - Transfer between sections

#### Admin Configuration

**`apps/academic/admin.py`** (~150 lines)

- **AcademicYearAdmin** - With set_as_current action
- **SemesterAdmin** - Date hierarchy, status filters
- **SubjectCategoryAdmin** - Subject count display
- **SubjectAdmin** - With prerequisite inline
- **ClassAdmin** - With section inline, subject selectors
- **SectionAdmin** - Capacity and teacher management
- **TeacherClassAssignmentAdmin** - Workload tracking
- **StudentSubjectEnrollmentAdmin** - Enrollment management
- **ClassEnrollmentAdmin** - Class roster management

#### URLs

**`apps/academic/urls.py`** - 9 viewsets, 50+ endpoints:

```
# Academic Years
GET    /api/academic/academic-years/              # List years
POST   /api/academic/academic-years/              # Create year
GET    /api/academic/academic-years/{id}/         # Get year
PATCH  /api/academic/academic-years/{id}/         # Update year
DELETE /api/academic/academic-years/{id}/         # Delete year
POST   /api/academic/academic-years/{id}/set_current/  # Set as current

# Semesters
GET    /api/academic/semesters/                   # List semesters
POST   /api/academic/semesters/                   # Create semester
GET    /api/academic/semesters/{id}/              # Get semester
PATCH  /api/academic/semesters/{id}/              # Update semester
DELETE /api/academic/semesters/{id}/              # Delete semester
POST   /api/academic/semesters/{id}/set_active/   # Set as active
POST   /api/academic/semesters/{id}/toggle_registration/  # Toggle registration

# Subject Categories
GET    /api/academic/subject-categories/          # List categories
POST   /api/academic/subject-categories/          # Create category
GET    /api/academic/subject-categories/{id}/     # Get category
PATCH  /api/academic/subject-categories/{id}/     # Update category
DELETE /api/academic/subject-categories/{id}/     # Delete category

# Subjects
GET    /api/academic/subjects/                    # List subjects
POST   /api/academic/subjects/                    # Create subject
GET    /api/academic/subjects/{id}/               # Get subject
PATCH  /api/academic/subjects/{id}/               # Update subject
DELETE /api/academic/subjects/{id}/               # Delete subject
POST   /api/academic/subjects/{id}/add_prerequisite/      # Add prerequisite
POST   /api/academic/subjects/{id}/remove_prerequisite/   # Remove prerequisite

# Classes
GET    /api/academic/classes/                     # List classes
POST   /api/academic/classes/                     # Create class
GET    /api/academic/classes/{id}/                # Get class
PATCH  /api/academic/classes/{id}/                # Update class
DELETE /api/academic/classes/{id}/                # Delete class
GET    /api/academic/classes/{id}/students/       # Get class students
GET    /api/academic/classes/{id}/statistics/     # Get class statistics

# Sections
GET    /api/academic/sections/                    # List sections
POST   /api/academic/sections/                    # Create section
GET    /api/academic/sections/{id}/               # Get section
PATCH  /api/academic/sections/{id}/               # Update section
DELETE /api/academic/sections/{id}/               # Delete section
GET    /api/academic/sections/{id}/students/      # Get section students

# Teacher Assignments
GET    /api/academic/teacher-assignments/         # List assignments
POST   /api/academic/teacher-assignments/         # Create assignment
GET    /api/academic/teacher-assignments/{id}/    # Get assignment
PATCH  /api/academic/teacher-assignments/{id}/    # Update assignment
DELETE /api/academic/teacher-assignments/{id}/    # Delete assignment
GET    /api/academic/teacher-assignments/by_teacher/?teacher_id=1  # By teacher
GET    /api/academic/teacher-assignments/workload/   # Workload summary

# Student Subject Enrollments
GET    /api/academic/student-enrollments/         # List enrollments
POST   /api/academic/student-enrollments/         # Create enrollment
GET    /api/academic/student-enrollments/{id}/    # Get enrollment
PATCH  /api/academic/student-enrollments/{id}/    # Update enrollment
DELETE /api/academic/student-enrollments/{id}/    # Delete enrollment
GET    /api/academic/student-enrollments/by_student/?student_id=1  # By student
GET    /api/academic/student-enrollments/eligible_subjects/  # Eligible subjects
POST   /api/academic/student-enrollments/{id}/drop/  # Drop subject

# Class Enrollments
GET    /api/academic/class-enrollments/           # List enrollments
POST   /api/academic/class-enrollments/           # Create enrollment
GET    /api/academic/class-enrollments/{id}/      # Get enrollment
PATCH  /api/academic/class-enrollments/{id}/      # Update enrollment
DELETE /api/academic/class-enrollments/{id}/      # Delete enrollment
GET    /api/academic/class-enrollments/by_class/?class_id=1  # By class
POST   /api/academic/class-enrollments/{id}/promote/  # Promote student
POST   /api/academic/class-enrollments/{id}/transfer/ # Transfer student
```

### 2. Frontend (Next.js)

#### API Client

**`lib/api-academic.ts`** (9 API modules, ~350 lines)

- **academicYearApi** - 6 methods
- **semesterApi** - 8 methods
- **subjectCategoryApi** - 5 methods
- **subjectApi** - 8 methods
- **classApi** - 8 methods
- **sectionApi** - 7 methods
- **teacherAssignmentApi** - 8 methods
- **studentEnrollmentApi** - 9 methods
- **classEnrollmentApi** - 9 methods

---

## What You Need To Do

### Prerequisites

- ✅ Phase 0 completed (infrastructure)
- ✅ Phase 1 completed (authentication)
- ✅ Docker running with all services

---

### Step 1: Run Database Migrations

The new academic models need to be migrated:

```bash
docker-compose exec backend python manage.py makemigrations academic
docker-compose exec backend python manage.py migrate
```

**Expected output:**
```
Migrations for 'academic':
  apps/academic/migrations/0001_initial.py
    - Create model AcademicYear
    - Create model Semester
    - Create model SubjectCategory
    - Create model Subject
    - Create model SubjectPrerequisite
    - Create model Class
    - Create model Section
    - Create model TeacherClassAssignment
    - Create model StudentSubjectEnrollment
    - Create model ClassEnrollment

Running migrations:
  Applying academic.0001_initial... OK
```

---

### Step 2: Create Initial Academic Data

#### Create an Academic Year

```bash
# Using Django shell
docker-compose exec backend python manage.py shell
```

```python
from apps.academic.models import AcademicYear, Semester, SubjectCategory, Subject
from datetime import date

# Create academic year
year = AcademicYear.objects.create(
    year_name="2024-2025",
    start_date=date(2024, 9, 1),
    end_date=date(2025, 6, 30),
    is_current=True
)

# Create semesters
first_sem = Semester.objects.create(
    academic_year=year,
    name='first',
    start_date=date(2024, 9, 1),
    end_date=date(2025, 1, 15),
    is_active=True,
    registration_open=True
)

second_sem = Semester.objects.create(
    academic_year=year,
    name='second',
    start_date=date(2025, 1, 16),
    end_date=date(2025, 6, 30),
    registration_open=False
)

# Create subject categories
math_cat = SubjectCategory.objects.create(name="Mathematics", department="Math Department")
science_cat = SubjectCategory.objects.create(name="Science", department="Science Department")
lang_cat = SubjectCategory.objects.create(name="Languages", department="Language Department")

print("Academic data created successfully!")
exit()
```

---

### Step 3: Verify Backend APIs

#### Test Academic Year API

```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"AdminPass123!"}' | jq -r '.access')

# List academic years
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/academic/academic-years/

# List semesters
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/academic/semesters/

# List subjects
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/academic/subjects/
```

---

### Step 4: Create Subjects and Classes

#### Using Django Admin

1. Go to http://localhost:8000/admin/
2. Login with superuser credentials
3. Navigate to "Academic" section
4. Create subjects:
   - Mathematics (MAT101) - 4 credits
   - Physics (PHY101) - 3 credits
   - English (ENG101) - 3 credits
5. Create a class:
   - Class 10 (2024-2025)
   - Assign subjects
   - Create sections (A, B)

#### Or via API

```bash
# Create a subject
curl -X POST http://localhost:8000/api/academic/subjects/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject_code": "MAT101",
    "subject_name": "Mathematics",
    "category": 1,
    "credit_hours": "4.00",
    "subject_type": "theory",
    "theory_full_marks": "100.00"
  }'

# Create a class
curl -X POST http://localhost:8000/api/academic/classes/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "class_code": "CLS10",
    "class_name": "Class 10",
    "grade_level": 10,
    "academic_year": 1,
    "compulsory_subject_ids": [1],
    "monthly_fee": "500.00"
  }'

# Create a section
curl -X POST http://localhost:8000/api/academic/sections/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "school_class": 1,
    "section_name": "A",
    "max_capacity": 40
  }'
```

---

### Step 5: Enroll Students

#### Create Test Students (if needed)

```bash
# Create a student user
curl -X POST http://localhost:8000/api/auth/users/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student1",
    "email": "student1@school.com",
    "password": "StudentPass123!",
    "password_confirm": "StudentPass123!",
    "first_name": "John",
    "last_name": "Doe",
    "is_student": true
  }'
```

#### Enroll Student in Class

```bash
# Enroll student in class
curl -X POST http://localhost:8000/api/academic/class-enrollments/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student": 2,
    "school_class": 1,
    "section": 1
  }'
```

#### Enroll Student in Subjects

```bash
# Enroll in subject
curl -X POST http://localhost:8000/api/academic/student-enrollments/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student": 2,
    "subject": 1,
    "semester": 1
  }'
```

---

### Step 6: Assign Teachers

#### Create Teacher User

```bash
curl -X POST http://localhost:8000/api/auth/users/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teacher1",
    "email": "teacher1@school.com",
    "password": "TeacherPass123!",
    "password_confirm": "TeacherPass123!",
    "first_name": "Jane",
    "last_name": "Smith",
    "is_teacher": true
  }'
```

#### Assign Teacher to Class

```bash
# Create assignment
curl -X POST http://localhost:8000/api/academic/teacher-assignments/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "teacher": 3,
    "subject": 1,
    "school_class": 1,
    "section": 1,
    "semester": 1,
    "weekly_periods": 5
  }'
```

---

## API Reference

### Academic Management Endpoints

#### Academic Years
```http
GET    /api/academic/academic-years/
POST   /api/academic/academic-years/
GET    /api/academic/academic-years/{id}/
PATCH  /api/academic/academic-years/{id}/
DELETE /api/academic/academic-years/{id}/
POST   /api/academic/academic-years/{id}/set_current/
```

#### Semesters
```http
GET    /api/academic/semesters/?academic_year=1&is_active=true
POST   /api/academic/semesters/
GET    /api/academic/semesters/{id}/
PATCH  /api/academic/semesters/{id}/
DELETE /api/academic/semesters/{id}/
POST   /api/academic/semesters/{id}/set_active/
POST   /api/academic/semesters/{id}/toggle_registration/
```

#### Subjects
```http
GET    /api/academic/subjects/?category=1&search=math
POST   /api/academic/subjects/
GET    /api/academic/subjects/{id}/
PATCH  /api/academic/subjects/{id}/
DELETE /api/academic/subjects/{id}/
POST   /api/academic/subjects/{id}/add_prerequisite/
POST   /api/academic/subjects/{id}/remove_prerequisite/
```

#### Classes
```http
GET    /api/academic/classes/?academic_year=1&grade_level=10
POST   /api/academic/classes/
GET    /api/academic/classes/{id}/
PATCH  /api/academic/classes/{id}/
DELETE /api/academic/classes/{id}/
GET    /api/academic/classes/{id}/students/
GET    /api/academic/classes/{id}/statistics/
```

#### Teacher Assignments
```http
GET    /api/academic/teacher-assignments/?teacher=3&semester=1
POST   /api/academic/teacher-assignments/
GET    /api/academic/teacher-assignments/workload/
```

#### Student Enrollments
```http
GET    /api/academic/student-enrollments/?student=2&semester=1
POST   /api/academic/student-enrollments/
GET    /api/academic/student-enrollments/eligible_subjects/?student_id=2&semester_id=1
POST   /api/academic/student-enrollments/{id}/drop/
```

---

## Features Implemented

✅ **Academic Structure:**
- Academic years with current year tracking
- Multiple semester types (First, Second, Summer, Quarters)
- Automatic date validation

✅ **Subject Management:**
- Subject categories with color coding
- Credit hours system
- Subject types (Theory, Practical, Hybrid)
- Prerequisite chain validation
- Marks distribution

✅ **Class & Section Management:**
- Grade levels with sections
- Capacity management
- Class teacher assignment
- Automatic roll number generation
- Compulsory and optional subjects

✅ **Enrollment System:**
- Class enrollment with capacity checking
- Subject enrollment with prerequisite validation
- Status tracking (enrolled, dropped, completed, etc.)
- Bulk enrollment support

✅ **Teacher Management:**
- Teacher-class-subject assignments
- Workload tracking (weekly periods)
- Teacher workload reports
- Schedule management

✅ **API Features:**
- 50+ REST endpoints
- Filtering, searching, ordering
- Custom actions (promote, transfer, drop)
- Statistics and reporting
- Eligibility checking

---

## Verification Checklist

Before moving to Phase 3, verify:

- [ ] Migrations applied successfully
- [ ] Can create academic year via API/Admin
- [ ] Can create semester
- [ ] Can create subject categories
- [ ] Can create subjects with prerequisites
- [ ] Can create classes with sections
- [ ] Can assign subjects to classes
- [ ] Can assign teachers to classes
- [ ] Can enroll students in classes
- [ ] Can enroll students in subjects
- [ ] Prerequisite validation works
- [ ] Section capacity limits work
- [ ] Roll numbers auto-generate
- [ ] Teacher workload API works
- [ ] Student eligible subjects API works
- [ ] Can promote/transfer students
- [ ] Can drop subjects
- [ ] Class statistics API works
- [ ] All API endpoints in Swagger docs

---

## What's Next (Phase 3)

Once Phase 2 is verified, proceed to **Phase 3: Fee Management & Finance**:

### Phase 3 Will Build:
1. Fee categories and structures
2. Student billing system
3. Payment recording and allocation
4. Scholarships and discounts
5. Financial reports
6. Receipt generation

### Skills Needed:
- Financial calculations
- Transaction management
- PDF generation
- Complex reporting
- Payment tracking

---

## Troubleshooting

### Issue: "Prerequisite not met" error

**Solution:** Enroll student in prerequisite subjects first, or mark them as completed.

### Issue: "Section is at full capacity"

**Solution:** Increase section capacity or create a new section.

### Issue: "Teacher is not a teacher"

**Solution:** Ensure user has `is_teacher=True` flag set.

### Issue: "Student is not a student"

**Solution:** Ensure user has `is_student=True` flag set.

---

**Ready to proceed?** Once you've verified all academic management features work correctly, we can begin **Phase 3: Fee Management & Finance**! 💰
