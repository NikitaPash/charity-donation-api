"""
Views for the campaign API.
"""
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import CampaignSerializer
from .models import Campaign

import logging

logger = logging.getLogger(__name__)


class CampaignViewSet(viewsets.ModelViewSet):
    """View for manage campaign API."""
    serializer_class = CampaignSerializer
    queryset = Campaign.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve ordered campaigns."""
        return self.queryset.all().order_by('-id')

    def perform_create(self, serializer):
        """Create a new campaign."""
        serializer.save(user=self.request.user)

    @action(methods=['GET'], detail=False, url_path='my-campaigns')
    def my_campaigns(self, request):
        """Retrieve campaigns created by request user."""
        campaigns = self.get_queryset().filter(user=request.user)
        serializer = CampaignSerializer(campaigns, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
