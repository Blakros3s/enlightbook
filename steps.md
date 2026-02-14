# EnlightBook - School Management System
## Step-by-Step Implementation Guide

---

## Project Overview

**EnlightBook** is a comprehensive school management system built with:
- **Backend**: Django 4.2 + Django REST Framework
- **Frontend**: Next.js 14+ with TypeScript
- **Database**: PostgreSQL + Redis
- **Background Tasks**: Celery

### Target Users
- School Administrators (Principal, Coordinator)
- Teachers (20-100)
- Students (200-3000)
- Parents (read-only access)
- Accountants (1-3)
- Drivers (5-20)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    NEXT.JS FRONTEND                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  Auth    │ │Academic  │ │ Finance  │ │Exams     │       │
│  │  Pages   │ │  Pages   │ │  Pages   │ │  Pages   │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST API
┌─────────────────────────▼───────────────────────────────────┐
│              DJANGO REST FRAMEWORK API                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  Auth    │ │ Academic │ │ Finance  │ │Examinatn │       │
│  │ Service  │ │ Service  │ │ Service  │ │ Service  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│  ┌──────────┐ ┌──────────┐                                  │
│  │Attendance│ │Communication                                    │
│  │ Service  │ │ Service  │                                  │
│  └──────────┘ └──────────┘                                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │    Redis     │  │    Celery    │
│  (Primary)   │  │  (Cache)     │  │  (Tasks)     │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## Phase 0: Project Initialization & Setup

### Step 0.1: Project Structure Setup
**Priority**: CRITICAL | **Estimated Time**: 2-3 hours

**Backend Setup:**
```bash
# Create project directory structure
mkdir -p enlightbook/backend/{apps/{users,core,academic,finance,exams,attendance,communication},common,config/settings,requirements}

# Initialize Django project
cd enlightbook/backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install django djangorestframework django-cors-headers django-filter django-redis drf-spectacular celery redis psycopg2-binary Pillow python-dotenv gunicorn whitenoise dj-database-url djangorestframework-simplejwt django-otp qrcode
```

**Frontend Setup:**
```bash
# Create Next.js project
cd enlightbook
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
cd frontend
npm install @tanstack/react-query zustand axios react-hook-form zod @hookform/resolvers date-fns lucide-react recharts socket.io-client js-cookie
```

**Files to Create:**
- [ ] `backend/config/settings/base.py` - Base Django settings
- [ ] `backend/config/settings/local.py` - Local development settings
- [ ] `backend/config/settings/production.py` - Production settings
- [ ] `backend/requirements/base.txt` - Base requirements
- [ ] `backend/requirements/local.txt` - Local requirements
- [ ] `backend/requirements/production.txt` - Production requirements
- [ ] `docker-compose.yml` - Docker development environment
- [ ] `.env.example` - Environment variables template

**Skills Reference:**
- `skills/templates/django-nextjs-project.md`
- `skills/devops/docker/containerization.md`

---

### Step 0.2: Database & Infrastructure Setup
**Priority**: CRITICAL | **Estimated Time**: 2 hours

**Backend Tasks:**
- [ ] Configure PostgreSQL database connection
- [ ] Set up Redis for caching and sessions
- [ ] Configure Celery for background tasks
- [ ] Create Docker Compose configuration
- [ ] Set up health check endpoints

**Frontend Tasks:**
- [ ] Configure environment variables
- [ ] Set up Axios with interceptors
- [ ] Configure Tailwind with custom theme
- [ ] Set up Shadcn UI components

**Verification:**
- [ ] `docker-compose up` starts all services
- [ ] Backend health check endpoint returns 200
- [ ] Frontend builds without errors
- [ ] Database migrations run successfully

---

## Phase 1: Authentication & User Management

### Step 1.1: Core Authentication System
**Priority**: CRITICAL | **Estimated Time**: 8-10 hours
**Reference**: `school planning/01-authentication-service.md`

**Backend Tasks:**
- [ ] Create custom User model with role fields
- [ ] Implement JWT authentication (SimpleJWT)
- [ ] Create login/logout API endpoints
- [ ] Add password validation (12+ chars, complexity)
- [ ] Implement token refresh mechanism
- [ ] Add security audit logging model
- [ ] Implement account lockout (5 failed attempts)

**Models:**
```python
# apps/users/models.py
class CustomUser(AbstractUser):
    # Role flags
    is_master = models.BooleanField(default=False)
    is_principal = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_accountant = models.BooleanField(default=False)
    is_driver = models.BooleanField(default=False)
    is_coordinator = models.BooleanField(default=False)
    
    # Security fields
    phone_number = models.CharField(max_length=20, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    password_changed_at = models.DateTimeField(null=True)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True)
```

**API Endpoints:**
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout  
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/password/change` - Change password
- `GET /api/auth/me` - Get current user profile

**Frontend Tasks:**
- [ ] Create authentication context
- [ ] Build login page with form validation
- [ ] Implement protected route components
- [ ] Add JWT token management (httpOnly cookies)
- [ ] Create password reset flow UI

**Verification:**
- [ ] User can login and receive JWT tokens
- [ ] Token refresh works automatically
- [ ] Account locks after 5 failed attempts
- [ ] Audit logs capture all auth attempts

---

### Step 1.2: User Management & Roles
**Priority**: HIGH | **Estimated Time**: 6-8 hours

**Backend Tasks:**
- [ ] Create User CRUD API endpoints
- [ ] Implement role assignment logic
- [ ] Create permission groups for each role
- [ ] Add user profile endpoints
- [ ] Implement password reset email flow
- [ ] Add bulk user import (CSV)

**API Endpoints:**
- `GET /api/users` - List users (admin only)
- `POST /api/users` - Create user
- `GET /api/users/:id` - Get user details
- `PUT /api/users/:id` - Update user
- `POST /api/users/:id/assign-role` - Assign role
- `POST /api/auth/password/reset` - Request password reset

**Frontend Tasks:**
- [ ] User management dashboard
- [ ] User creation/editing forms
- [ ] Role assignment interface
- [ ] User profile pages
- [ ] Password reset UI

**Verification:**
- [ ] Admin can create users with different roles
- [ ] Role-based permissions work correctly
- [ ] Password reset email sent successfully

---

### Step 1.3: Two-Factor Authentication (2FA)
**Priority**: MEDIUM | **Estimated Time**: 4-6 hours

**Backend Tasks:**
- [ ] Integrate django-otp for TOTP
- [ ] Create 2FA enable/disable endpoints
- [ ] Generate QR codes for authenticator apps
- - [ ] Implement backup codes generation
- [ ] Add 2FA verification to login flow

**API Endpoints:**
- `POST /api/auth/2fa/enable` - Enable 2FA
- `POST /api/auth/2fa/verify` - Verify 2FA code
- `POST /api/auth/2fa/disable` - Disable 2FA
- `GET /api/auth/2fa/recovery-codes` - Get backup codes

**Frontend Tasks:**
- [ ] 2FA enrollment UI with QR code
- [ ] 2FA verification modal during login
- [ ] Backup codes display/download
- [ ] Security settings page

---

## Phase 2: Academic Management

### Step 2.1: Academic Structure (Years, Semesters, Classes)
**Priority**: CRITICAL | **Estimated Time**: 8-10 hours
**Reference**: `school planning/02-academic-management-service.md`

**Backend Tasks:**
- [ ] Create AcademicYear model
- [ ] Create Semester model
- [ ] Create Class model with subjects
- [ ] Create Section model with capacity
- [ ] Add validation for date ranges
- [ ] Create auto-numbering for classes

**Models:**
```python
class AcademicYear(models.Model):
    year = models.CharField(max_length=20)  # "2024-2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

class Class(models.Model):
    class_code = models.CharField(max_length=20, unique=True)
    class_name = models.CharField(max_length=100)
    grade_level = models.IntegerField()
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

class Section(models.Model):
    school_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='sections')
    section_name = models.CharField(max_length=10)
    max_capacity = models.IntegerField(default=40)
    class_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
```

**API Endpoints:**
- `GET /api/academic/years` - List academic years
- `POST /api/academic/years` - Create academic year
- `GET /api/academic/classes` - List classes
- `POST /api/academic/classes` - Create class
- `GET /api/academic/classes/:id/sections` - List sections
- `POST /api/academic/classes/:id/sections` - Create section

**Frontend Tasks:**
- [ ] Academic year management interface
- [ ] Class creation/editing forms
- [ ] Section management with capacity display
- [ ] Academic calendar view

**Verification:**
- [ ] Can create academic year and set as current
- [ ] Classes have unique codes
- [ ] Sections show available seats correctly

---

### Step 2.2: Subject Management
**Priority**: HIGH | **Estimated Time**: 6-8 hours

**Backend Tasks:**
- [ ] Create SubjectCategory model
- [ ] Create Subject model with credit hours
- [ ] Add prerequisite system (self-referential ManyToMany)
- [ ] Create subject-class assignment
- [ ] Add subject type (theory/practical/hybrid)

**Models:**
```python
class Subject(models.Model):
    subject_code = models.CharField(max_length=20, unique=True)
    subject_name = models.CharField(max_length=100)
    category = models.ForeignKey(SubjectCategory, on_delete=models.SET_NULL, null=True)
    is_credit = models.BooleanField(default=True)
    credit_hours = models.DecimalField(max_digits=5, decimal_places=2)
    is_optional = models.BooleanField(default=False)
    prerequisites = models.ManyToManyField('self', through='SubjectPrerequisite', symmetrical=False)
```

**API Endpoints:**
- `GET /api/academic/subjects` - List subjects
- `POST /api/academic/subjects` - Create subject
- `GET /api/academic/subjects/:id/prerequisites` - Get prerequisites
- `POST /api/academic/subjects/:id/prerequisites` - Add prerequisite

**Frontend Tasks:**
- [ ] Subject catalog with search/filter
- [ ] Subject creation form
- [ ] Prerequisite tree visualization
- [ ] Subject enrollment statistics

---

### Step 2.3: Teacher & Student Management
**Priority**: CRITICAL | **Estimated Time**: 10-12 hours

**Backend Tasks:**
- [ ] Create Teacher model with qualifications
- [ ] Create Student model with parent info
- [ ] Create TeacherClassAssignment model
- [ ] Create StudentSubjectEnrollment model
- [ ] Add prerequisite validation
- [ ] Implement credit hour limit checking

**Models:**
```python
class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    qualifications = models.TextField()
    max_weekly_hours = models.IntegerField(default=35)

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    class_code = models.ForeignKey(Class, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=20)

class TeacherClassAssignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
```

**API Endpoints:**
- `GET /api/academic/teachers` - List teachers
- `POST /api/academic/teachers` - Create teacher
- `GET /api/academic/students` - List students
- `POST /api/academic/students` - Create student
- `POST /api/academic/teachers/:id/assignments` - Assign teacher
- `POST /api/academic/students/:id/enrollments` - Enroll student

**Frontend Tasks:**
- [ ] Teacher management dashboard
- [ ] Student registration form
- [ ] Teacher assignment interface
- [ ] Student enrollment portal
- [ ] Bulk import interface (CSV)

**Verification:**
- [ ] Teachers can be assigned to classes/subjects
- [ ] Students can enroll in subjects
- [ ] Prerequisites are validated
- [ ] Credit hour limits enforced

---

## Phase 3: Fee Management & Finance

### Step 3.1: Fee Structure & Billing
**Priority**: HIGH | **Estimated Time**: 10-12 hours
**Reference**: `school planning/04-fee-finance-service.md`

**Backend Tasks:**
- [ ] Create FeeCategoryName model
- [ ] Create FeeCategory model (class-specific amounts)
- [ ] Create StudentBill model with auto-numbering
- [ ] Create PaymentMethod model
- [ ] Create StudentPayment model
- [ ] Create PaymentAllocation model
- [ ] Implement bill generation workflow

**Models:**
```python
class FeeCategory(models.Model):
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)
    fee_category_name = models.ForeignKey(FeeCategoryName, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

class StudentBill(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    bill_number = models.CharField(max_length=20, unique=True)  # Auto: 2024B001
    billing_month = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[...])
    
    @property
    def outstanding_amount(self):
        return self.total_amount - self.amount_paid

class StudentPayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    payment_number = models.CharField(max_length=20, unique=True)  # Auto: 2024P001
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    verified = models.BooleanField(default=False)
```

**API Endpoints:**
- `GET /api/finance/fee-categories` - List fee categories
- `POST /api/finance/fee-categories` - Create fee category
- `GET /api/finance/bills` - List bills
- `POST /api/finance/bills` - Create bill
- `POST /api/finance/bills/bulk-generate` - Bulk generate bills
- `GET /api/finance/payments` - List payments
- `POST /api/finance/payments` - Record payment

**Frontend Tasks:**
- [ ] Fee structure management interface
- [ ] Bill generation dashboard
- [ ] Payment recording form
- [ ] Student ledger view
- [ ] Financial reports dashboard

**Verification:**
- [ ] Bills generate with correct auto-numbering
- [ ] Payment allocation works properly
- [ ] Outstanding amounts calculated correctly
- [ ] Receipts generated as PDF

---

### Step 3.2: Scholarships & Installments
**Priority**: MEDIUM | **Estimated Time**: 6-8 hours

**Backend Tasks:**
- [ ] Create Scholarship model
- [ ] Create FeeInstallmentPlan model
- [ ] Create FeeInstallment model
- [ ] Create StudentInstallmentPlan model
- [ ] Implement discount calculation logic
- [ ] Create FeeRefund model

**Frontend Tasks:**
- [ ] Scholarship creation interface
- [ ] Installment plan setup
- [ ] Refund processing workflow
- [ ] Scholarship impact dashboard

---

## Phase 4: Examination & Results

### Step 4.1: Grading System & Exam Management
**Priority**: HIGH | **Estimated Time**: 8-10 hours
**Reference**: `school planning/05-examination-service.md`

**Backend Tasks:**
- [ ] Create GradingScale model
- [ ] Create GradeRange model
- [ ] Create Exam model with publication status
- [ ] Create ExamDetail model
- [ ] Add exam scheduling (date, time, venue)
- [ ] Implement exam type (mid-term, final, unit test)

**Models:**
```python
class GradingScale(models.Model):
    name = models.CharField(max_length=100)
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)
    is_default = models.BooleanField(default=False)

class GradeRange(models.Model):
    grading_scale = models.ForeignKey(GradingScale, on_delete=models.CASCADE, related_name='ranges')
    grade = models.CharField(max_length=5)
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=4, decimal_places=2)

class Exam(models.Model):
    name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=50, choices=[...])
    is_timetable_published = models.BooleanField(default=False)
    is_result_published = models.BooleanField(default=False)
    allow_students_to_view_results = models.BooleanField(default=False)

class ExamDetail(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='details')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)
    full_marks = models.DecimalField(max_digits=6, decimal_places=2)
    theory_full_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    practical_full_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    passing_marks = models.DecimalField(max_digits=6, decimal_places=2)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
```

**API Endpoints:**
- `GET /api/grading-scales` - List grading scales
- `POST /api/grading-scales` - Create grading scale
- `GET /api/exams` - List exams
- `POST /api/exams` - Create exam
- `GET /api/exams/:id/details` - List exam details
- `POST /api/exams/:id/publish-timetable` - Publish timetable
- `POST /api/exams/:id/publish-results` - Publish results

**Frontend Tasks:**
- [ ] Grading scale configuration
- [ ] Exam creation wizard
- [ ] Timetable builder
- [ ] Exam scheduling interface

---

### Step 4.2: Mark Entry & Results
**Priority**: CRITICAL | **Estimated Time**: 10-12 hours

**Backend Tasks:**
- [ ] Create StudentResult model
- [ ] Create StudentOverallResult model
- [ ] Create ResultModificationLog model (audit trail)
- [ ] Implement automatic GPA calculation
- [ ] Add rank calculation (class and section)
- [ ] Create mark validation logic
- [ ] Implement bulk mark entry

**Models:**
```python
class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam_detail = models.ForeignKey(ExamDetail, on_delete=models.CASCADE)
    theory_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    practical_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    total_marks = models.DecimalField(max_digits=6, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5)
    gpa = models.DecimalField(max_digits=4, decimal_places=2)
    has_passed = models.BooleanField(default=False)

class StudentOverallResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    total_marks_obtained = models.DecimalField(max_digits=8, decimal_places=2)
    total_full_marks = models.DecimalField(max_digits=8, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    gpa = models.DecimalField(max_digits=4, decimal_places=2)
    class_rank = models.IntegerField(null=True)
    section_rank = models.IntegerField(null=True)
```

**API Endpoints:**
- `GET /api/exam-details/:id/results` - Get results for exam
- `POST /api/results` - Enter marks
- `PUT /api/results/:id` - Update marks
- `POST /api/results/bulk` - Bulk mark entry
- `GET /api/students/:id/results` - Get student's results
- `GET /api/results/:id/report-card` - Generate report card PDF

**Frontend Tasks:**
- [ ] Excel-like mark entry grid
- [ ] Result dashboard with analytics
- [ ] Report card viewer
- [ ] Result publication workflow

**Verification:**
- [ ] Marks validated against full marks
- [ ] GPA calculated correctly with credit hours
- [ ] Ranks auto-assigned by percentage/GPA
- [ ] Report cards generate accurate PDFs

---

## Phase 5: Attendance Management

### Step 5.1: Daily & Period Attendance
**Priority**: HIGH | **Estimated Time**: 8-10 hours
**Reference**: `school planning/06-attendance-service.md`

**Backend Tasks:**
- [ ] Create AttendancePeriod model
- [ ] Create DailyAttendance model
- [ ] Create PeriodAttendance model
- [ ] Implement bulk attendance marking
- [ ] Add attendance status (present, absent, late, excused)
- [ ] Create attendance summary calculation

**Models:**
```python
class DailyAttendance(models.Model):
    ATTENDANCE_STATUS = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused/Leave'),
        ('half_day', 'Half Day'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS)
    recorded_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    leave_application = models.ForeignKey('LeaveApplication', on_delete=models.SET_NULL, null=True)

class PeriodAttendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    period = models.ForeignKey(AttendancePeriod, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[...])
```

**API Endpoints:**
- `GET /api/attendance/daily` - List daily attendance
- `POST /api/attendance/daily` - Mark attendance
- `POST /api/attendance/daily/bulk` - Bulk mark attendance
- `GET /api/attendance/periods` - List period attendance
- `POST /api/attendance/periods` - Mark period attendance

**Frontend Tasks:**
- [ ] Attendance marking interface (grid view)
- [ ] Bulk entry with "Mark All Present"
- [ ] Period-wise attendance tracker
- [ ] Attendance calendar view

---

### Step 5.2: Leave Management
**Priority**: MEDIUM | **Estimated Time**: 6-8 hours

**Backend Tasks:**
- [ ] Create LeaveApplication model
- [ ] Implement leave approval workflow
- [ ] Add auto-mark attendance on leave approval
- [ ] Create AttendancePolicy model
- [ ] Add attendance percentage calculation

**Models:**
```python
class LeaveApplication(models.Model):
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    leave_date = models.DateField()
    days = models.IntegerField(default=1)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[...])
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='approved_leaves')
    auto_mark_attendance = models.BooleanField(default=True)

class StudentAttendanceSummary(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    month = models.DateField()
    total_days = models.IntegerField(default=0)
    present_days = models.IntegerField(default=0)
    absent_days = models.IntegerField(default=0)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2)
```

**API Endpoints:**
- `GET /api/attendance/leaves` - List leave applications
- `POST /api/attendance/leaves` - Apply for leave
- `POST /api/attendance/leaves/:id/approve` - Approve leave
- `GET /api/attendance/reports/summary` - Attendance summary
- `GET /api/attendance/students/:id/percentage` - Student's attendance %

**Frontend Tasks:**
- [ ] Leave application form
- [ ] Leave approval dashboard
- [ ] Attendance reports with filters
- [ ] Low attendance alerts

**Verification:**
- [ ] Teachers can mark attendance
- [ ] Bulk marking works correctly
- [ ] Leave approval auto-marks attendance
- [ ] Attendance percentage calculated accurately

---

## Phase 6: Communication System

### Step 6.1: Messaging & Notifications
**Priority**: MEDIUM | **Estimated Time**: 8-10 hours

**Backend Tasks:**
- [ ] Create Message model
- [ ] Create Communication model (broadcasts)
- [ ] Create DiscussionPost model
- [ ] Add file attachments support
- [ ] Implement read tracking
- [ ] Create notification system

**Models:**
```python
class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

class Communication(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    target_roles = models.JSONField()  # ['teacher', 'student']
    target_classes = models.ManyToManyField(Class, blank=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.CharField(max_length=20, choices=[('low', 'Low'), ('normal', 'Normal'), ('high', 'High')])
```

**API Endpoints:**
- `GET /api/messages` - List messages (inbox/sent)
- `POST /api/messages` - Send message
- `GET /api/communications` - List communications
- `POST /api/communications` - Create broadcast
- `GET /api/notifications` - Get notifications

**Frontend Tasks:**
- [ ] Messaging interface (inbox/sent)
- [ ] Message composer with recipient search
- [ ] Broadcast message composer
- [ ] Notification center
- [ ] Discussion forums UI

---

## Phase 7: Additional Features

### Step 7.1: Dashboards & Analytics
**Priority**: HIGH | **Estimated Time**: 8-10 hours

**Backend Tasks:**
- [ ] Create dashboard statistics endpoints
- [ ] Implement financial reports
- [ ] Add attendance analytics
- [ ] Create academic performance charts
- [ ] Build custom report builder

**Frontend Tasks:**
- [ ] Role-specific dashboards
- [ ] Widget-based layout
- [ ] Charts and graphs (Recharts)
- [ ] KPI cards
- [ ] Quick action buttons

---

### Step 7.2: Transportation Management
**Priority**: LOW | **Estimated Time**: 6-8 hours

**Backend Tasks:**
- [ ] Create Route model
- [ ] Create Bus model
- [ ] Create Driver model
- [ ] Add GPS tracking support
- [ ] Create student-bus assignments

**Frontend Tasks:**
- [ ] Route management
- [ ] Bus tracking map
- [ ] Driver assignments
- [ ] Student pickup/drop schedules

---

### Step 7.3: Events & Calendar
**Priority**: LOW | **Estimated Time**: 4-6 hours

**Backend Tasks:**
- [ ] Create Event model
- [ ] Add event types (academic, cultural, sports)
- [ ] Create calendar integration
- [ ] Add reminder notifications

**Frontend Tasks:**
- [ ] Calendar view (month/week/day)
- [ ] Event creation/editing
- [ ] Event details modal
- [ ] Calendar filters

---

## Phase 8: Testing & Deployment

### Step 8.1: Testing
**Priority**: CRITICAL | **Estimated Time**: 12-16 hours

**Backend Tasks:**
- [ ] Unit tests for models
- [ ] API integration tests
- [ ] Authentication flow tests
- [ ] Permission tests
- [ ] Load testing with Locust

**Frontend Tasks:**
- [ ] Component unit tests (Jest)
- [ ] Integration tests (React Testing Library)
- [ ] E2E tests (Cypress/Playwright)
- [ ] Visual regression tests

**Verification:**
- [ ] 80%+ test coverage
- [ ] All critical paths tested
- [ ] Performance benchmarks met

---

### Step 8.2: Deployment
**Priority**: CRITICAL | **Estimated Time**: 6-8 hours

**Backend Tasks:**
- [ ] Production settings configuration
- [ ] Docker production build
- [ ] Database migration scripts
- [ ] Static files collection
- [ ] SSL/TLS configuration

**Frontend Tasks:**
- [ ] Production build optimization
- [ ] Environment variables setup
- [ ] CDN configuration
- [ ] Image optimization

**DevOps Tasks:**
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Docker Compose production
- [ ] Nginx configuration
- [ ] Monitoring setup (Sentry)
- [ ] Backup automation

**Skills Reference:**
- `skills/devops/ci-cd/pipeline.md`
- `skills/devops/docker/containerization.md`

---

## Implementation Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 0: Setup | Week 1 | Week 1 |
| Phase 1: Authentication | Weeks 2-3 | Week 3 |
| Phase 2: Academic Management | Weeks 4-6 | Week 6 |
| Phase 3: Fee Management | Weeks 7-8 | Week 8 |
| Phase 4: Examination | Weeks 9-11 | Week 11 |
| Phase 5: Attendance | Weeks 12-13 | Week 13 |
| Phase 6: Communication | Week 14 | Week 14 |
| Phase 7: Additional Features | Weeks 15-16 | Week 16 |
| Phase 8: Testing & Deployment | Weeks 17-18 | Week 18 |

**Total Estimated Duration**: 18 weeks

---

## Quick Start Commands

```bash
# 1. Setup environment
cp .env.example .env

# 2. Start infrastructure
docker-compose up -d db redis

# 3. Run backend migrations
cd backend
python manage.py migrate
python manage.py createsuperuser

# 4. Start backend
python manage.py runserver

# 5. Start frontend (new terminal)
cd frontend
npm run dev

# 6. Access applications
# Backend API: http://localhost:8000/api/
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/docs/
```

---

## Skills Reference Quick Links

**New to the project? Start here:**
1. `skills/INDEX.md` - Complete documentation index
2. `skills/templates/django-nextjs-project.md` - Project template
3. `skills/AI_GUIDELINES.md` - Code generation guidelines

**Backend Development:**
- `skills/backend/django/architecture.md` - Django patterns
- `skills/backend/django/drf-patterns.md` - DRF best practices
- `skills/database/postgresql/schema-design.md` - Database design

**Frontend Development:**
- `skills/frontend/nextjs/architecture.md` - Next.js patterns
- `skills/api-design/rest-principles.md` - API standards

**DevOps:**
- `skills/devops/docker/containerization.md` - Docker setup
- `skills/devops/ci-cd/pipeline.md` - CI/CD pipeline

**Security & Testing:**
- `skills/security/best-practices.md` - Security guide
- `skills/testing/strategies.md` - Testing approach

---

## Success Criteria

### Technical Metrics
- [ ] 99.9% uptime
- [ ] API response time < 500ms
- [ ] Zero data loss
- [ ] < 1% error rate
- [ ] 80%+ test coverage

### User Adoption
- [ ] 90% teacher adoption in first month
- [ ] 70% parent app usage
- [ ] 95% data accuracy
- [ ] < 5 support tickets per day

### Business Impact
- [ ] 50% reduction in administrative time
- [ ] 30% improvement in parent communication
- [ ] 20% faster result publication
- [ ] 90% automated billing

---

## Next Steps

1. **Review this document** and ask questions about any unclear steps
2. **Start with Step 0.1** - Set up the project structure
3. **Follow the phases in order** - Each phase builds on the previous
4. **Reference the skills** - Use the patterns and templates provided
5. **Test at each step** - Verify before moving to the next step

Ready to begin? Let's start with **Step 0.1: Project Structure Setup**!
