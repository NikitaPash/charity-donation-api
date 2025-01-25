"""
Serializers for the campaign API view.
"""
from rest_framework import serializers

from .models import Campaign


class CampaignSerializer(serializers.ModelSerializer):
    """Serializer for campaigns."""

    class Meta:
        model = Campaign
        fields = [
            'id', 'user', 'title', 'description', 'goal_amount', 'raised_amount', 'status', 'deadline', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'raised_amount', 'status', 'created_at']
