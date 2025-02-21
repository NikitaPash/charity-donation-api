"""
Tests for Campaign model.
"""
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from campaign.models import Campaign, campaign_image_file_path


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

    @patch('campaign.models.uuid.uuid4')
    def test_campaign_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = campaign_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/campaign/{uuid}.jpg')
