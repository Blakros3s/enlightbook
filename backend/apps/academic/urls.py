from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AcademicYearViewSet, SemesterViewSet, SubjectCategoryViewSet,
    SubjectViewSet, ClassViewSet, SectionViewSet,
    TeacherClassAssignmentViewSet, StudentSubjectEnrollmentViewSet,
    ClassEnrollmentViewSet
)

app_name = 'academic'

router = DefaultRouter()
router.register(r'academic-years', AcademicYearViewSet)
router.register(r'semesters', SemesterViewSet)
router.register(r'subject-categories', SubjectCategoryViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'classes', ClassViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'teacher-assignments', TeacherClassAssignmentViewSet)
router.register(r'student-enrollments', StudentSubjectEnrollmentViewSet)
router.register(r'class-enrollments', ClassEnrollmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
