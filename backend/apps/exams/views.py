from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Max, Min, StdDev, Q, F
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from .models import (
    GradingScale, GradeRange, Exam, ExamDetail, StudentExamStatus,
    StudentResult, StudentOverallResult, ResultModificationLog,
    ReportCardTemplate, GeneratedReportCard
)
from .serializers import (
    GradingScaleListSerializer, GradingScaleDetailSerializer, GradingScaleCreateSerializer,
    GradeRangeSerializer, ExamListSerializer, ExamDetailSerializer,
    ExamDetailListSerializer, ExamDetailDetailSerializer, ExamDetailCreateSerializer,
    StudentExamStatusSerializer, StudentResultListSerializer, StudentResultDetailSerializer,
    StudentResultCreateSerializer, BulkResultEntrySerializer,
    StudentOverallResultListSerializer, StudentOverallResultDetailSerializer,
    ResultModificationLogSerializer, ReportCardTemplateSerializer,
    GeneratedReportCardSerializer, GenerateReportCardSerializer,
    MarkEntrySerializer, ExamStatisticsSerializer, RankCalculationSerializer,
    ResultPublishSerializer
)


class GradingScaleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing grading scales."""
    queryset = GradingScale.objects.prefetch_related('ranges')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['school_class', 'is_default', 'is_active']
    search_fields = ['name', 'description']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return GradingScaleCreateSerializer
        elif self.action == 'list':
            return GradingScaleListSerializer
        return GradingScaleDetailSerializer
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set this grading scale as default for the class."""
        scale = self.get_object()
        scale.is_default = True
        scale.save()
        return Response({'status': 'Grading scale set as default'})
    
    @action(detail=True, methods=['post'])
    def add_grade_range(self, request, pk=None):
        """Add a grade range to this scale."""
        scale = self.get_object()
        serializer = GradeRangeSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(grading_scale=scale)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExamViewSet(viewsets.ModelViewSet):
    """ViewSet for managing exams."""
    queryset = Exam.objects.select_related('academic_year', 'semester', 'created_by').prefetch_related('details')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['academic_year', 'semester', 'exam_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ExamListSerializer
        return ExamDetailSerializer
    
    @action(detail=True, methods=['post'])
    def publish_timetable(self, request, pk=None):
        """Publish exam timetable."""
        exam = self.get_object()
        exam.publish_timetable(request.user)
        return Response({'status': 'Timetable published successfully'})
    
    @action(detail=True, methods=['post'])
    def publish_results(self, request, pk=None):
        """Publish exam results."""
        serializer = ResultPublishSerializer(data={'exam_id': pk, **request.data})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        exam = self.get_object()
        
        # Calculate overall results for all students
        exam.calculate_overall_results()
        
        # Publish results
        exam.publish_results(request.user)
        
        return Response({
            'status': 'Results published successfully',
            'published_at': exam.result_published_date
        })
    
    @action(detail=True, methods=['post'])
    def calculate_ranks(self, request, pk=None):
        """Calculate class and section ranks."""
        exam = self.get_object()
        
        # Calculate class ranks
        from django.db.models import Window, F
        from django.db.models.functions import Rank
        
        StudentOverallResult.objects.filter(exam=exam).update(
            class_rank=Window(
                expression=Rank(),
                partition_by=[F('student__class_enrollments__school_class')],
                order_by=[F('percentage').desc(), F('grade_point_average').desc()]
            )
        )
        
        # Calculate section ranks
        StudentOverallResult.objects.filter(exam=exam).update(
            section_rank=Window(
                expression=Rank(),
                partition_by=[F('student__class_enrollments__section')],
                order_by=[F('percentage').desc(), F('grade_point_average').desc()]
            )
        )
        
        return Response({'status': 'Ranks calculated successfully'})
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get exam statistics."""
        exam = self.get_object()
        
        # Overall statistics
        overall_results = exam.overall_results.all()
        total_students = overall_results.count()
        
        if total_students == 0:
            return Response({
                'exam_id': exam.id,
                'exam_name': exam.name,
                'total_students': 0,
                'message': 'No results found'
            })
        
        appeared = overall_results.filter(subjects_appeared__gt=0)
        passed = overall_results.filter(overall_result='passed')
        failed = overall_results.filter(overall_result='failed')
        compartment = overall_results.filter(overall_result='compartment')
        
        # Grade distribution
        grade_distribution = {}
        for result in appeared:
            grade = result.grade or 'N/A'
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
        
        # Subject-wise statistics
        subject_stats = []
        for detail in exam.details.all():
            stats = detail.get_class_statistics()
            subject_stats.append({
                'subject_name': detail.subject.subject_name,
                'subject_code': detail.subject.subject_code,
                **stats
            })
        
        return Response({
            'exam_id': exam.id,
            'exam_name': exam.name,
            'total_students': total_students,
            'students_appeared': appeared.count(),
            'students_passed': passed.count(),
            'students_failed': failed.count(),
            'students_compartment': compartment.count(),
            'pass_percentage': (passed.count() / appeared.count() * 100) if appeared.count() > 0 else 0,
            'average_percentage': appeared.aggregate(avg=Avg('percentage'))['avg'] or 0,
            'highest_percentage': appeared.aggregate(max=Max('percentage'))['max'] or 0,
            'lowest_percentage': appeared.aggregate(min=Min('percentage'))['min'] or 0,
            'grade_distribution': grade_distribution,
            'subject_wise_statistics': subject_stats
        })


class ExamDetailViewSet(viewsets.ModelViewSet):
    """ViewSet for managing exam details."""
    queryset = ExamDetail.objects.select_related('exam', 'subject', 'school_class', 'section')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['exam', 'subject', 'school_class', 'section', 'exam_date', 'is_marks_entered', 'is_marks_verified']
    search_fields = ['subject__subject_name', 'venue']
    ordering = ['exam_date', 'start_time']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ExamDetailCreateSerializer
        elif self.action == 'list':
            return ExamDetailListSerializer
        return ExamDetailDetailSerializer
    
    @action(detail=True, methods=['post'])
    def confirm_marks_entry(self, request, pk=None):
        """Confirm marks entry for this exam detail."""
        exam_detail = self.get_object()
        
        exam_detail.is_marks_entered = True
        exam_detail.marks_entered_by = request.user
        exam_detail.marks_entered_at = timezone.now()
        exam_detail.save()
        
        return Response({'status': 'Marks entry confirmed'})
    
    @action(detail=True, methods=['post'])
    def verify_marks(self, request, pk=None):
        """Verify marks for this exam detail."""
        exam_detail = self.get_object()
        
        if not exam_detail.is_marks_entered:
            return Response(
                {'error': 'Marks must be entered before verification'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exam_detail.is_marks_verified = True
        exam_detail.marks_verified_by = request.user
        exam_detail.marks_verified_at = timezone.now()
        exam_detail.save()
        
        return Response({'status': 'Marks verified'})
    
    @action(detail=True, methods=['get'])
    def student_statuses(self, request, pk=None):
        """Get all student statuses for this exam."""
        exam_detail = self.get_object()
        statuses = exam_detail.student_statuses.select_related('student')
        serializer = StudentExamStatusSerializer(statuses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get all results for this exam detail."""
        exam_detail = self.get_object()
        results = exam_detail.student_results.select_related('student')
        serializer = StudentResultListSerializer(results, many=True)
        return Response(serializer.data)


class StudentExamStatusViewSet(viewsets.ModelViewSet):
    """ViewSet for managing student exam statuses."""
    queryset = StudentExamStatus.objects.select_related('student', 'exam_detail')
    serializer_class = StudentExamStatusSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'exam_detail', 'status']


class StudentResultViewSet(viewsets.ModelViewSet):
    """ViewSet for managing student results."""
    queryset = StudentResult.objects.select_related(
        'student', 'exam_detail', 'exam_detail__exam', 
        'exam_detail__subject', 'entered_by', 'verified_by'
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['student', 'exam_detail', 'has_passed', 'grade']
    search_fields = ['student__first_name', 'student__last_name', 'student__username']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StudentResultCreateSerializer
        elif self.action == 'list':
            return StudentResultListSerializer
        return StudentResultDetailSerializer
    
    def perform_create(self, serializer):
        result = serializer.save(entered_by=self.request.user, entered_at=timezone.now())
        return result
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a result entry."""
        result = self.get_object()
        result.verified_by = request.user
        result.verified_at = timezone.now()
        result.save()
        return Response({'status': 'Result verified'})
    
    @action(detail=True, methods=['post'])
    def modify(self, request, pk=None):
        """Modify a result with audit trail."""
        result = self.get_object()
        
        field_changed = request.data.get('field')
        old_value = getattr(result, field_changed, '')
        new_value = request.data.get('new_value')
        reason = request.data.get('reason', '')
        
        # Log the modification
        ResultModificationLog.objects.create(
            student_result=result,
            modified_by=request.user,
            field_changed=field_changed,
            old_value=str(old_value),
            new_value=str(new_value),
            reason=reason,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        # Update the field
        setattr(result, field_changed, new_value)
        result.save()
        
        # Recalculate result
        result.calculate_result()
        
        return Response({'status': 'Result modified successfully'})
    
    @action(detail=False, methods=['post'])
    def bulk_entry(self, request):
        """Bulk entry of results."""
        serializer = BulkResultEntrySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        exam_detail_id = data['exam_detail_id']
        results_data = data['results']
        
        created_results = []
        errors = []
        
        with transaction.atomic():
            for result_data in results_data:
                try:
                    result, created = StudentResult.objects.update_or_create(
                        student_id=result_data['student_id'],
                        exam_detail_id=exam_detail_id,
                        defaults={
                            'theory_marks': result_data.get('theory_marks'),
                            'practical_marks': result_data.get('practical_marks'),
                            'remarks': result_data.get('remarks', ''),
                            'entered_by': request.user,
                            'entered_at': timezone.now()
                        }
                    )
                    created_results.append({
                        'student_id': result_data['student_id'],
                        'status': 'created' if created else 'updated'
                    })
                except Exception as e:
                    errors.append({
                        'student_id': result_data.get('student_id'),
                        'error': str(e)
                    })
        
        return Response({
            'success_count': len(created_results),
            'error_count': len(errors),
            'results': created_results,
            'errors': errors
        })
    
    @action(detail=False, methods=['get'])
    def by_student(self, request):
        """Get all results for a specific student."""
        student_id = request.query_params.get('student_id')
        exam_id = request.query_params.get('exam_id')
        
        if not student_id:
            return Response(
                {'error': 'student_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(student_id=student_id)
        
        if exam_id:
            queryset = queryset.filter(exam_detail__exam_id=exam_id)
        
        serializer = StudentResultListSerializer(queryset, many=True)
        return Response(serializer.data)


class StudentOverallResultViewSet(viewsets.ModelViewSet):
    """ViewSet for managing overall results."""
    queryset = StudentOverallResult.objects.select_related('student', 'exam')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'exam', 'overall_result']
    search_fields = ['student__first_name', 'student__last_name']
    ordering_fields = ['percentage', 'grade_point_average', 'class_rank', 'section_rank']
    ordering = ['-percentage']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StudentOverallResultListSerializer
        return StudentOverallResultDetailSerializer
    
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalculate overall result."""
        overall_result = self.get_object()
        overall_result.calculate_aggregate()
        return Response({'status': 'Result recalculated'})
    
    @action(detail=False, methods=['get'])
    def toppers(self, request):
        """Get top performers."""
        exam_id = request.query_params.get('exam_id')
        limit = int(request.query_params.get('limit', 10))
        
        queryset = self.get_queryset()
        
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
        
        toppers = queryset.filter(overall_result='passed').order_by('-percentage')[:limit]
        serializer = StudentOverallResultListSerializer(toppers, many=True)
        return Response(serializer.data)


class ResultModificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for result modification logs (read-only)."""
    queryset = ResultModificationLog.objects.select_related(
        'student_result', 'modified_by', 'approved_by'
    )
    serializer_class = ResultModificationLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student_result', 'modified_by', 'approved_by']
    ordering = ['-modified_at']
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a result modification."""
        log = self.get_object()
        
        if log.approved_by:
            return Response(
                {'error': 'Modification is already approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        log.approved_by = request.user
        log.approved_at = timezone.now()
        log.save()
        
        return Response({'status': 'Modification approved'})


class ReportCardTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing report card templates."""
    queryset = ReportCardTemplate.objects.select_related('academic_year')
    serializer_class = ReportCardTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['academic_year', 'is_active']


class GeneratedReportCardViewSet(viewsets.ModelViewSet):
    """ViewSet for managing generated report cards."""
    queryset = GeneratedReportCard.objects.select_related(
        'student', 'exam', 'template', 'generated_by', 'distributed_by'
    )
    serializer_class = GeneratedReportCardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'exam', 'template', 'is_distributed']
    ordering = ['-generated_at']
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate report cards."""
        serializer = GenerateReportCardSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        exam_id = data['exam_id']
        template_id = data['template_id']
        student_ids = data.get('student_ids', [])
        
        # Get students
        if student_ids:
            students = CustomUser.objects.filter(
                id__in=student_ids,
                is_student=True
            )
        else:
            # Generate for all students who have results
            students = CustomUser.objects.filter(
                exam_results__exam_detail__exam_id=exam_id,
                is_student=True
            ).distinct()
        
        generated_cards = []
        errors = []
        
        template = ReportCardTemplate.objects.get(id=template_id)
        exam = Exam.objects.get(id=exam_id)
        
        for student in students:
            try:
                # Check if overall result exists
                overall_result = StudentOverallResult.objects.filter(
                    student=student,
                    exam_id=exam_id
                ).first()
                
                if not overall_result:
                    errors.append({
                        'student_id': student.id,
                        'error': 'No overall result found'
                    })
                    continue
                
                # Generate or update report card
                card, created = GeneratedReportCard.objects.update_or_create(
                    student=student,
                    exam_id=exam_id,
                    defaults={
                        'template': template,
                        'generated_by': request.user,
                        'is_distributed': False
                    }
                )
                
                # TODO: Generate PDF (would need additional library like WeasyPrint)
                
                generated_cards.append({
                    'student_id': student.id,
                    'student_name': student.get_full_name(),
                    'status': 'created' if created else 'updated'
                })
                
            except Exception as e:
                errors.append({
                    'student_id': student.id,
                    'error': str(e)
                })
        
        return Response({
            'generated_count': len(generated_cards),
            'error_count': len(errors),
            'generated_cards': generated_cards,
            'errors': errors
        })
    
    @action(detail=True, methods=['post'])
    def distribute(self, request, pk=None):
        """Mark report card as distributed."""
        card = self.get_object()
        card.is_distributed = True
        card.distributed_at = timezone.now()
        card.distributed_by = request.user
        card.save()
        
        return Response({'status': 'Report card marked as distributed'})


class MarkEntryViewSet(viewsets.ViewSet):
    """ViewSet for teachers to enter marks."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def enter_marks(self, request):
        """Enter marks for students."""
        serializer = MarkEntrySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        exam_detail_id = data['exam_detail_id']
        marks_data = data['marks_data']
        
        exam_detail = ExamDetail.objects.get(id=exam_detail_id)
        
        # Check if user is authorized (teacher for this exam)
        if not exam_detail.invigilators.filter(id=request.user.id).exists():
            return Response(
                {'error': 'You are not authorized to enter marks for this exam'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        created_results = []
        
        with transaction.atomic():
            for mark_data in marks_data:
                result, created = StudentResult.objects.update_or_create(
                    student_id=mark_data['student_id'],
                    exam_detail=exam_detail,
                    defaults={
                        'theory_marks': mark_data.get('theory_marks'),
                        'practical_marks': mark_data.get('practical_marks'),
                        'entered_by': request.user,
                        'entered_at': timezone.now()
                    }
                )
                created_results.append({
                    'student_id': mark_data['student_id'],
                    'created': created
                })
        
        return Response({
            'success_count': len(created_results),
            'results': created_results
        })
    
    @action(detail=False, methods=['get'])
    def eligible_exams(self, request):
        """Get exams where teacher can enter marks."""
        if not request.user.is_teacher:
            return Response({'error': 'Only teachers can access this'}, status=status.HTTP_403_FORBIDDEN)
        
        exam_details = ExamDetail.objects.filter(
            invigilators=request.user,
            is_marks_entered=False
        ).select_related('exam', 'subject', 'school_class')
        
        data = []
        for detail in exam_details:
            data.append({
                'exam_detail_id': detail.id,
                'exam_name': detail.exam.name,
                'subject_name': detail.subject.subject_name,
                'class_name': detail.school_class.class_name,
                'section_name': detail.section.section_name if detail.section else None,
                'exam_date': detail.exam_date,
                'total_students': detail.student_statuses.count()
            })
        
        return Response(data)


# Import at the end to avoid circular imports
from apps.users.models import CustomUser