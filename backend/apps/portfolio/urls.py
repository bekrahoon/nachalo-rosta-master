from django.urls import path

from .views import PortfolioPDFView, PortfolioSummaryView

app_name = 'portfolio'

urlpatterns = [
    path('', PortfolioSummaryView.as_view(), name='summary'),
    path('export/', PortfolioPDFView.as_view(), name='export_pdf'),
]
