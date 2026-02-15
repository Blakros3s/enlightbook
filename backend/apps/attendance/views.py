"""
Attendance Management Views for EnlightBook.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    AttendancePeriod, DailyAttendance, PeriodAttendance,
    LeaveApplication, AttendanceSummary, AttendancePolicy,
    AttendanceNotification, HolidayCalendar
)
from .serializers import (
    AttendancePeriodSerializer, DailyAttendanceListSerializer,
    DailyAttendanceDetailSerializer, DailyAttendanceCreateSerializer,
    BulkAttendanceSerializer, PeriodAttendanceSerializer,
    PeriodAttendanceCreateSerializer, LeaveApplicationListSerializer,
    LeaveApplicationDetailSerializer, LeaveApplicationCreateSerializer,
    AttendanceSummarySerializer, AttendancePolicySerializer,
    AttendanceNotificationSerializer, HolidayCalendarSerializer,
    AttendanceStatisticsSerializer, StudentAttendanceDetailSerializer,
    DefaulterListSerializer
)
from apps.academic.models import Class, Section, ClassEnrollment


class AttendancePeriodViewSet(viewsets.ModelViewSet):
    """ViewSet for managing attendance periods."""
    queryset = AttendancePeriod.objects.all()
    serializer_class = AttendancePeriodSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['order']


class DailyAttendanceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing daily attendance."""
    queryset = DailyAttendance.objects.select_related('student', 'recorded_by', 'leave_application')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'date', 'status', 'recorded_by']
    search_fields = ['student__first_name', 'student__last_name', 'student__username']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DailyAttendanceCreateSerializer
        elif self.action == 'list':
            return DailyAttendanceListSerializer
        return DailyAttendanceDetailSerializer
    
    @action(detail=False, methods=['post'])
    def bulk_mark(self, request):
        """Mark attendance for entire class."""
        serializer = BulkAttendanceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        school_class_id = data['school_class_id']
        section_id = data.get('section_id')
        date = data['date']
        attendance_data = data['attendance_data']
        
        # Get students
        students_query = ClassEnrollment.objects.filter(
            school_class_id=school_class_id,
            status='active'
        ).select_related('student')
        
        if section_id:
            students_query = students_query.filter(section_id=section_id)
        
        created_records = []
        errors = []
        
        with transaction.atomic():
            for record_data in attendance_data:
                try:
                    attendance, created = DailyAttendance.objects.update_or_create(
                        student_id=record_data['student_id'],
                        date=date,
                        defaults={
                            'status': record_data.get('status', 'present'),
                            'check_in_time': record_data.get('check_in_time'),
                            'check_out_time': record_data.get('check_out_time'),
                            'remarks': record_data.get('remarks', ''),
                            'recorded_by': request.user
                        }
                    )
                    created_records.append({
                        'student_id': record_data['student_id'],
                        'status': 'created' if created else 'updated'
                    })
                except Exception as e:
                    errors.append({
                        'student_id': record_data.get('student_id'),
                        'error': str(e)
                    })
        
        return Response({
            'success_count': len(created_records),
            'error_count': len(errors),
            'records': created_records,
            'errors': errors
        })
    
    @action(detail=False, methods=['get'])
    def by_class(self, request):
        """Get attendance for a specific class on a date."""
        school_class_id = request.query_params.get('school_class_id')
        section_id = request.query_params.get('section_id')
        date = request.query_params.get('date')
        
        if not school_class_id or not date:
            return Response(
                {'error': 'school_class_id and date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get enrolled students
        enrollments = ClassEnrollment.objects.filter(
            school_class_id=school_class_id,
            status='active'
        ).select_related('student')
        
        if section_id:
            enrollments = enrollments.filter(section_id=section_id)
        
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Get attendance records
        student_ids = [e.student_id for e in enrollments]
        attendance_records = DailyAttendance.objects.filter(
            student_id__in=student_ids,
            date=date_obj
        )
        
        # Create response
        data = []
        for enrollment in enrollments:
            attendance = attendance_records.filter(student=enrollment.student).first()
            data.append({
                'student_id': enrollment.student_id,
                'student_name': enrollment.student.get_full_name(),
                'roll_number': enrollment.roll_number,
                'status': attendance.status if attendance else None,
                'check_in_time': attendance.check_in_time if attendance else None,
                'check_out_time': attendance.check_out_time if attendance else None,
                'remarks': attendance.remarks if attendance else None
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def by_student(self, request):
        """Get attendance history for a student."""
        student_id = request.query_params.get('student_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not student_id:
            return Response(
                {'error': 'student_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(student_id=student_id)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        serializer = DailyAttendanceListSerializer(queryset, many=True)
        return Response(serializer.data)


class PeriodAttendanceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing period-wise attendance."""
    queryset = PeriodAttendance.objects.select_related(
        'student', 'period', 'subject', 'school_class', 'section', 'recorded_by'
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['student', 'date', 'period', 'subject', 'school_class', 'section', 'status']
    search_fields = ['student__first_name', 'student__last_name']
    ordering = ['-date', 'period__order']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PeriodAttendanceCreateSerializer
        return PeriodAttendanceSerializer
    
    @action(detail=False, methods=['post'])
    def bulk_mark(self, request):
        """Mark period attendance for multiple students."""
        records = request.data.get('records', [])
        
        created_records = []
        errors = []
        
        with transaction.atomic():
            for record in records:
                try:
                    attendance, created = PeriodAttendance.objects.update_or_create(
                        student_id=record['student_id'],
                        date=record['date'],
                        period_id=record['period_id'],
                        defaults={
                            'subject_id': record['subject_id'],
                            'school_class_id': record['school_class_id'],
                            'section_id': record.get('section_id'),
                            'status': record.get('status', 'present'),
                            'recorded_by': request.user
                        }
                    )
                    created_records.append({
                        'student_id': record['student_id'],
                        'created': created
                    })
                except Exception as e:
                    errors.append({
                        'student_id': record.get('student_id'),
                        'error': str(e)
                    })
        
        return Response({
            'success_count': len(created_records),
            'error_count': len(errors),
            'records': created_records,
            'errors': errors
        })


class LeaveApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing leave applications."""
    queryset = LeaveApplication.objects.select_related('applicant', 'approved_by')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['applicant', 'leave_type', 'status', 'start_date']
    search_fields = ['applicant__first_name', 'applicant__last_name', 'reason']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LeaveApplicationCreateSerializer
        elif self.action == 'list':
            return LeaveApplicationListSerializer
        return LeaveApplicationDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a leave application."""
        leave = self.get_object()
        
        if leave.status != 'pending':
            return Response(
                {'error': 'Only pending applications can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        remarks = request.data.get('remarks', '')
        leave.approve(request.user, remarks)
        
        return Response({'status': 'Leave application approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a leave application."""
        leave = self.get_object()
        
        if leave.status != 'pending':
            return Response(
                {'error': 'Only pending applications can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        remarks = request.data.get('remarks', '')
        leave.reject(request.user, remarks)
        
        return Response({'status': 'Leave application rejected'})
    
    @action(detail=False, methods=['get'])
    def my_leaves(self, request):
        """Get current user's leave applications."""
        leaves = self.get_queryset().filter(applicant=request.user)
        serializer = LeaveApplicationListSerializer(leaves, many=True)
        return Response(serializer.data)


class AttendanceSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for attendance summaries (read-only)."""
    queryset = AttendanceSummary.objects.select_related('student')
    serializer_class = AttendanceSummarySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'month']
    ordering = ['-month']
    
    @action(detail=False, methods=['get'])
    def by_student(self, request):
        """Get all summaries for a student."""
        student_id = request.query_params.get('student_id')
        
        if not student_id:
            return Response(
                {'error': 'student_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        summaries = self.get_queryset().filter(student_id=student_id)
        serializer = self.get_serializer(summaries, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Calculate summary for a student and month."""
        student_id = request.data.get('student_id')
        year = request.data.get('year')
        month = request.data.get('month')
        
        if not all([student_id, year, month]):
            return Response(
                {'error': 'student_id, year, and month are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from datetime import date
        month_date = date(year, month, 1)
        
        summary, created = AttendanceSummary.objects.get_or_create(
            student_id=student_id,
            month=month_date
        )
        
        summary.recalculate()
        
        serializer = self.get_serializer(summary)
        return Response({
            'status': 'Summary calculated',
            'created': created,
            'data': serializer.data
        })


class AttendancePolicyViewSet(viewsets.ModelViewSet):
    """ViewSet for managing attendance policies."""
    queryset = AttendancePolicy.objects.select_related('school_class')
    serializer_class = AttendancePolicySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['school_class', 'is_active']


class AttendanceNotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing attendance notifications."""
    queryset = AttendanceNotification.objects.select_related('student')
    serializer_class = AttendanceNotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'notification_type', 'is_read']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read."""
        notification = self.get_object()
        notification.mark_read()
        return Response({'status': 'Notification marked as read'})
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications for current user."""
        notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)


class HolidayCalendarViewSet(viewsets.ModelViewSet):
    """ViewSet for managing holiday calendar."""
    queryset = HolidayCalendar.objects.all()
    serializer_class = HolidayCalendarSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['holiday_type', 'is_active']
    ordering = ['-date']
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming holidays."""
        today = timezone.now().date()
        holidays = self.get_queryset().filter(
            date__gte=today,
            is_active=True
        )[:10]
        serializer = self.get_serializer(holidays, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_month(self, request):
        """Get holidays for a specific month."""
        year = int(request.query_params.get('year', timezone.now().year))
        month = int(request.query_params.get('month', timezone.now().month))
        
        from datetime import date
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        
        holidays = self.get_queryset().filter(
            date__gte=start_date,
            date__lt=end_date
        )
        serializer = self.get_serializer(holidays, many=True)
        return Response(serializer.data)


class AttendanceReportViewSet(viewsets.ViewSet):
    """ViewSet for attendance reports."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def statistics(self, request):
        """Generate attendance statistics."""
        school_class_id = request.data.get('school_class_id')
        section_id = request.data.get('section_id')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = DailyAttendance.objects.filter(date__range=[start_date, end_date])
        
        if school_class_id:
            # Filter by enrolled students
            student_ids = ClassEnrollment.objects.filter(
                school_class_id=school_class_id,
                status='active'
            ).values_list('student_id', flat=True)
            queryset = queryset.filter(student_id__in=student_ids)
        
        # Calculate statistics
        total_records = queryset.count()
        present_count = queryset.filter(status='present').count()
        absent_count = queryset.filter(status='absent').count()
        late_count = queryset.filter(status='late').count()
        excused_count = queryset.filter(status='excused').count()
        
        attendance_percentage = 0
        if total_records > 0:
            attendance_percentage = ((present_count + excused_count) / total_records) * 100
        
        # Daily breakdown
        daily_stats = queryset.values('date').annotate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent'))
        ).order_by('date')
        
        return Response({
            'total_records': total_records,
            'present_count': present_count,
            'absent_count': absent_count,
            'late_count': late_count,
            'excused_count': excused_count,
            'attendance_percentage': round(attendance_percentage, 2),
            'daily_breakdown': list(daily_stats)
        })
    
    @action(detail=False, methods=['get'])
    def defaulters(self, request):
        """Get list of students with low attendance."""
        school_class_id = request.query_params.get('school_class_id')
        threshold = float(request.query_params.get('threshold', 75.0))
        
        # Get latest summaries
        summaries = AttendanceSummary.objects.filter(
            attendance_percentage__lt=threshold
        ).select_related('student')
        
        if school_class_id:
            student_ids = ClassEnrollment.objects.filter(
                school_class_id=school_class_id,
                status='active'
            ).values_list('student_id', flat=True)
            summaries = summaries.filter(student_id__in=student_ids)
        
        data = []
        for summary in summaries:
            enrollment = ClassEnrollment.objects.filter(
                student=summary.student,
                status='active'
            ).first()
            
            if enrollment:
                data.append({
                    'student_id': summary.student_id,
                    'student_name': summary.student.get_full_name(),
                    'class_name': enrollment.school_class.class_name,
                    'section_name': enrollment.section.section_name if enrollment.section else None,
                    'attendance_percentage': summary.attendance_percentage,
                    'absent_days': summary.absent_days,
                    'parent_contact': summary.student.phone_number if hasattr(summary.student, 'phone_number') else None
                })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def student_detail(self, request):
        """Get detailed attendance for a specific student."""
        student_id = request.query_params.get('student_id')
        
        if not student_id:
            return Response(
                {'error': 'student_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get student info
        from apps.users.models import CustomUser
        try:
            student = CustomUser.objects.get(id=student_id, is_student=True)
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'Student not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get enrollment
        enrollment = ClassEnrollment.objects.filter(
            student=student,
            status='active'
        ).first()
        
        if not enrollment:
            return Response(
                {'error': 'Student is not enrolled in any active class'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get attendance policy
        policy = AttendancePolicy.objects.filter(
            school_class=enrollment.school_class
        ).first()
        
        required_percentage = policy.minimum_percentage if policy else 75.0
        
        # Get monthly summaries
        summaries = AttendanceSummary.objects.filter(student=student).order_by('-month')[:12]
        
        monthly_data = []
        for summary in summaries:
            monthly_data.append({
                'month': summary.month.strftime('%B %Y'),
                'working_days': summary.total_working_days,
                'present_days': summary.present_days,
                'absent_days': summary.absent_days,
                'attendance_percentage': summary.attendance_percentage
            })
        
        # Calculate overall stats
        total_working_days = sum(s.total_working_days for s in summaries)
        present_days = sum(s.present_days for s in summaries)
        absent_days = sum(s.absent_days for s in summaries)
        late_days = sum(s.late_days for s in summaries)
        excused_days = sum(s.excused_days for s in summaries)
        
        attendance_percentage = 0
        if total_working_days > 0:
            attendance_percentage = ((present_days + excused_days) / total_working_days) * 100
        
        is_compliant = attendance_percentage >= required_percentage
        
        return Response({
            'student_id': student_id,
            'student_name': student.get_full_name(),
            'class_name': enrollment.school_class.class_name,
            'section_name': enrollment.section.section_name if enrollment.section else None,
            'monthly_data': monthly_data,
            'total_working_days': total_working_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'excused_days': excused_days,
            'attendance_percentage': round(attendance_percentage, 2),
            'is_compliant': is_compliant,
            'required_percentage': required_percentage
        })