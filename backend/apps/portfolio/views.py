from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import PortfolioSerializer
from .services import build_portfolio_context


class PortfolioSummaryView(APIView):
    """JSON-сводка портфолио текущего пользователя"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        context = build_portfolio_context(request.user)
        serializer = PortfolioSerializer(context)
        return Response(serializer.data)


class PortfolioPDFView(APIView):
    """Скачать портфолио волонтёра в виде PDF"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from weasyprint import HTML

        context = build_portfolio_context(request.user)
        html_string = render_to_string('portfolio/portfolio_pdf.html', context)

        pdf_bytes = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        filename = f'portfolio_{request.user.email.split("@")[0]}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
