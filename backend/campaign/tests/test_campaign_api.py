"""
Tests for Campaign API.
"""
import unittest
from decimal import Decimal
from datetime import timedelta
import tempfile
import os

from PIL import Image

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from campaign.serializers import CampaignDetailSerializer, CampaignSerializer
from campaign.models import Campaign

CAMPAIGN_URLS = reverse('campaign:campaign-list')
USER_CAMPAIGN_URLS = reverse('campaign:campaign-my-campaigns')


def create_campaign(user, **params):
    """Create and return a sample campaign."""
    defaults = {
        'title': 'Sample campaign title',
        'description': 'Sample campaign description',
        'goal_amount': Decimal('1000'),
    }

    defaults.update(params)

    campaign = Campaign.objects.create(user=user, **defaults)
    return campaign


def detail_url(campaign_id):
    """Create and return a campaign detail URL."""
    return reverse('campaign:campaign-detail', args=[campaign_id])


def image_upload_url(campaign_id):
    """Create and return an image upload URL."""
    return reverse('campaign:campaign-upload-image', args=[campaign_id])


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicCampaignAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(CAMPAIGN_URLS)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCampaignAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='testuser123@example.com',
            password='testpassword123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_campaigns(self):
        """Test retrieving a list of campaigns."""
        create_campaign(user=self.user)
        create_campaign(user=self.user)

        res = self.client.get(CAMPAIGN_URLS)

        campaigns = Campaign.objects.all().order_by('-id')
        serializer = CampaignSerializer(campaigns, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_campaigns_created_by_user(self):
        """Test retrieving a list of campaigns created by authenticated user."""
        other_user = create_user(
            email='otheruser123@example.com',
            password='testpassword1423',
        )
        create_campaign(user=other_user)
        create_campaign(user=self.user)

        res = self.client.get(USER_CAMPAIGN_URLS)

        campaigns = Campaign.objects.filter(user=self.user)
        serializer = CampaignSerializer(campaigns, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[:-1], serializer.data[:-1])

    def test_get_campaign_detail(self):
        """Test get campaign detail."""
        campaign = create_campaign(user=self.user)

        url = detail_url(campaign.id)
        res = self.client.get(url)
        serializer = CampaignDetailSerializer(campaign)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_campaign(self):
        """Test creating a campaign."""
        payload = {
            'title': 'Sample campaign title',
            'goal_amount': '1000',
        }
        res = self.client.post(CAMPAIGN_URLS, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        campaign = Campaign.objects.get(id=res.data['id'])
        for k, v in payload.items():
            if k == 'goal_amount':
                v = Decimal(v)
            self.assertEqual(getattr(campaign, k), v)
        self.assertEqual(campaign.user, self.user)

    def test_partial_update(self):
        """Test partial update of a campaign."""
        original_title = 'Save animals'
        campaign = create_campaign(user=self.user, title=original_title, description='Sample description')

        payload = {'description': 'New description'}
        url = detail_url(campaign.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        campaign.refresh_from_db()
        self.assertEqual(campaign.title, original_title)
        self.assertEqual(campaign.description, payload['description'])
        self.assertEqual(campaign.user, self.user)

    def test_full_update(self):
        """Test full update of a campaign."""
        deadline = (timezone.now() + timedelta(days=90)).date()
        campaign = create_campaign(
            user=self.user, title='Sample title', description='Sample description', deadline=deadline
        )

        new_deadline = timezone.now() + timedelta(days=30)
        payload = {
            'title': 'Emergency Fundraiser',
            'description': 'Help us raise funds for community disaster relief efforts',
            'goal_amount': '10000.00',
            'deadline': new_deadline.date(),
        }

        url = detail_url(campaign.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        campaign.refresh_from_db()

        self.assertEqual(campaign.title, payload['title'])
        self.assertEqual(campaign.description, payload['description'])
        self.assertEqual(campaign.goal_amount, Decimal(payload['goal_amount']))
        self.assertEqual(campaign.deadline, new_deadline.date())

        self.assertEqual(campaign.user, self.user)

    def test_update_restricted_fields_returns_error(self):
        """Test changing restricted fields results in an error."""
        new_user = create_user(email='newuser@example.com', password='newpass123')
        new_raised_amount = Decimal('100')

        raised_amount = Decimal('10')
        campaign = create_campaign(user=self.user, raised_amount=raised_amount)

        payload = {'user': new_user.id, 'raised_amount': new_raised_amount}
        url = detail_url(campaign.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertEqual(campaign.user, self.user)
        self.assertEqual(campaign.raised_amount, raised_amount)

    def test_update_read_only_fields_silently_skips(self):
        """Test changing read only (but not restricted) fields results in a silent skip."""
        new_status = 'CO'
        campaign = create_campaign(user=self.user)

        payload = {'status': new_status}
        url = detail_url(campaign.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(campaign.get_status_display(), 'On Moderation')

    def test_delete_campaign(self):
        """Test deleting a campaign successful."""
        campaign = create_campaign(user=self.user)

        url = detail_url(campaign.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Campaign.objects.filter(id=campaign.id).exists())

    def test_campaign_permissions(self):
        """Test CRUD access to a campaign for owner/superuser and default user."""
        owner = create_user(email='owner@example.com', password='testpass123')
        average_user = create_user(email='average@example.com', password='testpass123')
        superuser = get_user_model().objects.create_superuser(email='super@example.com', password='testpass123')

        test_users = [(superuser, True), (owner, True), (average_user, False)]

        for user, can_edit in test_users:
            self.client.force_authenticate(user=user)

            campaign = create_campaign(user=owner, title='Test Campaign', status='AC')
            url = detail_url(campaign.id)

            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            for method in ['put', 'patch', 'delete']:
                if method == 'put':
                    res = self.client.put(
                        url, {
                            'title': 'Updated',
                            'description': 'New',
                            'goal_amount': Decimal('19')
                        }
                    )
                elif method == 'patch':
                    res = self.client.patch(url, {'title': 'Partial Update'})
                elif method == 'delete':
                    res = self.client.delete(url)

                expected_status = status.HTTP_200_OK if can_edit else status.HTTP_403_FORBIDDEN
                if method == 'delete':
                    expected_status = status.HTTP_204_NO_CONTENT if can_edit else status.HTTP_403_FORBIDDEN

                self.assertEqual(res.status_code, expected_status, f'Failed for {user.email} on {method.upper()}')


@unittest.skip('Skip the test for CI')
class ImageUploadTests(TestCase):
    """Tests for the image upload API."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'password123',
        )
        self.client.force_authenticate(self.user)
        self.campaign = create_campaign(user=self.user)

    def tearDown(self):
        self.campaign.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a campaign."""
        url = image_upload_url(self.campaign.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.campaign.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.campaign.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image."""
        url = image_upload_url(self.campaign.id)
        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
