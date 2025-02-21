"""
Tests for Donation model.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from campaign.models import Campaign

from donation.models import Donation


class DonationModelTests(TestCase):
    """Test Donation model."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'testuser123@example.com',
            'testpassword123',
        )

    def test_create_donation(self):
        """Test creating a donation object."""
        campaign = Campaign.objects.create(
            user=self.user,
            title='Sample campaign title',
            description='Sample campaign description',
            goal_amount=Decimal('1000')
        )

        donation = Donation.objects.create(user=self.user, campaign=campaign, amount=Decimal('100'))

        self.assertTrue(Donation.objects.filter(id=donation.id).exists())
