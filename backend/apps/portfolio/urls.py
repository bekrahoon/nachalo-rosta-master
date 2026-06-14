from django.urls import path

from .views import (
    PortfolioProfileView,
    PortfolioSummaryView,
    SavedListingDetailView,
    SavedListingListView,
)

app_name = 'portfolio'

urlpatterns = [
    path('', PortfolioSummaryView.as_view(), name='summary'),
    path('profile/', PortfolioProfileView.as_view(), name='profile'),
    path('saved/', SavedListingListView.as_view(), name='saved_list'),
    path('saved/<uuid:listing_id>/', SavedListingDetailView.as_view(), name='saved_detail'),
]
