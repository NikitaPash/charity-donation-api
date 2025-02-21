"""
Tests for Donation API..
"""
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from decimal import Decimal

from rest_framework import status
from rest_framework.test import APIClient

from campaign.models import Campaign

from donation.models import Donation
from donation.serializers import DonationSerializer

DONATIONS_URL = reverse('donation:donation-list')


def receipt_url(donation_id):
    return reverse('donation:donation-receipt', args=[donation_id])


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicDonationAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required to access donations endpoints."""
        res = self.client.get(DONATIONS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_donation_unauthorized(self):
        """Test creating a donation without authentication returns error."""
        payload = {'campaign': 1, 'amount': '100.00'}
        res = self.client.post(DONATIONS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_receipt_unauthorized(self):
        """Test accessing receipt without authentication returns error."""
        campaign = Campaign.objects.create(
            user=create_user(email='campaign@example.com', password='testpass'),
            title='Test Campaign',
            goal_amount=1000
        )
        donation = Donation.objects.create(
            user=create_user(email='test@example.com', password='testpass'),
            campaign=campaign,
            amount=Decimal('100.00')
        )
        url = receipt_url(donation.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDonationAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='testuser@example.com', password='testpass123', balance=Decimal('1000.00'))
        self.client.force_authenticate(self.user)
        self.campaign = Campaign.objects.create(user=self.user, title='Test Campaign', goal_amount=Decimal('5000.00'))

    def test_retrieve_donations(self):
        """Test retrieving a list of user's donations ordered by latest."""
        Donation.objects.create(user=self.user, campaign=self.campaign, amount=Decimal('100.00'))
        Donation.objects.create(user=self.user, campaign=self.campaign, amount=Decimal('200.00'))

        res = self.client.get(DONATIONS_URL)

        donations = Donation.objects.filter(user=self.user).order_by('-id')
        serializer = DonationSerializer(donations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[:-1], serializer.data[:-1])

    def test_donations_limited_to_user(self):
        """Test donations returned are limited to the authenticated user."""
        other_user = create_user(email='other@example.com', password='testpass123')
        other_campaign = Campaign.objects.create(
            user=other_user, title='Other Campaign', goal_amount=Decimal('2000.00')
        )
        Donation.objects.create(user=other_user, campaign=other_campaign, amount=500.00)
        donation = Donation.objects.create(user=self.user, campaign=self.campaign, amount=300.00)

        res = self.client.get(DONATIONS_URL)

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], donation.id)
        self.assertEqual(res.data[0]['amount'], '300.00')

    def test_create_donation_success(self):
        """Test creating a donation successfully updates user balance and campaign."""
        payload = {'campaign': self.campaign.id, 'amount': '500.00'}
        initial_balance = self.user.balance

        res = self.client.post(DONATIONS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.user.refresh_from_db()
        self.campaign.refresh_from_db()
        self.assertEqual(self.user.balance, initial_balance - Decimal(payload['amount']))
        self.assertEqual(self.campaign.raised_amount, Decimal(payload['amount']))
        self.assertIn('new_balance', res.data)
        self.assertIn('campaign_raised', res.data)

    def test_create_donation_insufficient_balance(self):
        """Test creating a donation with insufficient balance returns error."""
        payload = {'campaign': self.campaign.id, 'amount': '1500.00'}
        res = self.client.post(DONATIONS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.campaign.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal('1000.00'))
        self.assertEqual(self.campaign.raised_amount, Decimal('0.00'))

    def test_create_donation_invalid_amount(self):
        """Test creating a donation with invalid amount returns error."""
        payload = {'campaign': self.campaign.id, 'amount': '-100.00'}
        res = self.client.post(DONATIONS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_receipt_generation(self):
        """Test generating a receipt for a user's donation."""
        donation = Donation.objects.create(user=self.user, campaign=self.campaign, amount=Decimal('250.00'))
        url = receipt_url(donation.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename="receipt_', res['Content-Disposition'])
