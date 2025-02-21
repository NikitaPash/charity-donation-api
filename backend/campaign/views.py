"""
Views for the campaign API.
"""
from django.core.cache import cache

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from rest_framework_simplejwt.authentication import JWTAuthentication

from main_app.permissions import IsCampaignManager

from .serializers import CampaignDetailSerializer, CampaignImageSerializer, CampaignSerializer
from .models import Campaign

import logging

logger = logging.getLogger(__name__)


class CampaignViewSet(viewsets.ModelViewSet):
    """View for manage campaign API."""
    serializer_class = CampaignDetailSerializer
    queryset = Campaign.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCampaignManager]

    def get_queryset(self):
        """Retrieve ordered campaigns."""
        return self.queryset.order_by('-id')

    def perform_create(self, serializer):
        """Create a new campaign."""
        serializer.save(user=self.request.user)
        self._invalidate_cache()

    def get_serializer_class(self):
        """Return a serializer class for request."""
        actions = ['list', 'my_campaigns', 'create']
        if self.action in actions:
            return CampaignSerializer
        elif self.action == 'upload_image':
            return CampaignImageSerializer

        return self.serializer_class

    def list(self, request, *args, **kwargs):  # noqa
        """Retrieve ordered campaigns with caching."""
        cache_key = 'campaign_list'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 60 * 5)
        return response

    def create(self, request, *args, **kwargs):
        """Handle campaign creation."""
        try:
            response = super().create(request, *args, **kwargs)
            self._invalidate_cache()
            logger.info(f'New campaign created successfully by {request.user.email}')
            return response
        except ValidationError as e:
            logger.warning(f'Campaign creation validation error for {request.user.email}: {e.detail}')
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Handle campaign update."""
        response = super().update(request, *args, **kwargs)
        self._invalidate_cache()
        return response

    def partial_update(self, request, *args, **kwargs):
        """Handle campaign partial update."""
        response = super().partial_update(request, *args, **kwargs)
        self._invalidate_cache()
        return response

    def destroy(self, request, *args, **kwargs):
        """Handle campaign deletion."""
        response = super().destroy(request, *args, **kwargs)
        self._invalidate_cache()
        return response

    @action(methods=['GET'], detail=False, url_path='my-campaigns')
    def my_campaigns(self, request):
        """Retrieve campaigns created by the requesting user with caching."""
        cache_key = f'my_campaigns_{request.user.id}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        campaigns = self.get_queryset().filter(user=request.user)
        serializer = CampaignSerializer(campaigns, many=True)
        cache.set(cache_key, serializer.data, 60 * 5)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to campaign."""
        campaign = self.get_object()
        serializer = self.get_serializer(campaign, data=request.data)

        if serializer.is_valid():
            serializer.save()
            self._invalidate_cache()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _invalidate_cache(self):
        """Clear campaign-related cache."""
        cache.delete('campaign_list')
        cache.delete(f'my_campaigns_{self.request.user.id}')
