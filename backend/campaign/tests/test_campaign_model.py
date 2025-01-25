"""
Tests for Campaign model.
"""
from decimal import Decimal
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Campaign


class CampaignModelTests(TestCase):
    """Test Campaign model."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'testuser123@example.com',
            'testpassword123',
        )

    def test_create_campaign(self):
        """Test creating a campaign object."""
        campaign = Campaign.objects.create(
            user=self.user,
            title='Sample campaign title',
            description='Sample campaign description',
            goal_amount=Decimal('1000')
        )

        self.assertEqual(str(campaign), campaign.title)

    def test_deadline_validation(self):
        """Test throwing an error when wrong deadline provided."""
        with self.assertRaises(ValidationError):
            Campaign.objects.create(
                user=self.user,
                title='Sample campaign title',
                description='Sample campaign description',
                goal_amount=Decimal('1000'),
                deadline=now() - timedelta(days=30),
            )

    def test_status_change(self):
        """Test status code change after goal amount is reached."""
        campaign = Campaign.objects.create(
            user=self.user,
            title='Sample campaign title',
            description='Sample campaign description',
            goal_amount=Decimal('1000'),
        )

        status_when_created = campaign.status
        campaign.raised_amount += Decimal('1001')
        campaign.save()

        self.assertNotEqual(campaign.status, status_when_created)
        self.assertEqual(campaign.status, 'CO')
