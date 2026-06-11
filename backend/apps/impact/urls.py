from django.urls import path

from .views import ImpactAnalyticsView, MyImpactRecordsView

app_name = 'impact'

urlpatterns = [
    path('analytics/', ImpactAnalyticsView.as_view(), name='analytics'),
    path('records/', MyImpactRecordsView.as_view(), name='my_records'),
]
