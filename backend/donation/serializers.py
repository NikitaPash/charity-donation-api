"""
Serializers for the donation API view.
"""
from rest_framework import serializers

from .models import Donation

from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class DonationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Donation
        fields = ['id', 'campaign', 'amount', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        """Validate donation amount against user balance."""
        user = self.context['request'].user
        amount = attrs.get('amount', Decimal('0.00'))

        if amount <= Decimal('0.00'):
            logger.warning(f'Invalid donation amount attempt by {user.email}: {amount}')
            raise serializers.ValidationError({'amount': 'Donation amount must be positive.'})

        if amount > user.balance:
            logger.warning(
                f'Insufficient balance for donation by {user.email}. '
                f'Required: {amount}, Available: {user.balance}'
            )
            raise serializers.ValidationError({'amount': 'Insufficient balance for donation.'})

        return attrs
