from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecruitmentSlotViewSet, TeamApplicationViewSet, TeamViewSet

router = DefaultRouter()
router.register(r'applications', TeamApplicationViewSet, basename='team-application')
router.register(r'recruitment-slots', RecruitmentSlotViewSet, basename='recruitment-slot')
router.register(r'', TeamViewSet, basename='team')

app_name = 'teams'

urlpatterns = [
    path('', include(router.urls)),
]
