"""
Serializers for the campaign API view.
"""
from rest_framework import serializers

from main_app.serializer_utils import RestrictedFieldValidatorMixin

from .models import Campaign


class CampaignSerializer(serializers.ModelSerializer):
    """Serializer for campaigns."""

    class Meta:
        model = Campaign
        fields = ['id', 'title', 'goal_amount', 'raised_amount', 'status', 'deadline']
        read_only_fields = ['id', 'raised_amount', 'status']


class CampaignDetailSerializer(RestrictedFieldValidatorMixin, CampaignSerializer):
    """Serializer for campaign detail view."""

    class Meta(CampaignSerializer.Meta):
        fields = CampaignSerializer.Meta.fields + ['user', 'description', 'created_at']
        read_only_fields = CampaignSerializer.Meta.read_only_fields + ['user', 'created_at']
        restricted_fields = ['raised_amount', 'user']
