from rest_framework import serializers
from django.db import transaction
from decimal import Decimal

from .models import (
    GradingScale, GradeRange, Exam, ExamDetail, StudentExamStatus,
    StudentResult, StudentOverallResult, ResultModificationLog,
    ReportCardTemplate, GeneratedReportCard
)


class GradeRangeSerializer(serializers.ModelSerializer):
    """Serializer for grade ranges."""
    
    class Meta:
        model = GradeRange
        fields = ['id', 'grade', 'min_percentage', 'max_percentage', 'grade_point', 'description']
    
    def validate(self, data):
        if data.get('min_percentage') >= data.get('max_percentage'):
            raise serializers.ValidationError("Min percentage must be less than max percentage.")
        return data


class GradingScaleListSerializer(serializers.ModelSerializer):
    """List serializer for grading scales."""
    school_class_name = serializers.CharField(source='school_class.class_name', read_only=True)
    ranges_count = serializers.IntegerField(source='ranges.count', read_only=True)
    
    class Meta:
        model = GradingScale
        fields = ['id', 'name', 'school_class', 'school_class_name', 'is_default', 'ranges_count', 'is_active']


class GradingScaleDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for grading scales."""
    school_class_name = serializers.CharField(source='school_class.class_name', read_only=True)
    ranges = GradeRangeSerializer(many=True, read_only=True)
    
    class Meta:
        model = GradingScale
        fields = ['id', 'name', 'school_class', 'school_class_name', 'is_default', 'description', 'ranges', 'is_active', 'created_at']
        read_only_fields = ['created_at']


class GradingScaleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating grading scales with ranges."""
    ranges = GradeRangeSerializer(many=True, write_only=True)
    
    class Meta:
        model = GradingScale
        fields = ['name', 'school_class', 'is_default', 'description', 'ranges']
    
    @transaction.atomic
    def create(self, validated_data):
        ranges_data = validated_data.pop('ranges', [])
        scale = GradingScale.objects.create(**validated_data)
        
        for range_data in ranges_data:
            GradeRange.objects.create(grading_scale=scale, **range_data)
        
        return scale


class ExamListSerializer(serializers.ModelSerializer):
    """List serializer for exams."""
    academic_year_name = serializers.CharField(source='academic_year.year_name', read_only=True)
    semester_name = serializers.CharField(source='semester.get_name_display', read_only=True)
    exam_type_display = serializers.CharField(source='get_exam_type_display', read_only=True)
    total_subjects = serializers.IntegerField(source='details.count', read_only=True)
    
    class Meta:
        model = Exam
        fields = [
            'id', 'name', 'academic_year', 'academic_year_name',
            'semester', 'semester_name', 'exam_type', 'exam_type_display',
            'is_timetable_published', 'is_result_published',
            'allow_students_to_view_results', 'total_subjects',
            'start_date', 'end_date', 'is_active'
        ]


class ExamDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for exams."""
    academic_year_name = serializers.CharField(source='academic_year.year_name', read_only=True)
    semester_name = serializers.CharField(source='semester.get_name_display', read_only=True)
    exam_type_display = serializers.CharField(source='get_exam_type_display', read_only=True)
    timetable_published_by_name = serializers.CharField(source='timetable_published_by.get_full_name', read_only=True)
    result_published_by_name = serializers.CharField(source='result_published_by.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Exam
        fields = '__all__'
        read_only_fields = [
            'timetable_published_date', 'timetable_published_by',
            'result_published_date', 'result_published_by',
            'created_at', 'updated_at'
        ]


class ExamDetailListSerializer(serializers.ModelSerializer):
    """List serializer for exam details."""
    subject_name = serializers.CharField(source='subject.subject_name', read_only=True)
    subject_code = serializers.CharField(source='subject.subject_code', read_only=True)
    class_name = serializers.CharField(source='school_class.class_name', read_only=True)
    section_name = serializers.CharField(source='section.section_name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    
    class Meta:
        model = ExamDetail
        fields = [
            'id', 'exam', 'exam_name', 'subject', 'subject_name', 'subject_code',
            'school_class', 'class_name', 'section', 'section_name',
            'exam_date', 'start_time', 'end_time', 'venue',
            'full_marks', 'is_marks_entered', 'is_marks_verified'
        ]


class ExamDetailDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for exam details."""
    subject_name = serializers.CharField(source='subject.subject_name', read_only=True)
    subject_code = serializers.CharField(source='subject.subject_code', read_only=True)
    class_name = serializers.CharField(source='school_class.class_name', read_only=True)
    section_name = serializers.CharField(source='section.section_name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    invigilator_names = serializers.SerializerMethodField()
    statistics = serializers.SerializerMethodField()
    
    class Meta:
        model = ExamDetail
        fields = '__all__'
        read_only_fields = [
            'is_marks_entered', 'marks_entered_at', 'marks_entered_by',
            'is_marks_verified', 'marks_verified_at', 'marks_verified_by',
            'created_at', 'updated_at'
        ]
    
    def get_invigilator_names(self, obj):
        return [
            {'id': inv.id, 'name': inv.get_full_name()}
            for inv in obj.invigilators.all()
        ]
    
    def get_statistics(self, obj):
        return obj.get_class_statistics()


class ExamDetailCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating exam details."""
    invigilator_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = ExamDetail
        fields = [
            'exam', 'subject', 'school_class', 'section',
            'full_marks', 'theory_full_marks', 'practical_full_marks', 'passing_marks',
            'exam_date', 'start_time', 'end_time', 'duration_minutes',
            'venue', 'invigilator_ids'
        ]
    
    @transaction.atomic
    def create(self, validated_data):
        invigilator_ids = validated_data.pop('invigilator_ids', [])
        
        exam_detail = ExamDetail.objects.create(**validated_data)
        
        if invigilator_ids:
            exam_detail.invigilators.set(invigilator_ids)
        
        return exam_detail


class StudentExamStatusSerializer(serializers.ModelSerializer):
    """Serializer for student exam status."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_roll_number = serializers.CharField(source='student.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = StudentExamStatus
        fields = ['id', 'student', 'student_name', 'student_roll_number', 'exam_detail', 'status', 'status_display', 'remarks', 'recorded_at']
        read_only_fields = ['recorded_at']


class StudentResultListSerializer(serializers.ModelSerializer):
    """List serializer for student results."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_roll_number = serializers.CharField(source='student.username', read_only=True)
    exam_name = serializers.CharField(source='exam_detail.exam.name', read_only=True)
    subject_name = serializers.CharField(source='exam_detail.subject.subject_name', read_only=True)
    subject_code = serializers.CharField(source='exam_detail.subject.subject_code', read_only=True)
    
    class Meta:
        model = StudentResult
        fields = [
            'id', 'student', 'student_name', 'student_roll_number',
            'exam_detail', 'exam_name', 'subject_name', 'subject_code',
            'total_marks', 'percentage', 'grade', 'has_passed',
            'entered_by', 'verified_by', 'created_at'
        ]


class StudentResultDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for student results."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    exam_detail_info = ExamDetailListSerializer(source='exam_detail', read_only=True)
    entered_by_name = serializers.CharField(source='entered_by.get_full_name', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)
    
    class Meta:
        model = StudentResult
        fields = '__all__'
        read_only_fields = [
            'total_marks', 'percentage', 'grade', 'grade_point',
            'theory_grade', 'practical_grade', 'has_passed',
            'entered_at', 'verified_at', 'created_at', 'updated_at'
        ]


class StudentResultCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating student results."""
    
    class Meta:
        model = StudentResult
        fields = [
            'student', 'exam_detail', 'exam_status',
            'theory_marks', 'practical_marks', 'remarks'
        ]
    
    def validate(self, data):
        # Validate marks don't exceed full marks
        exam_detail = data.get('exam_detail')
        
        if data.get('theory_marks') and exam_detail.theory_full_marks:
            if data['theory_marks'] > exam_detail.theory_full_marks:
                raise serializers.ValidationError(
                    {"theory_marks": "Theory marks cannot exceed full marks."}
                )
        
        if data.get('practical_marks') and exam_detail.practical_full_marks:
            if data['practical_marks'] > exam_detail.practical_full_marks:
                raise serializers.ValidationError(
                    {"practical_marks": "Practical marks cannot exceed full marks."}
                )
        
        return data


class BulkResultEntrySerializer(serializers.Serializer):
    """Serializer for bulk result entry."""
    exam_detail_id = serializers.IntegerField()
    results = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate(self, data):
        try:
            ExamDetail.objects.get(id=data['exam_detail_id'])
        except ExamDetail.DoesNotExist:
            raise serializers.ValidationError("Exam detail not found.")
        return data


class StudentOverallResultListSerializer(serializers.ModelSerializer):
    """List serializer for overall results."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_roll_number = serializers.CharField(source='student.username', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    
    class Meta:
        model = StudentOverallResult
        fields = [
            'id', 'student', 'student_name', 'student_roll_number',
            'exam', 'exam_name', 'percentage', 'grade', 'grade_point_average',
            'class_rank', 'section_rank', 'subjects_passed', 'subjects_failed',
            'overall_result', 'updated_at'
        ]


class StudentOverallResultDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for overall results."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    subject_results = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentOverallResult
        fields = [
            'id', 'student', 'student_name', 'exam', 'exam_name',
            'total_marks_obtained', 'total_full_marks', 'percentage',
            'grade', 'grade_point_average', 'class_rank', 'section_rank',
            'subjects_appeared', 'subjects_passed', 'subjects_failed',
            'overall_result', 'remarks', 'subject_results', 'updated_at'
        ]
    
    def get_subject_results(self, obj):
        results = obj.student.exam_results.filter(exam_detail__exam=obj.exam)
        return StudentResultListSerializer(results, many=True).data


class ResultModificationLogSerializer(serializers.ModelSerializer):
    """Serializer for result modification logs."""
    student_result_info = serializers.SerializerMethodField()
    modified_by_name = serializers.CharField(source='modified_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = ResultModificationLog
        fields = [
            'id', 'student_result', 'student_result_info',
            'modified_by', 'modified_by_name', 'modified_at',
            'field_changed', 'old_value', 'new_value', 'reason',
            'approved_by', 'approved_by_name', 'approved_at'
        ]
    
    def get_student_result_info(self, obj):
        return {
            'student_name': obj.student_result.student.get_full_name(),
            'exam_name': obj.student_result.exam_detail.exam.name,
            'subject_name': obj.student_result.exam_detail.subject.subject_name
        }


class ReportCardTemplateSerializer(serializers.ModelSerializer):
    """Serializer for report card templates."""
    academic_year_name = serializers.CharField(source='academic_year.year_name', read_only=True)
    
    class Meta:
        model = ReportCardTemplate
        fields = [
            'id', 'name', 'academic_year', 'academic_year_name',
            'header_image', 'footer_text', 'show_signature', 'show_photo',
            'show_attendance', 'show_remarks', 'custom_fields',
            'is_active', 'created_at'
        ]
        read_only_fields = ['created_at']


class GeneratedReportCardSerializer(serializers.ModelSerializer):
    """Serializer for generated report cards."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    distributed_by_name = serializers.CharField(source='distributed_by.get_full_name', read_only=True)
    
    class Meta:
        model = GeneratedReportCard
        fields = [
            'id', 'student', 'student_name', 'exam', 'exam_name',
            'template', 'template_name', 'pdf_file',
            'generated_by', 'generated_by_name', 'generated_at',
            'is_distributed', 'distributed_at', 'distributed_by', 'distributed_by_name'
        ]
        read_only_fields = ['generated_at', 'distributed_at']


class GenerateReportCardSerializer(serializers.Serializer):
    """Serializer for generating report cards."""
    exam_id = serializers.IntegerField()
    template_id = serializers.IntegerField()
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    def validate(self, data):
        try:
            Exam.objects.get(id=data['exam_id'])
        except Exam.DoesNotExist:
            raise serializers.ValidationError("Exam not found.")
        
        try:
            ReportCardTemplate.objects.get(id=data['template_id'])
        except ReportCardTemplate.DoesNotExist:
            raise serializers.ValidationError("Template not found.")
        
        return data


class MarkEntrySerializer(serializers.Serializer):
    """Serializer for mark entry by teachers."""
    exam_detail_id = serializers.IntegerField()
    marks_data = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate(self, data):
        try:
            exam_detail = ExamDetail.objects.get(id=data['exam_detail_id'])
        except ExamDetail.DoesNotExist:
            raise serializers.ValidationError("Exam detail not found.")
        
        # Validate each mark entry
        for entry in data['marks_data']:
            theory = entry.get('theory_marks')
            practical = entry.get('practical_marks')
            
            if theory and exam_detail.theory_full_marks:
                if Decimal(str(theory)) > exam_detail.theory_full_marks:
                    raise serializers.ValidationError(
                        f"Theory marks cannot exceed {exam_detail.theory_full_marks}"
                    )
            
            if practical and exam_detail.practical_full_marks:
                if Decimal(str(practical)) > exam_detail.practical_full_marks:
                    raise serializers.ValidationError(
                        f"Practical marks cannot exceed {exam_detail.practical_full_marks}"
                    )
        
        return data


class ExamStatisticsSerializer(serializers.Serializer):
    """Serializer for exam statistics."""
    exam_id = serializers.IntegerField()
    total_students = serializers.IntegerField()
    students_appeared = serializers.IntegerField()
    students_passed = serializers.IntegerField()
    students_failed = serializers.IntegerField()
    pass_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    subject_wise_statistics = serializers.ListField(child=serializers.DictField())
    grade_distribution = serializers.DictField()


class RankCalculationSerializer(serializers.Serializer):
    """Serializer for rank calculation."""
    exam_id = serializers.IntegerField()
    calculate_class_rank = serializers.BooleanField(default=True)
    calculate_section_rank = serializers.BooleanField(default=True)
    
    def validate(self, data):
        try:
            Exam.objects.get(id=data['exam_id'])
        except Exam.DoesNotExist:
            raise serializers.ValidationError("Exam not found.")
        return data


class ResultPublishSerializer(serializers.Serializer):
    """Serializer for publishing results."""
    exam_id = serializers.IntegerField()
    allow_students_to_view = serializers.BooleanField(default=True)
    
    def validate(self, data):
        try:
            exam = Exam.objects.get(id=data['exam_id'])
        except Exam.DoesNotExist:
            raise serializers.ValidationError("Exam not found.")
        
        # Check if marks are entered and verified for all exam details
        unverified = exam.details.filter(is_marks_verified=False)
        if unverified.exists():
            raise serializers.ValidationError(
                f"Marks not verified for {unverified.count()} exam details."
            )
        
        return data