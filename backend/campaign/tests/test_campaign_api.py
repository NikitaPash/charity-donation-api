"""
Tests for recipe API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from ..serializers import CampaignSerializer
from ..models import Campaign

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
        self.assertEqual(res.data, serializer.data)
