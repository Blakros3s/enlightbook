from django.contrib import admin
from .models import (
    AcademicYear, Semester, SubjectCategory, Subject, SubjectPrerequisite,
    Class, Section, TeacherClassAssignment, StudentSubjectEnrollment, ClassEnrollment
)


class SectionInline(admin.TabularInline):
    model = Section
    extra = 1


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['year_name', 'start_date', 'end_date', 'is_current', 'is_active']
    list_filter = ['is_current', 'is_active']
    search_fields = ['year_name']
    date_hierarchy = 'start_date'
    actions = ['set_as_current']
    
    def set_as_current(self, request, queryset):
        if queryset.count() == 1:
            year = queryset.first()
            year.is_current = True
            year.save()
            self.message_user(request, f'{year.year_name} set as current academic year.')
    set_as_current.short_description = "Set selected as current year"


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'start_date', 'end_date', 'is_active', 'registration_open']
    list_filter = ['academic_year', 'name', 'is_active', 'registration_open']
    search_fields = ['name']
    date_hierarchy = 'start_date'


@admin.register(SubjectCategory)
class SubjectCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'subject_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code', 'department']
    
    def subject_count(self, obj):
        return obj.subjects.count()
    subject_count.short_description = 'Subjects'


class SubjectPrerequisiteInline(admin.TabularInline):
    model = SubjectPrerequisite
    fk_name = 'subject'
    extra = 1


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['subject_code', 'subject_name', 'category', 'credit_hours', 'is_optional', 'subject_type', 'is_active']
    list_filter = ['category', 'is_optional', 'subject_type', 'is_active', 'is_credit']
    search_fields = ['subject_code', 'subject_name']
    inlines = [SubjectPrerequisiteInline]


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['class_name', 'class_code', 'grade_level', 'academic_year', 'section_count', 'is_active']
    list_filter = ['academic_year', 'grade_level', 'is_active']
    search_fields = ['class_code', 'class_name']
    filter_horizontal = ['compulsory_subjects', 'optional_subjects']
    inlines = [SectionInline]
    
    def section_count(self, obj):
        return obj.sections.count()
    section_count.short_description = 'Sections'


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'max_capacity', 'class_teacher', 'room_number', 'is_active']
    list_filter = ['school_class__academic_year', 'is_active']
    search_fields = ['section_name', 'school_class__class_name', 'room_number']
    autocomplete_fields = ['class_teacher']


@admin.register(TeacherClassAssignment)
class TeacherClassAssignmentAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'subject', 'school_class', 'section', 'semester', 'weekly_periods', 'is_active']
    list_filter = ['semester', 'is_active']
    search_fields = ['teacher__first_name', 'teacher__last_name', 'subject__subject_name']
    autocomplete_fields = ['teacher', 'subject', 'school_class', 'section', 'semester']


@admin.register(StudentSubjectEnrollment)
class StudentSubjectEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'semester', 'status', 'enrollment_date']
    list_filter = ['semester', 'status']
    search_fields = ['student__first_name', 'student__last_name', 'subject__subject_name']
    autocomplete_fields = ['student', 'subject', 'semester']
    date_hierarchy = 'enrollment_date'


@admin.register(ClassEnrollment)
class ClassEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'school_class', 'section', 'roll_number', 'status', 'enrollment_date']
    list_filter = ['school_class__academic_year', 'status']
    search_fields = ['student__first_name', 'student__last_name', 'roll_number']
    autocomplete_fields = ['student', 'school_class', 'section']
    date_hierarchy = 'enrollment_date'
