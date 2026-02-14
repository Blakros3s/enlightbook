from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum

from .models import (
    AcademicYear, Semester, SubjectCategory, Subject, SubjectPrerequisite,
    Class, Section, TeacherClassAssignment, StudentSubjectEnrollment, ClassEnrollment
)
from .serializers import (
    AcademicYearSerializer, SemesterSerializer, SubjectCategorySerializer,
    SubjectListSerializer, SubjectDetailSerializer, SubjectCreateUpdateSerializer,
    SectionSerializer, ClassListSerializer, ClassDetailSerializer, ClassCreateUpdateSerializer,
    TeacherClassAssignmentSerializer, TeacherWorkloadSerializer,
    StudentSubjectEnrollmentSerializer, ClassEnrollmentSerializer, ClassEnrollmentCreateSerializer
)
from apps.users.models import CustomUser


class AcademicYearViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing academic years.
    """
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_current', 'is_active']
    search_fields = ['year_name', 'description']
    ordering_fields = ['start_date', 'year_name']
    ordering = ['-start_date']
    
    @action(detail=True, methods=['post'])
    def set_current(self, request, pk=None):
        """Set this academic year as current."""
        year = self.get_object()
        year.is_current = True
        year.save()
        return Response({'status': 'Academic year set as current'})


class SemesterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing semesters.
    """
    queryset = Semester.objects.select_related('academic_year')
    serializer_class = SemesterSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['academic_year', 'name', 'is_active', 'registration_open']
    search_fields = ['name', 'description']
    ordering = ['-academic_year__start_date', 'start_date']
    
    @action(detail=True, methods=['post'])
    def set_active(self, request, pk=None):
        """Set this semester as the active one."""
        semester = self.get_object()
        semester.is_active = True
        semester.save()
        return Response({'status': 'Semester set as active'})
    
    @action(detail=True, methods=['post'])
    def toggle_registration(self, request, pk=None):
        """Toggle registration open/closed."""
        semester = self.get_object()
        semester.registration_open = not semester.registration_open
        semester.save()
        status_text = 'opened' if semester.registration_open else 'closed'
        return Response({'status': f'Registration {status_text}'})


class SubjectCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing subject categories.
    """
    queryset = SubjectCategory.objects.annotate(subject_count=Count('subjects'))
    serializer_class = SubjectCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code', 'department']


class SubjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing subjects.
    """
    queryset = Subject.objects.select_related('category').prefetch_related('prerequisites_details')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_optional', 'subject_type', 'is_active', 'is_credit']
    search_fields = ['subject_code', 'subject_name', 'description']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SubjectCreateUpdateSerializer
        elif self.action == 'list':
            return SubjectListSerializer
        return SubjectDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by prerequisite
        has_prerequisites = self.request.query_params.get('has_prerequisites')
        if has_prerequisites is not None:
            if has_prerequisites.lower() == 'true':
                queryset = queryset.filter(prerequisites_details__is_mandatory=True).distinct()
            else:
                queryset = queryset.exclude(prerequisites_details__is_mandatory=True)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def add_prerequisite(self, request, pk=None):
        """Add a prerequisite to this subject."""
        subject = self.get_object()
        prereq_data = request.data
        
        prereq_subject_id = prereq_data.get('subject_id')
        if not prereq_subject_id:
            return Response(
                {'error': 'subject_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            prereq_subject = Subject.objects.get(id=prereq_subject_id)
        except Subject.DoesNotExist:
            return Response(
                {'error': 'Prerequisite subject not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check for circular dependency
        if prereq_subject_id == subject.id:
            return Response(
                {'error': 'A subject cannot be a prerequisite for itself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        SubjectPrerequisite.objects.create(
            subject=subject,
            prerequisite_subject=prereq_subject,
            minimum_grade=prereq_data.get('minimum_grade', ''),
            is_mandatory=prereq_data.get('is_mandatory', True)
        )
        
        return Response({'status': 'Prerequisite added successfully'})
    
    @action(detail=True, methods=['post'])
    def remove_prerequisite(self, request, pk=None):
        """Remove a prerequisite from this subject."""
        subject = self.get_object()
        prereq_subject_id = request.data.get('subject_id')
        
        if not prereq_subject_id:
            return Response(
                {'error': 'subject_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        SubjectPrerequisite.objects.filter(
            subject=subject,
            prerequisite_subject_id=prereq_subject_id
        ).delete()
        
        return Response({'status': 'Prerequisite removed successfully'})


class ClassViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing classes.
    """
    queryset = Class.objects.select_related('academic_year').prefetch_related('sections', 'compulsory_subjects', 'optional_subjects')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['academic_year', 'grade_level', 'is_active']
    search_fields = ['class_code', 'class_name']
    ordering_fields = ['grade_level', 'class_code']
    ordering = ['grade_level', 'class_code']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ClassCreateUpdateSerializer
        elif self.action == 'list':
            return ClassListSerializer
        return ClassDetailSerializer
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Get all students enrolled in this class."""
        school_class = self.get_object()
        enrollments = ClassEnrollment.objects.filter(
            school_class=school_class
        ).select_related('student', 'section')
        
        serializer = ClassEnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get class statistics."""
        school_class = self.get_object()
        
        total_students = ClassEnrollment.objects.filter(
            school_class=school_class
        ).count()
        
        section_stats = []
        for section in school_class.sections.all():
            count = ClassEnrollment.objects.filter(section=section).count()
            section_stats.append({
                'section_name': section.section_name,
                'total_students': count,
                'capacity': section.max_capacity,
                'available': section.max_capacity - count
            })
        
        return Response({
            'total_students': total_students,
            'total_sections': school_class.sections.count(),
            'compulsory_subjects': school_class.compulsory_subjects.count(),
            'optional_subjects': school_class.optional_subjects.count(),
            'section_statistics': section_stats
        })


class SectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing sections.
    """
    queryset = Section.objects.select_related('school_class', 'class_teacher')
    serializer_class = SectionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['school_class', 'class_teacher', 'is_active']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by academic year
        academic_year_id = self.request.query_params.get('academic_year')
        if academic_year_id:
            queryset = queryset.filter(school_class__academic_year_id=academic_year_id)
        
        # Filter by availability
        has_capacity = self.request.query_params.get('has_capacity')
        if has_capacity is not None:
            if has_capacity.lower() == 'true':
                queryset = queryset.filter(max_capacity__gt=models.Count('student_enrollments'))
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Get students in this section."""
        section = self.get_object()
        enrollments = ClassEnrollment.objects.filter(
            section=section
        ).select_related('student')
        
        serializer = ClassEnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)


class TeacherClassAssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing teacher assignments.
    """
    queryset = TeacherClassAssignment.objects.select_related(
        'teacher', 'subject', 'school_class', 'section', 'semester'
    )
    serializer_class = TeacherClassAssignmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['teacher', 'subject', 'school_class', 'section', 'semester', 'is_active']
    search_fields = ['teacher__first_name', 'teacher__last_name', 'subject__subject_name']
    
    @action(detail=False, methods=['get'])
    def by_teacher(self, request):
        """Get assignments grouped by teacher."""
        teacher_id = request.query_params.get('teacher_id')
        semester_id = request.query_params.get('semester_id')
        
        queryset = self.get_queryset()
        
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        if semester_id:
            queryset = queryset.filter(semester_id=semester_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def workload(self, request):
        """Get teacher workload summary."""
        semester_id = request.query_params.get('semester_id')
        
        teachers = CustomUser.objects.filter(is_teacher=True, is_active=True)
        
        workload_data = []
        for teacher in teachers:
            assignments = TeacherClassAssignment.objects.filter(
                teacher=teacher,
                is_active=True
            )
            
            if semester_id:
                assignments = assignments.filter(semester_id=semester_id)
            
            total_periods = assignments.aggregate(
                total=Sum('weekly_periods')
            )['total'] or 0
            
            total_classes = assignments.values('school_class').distinct().count()
            
            workload_data.append({
                'teacher_id': teacher.id,
                'teacher_name': teacher.get_full_name(),
                'total_periods': total_periods,
                'total_classes': total_classes,
                'assignment_count': assignments.count()
            })
        
        return Response(workload_data)


class StudentSubjectEnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing student subject enrollments.
    """
    queryset = StudentSubjectEnrollment.objects.select_related(
        'student', 'subject', 'semester'
    )
    serializer_class = StudentSubjectEnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['student', 'subject', 'semester', 'status']
    search_fields = ['student__first_name', 'student__last_name', 'subject__subject_name']
    ordering = ['-enrollment_date']
    
    @action(detail=False, methods=['get'])
    def by_student(self, request):
        """Get enrollments for a specific student."""
        student_id = request.query_params.get('student_id')
        semester_id = request.query_params.get('semester_id')
        
        if not student_id:
            return Response(
                {'error': 'student_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(student_id=student_id)
        
        if semester_id:
            queryset = queryset.filter(semester_id=semester_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def eligible_subjects(self, request):
        """Get subjects a student is eligible to enroll in."""
        student_id = request.query_params.get('student_id')
        semester_id = request.query_params.get('semester_id')
        
        if not student_id or not semester_id:
            return Response(
                {'error': 'Both student_id and semester_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            enrollment = ClassEnrollment.objects.get(
                student_id=student_id,
                status='active'
            )
            school_class = enrollment.school_class
        except ClassEnrollment.DoesNotExist:
            return Response(
                {'error': 'Student is not enrolled in any active class'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get compulsory and optional subjects
        compulsory = school_class.compulsory_subjects.filter(is_active=True)
        optional = school_class.optional_subjects.filter(is_active=True)
        
        # Check prerequisites for each subject
        eligible_compulsory = []
        for subject in compulsory:
            prereqs_met = self._check_prerequisites(student_id, subject)
            eligible_compulsory.append({
                'subject': SubjectListSerializer(subject).data,
                'prerequisites_met': prereqs_met
            })
        
        eligible_optional = []
        for subject in optional:
            prereqs_met = self._check_prerequisites(student_id, subject)
            eligible_optional.append({
                'subject': SubjectListSerializer(subject).data,
                'prerequisites_met': prereqs_met
            })
        
        return Response({
            'compulsory_subjects': eligible_compulsory,
            'optional_subjects': eligible_optional,
            'class_info': {
                'class_id': school_class.id,
                'class_name': school_class.class_name,
                'section_name': enrollment.section.section_name if enrollment.section else None
            }
        })
    
    def _check_prerequisites(self, student_id, subject):
        """Check if student has met all prerequisites for a subject."""
        prereqs = SubjectPrerequisite.objects.filter(subject=subject, is_mandatory=True)
        
        for prereq in prereqs:
            completed = StudentSubjectEnrollment.objects.filter(
                student_id=student_id,
                subject=prereq.prerequisite_subject,
                status='completed'
            ).exists()
            
            if not completed:
                return False
        
        return True
    
    @action(detail=True, methods=['post'])
    def drop(self, request, pk=None):
        """Drop an enrolled subject."""
        enrollment = self.get_object()
        
        if enrollment.status != 'enrolled':
            return Response(
                {'error': 'Can only drop enrolled subjects'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment.status = 'dropped'
        enrollment.dropped_date = timezone.now()
        enrollment.dropped_reason = request.data.get('reason', '')
        enrollment.save()
        
        return Response({'status': 'Subject dropped successfully'})


class ClassEnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing class enrollments.
    """
    queryset = ClassEnrollment.objects.select_related(
        'student', 'school_class', 'section'
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['student', 'school_class', 'section', 'status']
    search_fields = ['student__first_name', 'student__last_name', 'roll_number']
    ordering = ['-enrollment_date']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ClassEnrollmentCreateSerializer
        return ClassEnrollmentSerializer
    
    @action(detail=False, methods=['get'])
    def by_class(self, request):
        """Get enrollments for a specific class."""
        class_id = request.query_params.get('class_id')
        section_id = request.query_params.get('section_id')
        
        if not class_id:
            return Response(
                {'error': 'class_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(school_class_id=class_id)
        
        if section_id:
            queryset = queryset.filter(section_id=section_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def promote(self, request, pk=None):
        """Promote student to next grade."""
        enrollment = self.get_object()
        
        enrollment.status = 'promoted'
        enrollment.completion_date = timezone.now()
        enrollment.final_grade = request.data.get('final_grade', '')
        enrollment.save()
        
        return Response({'status': 'Student promoted successfully'})
    
    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        """Transfer student to different section or withdraw."""
        enrollment = self.get_object()
        new_section_id = request.data.get('new_section_id')
        
        if new_section_id:
            try:
                new_section = Section.objects.get(id=new_section_id)
                enrollment.section = new_section
                enrollment.save()
                return Response({'status': 'Student transferred successfully'})
            except Section.DoesNotExist:
                return Response(
                    {'error': 'Section not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            enrollment.status = 'withdrawn'
            enrollment.save()
            return Response({'status': 'Student withdrawn successfully'})


# Import for views
from django.utils import timezone
from django.db import models
