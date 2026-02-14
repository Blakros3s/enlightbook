from django.contrib import admin
from .models import (
    GradingScale, GradeRange, Exam, ExamDetail, StudentExamStatus,
    StudentResult, StudentOverallResult, ResultModificationLog,
    ReportCardTemplate, GeneratedReportCard
)


class GradeRangeInline(admin.TabularInline):
    model = GradeRange
    extra = 1


@admin.register(GradingScale)
class GradingScaleAdmin(admin.ModelAdmin):
    list_display = ['name', 'school_class', 'is_default', 'is_active']
    list_filter = ['is_default', 'is_active']
    search_fields = ['name']
    inlines = [GradeRangeInline]


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'academic_year', 'exam_type', 'is_timetable_published', 'is_result_published', 'is_active']
    list_filter = ['exam_type', 'is_timetable_published', 'is_result_published', 'is_active']
    search_fields = ['name']
    date_hierarchy = 'start_date'


@admin.register(ExamDetail)
class ExamDetailAdmin(admin.ModelAdmin):
    list_display = ['exam', 'subject', 'school_class', 'section', 'exam_date', 'is_marks_entered', 'is_marks_verified']
    list_filter = ['exam', 'is_marks_entered', 'is_marks_verified', 'exam_date']
    search_fields = ['subject__subject_name', 'venue']
    filter_horizontal = ['invigilators']
    date_hierarchy = 'exam_date'


@admin.register(StudentExamStatus)
class StudentExamStatusAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam_detail', 'status', 'recorded_at']
    list_filter = ['status', 'recorded_at']
    search_fields = ['student__first_name', 'student__last_name']


@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam_detail', 'total_marks', 'percentage', 'grade', 'has_passed']
    list_filter = ['has_passed', 'grade', 'created_at']
    search_fields = ['student__first_name', 'student__last_name']


@admin.register(StudentOverallResult)
class StudentOverallResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'percentage', 'grade', 'class_rank', 'section_rank', 'overall_result']
    list_filter = ['overall_result', 'updated_at']
    search_fields = ['student__first_name', 'student__last_name']


@admin.register(ResultModificationLog)
class ResultModificationLogAdmin(admin.ModelAdmin):
    list_display = ['student_result', 'field_changed', 'modified_by', 'modified_at', 'approved_by']
    list_filter = ['field_changed', 'modified_at']
    search_fields = ['student_result__student__first_name', 'reason']
    readonly_fields = ['modified_at']


@admin.register(ReportCardTemplate)
class ReportCardTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'academic_year', 'is_active']
    list_filter = ['is_active']


@admin.register(GeneratedReportCard)
class GeneratedReportCardAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'template', 'is_distributed', 'generated_at']
    list_filter = ['is_distributed', 'generated_at']
    search_fields = ['student__first_name', 'student__last_name']