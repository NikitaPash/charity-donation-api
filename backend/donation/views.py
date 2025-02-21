"""
Views for the Donation API.
"""
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse
from django.core.cache import cache

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from campaign.models import Campaign

from main_app.receipt_gen import generate_receipt

from .models import Donation
from .serializers import DonationSerializer

import logging

logger = logging.getLogger(__name__)


class DonationViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve ordered donations."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def list(self, request, *args, **kwargs):  # noqa
        """Retrieve ordered donations with caching."""
        cache_key = f'donation_list_{request.user.id}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 60 * 5)
        return response

    def create(self, request, *args, **kwargs):
        """Handle donation creation with validation."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
                donation = serializer.save(user=request.user)

                campaign = donation.campaign
                amount = donation.amount
                user = request.user

                Campaign.objects.filter(pk=campaign.pk).update(raised_amount=F('raised_amount') + amount)

                campaign.refresh_from_db()
                campaign.save()

                user.deduct_balance(amount)
                user.refresh_from_db()

            cache.delete(f'donation_list_{request.user.id}')
            logger.info(f'Donation was made successfully by {request.user.email}')
            return Response({ # noqa
                'status': 'Donation successful',
                'new_balance': user.balance,
                'campaign_raised': campaign.raised_amount
            }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            logger.warning(f'Donation validation failed for {request.user.email}: {e.detail}')
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        """Create a new donation."""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def receipt(self, request, pk=None):
        """Generate a receipt for a specific donation."""
        donation = self.get_object()

        if donation.user != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        receipt_buffer = generate_receipt(donation)
        response = HttpResponse(receipt_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{donation.id}.pdf"'

        return response
