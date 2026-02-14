from rest_framework import serializers
from django.db import transaction

from .models import (
    AcademicYear, Semester, SubjectCategory, Subject, SubjectPrerequisite,
    Class, Section, TeacherClassAssignment, StudentSubjectEnrollment, ClassEnrollment
)
from apps.users.models import CustomUser


class AcademicYearSerializer(serializers.ModelSerializer):
    """
    Serializer for AcademicYear model.
    """
    is_past = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AcademicYear
        fields = [
            'id', 'year_name', 'start_date', 'end_date', 'is_current',
            'is_active', 'is_past', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_is_past(self, obj):
        from django.utils import timezone
        return obj.end_date < timezone.now().date()


class SemesterSerializer(serializers.ModelSerializer):
    """
    Serializer for Semester model.
    """
    academic_year_name = serializers.CharField(source='academic_year.year_name', read_only=True)
    
    class Meta:
        model = Semester
        fields = [
            'id', 'academic_year', 'academic_year_name', 'name', 'get_name_display',
            'start_date', 'end_date', 'is_active', 'registration_open',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SubjectCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for SubjectCategory model.
    """
    subject_count = serializers.IntegerField(source='subjects.count', read_only=True)
    
    class Meta:
        model = SubjectCategory
        fields = [
            'id', 'name', 'code', 'department', 'description', 'color',
            'is_active', 'subject_count', 'created_at'
        ]
        read_only_fields = ['created_at']


class SubjectListSerializer(serializers.ModelSerializer):
    """
    List serializer for Subject (minimal data).
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Subject
        fields = [
            'id', 'subject_code', 'subject_name', 'category', 'category_name',
            'credit_hours', 'is_optional', 'subject_type', 'is_active'
        ]


class SubjectDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Subject.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    prerequisites = serializers.SerializerMethodField()
    total_full_marks = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    
    class Meta:
        model = Subject
        fields = [
            'id', 'subject_code', 'subject_name', 'category', 'category_name',
            'is_credit', 'credit_hours', 'is_optional', 'subject_type',
            'theory_full_marks', 'practical_full_marks', 'total_full_marks',
            'passing_percentage', 'description', 'syllabus',
            'prerequisites', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_prerequisites(self, obj):
        """Get list of prerequisite subjects."""
        prereqs = obj.prerequisites_details.filter(is_mandatory=True)
        return [
            {
                'id': p.prerequisite_subject.id,
                'subject_code': p.prerequisite_subject.subject_code,
                'subject_name': p.prerequisite_subject.subject_name,
                'minimum_grade': p.minimum_grade
            }
            for p in prereqs
        ]


class SubjectCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating subjects.
    """
    prerequisites = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Subject
        fields = [
            'id', 'subject_code', 'subject_name', 'category',
            'is_credit', 'credit_hours', 'is_optional', 'subject_type',
            'theory_full_marks', 'practical_full_marks', 'passing_percentage',
            'description', 'syllabus', 'prerequisites', 'is_active'
        ]
    
    @transaction.atomic
    def create(self, validated_data):
        prerequisites_data = validated_data.pop('prerequisites', [])
        subject = super().create(validated_data)
        self._save_prerequisites(subject, prerequisites_data)
        return subject
    
    @transaction.atomic
    def update(self, instance, validated_data):
        prerequisites_data = validated_data.pop('prerequisites', [])
        subject = super().update(instance, validated_data)
        self._save_prerequisites(subject, prerequisites_data)
        return subject
    
    def _save_prerequisites(self, subject, prerequisites_data):
        """Save prerequisite relationships."""
        if prerequisites_data is not None:
            # Clear existing prerequisites
            SubjectPrerequisite.objects.filter(subject=subject).delete()
            
            # Add new prerequisites
            for prereq_data in prerequisites_data:
                prereq_id = prereq_data.get('subject_id') or prereq_data.get('id')
                if prereq_id:
                    SubjectPrerequisite.objects.create(
                        subject=subject,
                        prerequisite_subject_id=prereq_id,
                        minimum_grade=prereq_data.get('minimum_grade', ''),
                        is_mandatory=prereq_data.get('is_mandatory', True)
                    )


class SectionSerializer(serializers.ModelSerializer):
    """
    Serializer for Section model.
    """
    class_teacher_name = serializers.CharField(source='class_teacher.get_full_name', read_only=True)
    current_enrollment = serializers.IntegerField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Section
        fields = [
            'id', 'school_class', 'section_name', 'max_capacity',
            'class_teacher', 'class_teacher_name', 'room_number',
            'current_enrollment', 'available_seats', 'is_full',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ClassListSerializer(serializers.ModelSerializer):
    """
    List serializer for Class.
    """
    academic_year_name = serializers.CharField(source='academic_year.year_name', read_only=True)
    section_count = serializers.IntegerField(source='sections.count', read_only=True)
    total_students = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = [
            'id', 'class_code', 'class_name', 'grade_level',
            'academic_year', 'academic_year_name', 'section_count',
            'total_students', 'monthly_fee', 'is_active'
        ]
    
    def get_total_students(self, obj):
        return ClassEnrollment.objects.filter(
            school_class=obj,
            status='active'
        ).count()


class ClassDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Class.
    """
    academic_year_name = serializers.CharField(source='academic_year.year_name', read_only=True)
    sections = SectionSerializer(many=True, read_only=True)
    compulsory_subjects = SubjectListSerializer(many=True, read_only=True)
    optional_subjects = SubjectListSerializer(many=True, read_only=True)
    total_students = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = [
            'id', 'class_code', 'class_name', 'grade_level',
            'academic_year', 'academic_year_name',
            'compulsory_subjects', 'optional_subjects',
            'min_credits', 'max_credits', 'min_optional_subjects', 'max_optional_subjects',
            'monthly_fee', 'sections', 'total_students',
            'description', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_students(self, obj):
        return ClassEnrollment.objects.filter(
            school_class=obj,
            status='active'
        ).count()


class ClassCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating classes.
    """
    compulsory_subject_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    optional_subject_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Class
        fields = [
            'id', 'class_code', 'class_name', 'grade_level',
            'academic_year', 'compulsory_subject_ids', 'optional_subject_ids',
            'min_credits', 'max_credits', 'min_optional_subjects', 'max_optional_subjects',
            'monthly_fee', 'description', 'is_active'
        ]
    
    @transaction.atomic
    def create(self, validated_data):
        compulsory_ids = validated_data.pop('compulsory_subject_ids', [])
        optional_ids = validated_data.pop('optional_subject_ids', [])
        
        class_obj = super().create(validated_data)
        
        # Set subjects
        if compulsory_ids:
            class_obj.compulsory_subjects.set(compulsory_ids)
        if optional_ids:
            class_obj.optional_subjects.set(optional_ids)
        
        return class_obj
    
    @transaction.atomic
    def update(self, instance, validated_data):
        compulsory_ids = validated_data.pop('compulsory_subject_ids', None)
        optional_ids = validated_data.pop('optional_subject_ids', None)
        
        class_obj = super().update(instance, validated_data)
        
        # Update subjects if provided
        if compulsory_ids is not None:
            class_obj.compulsory_subjects.set(compulsory_ids)
        if optional_ids is not None:
            class_obj.optional_subjects.set(optional_ids)
        
        return class_obj


class TeacherClassAssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer for TeacherClassAssignment.
    """
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.subject_name', read_only=True)
    class_name = serializers.CharField(source='school_class.class_name', read_only=True)
    section_name = serializers.CharField(source='section.section_name', read_only=True)
    semester_name = serializers.CharField(source='semester.__str__', read_only=True)
    
    class Meta:
        model = TeacherClassAssignment
        fields = [
            'id', 'teacher', 'teacher_name', 'subject', 'subject_name',
            'school_class', 'class_name', 'section', 'section_name',
            'semester', 'semester_name', 'weekly_periods', 'schedule_notes',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class TeacherWorkloadSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying teacher workload.
    """
    assignments = TeacherClassAssignmentSerializer(many=True, read_only=True)
    total_periods = serializers.IntegerField(read_only=True)
    total_classes = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'assignments', 'total_periods', 'total_classes']


class StudentSubjectEnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializer for StudentSubjectEnrollment.
    """
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.subject_name', read_only=True)
    subject_code = serializers.CharField(source='subject.subject_code', read_only=True)
    semester_name = serializers.CharField(source='semester.__str__', read_only=True)
    credit_hours = serializers.DecimalField(source='subject.credit_hours', max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = StudentSubjectEnrollment
        fields = [
            'id', 'student', 'student_name', 'subject', 'subject_name', 'subject_code',
            'semester', 'semester_name', 'credit_hours', 'enrollment_date',
            'status', 'final_grade', 'grade_points', 'dropped_date', 'dropped_reason'
        ]
        read_only_fields = ['enrollment_date']


class ClassEnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializer for ClassEnrollment.
    """
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_username = serializers.CharField(source='student.username', read_only=True)
    class_name = serializers.CharField(source='school_class.class_name', read_only=True)
    section_name = serializers.CharField(source='section.section_name', read_only=True)
    
    class Meta:
        model = ClassEnrollment
        fields = [
            'id', 'student', 'student_name', 'student_username',
            'school_class', 'class_name', 'section', 'section_name',
            'roll_number', 'enrollment_date', 'status',
            'completion_date', 'final_grade', 'remarks'
        ]
        read_only_fields = ['enrollment_date', 'roll_number']


class ClassEnrollmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating class enrollments with validation.
    """
    
    class Meta:
        model = ClassEnrollment
        fields = [
            'id', 'student', 'school_class', 'section',
            'roll_number', 'status', 'remarks'
        ]
    
    def validate(self, data):
        # Check if student already enrolled in this class
        if ClassEnrollment.objects.filter(
            student=data['student'],
            school_class=data['school_class']
        ).exists():
            raise serializers.ValidationError(
                "Student is already enrolled in this class."
            )
        
        # Check section capacity
        section = data['section']
        if section.is_full:
            raise serializers.ValidationError(
                f"Section {section.section_name} is at full capacity."
            )
        
        return data


# Import for serializers
from .models import SubjectPrerequisite, ClassEnrollment
