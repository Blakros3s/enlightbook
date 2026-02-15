from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random
import string

from apps.users.models import CustomUser
from apps.academic.models import (
    AcademicYear, Semester, SubjectCategory, Subject, 
    Class, Section, TeacherClassAssignment, ClassEnrollment
)
from apps.attendance.models import (
    AttendancePeriod, DailyAttendance, PeriodAttendance,
    LeaveApplication, HolidayCalendar
)
from apps.exams.models import (
    GradingScale, GradeRange, Exam, ExamDetail,
    StudentResult, StudentOverallResult, StudentExamStatus
)
from apps.finance.models import (
    FeeCategoryName, FeeStructure, PaymentMethod,
    StudentBill, BillItem, StudentPayment, PaymentAllocation, Scholarship
)


class Command(BaseCommand):
    help = 'Populate database with dummy data for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing data before populating',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Deleting existing data...'))
            self.delete_existing_data()
        
        self.stdout.write(self.style.SUCCESS('Starting data population...'))
        
        # Create data in order of dependencies
        self.create_academic_year()
        self.create_subjects()
        self.create_classes()
        self.create_users()
        self.create_teacher_assignments()
        self.enroll_students()
        self.create_attendance_periods()
        self.create_attendance()
        self.create_leave_applications()
        self.create_holidays()
        self.create_grading_scale()
        self.create_exams()
        self.create_exam_results()
        self.create_fee_categories()
        self.create_fee_structures()
        self.create_payment_methods()
        self.create_bills_and_payments()
        self.create_scholarships()
        
        self.stdout.write(self.style.SUCCESS('Data population completed successfully!'))
        self.print_summary()

    def delete_existing_data(self):
        """Delete all existing data."""
        models_to_delete = [
            PaymentAllocation, StudentPayment, BillItem, StudentBill,
            Scholarship, FeeStructure, FeeCategoryName, PaymentMethod,
            StudentOverallResult, StudentResult, StudentExamStatus,
            ExamDetail, Exam, GradeRange, GradingScale,
            DailyAttendance, PeriodAttendance, LeaveApplication,
            HolidayCalendar, AttendancePeriod, TeacherClassAssignment,
            ClassEnrollment, Section, Class, Semester,
            Subject, SubjectCategory, CustomUser,
            AcademicYear,
        ]
        
        for model in models_to_delete:
            try:
                count = model.objects.count()
                model.objects.all().delete()
                if count > 0:
                    self.stdout.write(f'  Deleted {count} {model.__name__} records')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  Could not delete {model.__name__}: {e}'))

    def create_academic_year(self):
        """Create academic years and semesters."""
        self.stdout.write('Creating academic years...')
        
        current_year = timezone.now().year
        
        # Current academic year
        ay2024, _ = AcademicYear.objects.get_or_create(
            year_name=f'{current_year}-{current_year+1}',
            defaults={
                'start_date': datetime(current_year, 4, 1).date(),
                'end_date': datetime(current_year+1, 3, 31).date(),
                'is_current': True,
                'description': f'Academic Year {current_year}-{current_year+1}'
            }
        )
        
        # Previous academic year
        ay2023, _ = AcademicYear.objects.get_or_create(
            year_name=f'{current_year-1}-{current_year}',
            defaults={
                'start_date': datetime(current_year-1, 4, 1).date(),
                'end_date': datetime(current_year, 3, 31).date(),
                'is_current': False,
                'description': f'Academic Year {current_year-1}-{current_year}'
            }
        )
        
        self.academic_year = ay2024
        
        # Create semesters
        self.stdout.write('Creating semesters...')
        self.semester1, _ = Semester.objects.get_or_create(
            academic_year=ay2024,
            name='first',
            defaults={
                'start_date': datetime(current_year, 4, 1).date(),
                'end_date': datetime(current_year, 9, 30).date(),
                'is_active': True,
                'description': 'First Semester'
            }
        )
        
        self.semester2, _ = Semester.objects.get_or_create(
            academic_year=ay2024,
            name='second',
            defaults={
                'start_date': datetime(current_year, 10, 1).date(),
                'end_date': datetime(current_year+1, 3, 31).date(),
                'is_active': False,
                'description': 'Second Semester'
            }
        )

    def create_subjects(self):
        """Create subject categories and subjects."""
        self.stdout.write('Creating subjects...')
        
        categories_data = [
            ('Mathematics', 'MATH', '#3B82F6'),
            ('Science', 'SCI', '#10B981'),
            ('Languages', 'LANG', '#F59E0B'),
            ('Social Studies', 'SOC', '#EF4444'),
            ('Arts', 'ARTS', '#8B5CF6'),
            ('Physical Education', 'PE', '#EC4899'),
            ('Computer Science', 'CS', '#6366F1'),
        ]
        
        self.subject_categories = {}
        for name, code, color in categories_data:
            cat, _ = SubjectCategory.objects.get_or_create(
                name=name,
                defaults={'code': code, 'color': color}
            )
            self.subject_categories[name] = cat
        
        # Create subjects
        subjects_data = [
            ('MAT101', 'Mathematics I', 'Mathematics', 'hybrid', 100, 50),
            ('MAT102', 'Mathematics II', 'Mathematics', 'hybrid', 100, 50),
            ('PHY101', 'Physics', 'Science', 'hybrid', 70, 30),
            ('CHE101', 'Chemistry', 'Science', 'hybrid', 70, 30),
            ('BIO101', 'Biology', 'Science', 'hybrid', 70, 30),
            ('ENG101', 'English', 'Languages', 'theory', 100, 0),
            ('HIN101', 'Hindi', 'Languages', 'theory', 100, 0),
            ('HIS101', 'History', 'Social Studies', 'theory', 100, 0),
            ('GEO101', 'Geography', 'Social Studies', 'theory', 100, 0),
            ('CIV101', 'Civics', 'Social Studies', 'theory', 100, 0),
            ('ART101', 'Art & Craft', 'Arts', 'practical', 0, 100),
            ('MUS101', 'Music', 'Arts', 'practical', 0, 100),
            ('PE101', 'Physical Education', 'Physical Education', 'practical', 0, 100),
            ('CS101', 'Computer Science', 'Computer Science', 'hybrid', 50, 50),
        ]
        
        self.subjects = {}
        for code, name, cat_name, subj_type, theory, practical in subjects_data:
            subject, _ = Subject.objects.get_or_create(
                subject_code=code,
                defaults={
                    'subject_name': name,
                    'category': self.subject_categories[cat_name],
                    'subject_type': subj_type,
                    'theory_full_marks': theory,
                    'practical_full_marks': practical,
                    'credit_hours': Decimal('3.00') if subj_type != 'practical' else Decimal('2.00')
                }
            )
            self.subjects[code] = subject

    def create_classes(self):
        """Create classes and sections."""
        self.stdout.write('Creating classes...')
        
        classes_data = [
            (1, 'Grade 1', 1500),
            (2, 'Grade 2', 1500),
            (3, 'Grade 3', 1500),
            (4, 'Grade 4', 1600),
            (5, 'Grade 5', 1600),
            (6, 'Grade 6', 1700),
            (7, 'Grade 7', 1700),
            (8, 'Grade 8', 1800),
            (9, 'Grade 9', 2000),
            (10, 'Grade 10', 2200),
            (11, 'Grade 11', 2500),
            (12, 'Grade 12', 2500),
        ]
        
        self.classes = {}
        for grade, name, fee in classes_data:
            class_obj, _ = Class.objects.get_or_create(
                class_code=f'CLS{grade:02d}',
                defaults={
                    'class_name': name,
                    'grade_level': grade,
                    'academic_year': self.academic_year,
                    'monthly_fee': fee,
                    'min_credits': Decimal('18.00'),
                    'max_credits': Decimal('24.00'),
                }
            )
            
            # Assign compulsory subjects (first 6 subjects)
            compulsory = list(self.subjects.values())[:6]
            class_obj.compulsory_subjects.set(compulsory)
            
            # Assign optional subjects (remaining)
            optional = list(self.subjects.values())[6:]
            class_obj.optional_subjects.set(optional)
            
            self.classes[grade] = class_obj
            
            # Create sections A and B for each class
            for section_name in ['A', 'B']:
                Section.objects.get_or_create(
                    school_class=class_obj,
                    section_name=section_name,
                    defaults={
                        'max_capacity': 40,
                        'room_number': f'{grade}0{section_name}'
                    }
                )

    def create_users(self):
        """Create admin, teachers, and students."""
        self.stdout.write('Creating users...')
        
        # Create Master Admin
        self.admin, _ = CustomUser.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@enlightbook.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_master': True,
                'is_active': True,
            }
        )
        self.admin.set_password('admin123')
        self.admin.save()
        
        # Create Principal
        self.principal, _ = CustomUser.objects.get_or_create(
            username='principal',
            defaults={
                'email': 'principal@enlightbook.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'is_principal': True,
                'is_active': True,
            }
        )
        self.principal.set_password('principal123')
        self.principal.save()
        
        # Create Coordinator
        self.coordinator, _ = CustomUser.objects.get_or_create(
            username='coordinator',
            defaults={
                'email': 'coordinator@enlightbook.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'is_coordinator': True,
                'is_active': True,
            }
        )
        self.coordinator.set_password('coordinator123')
        self.coordinator.save()
        
        # Create Accountant
        self.accountant, _ = CustomUser.objects.get_or_create(
            username='accountant',
            defaults={
                'email': 'accountant@enlightbook.com',
                'first_name': 'Michael',
                'last_name': 'Brown',
                'is_accountant': True,
                'is_active': True,
            }
        )
        self.accountant.set_password('accountant123')
        self.accountant.save()
        
        # Create teachers
        self.stdout.write('Creating teachers...')
        self.teachers = []
        teacher_names = [
            ('Alice', 'Williams', 'alice.williams'),
            ('Robert', 'Davis', 'robert.davis'),
            ('Emma', 'Miller', 'emma.miller'),
            ('James', 'Wilson', 'james.wilson'),
            ('Olivia', 'Moore', 'olivia.moore'),
            ('William', 'Taylor', 'william.taylor'),
            ('Sophia', 'Anderson', 'sophia.anderson'),
            ('Benjamin', 'Thomas', 'benjamin.thomas'),
            ('Mia', 'Jackson', 'mia.jackson'),
            ('Lucas', 'White', 'lucas.white'),
            ('Charlotte', 'Harris', 'charlotte.harris'),
            ('Henry', 'Martin', 'henry.martin'),
            ('Amelia', 'Thompson', 'amelia.thompson'),
            ('Alexander', 'Garcia', 'alexander.garcia'),
            ('Evelyn', 'Martinez', 'evelyn.martinez'),
        ]
        
        for first, last, username in teacher_names:
            teacher, _ = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@enlightbook.com',
                    'first_name': first,
                    'last_name': last,
                    'is_teacher': True,
                    'is_active': True,
                }
            )
            teacher.set_password('teacher123')
            teacher.save()
            self.teachers.append(teacher)
        
        # Create students
        self.stdout.write('Creating students...')
        self.students = []
        first_names = ['Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Oliver', 'Isabella', 'Elijah',
                      'Sophia', 'Lucas', 'Mia', 'Mason', 'Charlotte', 'Ethan', 'Amelia', 'Logan',
                      'Harper', 'Aiden', 'Evelyn', 'Jackson', 'Abigail', 'Caden', 'Emily', 'Grayson',
                      'Elizabeth', 'Michael', 'Sofia', 'Benjamin', 'Avery', 'Carter', 'Ella', 'Daniel',
                      'Madison', 'Matthew', 'Scarlett', 'Jayden', 'Victoria', 'Luke', 'Chloe', 'William']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                     'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
                     'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White']
        
        student_count = 0
        for grade in range(1, 13):
            class_obj = self.classes[grade]
            sections = list(class_obj.sections.all())
            
            # Create 30-40 students per grade
            num_students = random.randint(30, 40)
            for i in range(num_students):
                student_count += 1
                first = random.choice(first_names)
                last = random.choice(last_names)
                username = f'student{student_count:04d}'
                
                student, _ = CustomUser.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': f'{username}@enlightbook.com',
                        'first_name': first,
                        'last_name': last,
                        'is_student': True,
                        'is_active': True,
                        'phone_number': f'+91{random.randint(7000000000, 9999999999)}',
                    }
                )
                student.set_password('student123')
                student.save()
                self.students.append(student)

    def create_teacher_assignments(self):
        """Assign teachers to classes and subjects."""
        self.stdout.write('Creating teacher assignments...')
        
        subjects_list = list(self.subjects.values())
        
        for teacher in self.teachers:
            # Assign 2-4 subjects to each teacher
            num_assignments = random.randint(2, 4)
            for _ in range(num_assignments):
                subject = random.choice(subjects_list)
                class_obj = random.choice(list(self.classes.values()))
                section = random.choice(list(class_obj.sections.all()))
                
                # Set section as class teacher if not already assigned
                if not section.class_teacher:
                    section.class_teacher = teacher
                    section.save()
                
                TeacherClassAssignment.objects.get_or_create(
                    teacher=teacher,
                    subject=subject,
                    school_class=class_obj,
                    section=section,
                    semester=self.semester1,
                    defaults={
                        'weekly_periods': random.randint(4, 8),
                        'is_active': True
                    }
                )

    def enroll_students(self):
        """Enroll students in classes and sections."""
        self.stdout.write('Enrolling students...')
        
        student_index = 0
        for grade in range(1, 13):
            class_obj = self.classes[grade]
            sections = list(class_obj.sections.all())
            
            # Get students for this grade
            students_in_grade = [s for s in self.students[student_index:student_index + 40]]
            student_index += len(students_in_grade)
            
            # Distribute students across sections
            for i, student in enumerate(students_in_grade):
                section = sections[i % len(sections)]
                
                ClassEnrollment.objects.get_or_create(
                    student=student,
                    school_class=class_obj,
                    section=section,
                    defaults={
                        'status': 'active',
                        'roll_number': str(i + 1)
                    }
                )

    def create_attendance_periods(self):
        """Create attendance periods."""
        self.stdout.write('Creating attendance periods...')
        
        periods_data = [
            ('Period 1', '08:00', '08:45', 1),
            ('Period 2', '08:45', '09:30', 2),
            ('Period 3', '09:30', '10:15', 3),
            ('Break', '10:15', '10:30', 4),
            ('Period 4', '10:30', '11:15', 5),
            ('Period 5', '11:15', '12:00', 6),
            ('Lunch', '12:00', '12:30', 7),
            ('Period 6', '12:30', '13:15', 8),
            ('Period 7', '13:15', '14:00', 9),
            ('Period 8', '14:00', '14:45', 10),
        ]
        
        for name, start, end, order in periods_data:
            AttendancePeriod.objects.get_or_create(
                name=name,
                defaults={
                    'start_time': datetime.strptime(start, '%H:%M').time(),
                    'end_time': datetime.strptime(end, '%H:%M').time(),
                    'order': order,
                    'is_active': name not in ['Break', 'Lunch']
                }
            )

    def create_attendance(self):
        """Create attendance records for students."""
        self.stdout.write('Creating attendance records...')
        
        periods = list(AttendancePeriod.objects.filter(is_active=True))
        subjects_list = list(self.subjects.values())
        
        # Create attendance for last 30 days
        for day_offset in range(30):
            date = (timezone.now() - timedelta(days=day_offset)).date()
            
            # Skip weekends
            if date.weekday() >= 5:
                continue
            
            for student in self.students[:100]:  # Limit to first 100 students for performance
                # Daily attendance
                status = random.choices(
                    ['present', 'absent', 'late', 'excused'],
                    weights=[85, 10, 3, 2]
                )[0]
                
                DailyAttendance.objects.get_or_create(
                    student=student,
                    date=date,
                    defaults={
                        'status': status,
                        'recorded_by': random.choice(self.teachers) if self.teachers else None
                    }
                )
                
                # Period attendance for 2-3 periods
                if status == 'present':
                    for period in random.sample(periods, min(3, len(periods))):
                        class_enrollment = student.class_enrollments.filter(status='active').first()
                        if class_enrollment:
                            PeriodAttendance.objects.get_or_create(
                                student=student,
                                date=date,
                                period=period,
                                defaults={
                                    'subject': random.choice(subjects_list),
                                    'school_class': class_enrollment.school_class,
                                    'section': class_enrollment.section,
                                    'status': random.choice(['present', 'present', 'present', 'late']),
                                    'recorded_by': random.choice(self.teachers) if self.teachers else None
                                }
                            )

    def create_leave_applications(self):
        """Create leave applications."""
        self.stdout.write('Creating leave applications...')
        
        leave_types = ['sick', 'personal', 'family', 'medical', 'sports']
        
        for _ in range(20):
            student = random.choice(self.students[:50])
            start_date = timezone.now().date() - timedelta(days=random.randint(1, 30))
            days = random.randint(1, 5)
            
            LeaveApplication.objects.get_or_create(
                applicant=student,
                start_date=start_date,
                defaults={
                    'leave_type': random.choice(leave_types),
                    'end_date': start_date + timedelta(days=days - 1),
                    'days': days,
                    'reason': f'{random.choice(leave_types).title()} leave for personal reasons',
                    'status': random.choice(['pending', 'approved', 'approved', 'rejected']),
                    'approved_by': self.principal if random.choice([True, False]) else None
                }
            )

    def create_holidays(self):
        """Create holiday calendar."""
        self.stdout.write('Creating holidays...')
        
        holidays_data = [
            ('New Year', timezone.now().replace(month=1, day=1).date(), 'national'),
            ('Republic Day', timezone.now().replace(month=1, day=26).date(), 'national'),
            ('Independence Day', timezone.now().replace(month=8, day=15).date(), 'national'),
            ('Gandhi Jayanti', timezone.now().replace(month=10, day=2).date(), 'national'),
            ('Christmas', timezone.now().replace(month=12, day=25).date(), 'national'),
            ('Summer Vacation', timezone.now().replace(month=5, day=15).date(), 'vacation'),
            ('Winter Break', timezone.now().replace(month=12, day=24).date(), 'vacation'),
        ]
        
        for name, date, holiday_type in holidays_data:
            HolidayCalendar.objects.get_or_create(
                name=name,
                date=date,
                defaults={
                    'holiday_type': holiday_type,
                    'description': f'{name} - School Holiday'
                }
            )

    def create_grading_scale(self):
        """Create grading scales."""
        self.stdout.write('Creating grading scales...')
        
        scale, _ = GradingScale.objects.get_or_create(
            name='Standard Scale',
            defaults={
                'is_default': True,
                'description': 'Standard grading scale'
            }
        )
        
        grade_ranges = [
            ('A+', 90, 100, 10.0, 'Outstanding'),
            ('A', 80, 89.99, 9.0, 'Excellent'),
            ('B+', 70, 79.99, 8.0, 'Very Good'),
            ('B', 60, 69.99, 7.0, 'Good'),
            ('C+', 50, 59.99, 6.0, 'Satisfactory'),
            ('C', 40, 49.99, 5.0, 'Pass'),
            ('F', 0, 39.99, 0.0, 'Fail'),
        ]
        
        for grade, min_pct, max_pct, points, desc in grade_ranges:
            GradeRange.objects.get_or_create(
                grading_scale=scale,
                grade=grade,
                defaults={
                    'min_percentage': min_pct,
                    'max_percentage': max_pct,
                    'grade_point': points,
                    'description': desc
                }
            )

    def create_exams(self):
        """Create exams and exam details."""
        self.stdout.write('Creating exams...')
        
        exam_types = [
            ('Mid-Term Examination 2024', 'mid_term'),
            ('Final Examination 2024', 'final'),
            ('Unit Test 1', 'unit_test'),
            ('Unit Test 2', 'unit_test'),
        ]
        
        self.exams = []
        for name, exam_type in exam_types:
            exam, _ = Exam.objects.get_or_create(
                name=name,
                academic_year=self.academic_year,
                defaults={
                    'exam_type': exam_type,
                    'semester': self.semester1,
                    'weightage_percentage': Decimal('100.00'),
                    'max_marks': Decimal('100.00'),
                    'passing_percentage': Decimal('40.00'),
                    'start_date': timezone.now().date() - timedelta(days=random.randint(30, 60)),
                    'end_date': timezone.now().date() - timedelta(days=random.randint(1, 29)),
                    'is_timetable_published': True,
                    'is_result_published': True,
                    'allow_students_to_view_results': True,
                    'created_by': self.admin
                }
            )
            self.exams.append(exam)
            
            # Create exam details for each class and subject
            for class_obj in self.classes.values():
                sections = list(class_obj.sections.all())
                compulsory = list(class_obj.compulsory_subjects.all())[:4]  # Limit to 4 subjects
                
                for subject in compulsory:
                    for section in sections[:1]:  # Just first section
                        exam_date = exam.start_date + timedelta(days=random.randint(0, 10))
                        
                        ExamDetail.objects.get_or_create(
                            exam=exam,
                            subject=subject,
                            school_class=class_obj,
                            section=section,
                            defaults={
                                'full_marks': subject.total_full_marks,
                                'theory_full_marks': subject.theory_full_marks if subject.theory_full_marks else None,
                                'practical_full_marks': subject.practical_full_marks if subject.practical_full_marks else None,
                                'passing_marks': subject.total_full_marks * Decimal('0.4'),
                                'exam_date': exam_date,
                                'start_time': datetime.strptime('09:00', '%H:%M').time(),
                                'end_time': datetime.strptime('12:00', '%H:%M').time(),
                                'duration_minutes': 180,
                                'is_marks_entered': True,
                                'marks_entered_by': random.choice(self.teachers) if self.teachers else None
                            }
                        )

    def create_exam_results(self):
        """Create exam results for students."""
        self.stdout.write('Creating exam results...')
        
        for exam in self.exams:
            for exam_detail in exam.details.all():
                # Get enrolled students
                enrollments = ClassEnrollment.objects.filter(
                    school_class=exam_detail.school_class,
                    section=exam_detail.section,
                    status='active'
                ).select_related('student')
                
                for enrollment in enrollments[:30]:  # Limit to 30 students per exam
                    student = enrollment.student
                    
                    # Generate random marks (use Decimal) - ensure they don't exceed max marks
                    theory_marks = None
                    practical_marks = None
                    
                    if exam_detail.subject.subject_type in ['theory', 'hybrid']:
                        theory_max = float(exam_detail.theory_full_marks or exam_detail.full_marks)
                        theory_marks = Decimal(str(round(random.uniform(theory_max * 0.35, theory_max * 0.95), 2)))
                    
                    if exam_detail.subject.subject_type in ['practical', 'hybrid']:
                        practical_max = float(exam_detail.practical_full_marks or exam_detail.full_marks)
                        practical_marks = Decimal(str(round(random.uniform(practical_max * 0.35, practical_max * 0.95), 2)))
                    
                    # Create result
                    result, _ = StudentResult.objects.get_or_create(
                        student=student,
                        exam_detail=exam_detail,
                        defaults={
                            'theory_marks': theory_marks,
                            'practical_marks': practical_marks,
                            'entered_by': random.choice(self.teachers) if self.teachers else None,
                            'entered_at': timezone.now()
                        }
                    )

    def create_fee_categories(self):
        """Create fee categories."""
        self.stdout.write('Creating fee categories...')
        
        categories = [
            ('Tuition Fee', True, True),
            ('Admission Fee', True, False),
            ('Library Fee', True, True),
            ('Laboratory Fee', True, True),
            ('Sports Fee', True, True),
            ('Computer Fee', True, True),
            ('Transportation Fee', False, True),
            ('Examination Fee', True, False),
            ('Development Fee', True, False),
        ]
        
        self.fee_categories = {}
        for name, mandatory, recurring in categories:
            cat, _ = FeeCategoryName.objects.get_or_create(
                name=name,
                defaults={
                    'is_mandatory': mandatory,
                    'is_recurring': recurring
                }
            )
            self.fee_categories[name] = cat

    def create_fee_structures(self):
        """Create fee structures for each class."""
        self.stdout.write('Creating fee structures...')
        
        for class_obj in self.classes.values():
            # Tuition fee varies by class
            tuition_amount = class_obj.monthly_fee
            
            FeeStructure.objects.get_or_create(
                school_class=class_obj,
                fee_category_name=self.fee_categories['Tuition Fee'],
                academic_year=self.academic_year,
                defaults={'amount': tuition_amount}
            )
            
            # Other fees
            other_fees = [
                ('Library Fee', 100),
                ('Laboratory Fee', 150),
                ('Sports Fee', 100),
                ('Computer Fee', 200),
                ('Examination Fee', 500),
            ]
            
            for fee_name, amount in other_fees:
                FeeStructure.objects.get_or_create(
                    school_class=class_obj,
                    fee_category_name=self.fee_categories[fee_name],
                    academic_year=self.academic_year,
                    defaults={'amount': amount}
                )

    def create_payment_methods(self):
        """Create payment methods."""
        self.stdout.write('Creating payment methods...')
        
        methods = [
            ('Cash', 'CASH', False),
            ('Credit Card', 'CARD', True),
            ('Bank Transfer', 'BANK', True),
            ('Check', 'CHECK', True),
            ('Online Payment', 'ONLINE', True),
        ]
        
        self.payment_methods = {}
        for name, code, requires_ref in methods:
            method, _ = PaymentMethod.objects.get_or_create(
                name=name,
                defaults={
                    'code': code,
                    'requires_reference': requires_ref
                }
            )
            self.payment_methods[name] = method

    def create_bills_and_payments(self):
        """Create bills and payments for students."""
        self.stdout.write('Creating bills and payments...')
        
        # Create bills for first 50 students
        for student in self.students[:50]:
            enrollment = student.class_enrollments.filter(status='active').first()
            if not enrollment:
                continue
            
            # Create 1-3 bills per student
            for month_offset in range(random.randint(1, 3)):
                bill_date = timezone.now() - timedelta(days=30 * month_offset)
                due_date = bill_date + timedelta(days=15)
                
                bill, _ = StudentBill.objects.get_or_create(
                    student=student,
                    billing_month=bill_date.replace(day=1).date(),
                    defaults={
                        'due_date': due_date.date(),
                        'academic_year': self.academic_year,
                        'subtotal': enrollment.school_class.monthly_fee + 500,
                        'total_amount': enrollment.school_class.monthly_fee + 500,
                        'status': random.choice(['fully_paid', 'fully_paid', 'partially_paid', 'overdue']),
                        'issued_by': self.accountant
                    }
                )
                
                # Add bill items
                fee_structures = FeeStructure.objects.filter(
                    school_class=enrollment.school_class,
                    academic_year=self.academic_year
                )
                
                for fs in fee_structures[:4]:  # Limit items
                    BillItem.objects.get_or_create(
                        bill=bill,
                        fee_structure=fs,
                        defaults={
                            'description': fs.fee_category_name.name,
                            'amount': fs.amount
                        }
                    )
                
                # Create payment for paid bills
                if bill.status in ['fully_paid', 'partially_paid']:
                    payment_amount = bill.total_amount if bill.status == 'fully_paid' else bill.total_amount * Decimal('0.5')
                    
                    payment, _ = StudentPayment.objects.get_or_create(
                        student=student,
                        payment_date=bill_date.date(),
                        defaults={
                            'amount_paid': payment_amount,
                            'payment_method': random.choice(list(self.payment_methods.values())),
                            'status': 'verified',
                            'verified_by': self.accountant,
                            'verified_at': timezone.now(),
                            'created_by': self.accountant
                        }
                    )
                    
                    # Allocate payment to bill
                    PaymentAllocation.objects.get_or_create(
                        payment=payment,
                        bill=bill,
                        defaults={'amount_applied': payment_amount}
                    )

    def create_scholarships(self):
        """Create scholarships for students."""
        self.stdout.write('Creating scholarships...')
        
        scholarship_types = ['Merit', 'Need-based', 'Sports', 'Cultural']
        
        for _ in range(10):
            student = random.choice(self.students[:30])
            
            Scholarship.objects.get_or_create(
                student=student,
                scholarship_name=f'{random.choice(scholarship_types)} Scholarship',
                defaults={
                    'scholarship_type': random.choice(scholarship_types),
                    'discount_type': random.choice(['percentage', 'fixed']),
                    'discount_value': random.choice([25, 50, 100]),
                    'applicable_to_all_fees': True,
                    'valid_from': timezone.now().date(),
                    'valid_until': timezone.now().date() + timedelta(days=365),
                    'academic_year': self.academic_year,
                    'approved_by': self.principal,
                    'approved_at': timezone.now()
                }
            )

    def print_summary(self):
        """Print summary of created data."""
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('DATA POPULATION SUMMARY'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        summary = {
            'Academic Years': AcademicYear.objects.count(),
            'Semesters': Semester.objects.count(),
            'Subjects': Subject.objects.count(),
            'Classes': Class.objects.count(),
            'Sections': Section.objects.count(),
            'Users - Total': CustomUser.objects.count(),
            '  - Admins': CustomUser.objects.filter(is_master=True).count(),
            '  - Principals': CustomUser.objects.filter(is_principal=True).count(),
            '  - Teachers': CustomUser.objects.filter(is_teacher=True).count(),
            '  - Students': CustomUser.objects.filter(is_student=True).count(),
            'Teacher Assignments': TeacherClassAssignment.objects.count(),
            'Class Enrollments': ClassEnrollment.objects.count(),
            'Attendance Records': DailyAttendance.objects.count(),
            'Leave Applications': LeaveApplication.objects.count(),
            'Exams': Exam.objects.count(),
            'Exam Results': StudentResult.objects.count(),
            'Fee Structures': FeeStructure.objects.count(),
            'Bills': StudentBill.objects.count(),
            'Payments': StudentPayment.objects.count(),
            'Scholarships': Scholarship.objects.count(),
        }
        
        for item, count in summary.items():
            self.stdout.write(f'  {item:<25}: {count:>5}')
        
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('\nLogin Credentials:'))
        self.stdout.write(self.style.SUCCESS('  Admin:      username=admin, password=admin123'))
        self.stdout.write(self.style.SUCCESS('  Principal:  username=principal, password=principal123'))
        self.stdout.write(self.style.SUCCESS('  Teacher:    username=alice.williams, password=teacher123'))
        self.stdout.write(self.style.SUCCESS('  Student:    username=student0001, password=student123'))
        self.stdout.write(self.style.SUCCESS('='*60))
