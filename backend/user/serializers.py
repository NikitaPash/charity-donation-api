"""
Serializers for the user API View.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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


class UserProfileSerializer(UserSerializer):
    """Serializer for the user profile."""

    role = serializers.CharField(source='get_role_display', read_only=True)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['first_name', 'last_name', 'role', 'balance']

    def validate(self, data):
        """Validate that restricted fields (balance, role) are not being updated."""
        restricted_fields = ['balance', 'role']
        for field in restricted_fields:
            if field in self.initial_data:
                user_email = self.instance.email if self.instance else 'unknown'
                logger.warning(f"User {user_email} attempted to update restricted field '{field}'")
                raise ValidationError({field: f'Updating {field} is not allowed.'})

        return data

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
