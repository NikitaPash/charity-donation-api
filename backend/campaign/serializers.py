"""
Serializers for the campaign API view.
"""
from django.utils.timezone import now

from rest_framework import serializers

from main_app.serializer_utils import RestrictedFieldValidatorMixin

from .models import Campaign


class CampaignSerializer(serializers.ModelSerializer):
    """Serializer for campaigns."""

    class Meta:
        model = Campaign
        fields = ['id', 'title', 'goal_amount', 'raised_amount', 'status', 'deadline']
        read_only_fields = ['id', 'raised_amount', 'status']

    def validate_deadline(self, value):
        """Ensure deadline is in the future."""
        if value <= now():
            raise serializers.ValidationError('Deadline must be in the future.')
        return value


class CampaignDetailSerializer(RestrictedFieldValidatorMixin, CampaignSerializer):
    """Serializer for campaign detail view."""

    class Meta(CampaignSerializer.Meta):
        fields = CampaignSerializer.Meta.fields + ['user', 'description', 'created_at', 'image']
        read_only_fields = CampaignSerializer.Meta.read_only_fields + ['user', 'created_at']
        restricted_fields = ['raised_amount', 'user']

    def validate_deadline(self, value):
        return super().validate_deadline(value)


class CampaignImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to campaigns."""

    class Meta:
        model = Campaign
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}
