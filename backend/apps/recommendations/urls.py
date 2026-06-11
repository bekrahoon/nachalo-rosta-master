from django.urls import path

from .views import MyRecommendationsView, RefreshRecommendationsView

app_name = 'recommendations'

urlpatterns = [
    path('', MyRecommendationsView.as_view(), name='my_recommendations'),
    path('refresh/', RefreshRecommendationsView.as_view(), name='refresh'),
]
