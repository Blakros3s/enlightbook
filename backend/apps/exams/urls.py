from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    GradingScaleViewSet, ExamViewSet, ExamDetailViewSet,
    StudentExamStatusViewSet, StudentResultViewSet,
    StudentOverallResultViewSet, ResultModificationLogViewSet,
    ReportCardTemplateViewSet, GeneratedReportCardViewSet,
    MarkEntryViewSet
)

app_name = 'exams'

router = DefaultRouter()
router.register(r'grading-scales', GradingScaleViewSet)
router.register(r'exams', ExamViewSet)
router.register(r'exam-details', ExamDetailViewSet)
router.register(r'student-statuses', StudentExamStatusViewSet)
router.register(r'results', StudentResultViewSet)
router.register(r'overall-results', StudentOverallResultViewSet)
router.register(r'modification-logs', ResultModificationLogViewSet)
router.register(r'report-card-templates', ReportCardTemplateViewSet)
router.register(r'report-cards', GeneratedReportCardViewSet)
router.register(r'mark-entry', MarkEntryViewSet, basename='mark-entry')

urlpatterns = [
    path('', include(router.urls)),
]