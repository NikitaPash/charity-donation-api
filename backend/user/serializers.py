"""
Serializers for the user API View.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model

from rest_framework import serializers

from main_app.serializer_utils import RestrictedFieldValidatorMixin

import logging

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)


class UserProfileSerializer(RestrictedFieldValidatorMixin, UserSerializer):
    """Serializer for the user profile."""

    role = serializers.CharField(source='get_role_display', read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['first_name', 'last_name', 'role', 'balance']
        restricted_fields = ['balance', 'role']
        read_only_fields = ['balance', 'role']

    def update(self, instance, validated_data):
        """Update and return a user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
            logger.info(f'User {user.email} updated their password')

        return user


class TopUpSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
